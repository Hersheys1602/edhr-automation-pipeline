import xml.etree.ElementTree as ET
from pathlib import Path


def parse_axi_xml(filepath: str) -> dict:
    """
    Parse an AXI XML file and map the data to the user's eDHR template structure.
    """

    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"AXI file not found: {filepath}")

    tree = ET.parse(path)
    root = tree.getroot()

    ns = {"ns1": "http://tempuri.org/BoardTestXMLExport.xsd"}

    board = root.find("ns1:BoardXML", ns)
    station = root.find("ns1:StationXML", ns)
    repair_event = root.find("ns1:RepairEventXML", ns)

    def get_attr(element, attr_name):
        if element is not None:
            return element.attrib.get(attr_name)
        return None

    def safe_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    # -----------------------------
    # 1. DEVICE IDENTIFICATION
    # -----------------------------
    device_identification = {
        "serial_number": get_attr(board, "serialNumber"),
        "assembly_revision": get_attr(board, "assemblyRevision"),
        "board_type": get_attr(board, "boardType"),
        "board_revision": get_attr(board, "boardRevision"),
        "image_id": get_attr(board, "imageId"),
        # leave these blank because AXI sample does not provide them directly
        "assembly_id": None,
        "customer": None,
        "manufacturing_start_time": None,
        "manufacturing_end_time": None,
    }

    # -----------------------------
    # 2. PROCESS EXECUTION SUMMARY
    # -----------------------------
    process_execution_summary = [
        {
            "route_name": None,
            "process_step": "AXI",
            "equipment_id": get_attr(station, "testerName"),
            "system_version": get_attr(station, "stage"),
            "operator_id": get_attr(repair_event, "repairOperator"),
            "start_time": get_attr(root, "testerTestStartTime"),
            "end_time": get_attr(root, "testerTestEndTime"),
            "status": get_attr(root, "testStatus"),
        }
    ]

    # -----------------------------
    # 3. INSPECTION SUMMARY - AXI
    # -----------------------------
    inspection_summary_axi = {
        "test_start_time": get_attr(root, "testerTestStartTime"),
        "test_end_time": get_attr(root, "testerTestEndTime"),
        "test_status": get_attr(root, "testStatus"),
        "tester_name": get_attr(station, "testerName"),
        "stage": get_attr(station, "stage"),
        "components_tested": safe_int(get_attr(root, "numberOfComponentsTested")),
        "joints_tested": safe_int(get_attr(root, "numberOfJointsTested")),
        "indicted_components": safe_int(get_attr(root, "numberOfIndictedComponents")),
        "indicted_pins": safe_int(get_attr(root, "numberOfIndictedPins")),
        "total_defects": safe_int(get_attr(root, "numberOfDefects")),
        "repaired_defects": safe_int(get_attr(repair_event, "numberOfRepairedDefects")),
        "false_called_defects": safe_int(get_attr(repair_event, "numberOfFalseCalledDefects")),
        "active_defects": safe_int(get_attr(repair_event, "numberOfActiveDefects")),
        "variation_ok_defects": safe_int(get_attr(repair_event, "numberOfVariationOkDefects")),
        "repair_later_defects": safe_int(get_attr(repair_event, "numberOfRepairLaterDefects")),
    }

    # -----------------------------
    # 4. DEFECT SUMMARY
    # -----------------------------
    defect_summary = []

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

        defect_summary.append(defect_row)

    # -----------------------------
    # 5. REWORK DOCUMENTATION
    # -----------------------------
    rework_documentation = []

    if repair_event is not None:
        rework_documentation.append(
            {
                "defect": None,
                "reworked_by": get_attr(repair_event, "repairOperator"),
                "date": get_attr(repair_event, "repairEndTime"),
                "repair_start_time": get_attr(repair_event, "repairStartTime"),
                "repair_end_time": get_attr(repair_event, "repairEndTime"),
                "rework_status": get_attr(root, "repairStatus"),
                "rework_flag": "AXI Repair Event",
                "rework_category": "AXI Review",
                "comment": (
                    f"ActiveDefects={get_attr(repair_event, 'numberOfActiveDefects')}; "
                    f"FalseCalledDefects={get_attr(repair_event, 'numberOfFalseCalledDefects')}; "
                    f"RepairedDefects={get_attr(repair_event, 'numberOfRepairedDefects')}; "
                    f"RepairLaterDefects={get_attr(repair_event, 'numberOfRepairLaterDefects')}; "
                    f"VariationOkDefects={get_attr(repair_event, 'numberOfVariationOkDefects')}"
                ),
            }
        )

    return {
        "device_identification": device_identification,
        "process_execution_summary": process_execution_summary,
        "inspection_summary_axi": inspection_summary_axi,
        "defect_summary": defect_summary,
        "rework_documentation": rework_documentation,
    }