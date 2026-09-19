import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import ForeignKey, String, Integer, DateTime, Numeric, Index, text, UniqueConstraint, Boolean, Date, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid as UUID, JSON as JSONB

class Base(DeclarativeBase):
    pass

class Brand(Base):
    __tablename__ = 'brand'
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(String)
    country_of_origin: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, nullable=False, default='active')

    products: Mapped[list["Product"]] = relationship(back_populates="brand")

class Category(Base):
    __tablename__ = 'category'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey('category.id'))
    name: Mapped[str] = mapped_column(String, nullable=False)
    scoring_profile_id: Mapped[Optional[str]] = mapped_column(String)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    parent: Mapped[Optional["Category"]] = relationship(remote_side=[id], backref="children")
    products: Mapped[list["Product"]] = relationship(back_populates="category")

class Market(Base):
    __tablename__ = 'market'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    currency_code: Mapped[Optional[str]] = mapped_column(String)
    regulator_name: Mapped[Optional[str]] = mapped_column(String)

class Product(Base):
    __tablename__ = 'product'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    brand_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('brand.id'), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('category.id'), nullable=False)
    canonical_name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default='active')

    brand: Mapped["Brand"] = relationship(back_populates="products")
    category: Mapped["Category"] = relationship(back_populates="products")

class ProductVariant(Base):
    __tablename__ = 'product_variant'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('product.id'), nullable=False)
    market_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('market.id'), nullable=False)
    gtin: Mapped[Optional[str]] = mapped_column(String)
    local_name: Mapped[Optional[str]] = mapped_column(String)
    pack_quantity: Mapped[Optional[Numeric]] = mapped_column(Numeric)
    pack_unit: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, nullable=False, default='active')

    __table_args__ = (
        Index('ix_product_variant_market_gtin', 'market_id', 'gtin', unique=True, postgresql_where=text("gtin IS NOT NULL")),
    )

class LabelVersion(Base):
    __tablename__ = 'label_version'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('product_variant.id'), nullable=False)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    ingredients_raw: Mapped[Optional[str]] = mapped_column(String)
    language: Mapped[Optional[str]] = mapped_column(String)
    serving_quantity: Mapped[Optional[Numeric]] = mapped_column(Numeric)
    serving_unit: Mapped[Optional[str]] = mapped_column(String)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    review_status: Mapped[str] = mapped_column(String, nullable=False, default='draft')
    label_image_id: Mapped[Optional[str]] = mapped_column(String)
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))

    __table_args__ = (
        Index('ix_label_version_variant_version', 'variant_id', 'version_no', unique=True),
    )

class NutritionFacts(Base):
    __tablename__ = 'nutrition_facts'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('label_version.id'), unique=True, nullable=False)
    basis_quantity: Mapped[Optional[Numeric]] = mapped_column(Numeric)
    basis_unit: Mapped[Optional[str]] = mapped_column(String)
    energy: Mapped[Optional[Numeric]] = mapped_column(Numeric)
    fat: Mapped[Optional[Numeric]] = mapped_column(Numeric)
    saturated_fat: Mapped[Optional[Numeric]] = mapped_column(Numeric)
    trans_fat: Mapped[Optional[Numeric]] = mapped_column(Numeric)
    carbohydrate: Mapped[Optional[Numeric]] = mapped_column(Numeric)
    sugars: Mapped[Optional[Numeric]] = mapped_column(Numeric)
    added_sugars: Mapped[Optional[Numeric]] = mapped_column(Numeric)
    protein: Mapped[Optional[Numeric]] = mapped_column(Numeric)
    fibre: Mapped[Optional[Numeric]] = mapped_column(Numeric)
    sodium: Mapped[Optional[Numeric]] = mapped_column(Numeric)

class Ingredient(Base):
    __tablename__ = 'ingredient'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    canonical_name: Mapped[str] = mapped_column(String, nullable=False)
    INS_number: Mapped[Optional[str]] = mapped_column(String)
    E_number: Mapped[Optional[str]] = mapped_column(String)
    ingredient_type: Mapped[Optional[str]] = mapped_column(String)
    technical_function: Mapped[Optional[str]] = mapped_column(String)
    public_summary: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, nullable=False, default='active')

class Source(Base):
    __tablename__ = "source"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String, nullable=False)
    publisher: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    publication_date: Mapped[Optional[date]] = mapped_column(Date)
    version: Mapped[Optional[str]] = mapped_column(String)
    accessed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String)
    archived_url: Mapped[Optional[str]] = mapped_column(String)
    canonical_url: Mapped[Optional[str]] = mapped_column(String, unique=True)

class IngredientEvidence(Base):
    __tablename__ = "ingredient_evidence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ingredient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingredient.id"), nullable=False)
    effect_type: Mapped[str] = mapped_column(String, nullable=False)
    population: Mapped[Optional[str]] = mapped_column(String)
    dose_context: Mapped[Optional[str]] = mapped_column(String)
    evidence_grade: Mapped[str] = mapped_column(String, nullable=False)
    summary: Mapped[str] = mapped_column(String, nullable=False)
    jurisdiction: Mapped[Optional[str]] = mapped_column(String)
    review_status: Mapped[str] = mapped_column(String, nullable=False)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

