from enum import Enum

from pydantic import BaseModel


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class BankingTransactionAnalysis(BaseModel):
    transaction_id: str
    risk_level: RiskLevel
    explanation: str
    requires_review: bool