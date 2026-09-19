from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from sqlalchemy import select, func, literal, desc, union_all
import string
import random
import traceback
from datetime import timezone, datetime
from uuid import UUID

from . import models, schemas
from .database import get_db
from .auth import verify_admin_role, verify_cron_job
from .logger import setup_logger

logger = setup_logger()

app = FastAPI(
    title="Gud Fud API",
    description="Public search and catalogue API for transparent food label analysis.",
    version="1.0.0"
)

@app.get("/v1/admin/fix-market")
def fix_market(db: Session = Depends(get_db)):
    # Create or get India market
    market_in = db.query(models.Market).filter_by(country_code="IN").first()
    if not market_in:
        market_in = models.Market(name="India", country_code="IN")
        db.add(market_in)
        db.flush()
    
    # Update all product variants to India
    db.query(models.ProductVariant).update({"market_id": market_in.id})
    db.commit()
    return {"status": "fixed", "market_id": market_in.id}

@app.get("/v1/catalogue", response_model=schemas.PaginatedCatalogue)
def get_catalogue(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(24, ge=1, le=100, description="Items per page"),
    market: str = Query(None, description="Market code to filter by"),
    db: Session = Depends(get_db)
):
    offset = (page - 1) * size

    # Build the core query to retrieve current, published product variants
    query = (
        select(
            models.Product.slug,
            models.Product.canonical_name,
            models.Brand.name.label("brand_name"),
            models.Brand.slug.label("brand_slug"),
            models.Category.name.label("category_name"),
            models.Category.slug.label("category_slug"),
            models.Rating.band.label("rating_band"),
            models.Rating.confidence_grade,
            models.Market.country_code.label("market_code"),
            models.LabelVersion.label_image_id.label("image_url"),
            models.Rating.published_at.label("last_reviewed_at")
        )
        .select_from(models.Product)
        .join(models.Brand, models.Product.brand_id == models.Brand.id)
        .join(models.Category, models.Product.category_id == models.Category.id)
        .join(models.ProductVariant, models.ProductVariant.product_id == models.Product.id)
        .join(models.Market, models.ProductVariant.market_id == models.Market.id)
        .join(models.LabelVersion, models.LabelVersion.variant_id == models.ProductVariant.id)
        .join(models.Rating, models.Rating.label_version_id == models.LabelVersion.id)
        .where(
            models.Product.status == "active",
            models.LabelVersion.review_status == "published"
        )
    )

    if market:
        query = query.where(models.Market.country_code == market.upper())

    # Calculate total matching records
    total_query = select(func.count()).select_from(query.subquery())
    total = db.scalar(total_query) or 0

    # Execute the paginated query
    paginated_query = query.limit(size).offset(offset)
    results = db.execute(paginated_query).all()

    # Format the response to match the Pydantic schema structure
    items = []
    for row in results:
        items.append({
            "slug": row.slug,
            "canonical_name": row.canonical_name,
            "brand": {
                "name": row.brand_name,
                "slug": row.brand_slug
            },
            "category": {
                "name": row.category_name,
                "slug": row.category_slug
            },
            "rating_band": row.rating_band,
            "confidence_grade": row.confidence_grade,
            "market_code": row.market_code,
            "image_url": row.image_url,
            "last_reviewed_at": row.last_reviewed_at
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size
    }

@app.get("/v1/search", response_model=schemas.SearchResponse)
def search_catalogue(
    q: str = Query(..., min_length=2, description="Search query string"),
    limit: int = Query(10, ge=1, le=50, description="Max results"),
    market: str = Query(None, description="Market code to filter by"),
    db: Session = Depends(get_db)
):
    product_query = select(
        literal("product").label("type"),
        models.Product.canonical_name.label("name"),
        models.Product.slug,
        models.Brand.name.label("subtitle"),
        func.similarity(models.Product.canonical_name, q).label("sim_score")
    ).join(models.Brand, models.Product.brand_id == models.Brand.id).where(
        models.Product.status == "active",
        func.similarity(models.Product.canonical_name, q) > 0.1
    )

    brand_query = select(
        literal("brand").label("type"),
        models.Brand.name.label("name"),
        models.Brand.slug,
        literal("Brand").label("subtitle"),
        func.similarity(models.Brand.name, q).label("sim_score")
    ).where(
        models.Brand.status == "active",
        func.similarity(models.Brand.name, q) > 0.1
    )

    gtin_query = select(
        literal("product").label("type"),
        models.Product.canonical_name.label("name"),
        models.Product.slug,
        models.ProductVariant.gtin.label("subtitle"),
        literal(1.0).label("sim_score")
    ).join(models.ProductVariant, models.ProductVariant.product_id == models.Product.id).where(
        models.Product.status == "active",
        models.ProductVariant.gtin == q
    )

    if market:
        market = market.upper()
        market_subquery = select(models.ProductVariant.product_id).join(models.Market, models.ProductVariant.market_id == models.Market.id).where(models.Market.country_code == market)
        product_query = product_query.where(models.Product.id.in_(market_subquery))
        gtin_query = gtin_query.join(models.Market, models.ProductVariant.market_id == models.Market.id).where(models.Market.country_code == market)

    combined = union_all(product_query, brand_query, gtin_query).alias("combined")
    final_query = select(combined).order_by(desc(combined.c.sim_score)).limit(limit)

    results = db.execute(final_query).all()

    items = []
    for row in results:
        items.append({
            "type": row.type,
            "name": row.name,
            "slug": row.slug,
            "subtitle": row.subtitle,
            "similarity_score": float(row.sim_score)
        })

    return {
        "query": q,
        "items": items
    }

@app.get("/v1/products/{slug}", response_model=schemas.ProductAnalysis)
def get_product_analysis(
    slug: str,
    db: Session = Depends(get_db)
):
    # Fetch the core product, current published variant, and rating
    result = (
        db.query(
            models.Product.slug,
            models.Product.canonical_name,
            models.Brand.name.label("brand_name"),
            models.Market.country_code.label("market_code"),
            models.Rating.total_score.label("rating_total"),
            models.Rating.band.label("rating_band"),
            models.Rating.confidence_grade,
            models.Rating.explanation,
            models.Rating.published_at.label("last_reviewed_at"),
            models.LabelVersion.label_image_id.label("image_url"),
            models.LabelVersion.id.label("label_version_id")
        )
        .join(models.Brand, models.Product.brand_id == models.Brand.id)
        .join(models.ProductVariant, models.ProductVariant.product_id == models.Product.id)
        .join(models.Market, models.ProductVariant.market_id == models.Market.id)
        .join(models.LabelVersion, models.LabelVersion.variant_id == models.ProductVariant.id)
        .join(models.Rating, models.Rating.label_version_id == models.LabelVersion.id)
        .filter(
            models.Product.slug == slug,
            models.Product.status == "active",
            models.LabelVersion.review_status == "published"
        )
        .first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Product not found or not yet published")

    # Fetch Nutrition Facts
    nutrition = db.query(models.NutritionFacts).filter(
        models.NutritionFacts.label_version_id == result.label_version_id
    ).first()

    # Fetch ordered ingredients and their canonical mappings
    ingredients_query = (
        db.query(
            models.LabelIngredient.label_text,
            models.LabelIngredient.position,
            models.Ingredient.canonical_name,
            models.Ingredient.slug
        )
        .outerjoin(models.Ingredient, models.LabelIngredient.ingredient_id == models.Ingredient.id)
        .filter(models.LabelIngredient.label_version_id == result.label_version_id)
        .order_by(models.LabelIngredient.position)
        .all()
    )

    mapped_ingredients = [
        {
            "label_text": ing.label_text,
            "position": ing.position,
            "canonical_name": ing.canonical_name,
            "slug": ing.slug
        } for ing in ingredients_query
    ]

    return schemas.ProductAnalysis(
        slug=result.slug,
        canonical_name=result.canonical_name,
        brand_name=result.brand_name,
        market_code=result.market_code,
        rating_total=result.rating_total,
        rating_band=result.rating_band,
        confidence_grade=result.confidence_grade,
        explanation=result.explanation,
        nutrition=nutrition,
        ingredients=mapped_ingredients,
        image_url=result.image_url,
        last_reviewed_at=result.last_reviewed_at
    )

@app.get("/v1/ingredients/{slug}", response_model=schemas.IngredientAnalysis)
def get_ingredient_analysis(slug: str, db: Session = Depends(get_db)):
    # 1. Retrieve canonical ingredient or resolve from an alias
    ingredient = db.query(models.Ingredient).filter(
        models.Ingredient.slug == slug,
        models.Ingredient.status == "active"
    ).first()

    if not ingredient:
        alias = db.query(models.IngredientAlias).filter(
            models.IngredientAlias.alias_normalized == slug.lower()
        ).first()
        if alias:
            ingredient = db.query(models.Ingredient).filter(
                models.Ingredient.id == alias.ingredient_id,
                models.Ingredient.status == "active"
            ).first()

    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    # 2. Fetch Aliases
    aliases = [a[0] for a in db.query(models.IngredientAlias.alias).filter(
        models.IngredientAlias.ingredient_id == ingredient.id
    ).all()]

    # 3. Fetch Evidence & Sources
    evidence_records = db.query(models.IngredientEvidence).filter(
        models.IngredientEvidence.ingredient_id == ingredient.id,
        models.IngredientEvidence.review_status == "published"
    ).all()

    evidence_list = []
    for ev in evidence_records:
        sources = db.query(models.Source).join(
            models.EvidenceSource, models.EvidenceSource.source_id == models.Source.id
        ).filter(models.EvidenceSource.ingredient_evidence_id == ev.id).all()
        
        evidence_list.append({
            "effect_type": ev.effect_type,
            "population": ev.population,
            "dose_context": ev.dose_context,
            "evidence_grade": ev.evidence_grade,
            "summary": ev.summary,
            "jurisdiction": ev.jurisdiction,
            "sources": [{"title": s.title, "publisher": s.publisher, "url": s.url, "publication_date": s.publication_date} for s in sources]
        })

    # 4. Fetch Regulatory Statuses & Jurisdiction
    reg_records = db.query(models.RegulatoryStatus, models.Market.country_code).join(
        models.Market, models.RegulatoryStatus.market_id == models.Market.id
    ).filter(models.RegulatoryStatus.ingredient_id == ingredient.id).all()

    reg_list = []
    for reg, market_code in reg_records:
        source_dict = None
        if reg.source_id:
            src = db.query(models.Source).filter(models.Source.id == reg.source_id).first()
            if src:
                source_dict = {"title": src.title, "publisher": src.publisher, "url": src.url, "publication_date": src.publication_date}
        
        reg_list.append({
            "market_code": market_code,
            "status": reg.status,
            "use_category": reg.use_category,
            "conditions": reg.conditions,
            "max_level": reg.max_level,
            "effective_from": reg.effective_from,
            "source": source_dict
        })

    # 5. Fetch published products currently using this ingredient
    product_records = db.query(
        models.Product.slug,
        models.Product.canonical_name,
        models.Brand.name.label("brand_name"),
        models.Rating.band.label("rating_band")
    ).select_from(models.Product).join(
        models.Brand, models.Product.brand_id == models.Brand.id
    ).join(
        models.ProductVariant, models.ProductVariant.product_id == models.Product.id
    ).join(
        models.LabelVersion, models.LabelVersion.variant_id == models.ProductVariant.id
    ).join(
        models.LabelIngredient, models.LabelIngredient.label_version_id == models.LabelVersion.id
    ).outerjoin(
        models.Rating, models.Rating.label_version_id == models.LabelVersion.id
    ).filter(
        models.LabelIngredient.ingredient_id == ingredient.id,
        models.Product.status == "active",
        models.LabelVersion.review_status == "published"
    ).distinct().all()

    return {
        "slug": ingredient.slug,
        "canonical_name": ingredient.canonical_name,
        "INS_number": ingredient.INS_number,
        "E_number": ingredient.E_number,
        "ingredient_type": ingredient.ingredient_type,
        "technical_function": ingredient.technical_function,
        "public_summary": ingredient.public_summary,
        "aliases": aliases,
        "evidence": evidence_list,
        "regulatory_statuses": reg_list,
        "products": [{"slug": p.slug, "canonical_name": p.canonical_name, "brand_name": p.brand_name, "rating_band": p.rating_band} for p in product_records]
    }

@app.get("/v1/compare/{product_slug}", response_model=schemas.ProductComparisonResponse)
def compare_product_variants(
    product_slug: str,
    markets: List[str] = Query(..., description="List of market country codes to compare"),
    db: Session = Depends(get_db)
):
    # 1. Fetch the canonical product
    product = db.query(
        models.Product.id,
        models.Product.slug,
        models.Product.canonical_name,
        models.Brand.name.label("brand_name")
    ).join(
        models.Brand, models.Product.brand_id == models.Brand.id
    ).filter(
        models.Product.slug == product_slug,
        models.Product.status == "active"
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # 2. Fetch variants matching the requested markets
    variants = db.query(
        models.ProductVariant.id.label("variant_id"),
        models.ProductVariant.local_name,
        models.ProductVariant.pack_quantity,
        models.ProductVariant.pack_unit,
        models.Market.country_code.label("market_code")
    ).join(
        models.Market, models.ProductVariant.market_id == models.Market.id
    ).filter(
        models.ProductVariant.product_id == product.id,
        models.Market.country_code.in_(markets)
    ).all()

    variant_cards = []

    for v in variants:
        # 3. Retrieve the current published label version and its rating methodology
        label = db.query(
            models.LabelVersion.id,
            models.LabelVersion.serving_quantity,
            models.LabelVersion.serving_unit,
            models.LabelVersion.captured_at,
            models.MethodologyVersion.version.label("methodology_version")
        ).join(
            models.Rating, models.Rating.label_version_id == models.LabelVersion.id
        ).join(
            models.MethodologyVersion, models.Rating.methodology_version_id == models.MethodologyVersion.id
        ).filter(
            models.LabelVersion.variant_id == v.variant_id,
            models.LabelVersion.review_status == "published"
        ).order_by(
            desc(models.LabelVersion.effective_from)
        ).first()

        if not label:
            continue

        # 4. Fetch normalized nutrition facts
        nutrition = db.query(models.NutritionFacts).filter(
            models.NutritionFacts.label_version_id == label.id
        ).first()

        # 5. Fetch ordered mapped ingredients
        ingredients_query = (
            db.query(
                models.LabelIngredient.label_text,
                models.LabelIngredient.position,
                models.Ingredient.canonical_name,
                models.Ingredient.slug
            )
            .outerjoin(models.Ingredient, models.LabelIngredient.ingredient_id == models.Ingredient.id)
            .filter(models.LabelIngredient.label_version_id == label.id)
            .order_by(models.LabelIngredient.position)
            .all()
        )
        
        mapped_ingredients = [
            {
                "label_text": ing.label_text,
                "position": ing.position,
                "canonical_name": ing.canonical_name,
                "slug": ing.slug
            } for ing in ingredients_query
        ]

        variant_cards.append({
            "market_code": v.market_code,
            "label_version_id": label.id,
            "local_name": v.local_name,
            "pack_quantity": v.pack_quantity,
            "pack_unit": v.pack_unit,
            "serving_quantity": label.serving_quantity,
            "serving_unit": label.serving_unit,
            "captured_at": label.captured_at,
            "methodology_version": label.methodology_version,
            "nutrition": nutrition,
            "ingredients": mapped_ingredients
        })

    return {
        "slug": product.slug,
        "canonical_name": product.canonical_name,
        "brand_name": product.brand_name,
        "variants": variant_cards
    }

@app.get("/v1/products/{slug}/history", response_model=schemas.ProductHistoryResponse)
def get_product_history(
    slug: str,
    db: Session = Depends(get_db)
):
    history_records = (
        db.query(
            models.LabelVersion.id.label("label_version_id"),
            models.LabelVersion.version_no,
            models.LabelVersion.effective_from,
            models.LabelVersion.captured_at,
            models.LabelVersion.review_status.label("status"),
            models.MethodologyVersion.version.label("methodology_version"),
            models.Rating.total_score,
            models.Rating.band.label("rating_band")
        )
        .select_from(models.Product)
        .join(models.ProductVariant, models.ProductVariant.product_id == models.Product.id)
        .join(models.LabelVersion, models.LabelVersion.variant_id == models.ProductVariant.id)
        .join(models.Rating, models.Rating.label_version_id == models.LabelVersion.id)
        .join(models.MethodologyVersion, models.Rating.methodology_version_id == models.MethodologyVersion.id)
        .filter(
            models.Product.slug == slug,
            models.LabelVersion.review_status.in_(["published", "archived"])
        )
        .order_by(desc(models.LabelVersion.effective_from))
        .all()
    )

    formatted_history = []
    for record in history_records:
        formatted_history.append({
            "label_version_id": record.label_version_id,
            "version_no": record.version_no,
            "effective_from": record.effective_from,
            "captured_at": record.captured_at,
            "status": record.status,
            "methodology_version": record.methodology_version,
            "total_score": record.total_score,
            "rating_band": record.rating_band
        })

    return {"history": formatted_history}

def generate_reference_number(length=8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.post("/v1/corrections", status_code=201)
def submit_correction(
    report: schemas.CorrectionReportCreate,
    db: Session = Depends(get_db)
):
    reference = f"CORR-{generate_reference_number()}"
    
    new_report = models.CorrectionReport(
        public_reference=reference,
        reporter_contact=report.reporter_contact,
        entity_type=report.entity_type,
        entity_id=report.entity_id,
        message=report.message,
        evidence_asset_id=report.evidence_asset_id,
        status="open",
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(new_report)
    db.commit()
    
    return {"reference_number": reference, "status": "submitted"}


@app.post("/v1/admin/labels/{label_version_id}/publish")
def publish_label_transaction(
    label_version_id: UUID,
    request: schemas.PublishRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin_role)
):
    try:
        # 1. Lock the label version row to prevent race conditions
        label = db.query(models.LabelVersion).with_for_update().filter(
            models.LabelVersion.id == label_version_id
        ).first()

        if not label:
            raise HTTPException(status_code=404, detail="Label version not found")
        
        if label.review_status == "published":
            raise HTTPException(status_code=400, detail="Label is already published")

        # 2. Archive any currently published versions for this exact product variant
        previous_labels = db.query(models.LabelVersion).filter(
            models.LabelVersion.variant_id == label.variant_id,
            models.LabelVersion.review_status == "published",
            models.LabelVersion.id != label_version_id
        ).all()
        
        for prev in previous_labels:
            prev.review_status = "archived"

        # 3. Mark the target label as published
        label.review_status = "published"

        # 4. Insert the immutable rating tied to the methodology version
        rating = models.Rating(
            label_version_id=label.id,
            methodology_version_id=request.methodology_version_id,
            total_score=request.total_score,
            band=request.band,
            nutrition_score=request.nutrition_score,
            ingredient_score=request.ingredient_score,
            context_score=request.context_score,
            confidence_grade=request.confidence_grade,
            explanation=request.explanation,
            calculated_at=datetime.now(timezone.utc),
            published_at=datetime.now(timezone.utc)
        )
        db.add(rating)

        # 5. Append the immutable audit log
        audit_event = models.AuditLog(
            actor_id=request.actor_id,
            action="publish_label",
            entity_type="label_version",
            entity_id=str(label.id),
            after_json={"status": "published", "methodology": str(request.methodology_version_id)},
            created_at=datetime.now(timezone.utc)
        )
        db.add(audit_event)

        # 6. Queue the search reindexing outbox event
        outbox_event = models.OutboxEvent(
            event_type="label_published",
            payload={
                "label_version_id": str(label.id),
                "product_variant_id": str(label.variant_id)
            },
            status="pending",
            created_at=datetime.now(timezone.utc)
        )
        db.add(outbox_event)

        # 7. Commit the entire transaction atomically
        db.commit()

        return {"status": "success", "published_label_id": label.id}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            "Publication transaction failed",
            extra={
                "label_version_id": str(label_version_id),
                "error": str(e)
            },
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Publication transaction failed")

@app.get("/v1/products/barcode/{gtin}")
def get_product_by_barcode(gtin: str, db: Session = Depends(get_db)):
    result = (
        db.query(models.Product.slug)
        .join(models.ProductVariant, models.ProductVariant.product_id == models.Product.id)
        .join(models.LabelVersion, models.LabelVersion.variant_id == models.ProductVariant.id)
        .filter(
            models.ProductVariant.gtin == gtin,
            models.Product.status == "active",
            models.LabelVersion.review_status == "published"
        ).first()
    )

    if not result:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"slug": result.slug}

@app.post("/v1/admin/import/bulk")
def bulk_import_drafts(
    request: schemas.BulkImportRequest,
    db: Session = Depends(get_db),
    admin: dict = Depends(verify_admin_role)
):
    try:
        inserted_variants = []
        for item in request.items:
            # 1. Resolve or create Brand
            brand = db.query(models.Brand).filter(models.Brand.slug == item.brand_slug).first()
            if not brand:
                brand = models.Brand(slug=item.brand_slug, name=item.brand_name)
                db.add(brand)
                db.flush()

            # 2. Resolve Category
            category = db.query(models.Category).filter(models.Category.slug == item.category_slug).first()
            if not category:
                raise HTTPException(status_code=400, detail=f"Category '{item.category_slug}' not found")

            # 3. Resolve Market
            market = db.query(models.Market).filter(models.Market.country_code == item.market_code).first()
            if not market:
                raise HTTPException(status_code=400, detail=f"Market '{item.market_code}' not found")

            # 4. Resolve or create Product
            product = db.query(models.Product).filter(models.Product.slug == item.product_slug).first()
            if not product:
                product = models.Product(
                    slug=item.product_slug,
                    brand_id=brand.id,
                    category_id=category.id,
                    canonical_name=item.canonical_name,
                    status="active"
                )
                db.add(product)
                db.flush()

            # 5. Create ProductVariant
            variant = models.ProductVariant(
                product_id=product.id,
                market_id=market.id,
                gtin=item.gtin,
                local_name=item.local_name,
                status="active"
            )
            db.add(variant)
            db.flush()
            inserted_variants.append(str(variant.id))

            # 6. Create LabelVersion
            label = models.LabelVersion(
                variant_id=variant.id,
                version_no=1,
                ingredients_raw=item.ingredients_raw,
                language=item.language,
                captured_at=datetime.now(timezone.utc),
                review_status="draft"
            )
            db.add(label)
        
        db.commit()
        return {"status": "success", "imported_variants_count": len(inserted_variants)}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error("Bulk import failed", extra={"error": str(e)}, exc_info=True)
        raise HTTPException(status_code=500, detail="Bulk import transaction failed")

@app.post("/v1/admin/worker/process")
def process_outbox_events(
    auth: dict = Depends(verify_cron_job),
    db: Session = Depends(get_db)
):
    """
    HTTP-triggered worker endpoint for Serverless CRON.
    Processes pending outbox events (e.g. label published events).
    """
    try:
        # Fetch up to 50 pending events, locking them for update to prevent concurrent worker clashes
        pending_events = db.query(models.OutboxEvent).with_for_update(skip_locked=True).filter(
            models.OutboxEvent.status == "pending"
        ).order_by(models.OutboxEvent.created_at).limit(50).all()

        if not pending_events:
            return {"status": "success", "processed_events_count": 0, "message": "No pending events"}

        for event in pending_events:
            event.status = "processing"
        db.commit()

        processed_count = 0
        for event in pending_events:
            try:
                if event.event_type == "label_published":
                    # Placeholder for the actual search re-indexing logic
                    label_id = event.payload.get("label_version_id")
                    logger.info(f"Re-indexing search for published label: {label_id}")
                    # e.g., trigger pg_trgm materialized view refresh or external search sync

                event.status = "completed"
                event.processed_at = datetime.now(timezone.utc)
                processed_count += 1
            except Exception as e:
                db.rollback()
                logger.error("Failed to process event", extra={"event_id": str(event.id), "error": str(e)})
                event.status = "failed"
                event.error_message = str(e)
            
            db.commit()

        return {"status": "success", "processed_events_count": processed_count}

    except Exception as e:
        db.rollback()
        logger.error("Worker process failed", extra={"error": str(e)}, exc_info=True)
        raise HTTPException(status_code=500, detail="Worker process failed")

@app.post("/v1/admin/run_scripts")
def run_scripts():
    import os, sys
    # Add project root to path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from scripts.purge_data import purge
    from scripts.import_openfoodfacts import import_data
    purge()
    import_data()
    return {"status": "success"}
