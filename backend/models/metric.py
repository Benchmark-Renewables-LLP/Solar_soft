from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Metric(BaseModel):
    customer_id: str = Field(..., description="Customer ID")
    total_energy_today: float = Field(0.0, description="Total energy today")
    avg_pr: float = Field(0.0, description="Average PR")
    active_devices: int = Field(0, description="Number of active devices")

class MetricUpdate(BaseModel):
    total_energy_today: Optional[float] = Field(None, description="Total energy today")
    avg_pr: Optional[float] = Field(None, description="Average PR")
    active_devices: Optional[int] = Field(None, description="Number of active devices")

class MetricOut(BaseModel):
    customer_id: str
    total_energy_today: float
    avg_pr: float
    active_devices: int
    updated_at: datetime

    class Config:
        from_attributes = True