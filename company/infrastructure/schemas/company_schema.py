from pydantic import BaseModel
from uuid import UUID

class CompanyResponse(BaseModel):
    id: UUID
    name: str
    email: str

    class Config:
        orm_mode = True
