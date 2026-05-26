# Data Model Decisions

## Why JSONField for raw_data
Preserves immutable source-of-truth. No schema migration needed when input format changes.

## Why separate AuditLog table
Append-only trail. Records who changed what and when, never updated.

## Multi-tenancy via FK
Simpler than schema-per-tenant for a prototype. All tenants share one DB.

## Why co2e_kg is nullable
Some records arrive without emission factors applied yet.

## Scope mapping
Scope 1 = direct fuel combustion (SAP)
Scope 2 = purchased electricity (Utility)
Scope 3 = business travel (Concur/Navan)