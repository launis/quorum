
@echo off
cd c:\src\quorum\backend
python -m pytest c:\src\quorum\backend\tests\api\transformers > test_results.txt 2>&1
echo Done.
