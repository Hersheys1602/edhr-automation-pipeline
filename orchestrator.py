from pathlib import Path
from render_docx import render_edhr_docx
from logger_utils import log_event
from metadata_store import record_failed_source

from metadata_store import (
    load_metadata,
    save_metadata,
    update_board_record,
    get_board_record,
)

from assembler import assemble_edhr, save_edhr_output

from aoi_parser import parse_aoi_for_pipeline
from fp_parser import parse_fp_for_pipeline
from mes_parser import parse_mes_for_pipeline
from axi_parser import parse_axi_for_pipeline


def detect_source_type(file_path):
    """
    Detect source type based on folder name or file extension.
    Assumes folder names include 'aoi', 'axi', 'fp', or 'mes'.
    """
    path = Path(file_path)
    parts_lower = [part.lower() for part in path.parts]
    suffix = path.suffix.lower()

    if "aoi" in parts_lower and suffix == ".xml":
        return "AOI"
    
    if "axi" in parts_lower and suffix == ".xml":
        return "AXI"

    if "fp" in parts_lower and (
    path.name.lower().endswith(".ngdx")
    or path.name.lower().endswith(".ngdx.txt")):
     return "FP"

    if "mes" in parts_lower and suffix in [".xlsx", ".xlsm", ".xls"]:
        return "MES"

    return None


def parse_file_by_source(file_path, source_type):
    """
    Route file to the correct parser.
    """
    if source_type == "AOI":
        return parse_aoi_for_pipeline(file_path)
    
    if source_type == "AXI":
        return parse_axi_for_pipeline(file_path)

    if source_type == "FP":
        return parse_fp_for_pipeline(file_path)

    if source_type == "MES":
        return parse_mes_for_pipeline(file_path)

    raise ValueError(f"Unsupported source type: {source_type}")


def process_file(file_path):
    """
    Process a single incoming file:
    detect source, parse, update metadata, assemble if ready.
    """
    source_type = detect_source_type(file_path)

    if source_type is None:
        print(f"Skipping unrecognized file: {file_path}")
        log_event(
            event_type="FILE_SKIPPED",
            message="Unrecognized file type skipped",
            extra={"path": str(file_path)}
        )
        return

    print(f"Processing {source_type} file: {file_path}")
    log_event(
        event_type="PROCESSING_STARTED",
        message=f"Processing {source_type} file",
        source_type=source_type,
        extra={"path": str(file_path)}
    )

    try:
        parsed_record = parse_file_by_source(file_path, source_type)

        serial_number = parsed_record["serial_number"]

        log_event(
            event_type="PARSE_SUCCESS",
            message=f"Parsed {source_type} file successfully",
            serial_number=serial_number,
            source_type=source_type
        )

        metadata = load_metadata()
        metadata = update_board_record(metadata, parsed_record)
        save_metadata(metadata)

        board_record = get_board_record(metadata, serial_number)

        if board_record and board_record.get("ready_for_assembly") and not board_record.get("output_created"):
            print(f"Board {serial_number} is ready for assembly.")
            log_event(
                event_type="ASSEMBLY_READY",
                message="Board is ready for assembly",
                serial_number=serial_number
            )

            edhr_record = assemble_edhr(serial_number, board_record)
            json_path = save_edhr_output(serial_number, edhr_record)

            docx_path = json_path.replace(".json", ".docx")
            render_edhr_docx(json_path, docx_path)

            board_record["output_created"] = True
            save_metadata(metadata)

            print(f"eDHR JSON created: {json_path}")
            print(f"eDHR DOCX created: {docx_path}")

            log_event(
                event_type="ASSEMBLY_COMPLETE",
                message="eDHR JSON and DOCX created",
                serial_number=serial_number,
                extra={"json_path": json_path, "docx_path": docx_path}
            )

        elif board_record and board_record.get("output_created"):
            print(f"Board {serial_number} has already been assembled.")
            log_event(
                event_type="ASSEMBLY_SKIPPED",
                message="Board already assembled",
                serial_number=serial_number
            )

        else:
            print(f"Board {serial_number} is not ready yet.")
            log_event(
                event_type="ASSEMBLY_WAITING",
                message="Board is not ready yet",
                serial_number=serial_number,
                extra={"sources_received": board_record.get("sources_received", {}) if board_record else {}}
            )

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        log_event(
            event_type="PROCESSING_ERROR",
            message=str(e),
            source_type=source_type,
            extra={"path": str(file_path)}
        )

        metadata = load_metadata()
        metadata = record_failed_source(
            metadata=metadata,
            source_type=source_type if source_type else "UNKNOWN",
            file_path=str(file_path),
            error_message=str(e),
            serial_number=None
        )
        save_metadata(metadata)