from typing import Optional, List
from pydantic import BaseModel

class EligibilityResult(BaseModel):
    eligible: bool
    reason: str
    failed_rule: Optional[str] = None  # 'R1', 'R2', 'R3', 'R4' or None
    min_cgpa: float
    max_backlogs: int
    allowed_branches: List[str]
    student_cgpa: float
    student_backlogs: int
    student_branch: str
    student_has_offer: bool
