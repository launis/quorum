
try:
    from google.cloud import aiplatform
    print(f"Version: {aiplatform.__version__}")
    
    from google.cloud import aiplatform_v1
    print(f"V1 Version: {aiplatform_v1.__name__}")
    
    client = aiplatform.gapic.ModelGardenServiceClient()
    methods = [m for m in dir(client) if "list" in m]
    print(f"Methods: {methods}")
    
except Exception as e:
    print(f"Error: {e}")
