from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class StudentBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    student_id: str = Field(..., min_length=1, max_length=20)
    course: str = Field(..., min_length=1, max_length=100)
    grade: Optional[str] = None
    attendance: float = Field(0.0, ge=0.0, le=100.0)

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    student_id: Optional[str] = Field(None, min_length=1, max_length=20)
    course: Optional[str] = Field(None, min_length=1, max_length=100)
    grade: Optional[str] = None
    attendance: Optional[float] = Field(None, ge=0.0, le=100.0)

class StudentResponse(StudentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
