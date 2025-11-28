@echo off
echo Cleaning up caches...
if exist __pycache__ rmdir /s /q __pycache__
if exist frontend\__pycache__ rmdir /s /q frontend\__pycache__

echo Starting Cognitive Quorum v2...
echo Ensure you are running this from the root directory (c:\Users\risto\OneDrive\quorum)
streamlit run ui.py --server.runOnSave false --server.port 8501
pause
