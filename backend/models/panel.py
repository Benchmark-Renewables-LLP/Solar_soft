from pydantic import BaseModel, Field
from typing import Optional

class Panel(BaseModel):
    panel_id: str = Field(..., description="Panel ID")
    customer_id: str = Field(..., description="Customer ID")
    panel_brand: str = Field(..., description="Panel brand")
    panel_capacity: float = Field(..., description="Panel capacity in kW")
    panel_type: str = Field(..., description="Panel type")
    install_date: Optional[str] = Field(None, description="Install date")

class PanelUpdate(BaseModel):
    panel_brand: Optional[str] = Field(None, description="Panel brand")
    panel_capacity: Optional[float] = Field(None, description="Panel capacity in kW")
    panel_type: Optional[str] = Field(None, description="Panel type")
    install_date: Optional[str] = Field(None, description="Install date")

class PanelOut(BaseModel):
    panel_id: str
    customer_id: str
    panel_brand: str
    panel_capacity: float
    panel_type: str
    install_date: Optional[str]

    class Config:
        from_attributes = True