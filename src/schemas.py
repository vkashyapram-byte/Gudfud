from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date

class BrandBase(BaseModel):
    name: str
    slug: str
    
    model_config = ConfigDict(from_attributes=True)

class CategoryBase(BaseModel):
    name: str
    slug: str
    
    model_config = ConfigDict(from_attributes=True)

class ProductCard(BaseModel):
    slug: str
    canonical_name: str
    brand: BrandBase
    category: CategoryBase
    rating_band: Optional[str] = None
    confidence_grade: Optional[str] = None
    market_code: str
    last_reviewed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class PaginatedCatalogue(BaseModel):
    items: List[ProductCard]
    total: int
    page: int
    size: int

class SearchResultItem(BaseModel):
    type: str
    name: str
    slug: str
    subtitle: Optional[str] = None
    similarity_score: float
    
    model_config = ConfigDict(from_attributes=True)

class SearchResponse(BaseModel):
    query: str
    items: List[SearchResultItem]

class NutritionFactsBase(BaseModel):
    energy: Optional[float] = None
    fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    sugars: Optional[float] = None
    sodium: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)

class IngredientMapping(BaseModel):
    label_text: str
    position: int
    canonical_name: Optional[str] = None
    slug: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProductAnalysis(BaseModel):
    slug: str
    canonical_name: str
    brand_name: str
    market_code: str
    rating_total: Optional[int] = None
    rating_band: Optional[str] = None
    confidence_grade: str
    explanation: Dict[str, Any]
    nutrition: Optional[NutritionFactsBase] = None
    ingredients: List[IngredientMapping] = []
    last_reviewed_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class SourceBase(BaseModel):
    title: str
    publisher: str
    url: Optional[str] = None
    publication_date: Optional[date] = None
    
    model_config = ConfigDict(from_attributes=True)

class IngredientEvidenceBase(BaseModel):
    effect_type: str
    population: Optional[str] = None
    dose_context: Optional[str] = None
    evidence_grade: str
    summary: str
    jurisdiction: Optional[str] = None
    sources: List[SourceBase] = []
    
    model_config = ConfigDict(from_attributes=True)

class RegulatoryStatusBase(BaseModel):
    market_code: str
    status: str
    use_category: str
    conditions: Optional[str] = None
    max_level: Optional[str] = None
    effective_from: date
    source: Optional[SourceBase] = None
    
    model_config = ConfigDict(from_attributes=True)

class IngredientProductCard(BaseModel):
    slug: str
    canonical_name: str
    brand_name: str
    rating_band: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class IngredientAnalysis(BaseModel):
    slug: str
    canonical_name: str
    INS_number: Optional[str] = None
    E_number: Optional[str] = None
    ingredient_type: Optional[str] = None
    technical_function: Optional[str] = None
    public_summary: Optional[str] = None
    aliases: List[str] = []
    evidence: List[IngredientEvidenceBase] = []
    regulatory_statuses: List[RegulatoryStatusBase] = []
    products: List[IngredientProductCard] = []
    
    model_config = ConfigDict(from_attributes=True)

class VariantComparisonCard(BaseModel):
    market_code: str
    label_version_id: UUID
    local_name: Optional[str] = None
    pack_quantity: Optional[float] = None
    pack_unit: Optional[str] = None
    serving_quantity: Optional[float] = None
    serving_unit: Optional[str] = None
    captured_at: datetime
    methodology_version: str
    nutrition: Optional[NutritionFactsBase] = None
    ingredients: List[IngredientMapping] = []
    
    model_config = ConfigDict(from_attributes=True)

class ProductComparisonResponse(BaseModel):
    slug: str
    canonical_name: str
    brand_name: str
    variants: List[VariantComparisonCard]

class CorrectionReportCreate(BaseModel):
    reporter_contact: Optional[str] = None
    entity_type: str
    entity_id: UUID
    message: str
    evidence_asset_id: Optional[UUID] = None

class PublishRequest(BaseModel):
    actor_id: str
    methodology_version_id: UUID
    total_score: Optional[int] = None
    band: Optional[str] = None
    nutrition_score: Optional[int] = None
    ingredient_score: Optional[int] = None
    context_score: Optional[int] = None
    confidence_grade: str
    explanation: Dict[str, Any]

class ProductHistoryRecord(BaseModel):
    label_version_id: UUID
    version_no: int
    effective_from: Optional[datetime] = None
    captured_at: datetime
    status: str
    methodology_version: str
    total_score: Optional[int] = None
    rating_band: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ProductHistoryResponse(BaseModel):
    history: List[ProductHistoryRecord]

class BulkImportItem(BaseModel):
    brand_name: str
    brand_slug: str
    product_slug: str
    canonical_name: str
    category_slug: str
    market_code: str
    gtin: Optional[str] = None
    local_name: Optional[str] = None
    ingredients_raw: str
    language: Optional[str] = "en"
    
    model_config = ConfigDict(from_attributes=True)

class BulkImportRequest(BaseModel):
    items: List[BulkImportItem]
