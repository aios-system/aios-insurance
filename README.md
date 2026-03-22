# aios-insurance

Insurance Claims Processing vertical application built on the AIOS platform. AI-powered claims triage and settlement for regional insurers with strict data isolation and regulatory compliance.

## Modules

- **Ontology**: 5 ObjectTypes (Policy, Claim, Investigation, ClaimPayment, Subrogation), 5 LinkTypes, 3 computed properties
- **Security**: 5 markings, 6 user mappings, 5 security policies (column masking + row filtering)
- **Agents**: Claims Triage (RULE), Fraud Detection (RULE), Claims Advisor (LLM)
- **Data**: 2 transform pipelines, 5 connectors, 3-tier lineage graph
- **Deployment**: 8 spokes across 6 US regions, 3 release channels, production constraints

## Install & Test

```bash
pip install -e ".[dev]"
make test
```

## Dependencies

- **Depends on**: aios-core, aios-ontology, aios-data, aios-deploy, aios-api
