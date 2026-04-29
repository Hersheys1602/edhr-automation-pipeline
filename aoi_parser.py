import xml.etree.ElementTree as ET


def parse_aoi_xml(aoi_filepath):
    """
    Parse an AOI XML file and return data mapped to the eDHR schema.
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
            return 0

    # basic repair fields
    repair_start = get_attr(repair, "repairStartTime")
    repair_end = get_attr(repair, "repairEndTime")
    repair_operator = get_attr(repair, "repairOperator")
    repair_status = get_attr(root, "repairStatus")

    # rework documentation list
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

    # repair metrics
    repaired_defects = safe_int(get_attr(repair, "numberOfRepairedDefects"))
    false_called_defects = safe_int(get_attr(repair, "numberOfFalseCalledDefects"))
    active_defects = safe_int(get_attr(repair, "numberOfActiveDefects"))
    variation_ok_defects = safe_int(get_attr(repair, "numberOfVariationOkDefects"))
    repair_later_defects = safe_int(get_attr(repair, "numberOfRepairLaterDefects"))

    # AOI summary
    aoi_summary = {
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

        # always include repair-related metrics, even when zero
        "repaired_defects": repaired_defects,
        "false_called_defects": false_called_defects,
        "active_defects": active_defects,
        "variation_ok_defects": variation_ok_defects,
        "repair_later_defects": repair_later_defects,
    }

    raw_fields = {
        "root": dict(root.attrib),
        "board": dict(board.attrib) if board is not None else {},
        "station": dict(station.attrib) if station is not None else {},
        "repair": dict(repair.attrib) if repair is not None else {},
    }

    parsed_data = {
        "device_identification": {
            "serial_number": get_attr(board, "serialNumber"),
            "assembly_id": get_attr(board, "boardType"),
            "assembly_revision": get_attr(board, "assemblyRevision"),
            "board_type": get_attr(board, "boardType"),
            "board_revision": get_attr(board, "boardRevision"),
            "image_id": get_attr(board, "imageId"),
            "customer": None,
            "manufacturing_start_time": get_attr(root, "testerTestStartTime"),
            "manufacturing_end_time": get_attr(root, "testerTestEndTime"),
        },

        "inspection_and_defects": {
            "inspection_summary": {
                "aoi": aoi_summary
            }
        },

        "rework_documentation": rework_documentation,

        "raw_fields": raw_fields
    }

    return parsed_data