class EvidenceSource(Base):
    __tablename__ = "evidence_source"

    ingredient_evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingredient_evidence.id"), primary_key=True)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("source.id"), primary_key=True)
    locator: Mapped[Optional[str]] = mapped_column(String)
    note: Mapped[Optional[str]] = mapped_column(String)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

class RegulatoryStatus(Base):
    __tablename__ = "regulatory_status"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ingredient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingredient.id"), nullable=False)
    market_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("market.id"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    use_category: Mapped[str] = mapped_column(String, nullable=False)
    conditions: Mapped[Optional[str]] = mapped_column(String)
    max_level: Mapped[Optional[str]] = mapped_column(String)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[Optional[date]] = mapped_column(Date)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("source.id"))

    __table_args__ = (
        UniqueConstraint("ingredient_id", "market_id", "use_category", "effective_from", name="uq_regulatory_status_ingredient_market_category_date"),
        Index("ix_regulatory_status_market_effective", "ingredient_id", "market_id", "effective_from"),
    )

class VariantSource(Base):
    __tablename__ = "variant_source"

    label_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("label_version.id"), primary_key=True)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("source.id"), primary_key=True)
    field_path: Mapped[str] = mapped_column(String, primary_key=True)
    locator: Mapped[Optional[str]] = mapped_column(String)
    verification_note: Mapped[Optional[str]] = mapped_column(String)

class MethodologyVersion(Base):
    __tablename__ = "methodology_version"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    rules: Mapped[dict] = mapped_column(JSONB, nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    retired_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    reviewer: Mapped[str] = mapped_column(String, nullable=False)
    change_summary: Mapped[Optional[str]] = mapped_column(String)

class OutboxEvent(Base):
    __tablename__ = "outbox_event"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(String)

    __table_args__ = (
        Index("ix_outbox_event_status_created", "status", "created_at"),
    )

class Rating(Base):
    __tablename__ = "rating"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("label_version.id"), nullable=False)
    methodology_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("methodology_version.id"), nullable=False)
    total_score: Mapped[Optional[int]] = mapped_column(Integer)
    band: Mapped[Optional[str]] = mapped_column(String)
    nutrition_score: Mapped[Optional[int]] = mapped_column(Integer)
    ingredient_score: Mapped[Optional[int]] = mapped_column(Integer)
    context_score: Mapped[Optional[int]] = mapped_column(Integer)
    confidence_grade: Mapped[str] = mapped_column(String, nullable=False)
    explanation: Mapped[dict] = mapped_column(JSONB, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint("label_version_id", "methodology_version_id", name="uq_rating_label_methodology"),
    )

class Alternative(Base):
    __tablename__ = "alternative"

    source_variant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product_variant.id"), primary_key=True)
    alternative_variant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("product_variant.id"), primary_key=True)
    methodology_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("methodology_version.id"), primary_key=True)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    reviewed_by: Mapped[str] = mapped_column(String, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class LabelIngredient(Base):
    __tablename__ = "label_ingredient"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    label_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("label_version.id"), nullable=False)
    ingredient_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("ingredient.id"))
    label_text: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    declared_percent: Mapped[Optional[float]] = mapped_column(Numeric, nullable=True)

class IngredientAlias(Base):
    __tablename__ = "ingredient_alias"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ingredient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ingredient.id"), nullable=False)
    alias: Mapped[str] = mapped_column(String, nullable=False)
    alias_normalized: Mapped[str] = mapped_column(String, nullable=False, index=True)

class AdminUser(Base):
    __tablename__ = "admin_user"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    auth_subject: Mapped[Optional[str]] = mapped_column(String)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

class TeamMember(Base):
    __tablename__ = "team_member"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    role_title: Mapped[str] = mapped_column(String, nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(String)
    photo_asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

class ReviewTask(Base):
    __tablename__ = "review_task"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    assigned_to: Mapped[Optional[str]] = mapped_column(String)
    requested_by: Mapped[str] = mapped_column(String, nullable=False)
    checklist: Mapped[Optional[dict]] = mapped_column(JSONB)
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_review_task_status_assigned_due", "status", "assigned_to", "due_at"),
    )

class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    actor_id: Mapped[str] = mapped_column(String, nullable=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[str] = mapped_column(String, nullable=False)
    before_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    after_json: Mapped[Optional[dict]] = mapped_column(JSONB)
    ip_hash: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class CorrectionReport(Base):
    __tablename__ = "correction_report"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public_reference: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    reporter_contact: Mapped[Optional[str]] = mapped_column(String)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    message: Mapped[str] = mapped_column(String, nullable=False)
    evidence_asset_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    status: Mapped[str] = mapped_column(String, nullable=False)
    assigned_to: Mapped[Optional[str]] = mapped_column(String)
    resolution: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        Index("ix_correction_report_status_created", "status", "created_at"),
    )
