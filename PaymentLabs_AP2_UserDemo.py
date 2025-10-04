"""
PaymentLabs_AP2_UserDemo.py
End-user Streamlit demo:
Aamir uses Alexa (simulated) to search for hiking shoes, selects one,
Alexa places the order, then AP2 workflow runs:
Consent -> CBUAE register -> Registry -> Risk -> Payment -> Audit
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
from ap2_lib import (
    create_intent_mandate,
    register_with_cbuae,
    convert_intent_to_payment,
    risk_check,
    mock_payment,
    append_audit,
    Mandate,
)

# ---------------------------
# Page config & font
# ---------------------------
st.set_page_config(page_title="AP2 - User Demo (Aamir + Alexa)", layout="centered")

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Oxanium:wght@400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Oxanium', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Load product data
# ---------------------------
DATA_PATH = Path("data") / "products.json"
if not DATA_PATH.exists():
    st.error("Missing data/products.json — make sure you added it to the repo.")
    st.stop()

with open(DATA_PATH, "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)

# ---------------------------
# Helper UI functions
# ---------------------------
def reset_demo():
    st.session_state.page = "landing"
    st.session_state.alexa_messages = []
    st.session_state.shortlist = []
    st.session_state.current_product = None
    st.session_state.workflow_mandate = None
    st.session_state.audit_log = []
    st.session_state.payment_resp = None

def show_alexa_message(text: str):
    if "alexa_messages" not in st.session_state:
        st.session_state.alexa_messages = []
    st.session_state.alexa_messages.append({"ts": datetime.utcnow().isoformat(), "text": text})

def add_audit(record: dict):
    st.session_state.audit_log.append(record)

# ---------------------------
# Init session state
# ---------------------------
defaults = {
    "page": "landing",
    "alexa_messages": [],
    "shortlist": [],
    "current_product": None,
    "workflow_mandate": None,
    "audit_log": [],
    "payment_resp": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

USER = {
    "name": "Aamir Al Harthy",
    "shipping_address": "Apartment 21B, Downtown Tower, Dubai, UAE"
}

# ---------------------------
# Landing Page
# ---------------------------
if st.session_state.page == "landing":
    st.title("Aamir — Shopping with Alexa")
    st.write("Context: Aamir is preparing for a snowy trip to Switzerland. He asks Alexa to find hiking shoes suitable for snow.")

    if st.button("Ask Alexa to search hiking shoes", key="ask_alexa"):
        show_alexa_message("Searching Amazon.ae for hiking shoes suitable for snowy Switzerland...")
        st.session_state.shortlist = PRODUCTS[:3]
        show_alexa_message(f"I found {len(st.session_state.shortlist)} options - showing them now.")
        st.session_state.page = "shortlist"
        st.rerun()

    st.subheader("Alexa Messages")
    for msg in st.session_state.alexa_messages[-4:]:
        st.info(msg["text"])

    st.button("Reset demo", key="reset_demo", on_click=reset_demo)

# ---------------------------
# Shortlist Page
# ---------------------------
elif st.session_state.page == "shortlist":
    st.header("Alexa: Shortlisted Options")
    st.write("Alexa found these three hiking shoes on Amazon UAE. Tap one to order.")

    for p in st.session_state.shortlist:
        with st.container():
            st.image(p["image"], use_container_width=True)
            st.markdown(f"**{p['title']}**  \n{p['specs']}  \n**{p['currency']} {p['price']:.2f}**")
            if st.button("Order with Alexa", key=f"order_{p['id']}"):
                st.session_state.current_product = p
                st.session_state.page = "checkout"
                st.rerun()

    st.button("Back", key="back_to_landing", on_click=reset_demo)

# ---------------------------
# Checkout Page
# ---------------------------
elif st.session_state.page == "checkout":
    p = st.session_state.current_product
    st.header("Order Summary")
    st.image(p["image"], width=300)
    st.write(f"**{p['title']}**")
    st.write(p["specs"])
    st.write(f"Price: {p['currency']} {p['price']:.2f}")
    st.write(f"Shipping to: {USER['shipping_address']}")

    if st.button("Confirm — Place Order", key="confirm_order"):
        # Create mandate
        mandate = create_intent_mandate(
            USER["name"], "merchant:amazon-uae", p["price"], p["currency"], f"Order {p['title']}"
        )
        st.session_state.workflow_mandate = mandate
        add_audit({"event": "MANDATE_ISSUED", "mandate_id": mandate.mandate_id, "timestamp": datetime.utcnow().isoformat()})

        # Register with CBUAE
        add_audit(register_with_cbuae(mandate))

        # Convert to PaymentMandate
        mandate = convert_intent_to_payment(mandate)

        # Risk check
        risk = risk_check(mandate)
        add_audit(risk)

        # Payment
        payment_resp = mock_payment(mandate, rail="Aani")
        add_audit({
            "event": "PAYMENT_EXECUTED",
            "mandate_id": mandate.mandate_id,
            "transaction_id": payment_resp["transactionId"],
            "status": payment_resp["status"],
            "rail": payment_resp["rail"],
            "timestamp": datetime.utcnow().isoformat(),
            "response": payment_resp,
        })

        st.session_state.payment_resp = payment_resp
        st.session_state.page = "confirmation"
        st.rerun()

    st.button("Cancel", key="cancel_order", on_click=reset_demo)

# ---------------------------
# Confirmation Page
# ---------------------------
elif st.session_state.page == "confirmation":
    p = st.session_state.current_product
    payment_resp = st.session_state.payment_resp

    st.success("✅ Order Confirmed!")
    st.image(p["image"], width=250)
    st.write(f"**{p['title']}** ordered successfully.")
    st.write(f"Transaction ID: {payment_resp['transactionId']}")
    st.write(f"Status: {payment_resp['status']}")
    st.write(f"Settlement Time: {payment_resp['settlementTime']}")
    st.write(f"Rail: {payment_resp['rail']}")

    st.subheader("Audit Trail")
    for entry in st.session_state.audit_log:
        with st.expander(f"{entry.get('timestamp','')} — {entry.get('event')}"):
            st.json(entry)

    st.button("Restart Demo", key="restart", on_click=reset_demo)
