import re
from datetime import datetime


def parse_fp_ngdx(fp_filepath):
    """
    Parse a Flying Probe .ngdx file and return data mapped to the eDHR schema.
    """

    raw_fields = {}

    with open(fp_filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = [line.strip() for line in f.readlines()]

    for line in lines:
        if not line or line == "@":
            continue

        # Example: * PASS *
        if line.startswith("*") and line.endswith("*"):
            raw_fields["overall_result"] = line.replace("*", "").strip()
            continue

        # Example: D.T:1    D.P:1    D.F:0    G.P:1    G.F:0
        if any(metric in line for metric in ["D.T:", "D.P:", "D.F:", "G.P:", "G.F:"]):
            matches = re.findall(r"([A-Z]\.[A-Z]):\s*([^\t]+)", line)
            for key, value in matches:
                raw_fields[key.strip()] = value.strip()
            continue

        # Standard key:value line
        if ":" in line:
            key, value = line.split(":", 1)
            raw_fields[key.strip()] = value.strip()

    def safe_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def parse_test_datetime(value):
        """
        Example:
        1/16/2026 11:44:25 AM
        """
        if not value:
            return None
        try:
            return datetime.strptime(value, "%m/%d/%Y %I:%M:%S %p").isoformat()
        except ValueError:
            return value

    def parse_test_duration(value):
        """
        Example:
        265 s (00:04:25)

        Return the full original string or seconds depending on your preference.
        For now, I recommend returning seconds as int for easier downstream use.
        """
        if not value:
            return None
        match = re.search(r"(\d+)\s*s", value)
        if match:
            return int(match.group(1))
        return None

    parsed_data = {
        "device_identification": {
            "serial_number": raw_fields.get("Serial No."),
            "assembly_id": raw_fields.get("Assembly No."),
            "assembly_revision": raw_fields.get("Assembly Rev") or None,
            "board_type": raw_fields.get("Model"),
            "board_revision": None,
            "image_id": None,
            "customer": raw_fields.get("Customer Name"),
            "manufacturing_start_time": None,
            "manufacturing_end_time": None,
        },

        "inspection_and_defects": {
            "inspection_summary": {
                "flying_probe": {
                    "test_time": parse_test_datetime(raw_fields.get("Date")),
                    "test_duration": parse_test_duration(raw_fields.get("Test Time")),
                    "overall_result": raw_fields.get("overall_result"),
                    "tester_name": raw_fields.get("Tester Name"),
                    "test_process": raw_fields.get("Test Process"),
                    "test_points": safe_int(raw_fields.get("Test Point")),
                    "test_steps": raw_fields.get("Test Steps"),
                    "defect_total": safe_int(raw_fields.get("D.T")),
                    "defect_pass": safe_int(raw_fields.get("D.P")),
                    "defect_fail": safe_int(raw_fields.get("D.F")),
                    "global_pass": safe_int(raw_fields.get("G.P")),
                    "global_fail": safe_int(raw_fields.get("G.F")),
                }
            }
        },

        "electrical_test_certification": {
            "test_type": raw_fields.get("Test Process"),
            "tester": raw_fields.get("Tester Name"),
            "test_duration": parse_test_duration(raw_fields.get("Test Time")),
            "final_result": raw_fields.get("overall_result"),
        },

        "raw_fields": raw_fields
    }

    return parsed_data