# Source Research

## SAP (Scope 1 — Fuel)
Real SAP exports via transaction ME2M or custom reports.
Columns: WERKS (plant), MATNR (material), MENGE (quantity), MEINS (unit), BLDAT (date).
Units normalized: L/LTR → litre, GAL → ×3.785 litres.
Production gap: German SAP exports have headers in German, dates as TT.MM.JJJJ.

## Utility Portal (Scope 2 — Electricity)
CSV export from utility portal with one row per meter per billing period.
Emission factor: DEFRA 2024 — 0.20704 kgCO2e/kWh (UK grid).
Production gap: billing periods don't always align to calendar months.

## Concur/Navan (Scope 3 — Travel)
CSV trip export with IATA airport codes, expense type, hotel nights.
Flight distances calculated using Haversine formula on airport coordinates.
Emission factors: DEFRA 2024 — Air 0.195, Hotel 0.069, Ground 0.142 kgCO2e.
Production gap: actual distance data from Navan would be more accurate.