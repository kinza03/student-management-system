from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    student_id = Column(String, unique=True, index=True, nullable=False)
    course = Column(String, nullable=False)
    grade = Column(String, nullable=True)  # E.g., 'A', 'B', 'Pass', or '85.5'
    attendance = Column(Float, default=0.0)  # E.g., attendance percentage (0 to 100)
