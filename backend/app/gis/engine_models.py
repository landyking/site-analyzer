from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class RestrictedFactor(BaseModel):
    kind: str
    buffer_distance: int

class SuitabilityFactor(BaseModel):
    kind: str
    weight: float
    ranges: Optional[List[tuple[float, float, int]]] = None

class EngineConfigs(BaseModel):
    restricted_factors: List[RestrictedFactor]
    suitability_factors: List[SuitabilityFactor]