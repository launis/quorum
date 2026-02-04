import pytest
import sys
import io

# Capture stdout/stderr
class CatchOut:
    def __init__(self):
        self.value = io.StringIO()
    def write(self, txt):
        self.value.write(txt)
    def flush(self):
        pass

if __name__ == "__main__":
    # We can't easily capture pytest output via sys.stdout redirect inside the same process 
    # because pytest captures it. 
    # But we can try using capsys fixture logic manually or just rely on default output if run from python.
    # The issue might be just that 'command_status' truncates or has encoding issues with the previous run.
    
    # Let's try to run pytest and let it print to stdout, but we ensure we read it 
    # by running this script via run_command and checking output in small chunks if needed.
    # OR we write to a file explicitly in python.
    
    from _pytest.main import Session
    from _pytest.runner import call_and_report
    
    # Simpler: redirect stdout/stderr at system level
    sys.stdout = open('py_test_output.txt', 'w', encoding='utf-8')
    sys.stderr = sys.stdout
    
    retcode = pytest.main(["-vv", "-o", "asyncio_mode=auto", "backend/tests/api/test_builder_preview.py"])
    
    sys.stdout.close()
    sys.exit(retcode)
