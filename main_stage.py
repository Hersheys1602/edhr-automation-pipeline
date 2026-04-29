from edhr_template import create_blank_edhr
from fp_parser import parse_fp_ngdx
from aoi_parser import parse_aoi_xml
from axi_parser import parse_axi_xml
from mes_parser import parse_mes_board_history
from render_docx import render_edhr_docx
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import time

workflow_start = time.perf_counter()
edhr = create_blank_edhr()


def choose_file(prompt_text: str, filetypes: list[tuple[str, str]]) -> str:
    """
    Show a terminal prompt, then open a file picker.
    Returns the selected file path.
    """
    print(prompt_text)

    root = tk.Tk()
    root.withdraw()  # hide main tkinter window
    root.attributes("-topmost", True)  # bring dialog to front

    filepath = filedialog.askopenfilename(
        title=prompt_text,
        filetypes=filetypes
    )

    root.destroy()

    if not filepath:
        raise ValueError(f"No file selected for: {prompt_text}")

    return filepath


# prompt user + open file picker
fp_filepath = choose_file(
    "Select Flying Probe .ngdx file",
    [("Flying Probe files", "*.ngdx *.txt"), ("All files", "*.*")]
)

aoi_filepath = choose_file(
    "Select AOI .xml file",
    [("XML files", "*.xml"), ("All files", "*.*")]
)

axi_filepath = choose_file(
    "Select AXI .xml file",
    [("XML files", "*.xml"), ("All files", "*.*")]
)

mes_filepath = choose_file(
    "Select MES board history Excel file",
    [("Excel files", "*.xlsx *.xls *.xlsm"), ("All files", "*.*")]
)

#measure execution time
script_start = time.perf_counter()

# populate document
edhr["document_control"]["issuance_date"] = datetime.now(
    ZoneInfo("America/Los_Angeles")
).strftime("%Y-%m-%d %H:%M:%S %Z")

fp_data = parse_fp_ngdx(fp_filepath)
aoi_data = parse_aoi_xml(aoi_filepath)
axi_data = parse_axi_xml(axi_filepath)
mes_data = parse_mes_board_history(mes_filepath)

# populate device identification
for key, value in fp_data["device_identification"].items():
    if value not in [None, ""]:
        edhr["device_identification"][key] = value

# populate AOI inspection summary
for key, value in aoi_data["inspection_and_defects"]["inspection_summary"]["aoi"].items():
    if value not in [None, ""]:
        edhr["inspection_and_defects"]["inspection_summary"]["aoi"][key] = value
for entry in aoi_data["rework_documentation"]:
    edhr["rework_documentation"].append(entry)

# populate device identification from AOI
for key, value in aoi_data["device_identification"].items():
    if value not in [None, ""]:
        edhr["device_identification"][key] = value

# populate flying probe summary
for key, value in fp_data["inspection_and_defects"]["inspection_summary"]["flying_probe"].items():
    if value not in [None, ""]:
        edhr["inspection_and_defects"]["inspection_summary"]["flying_probe"][key] = value

# populate electrical test certification
for key, value in fp_data["electrical_test_certification"].items():
    if value not in [None, ""]:
        edhr["electrical_test_certification"][key] = value

# populate AXI inspection summary
for key, value in axi_data["inspection_summary_axi"].items():
    if value not in [None, ""]:
        edhr["inspection_and_defects"]["inspection_summary"]["axi"][key] = value

# populate defect summary
for row in axi_data["defect_summary"]:
    edhr["inspection_and_defects"]["defect_summary"].append(row)

# populate rework documentation
for row in axi_data["rework_documentation"]:
    edhr["rework_documentation"].append(row)

# populate process execution summary from MES
for row in mes_data["process_execution_summary"]:
    edhr["process_execution_summary"].append(row)

# populate device identification from MES
for key, value in mes_data["device_identification"].items():
    if value not in [None, ""]:
        edhr["device_identification"][key] = value

# output directory
BASE_DIR = Path(__file__).resolve().parent
output_dir = BASE_DIR / "output"
output_dir.mkdir(parents=True, exist_ok=True)

# get serial number safely
serial = edhr["device_identification"].get("serial_number") or "unknown"

# define file paths
json_path = output_dir / f"{serial}_edhr.json"
docx_path = output_dir / f"{serial}_edhr.docx"

# save JSON
with open(json_path, "w") as f:
    json.dump(edhr, f, indent=2)

# generate DOCX
render_edhr_docx(str(json_path), str(docx_path))

print(f"JSON saved to: {json_path}")
print(f"DOCX saved to: {docx_path}")

#time to finish doc
script_end = time.perf_counter()

total_execution_time = script_end - workflow_start
script_execution_time = script_end - script_start

print(f"Workflow time: {total_execution_time:.3f} seconds")
print(f"Script Eexecution time: {script_execution_time:.3f} seconds")

