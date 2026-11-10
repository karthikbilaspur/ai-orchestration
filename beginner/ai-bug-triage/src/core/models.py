
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

ErrorCategory = Literal["syntax","runtime","dependency","logic","config","network","unknown"]

class StackFrame(BaseModel):
    file: Optional[str]=None
    line: Optional[int]=None
    function: Optional[str]=None
    code: Optional[str]=None

class ParsedError(BaseModel):
    raw: str
    exception_type: Optional[str]=None
    message: str=""
    file: Optional[str]=None
    line: Optional[int]=None
    frames: List[StackFrame]=[]
    language_hint: Optional[str]=None
    code_snippet: Optional[str]=None

class Classification(BaseModel):
    category: ErrorCategory
    confidence: float = Field(ge=0, le=1)
    reasoning: str
    scores: dict = {}

class Fix(BaseModel):
    title: str
    root_cause: str
    diff: str = ""
    explanation: str
    verification: List[str] = []
    prevention: str = ""
    risk: str = "Low"

class Review(BaseModel):
    verdict: Literal["APPROVED","NEEDS_REVISION"]
    addresses_root_cause: bool
    is_minimal: bool
    is_safe: bool
    feedback: str
    suggested_change: str = ""

class TriageResult(BaseModel):
    parsed: ParsedError
    classification: Classification
    fix: Fix
    review: Review
    iterations: int = 1
    route: str = ""
