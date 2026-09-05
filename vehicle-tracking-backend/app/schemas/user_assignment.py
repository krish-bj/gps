from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class UserAssignmentBase(BaseModel):
    user_id: int
    route_id: int
    vehicle_id: int
    is_active: bool = True

class UserAssignmentCreate(UserAssignmentBase):
    pass

class UserAssignmentResponse(UserAssignmentBase):
    id: int
    assigned_at: datetime

    model_config = ConfigDict(from_attributes=True)
