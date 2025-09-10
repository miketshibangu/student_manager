from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Faculty:
    id: Optional[int]
    name: str
    code: str
    description: Optional[str] = None

@dataclass
class Department:
    id: Optional[int]
    name: str
    code: str
    faculty_id: int

@dataclass
class Promotion:
    id: Optional[int]
    name: str
    year: int
    department_id: int

@dataclass
class Student:
    id: Optional[int]
    last_name: str
    postnom: str
    first_name: str
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    emergency_contact: Optional[str]
    emergency_phone: Optional[str]
    registration_number: str
    photo_path: Optional[str]
    promotion_id: int
    created_at: Optional[datetime] = None
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
