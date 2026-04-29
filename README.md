Semi-Automated eDHR Assembly Pipeline

This repository contains a Python-based pipeline for assembling electronic Device History Records (eDHRs) from multi-source SMT manufacturing data.

Supported Inputs:
- AOI XML
- AXI XML
- Flying Probe (.ngdx)
- MES Board History (Excel)
  
Workflow:
i) User selects input files
ii) Data is parsed and standardized
iii) eDHR is assembled into a unified schema

Outputs generated:
JSON record
DOCX report
