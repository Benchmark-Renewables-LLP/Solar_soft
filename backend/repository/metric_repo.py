from sqlalchemy.orm import Session
from backend.models.metric import MetricOut

def get_customer_metrics(db: Session, customer_id: str) -> MetricOut:
    """Get customer metrics from the materialized view."""
    result = db.execute(
        "SELECT * FROM customer_metrics WHERE customer_id = :customer_id",
        {"customer_id": customer_id}
    ).first()
    if result:
        return MetricOut(**result)
    return MetricOut(customer_id=customer_id, total_energy_today=0.0, avg_pr=0.0, active_devices=0)

def update_customer_metrics(db: Session, metrics: dict):
    """Update customer metrics in the materialized view."""
    db.execute(
        """
        REFRESH MATERIALIZED VIEW customer_metrics;
        INSERT INTO customer_metrics (customer_id, total_energy_today, avg_pr, active_devices)
        VALUES (:customer_id, :total_energy_today, :avg_pr, :active_devices)
        ON CONFLICT (customer_id) DO UPDATE SET
            total_energy_today = EXCLUDED.total_energy_today,
            avg_pr = EXCLUDED.avg_pr,
            active_devices = EXCLUDED.active_devices
        """,
        metrics
    )