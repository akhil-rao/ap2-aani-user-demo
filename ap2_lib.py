# ap2_lib.py - mock implementation for demo

import uuid
from datetime import datetime

class Mandate:
    def __init__(self, mandate_id, user, merchant, amount, currency, description):
        self.mandate_id = mandate_id
        self.user = user
        self.merchant = merchant
        self.amount = amount
        self.currency = currency
        self.description = description

def create_intent_mandate(user, merchant, amount, currency, description):
    return Mandate(str(uuid.uuid4()), user, merchant, amount, currency, description)

def register_with_cbuae(mandate: Mandate):
    return {
        "event": "REGISTERED_WITH_CBUAE",
        "mandate_id": mandate.mandate_id,
        "timestamp": datetime.utcnow().isoformat()
    }

def convert_intent_to_payment(mandate: Mandate):
    # For demo, just return the same object
    return mandate

def risk_check(mandate: Mandate):
    return {
        "event": "RISK_CHECK",
        "mandate_id": mandate.mandate_id,
        "risk_score": "LOW",
        "timestamp": datetime.utcnow().isoformat()
    }

def mock_payment(mandate: Mandate, rail="Aani"):
    return {
        "transactionId": str(uuid.uuid4()),
        "status": "SUCCESS",
        "rail": rail,
        "settlementTime": datetime.utcnow().isoformat()
    }

def append_audit(session_state, record: dict):
    if "audit_log" not in session_state:
        session_state.audit_log = []
    session_state.audit_log.append(record)
