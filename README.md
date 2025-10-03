# AP2 + Aani — End-User Demo (ap2-aani-user-demo)

This is an **end-user** demo showing an operational flow:
Aamir uses Alexa (simulated) to find hiking shoes on Amazon UAE → selects a product → Alexa places the order → the app triggers the AP2 workflow (Consent → CBUAE registration → Mandate Registry → Risk & AML check → Payment execution via Aani/UAEFTS → Audit).

This demo is intended for operational stakeholders and is mobile-friendly.

---

## Files in this repo

- `PaymentLabs_AP2_UserDemo.py` — Streamlit app (end-user demo)
- `ap2_lib.py` — library of AP2 helper functions (mandate creation, registration, risk check, mock payment)
- `data/products.json` — 3 product entries used by the demo
- `requirements.txt` — dependencies

---

## Quick run (Streamlit Cloud)

1. Push the repo to GitHub.
2. Deploy on Streamlit Cloud (link repo). Streamlit Cloud will install dependencies from `requirements.txt`.
3. Open the app in mobile browser or desktop.

---

## Run locally (optional)

```bash
git clone <your-repo-url>
cd ap2-aani-user-demo
pip install -r requirements.txt
streamlit run PaymentLabs_AP2_UserDemo.py
```

---

## Notes for reviewers

- All payment calls are **mocked** and do not call real Aani or Amazon APIs.
- The flow demonstrates how user UX maps to AP2 & Open Finance requirements: explicit consent, registry, AML screening, payment execution, and an audit trail.
- The app is intentionally simple and focused on the operational story.
