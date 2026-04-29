Event-Driven eDHR Assembly Pipeline (Automated)

This repository contains an event-driven pipeline for automated assembly of electronic Device History Records (eDHRs) from multi-source SMT manufacturing data. The system detects incoming files, parses and standardizes data, tracks completeness by serial number, and generates a complete eDHR once all required inputs are available.

Supported Data Sources:
- AOI XML
- AXI XML
- Flying Probe .ngdx
- MES Board History Excel

Workflow:

i) Files are placed into a structured incoming/ directory

ii) When main.py is run, the system automatically:
  - detects file type
  - parses and standardizes data
  - associates data by serial number
  - Metadata tracks completeness across sources
    
iii) When all required inputs are present, the system:
  - assembles the eDHR
  - generates JSON and DOCX outputs
