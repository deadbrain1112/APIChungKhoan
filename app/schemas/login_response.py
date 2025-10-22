from pydantic import BaseModel
from typing import Optional, Any

class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
