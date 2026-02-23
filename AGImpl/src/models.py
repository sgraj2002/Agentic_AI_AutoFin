from pydantic import BaseModel
from typing import Optional

class Briefcase(BaseModel):
    s3_path: str
    ssn_last4: Optional[str] = None  # Provided by user
    extracted_ssn: Optional[str] = None # Extracted by AI
    name: Optional[str] = None
    income: Optional[float] = None
    loyalty_tier: Optional[str] = None
    base_apr: float = 6.0
    final_apr: Optional[float] = None
    error: Optional[str] = None # For validation failures
