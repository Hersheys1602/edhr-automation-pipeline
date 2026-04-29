def create_blank_edhr():
    return {

        "document_control": {
            "issued_by": {
                "name": None,
                "position": None,
                "company": "Jabil, Inc"
                        },
            "issuance_date": None,
            "manufacturing_instructions": "[MANUFACTURING INSTRUCTIONS]"
        },  
        # 1. DEVICE IDENTIFICATION
        "device_identification": {
            "serial_number": None,
            "assembly_id": None,
            "assembly_revision": None,
            "board_type": None,
            "board_revision": None,
            "image_id": None,
            "customer": None,
            "manufacturing_start_time": None,
            "manufacturing_end_time": None
        },

        # 2. PROCESS EXECUTION SUMMARY (MES-driven)
        "process_execution_summary": [
        {
    
        "route_name": None,              # Main  Building / SAN Line 2 / Bay 2
        "process_step": None,            # e.g., AOI, Reflow, SPI
        "equipment_id": None,            # machine name/ID
        "system_version": None,          # what firmware version
        "operator_id": None,             # who ran it
        "start_time": None,
        "end_time": None,
        "status": None                  # PASS / FAIL / REWORK / SKIPPED
        }
],
    

        # 3. INSPECTION & DEFECTS
        "inspection_and_defects": {

            # A. Defect list (MES/AOI/AXI merged view)
          "defect_summary": [ 
              {
    
        "source": None,              # AOI / AXI / FP / MES
       "defect_code": None,
        "defect_name": None,         # e.g., Solder Bridge
       "component_refdes": None,    # e.g., U14, R32
        "pin_or_location": None,     # pin number / joint / coordinate
        "disposition": None,         # Reworked / False Call / Repair Later / Variation OK
        "acceptance_status": None,   # Accept / Reject / Open / Closed
        "reviewer": None,
        "time_in": None,
        "time_out": None,
        "comments": None
              }
    
],

            # B. Inspection summaries
            "inspection_summary": {

               "aoi": {
    "test_start_time": None,
    "test_end_time": None,
    "test_status": None,
    "tester_name": None,
    "stage": None,
    "components_tested": None,
    "joints_tested": None,
    "indicted_components": None,
    "indicted_pins": None,
    "total_defects": None
},

                "axi": {
    "test_start_time": None,
    "test_end_time": None,
    "test_status": None,
    "tester_name": None,
    "stage": None,
    "components_tested": None,
    "joints_tested": None,
    "indicted_components": None,
    "indicted_pins": None,
    "total_defects": None,
    "repaired_defects": None,
    "false_called_defects": None,
    "active_defects": None,
    "variation_ok_defects": None,
    "repair_later_defects": None
},

                "flying_probe": {
    "test_time": None,
    "test_duration": None,
    "overall_result": None,
    "tester_name": None,
    "test_process": None,
    "test_points": None,
    "test_steps": None,
    "defect_total": None,    # D.T
    "defect_pass": None,     # D.P
    "defect_fail": None,     # D.F
    "global_pass": None,     # G.P
    "global_fail": None      # G.F
}
            }
        },

        #4. REWORK DOCUMENTATION
       "rework_documentation": [],   

         #5. DEVIATION DOCUMENTATION
        "deviation_documentation": [
            {             
                "deviation_number": None,
                "deviation_type": None,
                "from_date": None,
                "to_date": None,
                "memo": None
            }             
        ],

         #6. COMPONENT TRACEABILITY 
       "component_traceability": [
    {
        "part_number": None,
        "lot_number": None,
        "supplier": None,
        "reel_id": None,
        "feeder_slot_id": None,
        "reference_designator": None,   # e.g., R12, U3
        "board_location": None,         
        "quantity_used": None
    }
],

        # 7. ELECTRICAL TEST CERTIFICATION (FP summary)
        "electrical_test_certification": {
            "test_type": None,
            "tester": None,
            "test_duration": None,
            "final_result": None
        }
    }

