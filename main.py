from pathlib import Path
from orchestrator import process_file
from logger_utils import log_event
import time

#start execution timer
script_start = time.perf_counter()

def process_all_incoming_files():
    incoming_root = Path(__file__).parent / "data" / "incoming"

    print("Looking in:", incoming_root)

    if not incoming_root.exists():
        print("Incoming folder does not exist.")
        log_event(
            event_type="SYSTEM_WARNING",
            message="Incoming folder does not exist",
            extra={"incoming_root": str(incoming_root)}
        )
        return

    for file_path in incoming_root.rglob("*"):
        if file_path.is_file():
            print("FOUND FILE:", file_path)
            log_event(
                event_type="FILE_DETECTED",
                message="File detected in incoming folder",
                extra={"path": str(file_path)}
            )
            process_file(file_path)


if __name__ == "__main__":
    process_all_incoming_files()

#end time
script_end = time.perf_counter()

script_execution_time = script_end - script_start
print(f"Script execution time: {script_execution_time:.3f} seconds")