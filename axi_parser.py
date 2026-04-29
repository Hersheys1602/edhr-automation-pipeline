import xml.etree.ElementTree as ET
from pathlib import Path
from utils import normalize_serial


def parse_axi_for_pipeline(axi_filepath):
    """
    Parse an AXI XML file and return a standardized record
    for the AWS-style simulation pipeline.
    """

    tree = ET.parse(axi_filepath)
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

    repair_start = get_attr(repair, "repairStartTime")
    repair_end = get_attr(repair, "repairEndTime")
    repair_operator = get_attr(repair, "repairOperator")
    repair_status = get_attr(root, "repairStatus")

    # -----------------------------
    # 1. REWORK DOCUMENTATION
    # -----------------------------
    rework_documentation = []

    if repair_status and repair_status.strip().lower() != "repair none":
        rework_documentation.append({
            "source": "AXI",
            "defect_name": None,
            "component_refdes": None,
            "pin_or_location": None,
            "reworked_by": repair_operator,
            "rework_date": repair_start[:10] if repair_start else None,
            "repair_start_time": repair_start,
            "repair_end_time": repair_end,
            "rework_status": repair_status,
            "rework_category": "AXI Post-Repair Event",
            "comments": (
                f"ActiveDefects={get_attr(repair, 'numberOfActiveDefects')}; "
                f"FalseCalledDefects={get_attr(repair, 'numberOfFalseCalledDefects')}; "
                f"RepairedDefects={get_attr(repair, 'numberOfRepairedDefects')}; "
                f"RepairLaterDefects={get_attr(repair, 'numberOfRepairLaterDefects')}; "
                f"VariationOkDefects={get_attr(repair, 'numberOfVariationOkDefects')}"
            )
        })

    # -----------------------------
    # 2. AXI SUMMARY
    # -----------------------------
    axi_summary = {
        "test_status": get_attr(root, "testStatus"),
        "tester_name": get_attr(station, "testerName"),
        "stage": get_attr(station, "stage"),
        "image_id": get_attr(board, "imageId"),
        "components_tested": safe_int(get_attr(root, "numberOfComponentsTested")),
        "joints_tested": safe_int(get_attr(root, "numberOfJointsTested")),
        "indicted_components": safe_int(get_attr(root, "numberOfIndictedComponents")),
        "indicted_pins": safe_int(get_attr(root, "numberOfIndictedPins")),
        "total_defects": safe_int(get_attr(root, "numberOfDefects")),
        "repair_status": repair_status,
    }

    # -----------------------------
    # 3. DEFECT SUMMARY ROWS
    # -----------------------------
    defect_summary_rows = []

    for test in root.findall("ns1:TestXML", ns):
        test_name = get_attr(test, "name")
        indictment = test.find("ns1:IndictmentXML", ns)
        if indictment is None:
            continue

        repair_action = indictment.find("ns1:RepairActionXML", ns)
        component = indictment.find("ns1:ComponentXML", ns)

        defect_row = {
            "source": "AXI",
            "defect_code": None,
            "defect_name": get_attr(indictment, "indictmentType"),
            "component_refdes": get_attr(component, "designator"),
            "pin_or_location": get_attr(component, "pin"),
            "disposition": get_attr(repair_action, "repairStatus"),
            "acceptance_status": get_attr(root, "repairStatus"),
            "reviewer": get_attr(repair_action, "repairOperator"),
            "time_in": get_attr(root, "testerTestStartTime"),
            "time_out": get_attr(repair_action, "repairTime"),
            "comments": (
                f"test={test_name}; "
                f"algorithm={get_attr(indictment, 'algorithm')}; "
                f"subType={get_attr(indictment, 'subType')}; "
                f"jointType={get_attr(indictment, 'jointType')}; "
                f"packageId={get_attr(component, 'packageId')}; "
                f"repairActionType={get_attr(repair_action, 'repairActionType')}; "
                f"comment={get_attr(repair_action, 'comment')}"
            ),
        }

        defect_summary_rows.append(defect_row)

    # -----------------------------
    # 4. RAW DATA
    # -----------------------------
    raw_data = {
        "root": dict(root.attrib),
        "board": dict(board.attrib) if board is not None else {},
        "station": dict(station.attrib) if station is not None else {},
        "repair": dict(repair.attrib) if repair is not None else {},
    }

    # -----------------------------
    # 5. STANDARDIZED RECORD
    # -----------------------------
    standardized_record = {
        "source_type": "AXI",
        "serial_number_raw": get_attr(board, "serialNumber"),
        "serial_number": normalize_serial(get_attr(board, "serialNumber")),
        "assembly_id": None,
        "assembly_revision": get_attr(board, "assemblyRevision"),
        "board_type": get_attr(board, "boardType"),
        "board_revision": get_attr(board, "boardRevision"),
        "customer": None,
        "start_time": get_attr(root, "testerTestStartTime"),
        "end_time": get_attr(root, "testerTestEndTime"),
        "event_time": get_attr(root, "testTime"),
        "route_step": None,
        "source_file_name": Path(axi_filepath).name,
        "source_file_path": str(Path(axi_filepath)),
        "standardized_data": axi_summary,
        "defect_summary_rows": defect_summary_rows,
        "rework_documentation": rework_documentation,
        "raw_data": raw_data
    }

    return standardized_record