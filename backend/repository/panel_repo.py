from sqlalchemy.orm import Session
from backend.models.panel import PanelOut

def get_panels(db: Session, customer_id: str) -> list[PanelOut]:
    """Get all panels for a customer."""
    result = db.execute(
        "SELECT * FROM panels WHERE customer_id = :customer_id",
        {"customer_id": customer_id}
    ).all()
    return [PanelOut(**row) for row in result]

def get_panel_by_id(db: Session, panel_id: str) -> PanelOut | None:
    """Get a specific panel by ID."""
    result = db.execute(
        "SELECT * FROM panels WHERE panel_id = :panel_id",
        {"panel_id": panel_id}
    ).first()
    if result:
        return PanelOut(**result)
    return None

def update_panel(db: Session, panel_id: str, panel_update: dict):
    """Update a panel."""
    db.execute(
        """
        UPDATE panels SET
            panel_brand = :panel_brand,
            panel_capacity = :panel_capacity,
            panel_type = :panel_type,
            install_date = :install_date
        WHERE panel_id = :panel_id
        """,
        {**panel_update, "panel_id": panel_id}
    )