import xml.etree.ElementTree as ET
from pathlib import Path
from utils import normalize_serial


def parse_aoi_for_pipeline(aoi_filepath):
    """
    Parse an AOI XML file and return a standardized record
    for the AWS-style simulation pipeline.
    """

    tree = ET.parse(aoi_filepath)
    root = tree.getroot()

    ns = {"ns1": "http://tempuri.org/BoardTestXMLExport.xsd"}

    board = root.find("ns1:BoardXML", ns)
    station = root.find("ns1:StationXML", ns)
    repair = root.find("ns1:RepairEventXML", ns)

    def get_attr(element, attr_name):
        if element is not None:
            return element.attrib.get(attr_name)
        return None

    def safe_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    # Basic repair fields
    repair_start = get_attr(repair, "repairStartTime")
    repair_end = get_attr(repair, "repairEndTime")
    repair_operator = get_attr(repair, "repairOperator")
    repair_status = get_attr(root, "repairStatus")

    # Rework documentation list
    rework_documentation = []

    if repair_status and repair_status.strip().lower() != "repair none":
        rework_documentation.append({
            "source": "AOI",
            "defect_name": None,
            "component_refdes": None,
            "pin_or_location": None,
            "reworked_by": repair_operator,
            "rework_date": repair_start[:10] if repair_start else None,
            "repair_start_time": repair_start,
            "repair_end_time": repair_end,
            "rework_status": repair_status,
            "rework_category": "AOI Post-Repair Event",
            "comments": None
        })

    # Repair metrics
    repaired_defects = safe_int(get_attr(repair, "numberOfRepairedDefects"))
    false_called_defects = safe_int(get_attr(repair, "numberOfFalseCalledDefects"))
    active_defects = safe_int(get_attr(repair, "numberOfActiveDefects"))
    variation_ok_defects = safe_int(get_attr(repair, "numberOfVariationOkDefects"))
    repair_later_defects = safe_int(get_attr(repair, "numberOfRepairLaterDefects"))

    # Standardized AOI summary
    aoi_summary = {
        "test_status": get_attr(root, "testStatus"),
        "tester_name": get_attr(station, "testerName"),
        "stage": get_attr(station, "stage"),
        "image_id": get_attr(board, "imageId"),
        "components_tested": safe_int(get_attr(root, "numberOfComponentsTested")),
        "joints_tested": safe_int(get_attr(root, "numberOfJointsTested")),
        "indicted_components": safe_int(get_attr(root, "numberOfIndictedComponents")),
        "indicted_pins": safe_int(get_attr(root, "numberOfIndictedPins")),
        "total_defects": safe_int(get_attr(root, "numberOfDefects")),
    }

    if repaired_defects and repaired_defects > 0:
        aoi_summary["repaired_defects"] = repaired_defects

    if false_called_defects and false_called_defects > 0:
        aoi_summary["false_called_defects"] = false_called_defects

    if active_defects and active_defects > 0:
        aoi_summary["active_defects"] = active_defects

    if variation_ok_defects and variation_ok_defects > 0:
        aoi_summary["variation_ok_defects"] = variation_ok_defects

    if repair_later_defects and repair_later_defects > 0:
        aoi_summary["repair_later_defects"] = repair_later_defects

    raw_data = {
        "root": dict(root.attrib),
        "board": dict(board.attrib) if board is not None else {},
        "station": dict(station.attrib) if station is not None else {},
        "repair": dict(repair.attrib) if repair is not None else {},
    }

    standardized_record = {
        "source_type": "AOI",
        "serial_number_raw": get_attr(board, "serialNumber"),
        "serial_number": normalize_serial(get_attr(board, "serialNumber")),
        "assembly_id": None,  # AOI file does not clearly provide this
        "assembly_revision": get_attr(board, "assemblyRevision"),
        "board_type": get_attr(board, "boardType"),
        "board_revision": get_attr(board, "boardRevision"),
        "customer": None,
        "start_time": get_attr(root, "testerTestStartTime"),
        "end_time": get_attr(root, "testerTestEndTime"),
        "event_time": get_attr(root, "testTime"),
        "route_step": None,
        "source_file_name": Path(aoi_filepath).name,
        "source_file_path": str(Path(aoi_filepath)),
        "standardized_data": aoi_summary,
        "rework_documentation": rework_documentation,
        "raw_data": raw_data
    }

    return standardized_record