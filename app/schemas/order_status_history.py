from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrderStatusHistoryResponse(BaseModel):
    id: int
    order_id: int
    status: str
    changed_by_id: int | None = None
    changed_by_role: str | None = None
    note: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)