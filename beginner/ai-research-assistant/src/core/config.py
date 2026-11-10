from dataclasses import dataclass
@dataclass
class Config:
    confidence_threshold: float = 0.75
    max_retries: int = 2
    max_subtopics: int = 4
    max_claims_per_subtopic: int = 5
    min_evidence_length: int = 20

DEFAULT_CONFIG = Config()
