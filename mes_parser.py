from pathlib import Path
from datetime import datetime
import openpyxl
from utils import normalize_serial


def clean_string(value):
    if value is None:
        return None
    value = str(value).strip()
    return value if value else None


def format_datetime(value):
    """
    Convert Excel datetime / date / time objects to ISO-like strings.
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        return value.isoformat(sep=" ")

    return str(value).strip()


def parse_mes_for_pipeline(filepath: str) -> dict:
    """
    Parse MES board history Excel file and return a standardized record
    for the AWS-style simulation pipeline.
    """

    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"MES file not found: {filepath}")

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[wb.sheetnames[0]]

    # Read headers
    headers = [ws.cell(row=1, column=col).value for col in range(1, ws.max_column + 1)]
    header_map = {header: idx + 1 for idx, header in enumerate(headers) if header is not None}

    def cell(row_num, header_name):
        col_num = header_map.get(header_name)
        if col_num is None:
            return None
        return ws.cell(row=row_num, column=col_num).value

    serial_number = None
    serial_number_raw = None
    assembly_id = None
    assembly_revision = None
    customer = None
    route_step = None

    process_execution_summary = []
    raw_rows = []

    earliest_start = None
    latest_end = None
    earliest_event = None

    for row_num in range(2, ws.max_row + 1):
        row_serial = clean_string(cell(row_num, "Serial Number"))
        row_assembly = clean_string(cell(row_num, "Assembly"))
        row_customer = clean_string(cell(row_num, "Customer"))
        row_route_step = clean_string(cell(row_num, "Route Step"))

        military_time = cell(row_num, "Military Time")
        start_date = cell(row_num, "Start Date")
        end_date = cell(row_num, "End Date")

        # Fill shared identity fields from first usable row
        if serial_number_raw is None and row_serial:
            serial_number_raw = row_serial

        if serial_number is None and row_serial:
            serial_number = normalize_serial(row_serial)

        if assembly_id is None and row_assembly:
            assembly_id = row_assembly

        if customer is None and row_customer:
            customer = row_customer

        if route_step is None and row_route_step:
            route_step = row_route_step

        # Optional conservative assembly revision parsing
        if assembly_revision is None and row_assembly and "/" in row_assembly:
            parts = [p.strip() for p in row_assembly.split("/")]
            if len(parts) >= 2 and parts[1]:
                assembly_revision = parts[1]

        # Track earliest and latest manufacturing times
        if isinstance(start_date, datetime):
            if earliest_start is None or start_date < earliest_start:
                earliest_start = start_date

        if isinstance(end_date, datetime):
            if latest_end is None or end_date > latest_end:
                latest_end = end_date

        if isinstance(military_time, datetime):
            if earliest_event is None or military_time < earliest_event:
                earliest_event = military_time

        row_data = {
            "route_name": clean_string(cell(row_num, "Factory / Route / MA")),
            "process_step": row_route_step,
            "equipment_id": clean_string(cell(row_num, "Equipment")),
            "system_version": clean_string(cell(row_num, "CRD")),
            "operator_id": clean_string(cell(row_num, "Operator Name")),
            "military_time": format_datetime(military_time),
            "status": clean_string(cell(row_num, "Status")),
        }

        if any(value not in [None, "", " "] for value in row_data.values()):
            process_execution_summary.append(row_data)
            raw_rows.append(row_data.copy())

    mes_summary = {
        "manufacturing_start_time": format_datetime(earliest_start),
        "manufacturing_end_time": format_datetime(latest_end),
        "process_execution_summary": process_execution_summary,
    }

    standardized_record = {
        "source_type": "MES",
        "serial_number": serial_number,
        "assembly_id": assembly_id,
        "assembly_revision": assembly_revision,
        "board_type": None,
        "board_revision": None,
        "customer": customer,
        "start_time": format_datetime(earliest_start),
        "end_time": format_datetime(latest_end),
        "event_time": format_datetime(earliest_event),
        "route_step": route_step,
        "source_file_name": path.name,
        "source_file_path": str(path),
        "standardized_data": mes_summary,
        "rework_documentation": [],
        "raw_data": {
            "rows": raw_rows
        }
    }

    return standardized_record