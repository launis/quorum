
import sys
import pytest

with open("test_result_log.txt", "w", encoding="utf-8") as f:
    class FilePlugin:
        def pytest_runtest_logreport(self, report):
            if report.when == "call":
                f.write(f"TEST: {report.nodeid}\n")
                f.write(f"RESULT: {report.outcome.upper()}\n")
                if report.longrepr:
                    f.write(f"FAILURE DETAILS:\n{str(report.longrepr)}\n")
                f.write("-" * 40 + "\n")

    sys.exit(pytest.main(["tests/test_admin_error_compliance.py", "-v"], plugins=[FilePlugin()]))
