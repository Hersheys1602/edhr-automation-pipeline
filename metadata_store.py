import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
METADATA_PATH = BASE_DIR / "state" / "metadata.json"

def load_metadata():
    """
    Load metadata from JSON file.
    If file does not exist, return empty dict.
    """
    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_metadata(metadata):
    """
    Save metadata dictionary to JSON file.
    """
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)


def initialize_board_record(serial_number):
    """
    Create a blank board record for a new serial number.
    """
    return {
        "serial_number": serial_number,
        "assembly_id": None,
        "assembly_revision": None,
        "board_type": None,
        "board_revision": None,
        "customer": None,
        "sources_received": {
            "AOI": False,
            "AXI": False,
            "FP": False,
            "MES": False
        },
        "source_files": {},
        "records": {},
        "ready_for_assembly": False,
        "output_created": False,
        "failed_sources": {},
        "manual_review_required": False,
        "status": "IN_PROGRESS"
    }

def record_failed_source(metadata, source_type, file_path, error_message, serial_number=None):
    """
    Record a failed file parse in metadata.
    If serial number is unknown, group under UNRESOLVED_FILES.
    """
    key = serial_number if serial_number else "UNRESOLVED_FILES"

    if key not in metadata:
        if key == "UNRESOLVED_FILES":
            metadata[key] = {
                "failed_files": []
            }
        else:
            metadata[key] = initialize_board_record(key)

    if key == "UNRESOLVED_FILES":
        metadata[key]["failed_files"].append({
            "source_type": source_type,
            "file_path": file_path,
            "error_message": error_message
        })
    else:
        metadata[key]["failed_sources"][source_type] = {
            "file_path": file_path,
            "error_message": error_message
        }
        metadata[key]["manual_review_required"] = True
        metadata[key]["status"] = "WAITING_FOR_REVIEW"

    return metadata


def update_board_record(metadata, parsed_record):
    """
    Update metadata for a single parsed source record.
    """
    serial_number = parsed_record.get("serial_number")
    source_type = parsed_record.get("source_type")

    if not serial_number:
        raise ValueError("Parsed record is missing serial_number")

    if not source_type:
        raise ValueError("Parsed record is missing source_type")

    if serial_number not in metadata:
        metadata[serial_number] = initialize_board_record(serial_number)

    board_record = metadata[serial_number]

    # Fill shared fields only if currently empty
    for field in [
        "assembly_id",
        "assembly_revision",
        "board_type",
        "board_revision",
        "customer"
    ]:
        if board_record.get(field) is None and parsed_record.get(field) is not None:
            board_record[field] = parsed_record.get(field)

    # Mark source as received
    board_record["sources_received"][source_type] = True

    # Save file info
    board_record["source_files"][source_type] = parsed_record.get("source_file_name")

    # Save full parsed record by source
    board_record["records"][source_type] = parsed_record

    # Update ready flag
    board_record["ready_for_assembly"] = check_ready_for_assembly(board_record)

    if board_record["manual_review_required"]:
        board_record["status"] = "WAITING_FOR_REVIEW"

    elif board_record["ready_for_assembly"] and not board_record["output_created"]:
        board_record["status"] = "READY_FOR_ASSEMBLY"

    elif board_record["output_created"]:
        board_record["status"] = "COMPLETED"

    else:
        board_record["status"] = "IN_PROGRESS"

    return metadata


def check_ready_for_assembly(board_record, required_sources=None):
    """
    Check if all required sources have been received.
    first-pass requirement: AOI + AXI + FP + MES
    """
    if required_sources is None:
        required_sources = ["AOI", "AXI", "FP", "MES"]

    return all(board_record["sources_received"].get(source, False) for source in required_sources)


def get_board_record(metadata, serial_number):
    """
    Return one board record if it exists, otherwise None.
    """
    return metadata.get(serial_number)

