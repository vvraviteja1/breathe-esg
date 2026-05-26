# Ambiguity Decisions

| Ambiguity | Decision | Reason |
|-----------|----------|--------|
| SAP format | Flat file CSV | No live API access in prototype |
| Utility format | Portal CSV | PDF parsing too fragile |
| Travel distances | Haversine on IATA codes | Distances rarely in exports |
| Emission factors | DEFRA 2024 hardcoded | Need a versioned source |
| Multi-tenancy | FK-based | Simpler than schema-per-tenant |