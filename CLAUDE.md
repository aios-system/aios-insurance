# aios-insurance

Insurance Claims Processing — vertical application built on the AIOS platform.

## Commands
```bash
pip install -e ".[dev]"
make test
```

## Key Facts
- Uses AIOS ontology for insurance data modeling (Policy, Claim, Investigation, ClaimPayment, Subrogation)
- Markings-based security (PII, FINANCIAL, RESTRICTED, CLAIMS, MANAGEMENT)
- 3 agents: Claims Triage (RULE), Fraud Detection (RULE), Claims Advisor (LLM)
- Hub-and-spoke deployment across 6 US regions
