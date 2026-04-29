import re

def normalize_serial(serial):
    if not serial:
        return None

    serial = str(serial).strip().upper()
    serial = re.sub(r"-\d+$", "", serial)
    return serial