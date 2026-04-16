from pydantic import BaseModel, Field
from typing import Optional, List

# Schema 1: What Stage 1 LLM outputs
class ExtractedFeatures(BaseModel):
    overall_qual: Optional[int] = Field(None, ge=1, le=10, description="Overall quality 1-10")
    gr_liv_area: Optional[float] = Field(None, description="Above ground living area in sqft")
    total_bsmt_sf: Optional[float] = Field(None, description="Total basement area in sqft")
    garage_cars: Optional[int] = Field(None, ge=0, le=4, description="Garage capacity in cars")
    garage_finish: Optional[str] = Field(None, description="Garage interior: None/Unf/RFn/Fin")
    fireplaces: Optional[int] = Field(None, ge=0, description="Number of fireplaces")
    kitchen_qual: Optional[str] = Field(None, description="Kitchen quality: Po/Fa/TA/Gd/Ex")
    neighborhood: Optional[str] = Field(None, description="Neighborhood name in Ames")
    year_built: Optional[int] = Field(None, description="Year the house was built")
    year_remod: Optional[int] = Field(None, description="Year of last remodel")
    full_bath: Optional[int] = Field(None, ge=0, description="Number of full bathrooms")
    half_bath: Optional[int] = Field(None, ge=0, description="Number of half bathrooms")
    extracted_fields: List[str] = Field(default_factory=list, description="Fields confidently extracted")
    missing_fields: List[str] = Field(default_factory=list, description="Fields not found in query")

class QueryRequest (BaseModel):
    query: str = Field( Description = " Natural language property description ")

# Schema 2: What the API returns
class PredictionResponse(BaseModel):
    success: bool
    features: Optional[ExtractedFeatures] = None
    predicted_price: Optional[float] = None
    interpretation: Optional[str] = None
    confidence_note: Optional[str] = None
    message: Optional[str] = None
    suggestions: Optional[List[str]] = None
    example: Optional[str] = None
  