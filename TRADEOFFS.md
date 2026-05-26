# Deliberate Omissions

## 1. No live API integrations
Built file upload instead. Real Concur/SAP/utility APIs require OAuth and credentials.
File upload covers 80% of real-world client handoffs.

## 2. No emission factor database
Hardcoded DEFRA 2024 factors. A real system needs a versioned factor library
with time-dimension lookup (GHG Protocol, DEFRA, EXIOBASE).

## 3. No role-based access control
All authenticated users can approve/reject. Real deployment needs
analyst vs admin vs read-only roles with tenant-level access control.