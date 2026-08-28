import pytest
from pydantic import ValidationError

from local_llm.contracts import (
    BankingTransactionAnalysis,
)

# We are not testing the LLM.

# We are testing the contract boundary.

def test_valid_transaction_analysis():
    result = BankingTransactionAnalysis(
        transaction_id="TXN-1",
        risk_level="HIGH",
        explanation="Transaction is significantly larger than history.",
        requires_review=True,
    )

    assert result.risk_level == "HIGH"


def test_invalid_transaction_analysis():
    with pytest.raises(ValidationError):
        BankingTransactionAnalysis.model_validate(
            {
                "transaction_id": "TXN-1",
                "risk_level": "HIGH",
                "requires_review": True,
            }
        )