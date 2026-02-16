
from googleapiclient import discovery
import google.auth
from dotenv import load_dotenv
import os

load_dotenv(override=True)

try:
    credentials, project = google.auth.default()
    service = discovery.build(
        "aiplatform", 
        "v1", 
        credentials=credentials,
        discoveryServiceUrl="https://us-central1-aiplatform.googleapis.com/$discovery/rest?version=v1"
    )
    
    print(f"Service Attributes (subset): {[m for m in dir(service) if not m.startswith('_')]}")
    
    # Check top level
    if hasattr(service, 'projects'):
        print("✅ Found 'projects' resource")
        projects = service.projects()
        
        if hasattr(projects, 'locations'):
            print("✅ Found 'projects.locations' resource")
            locations = projects.locations()
            
            if hasattr(locations, 'publishers'):
                print("✅ Found 'projects.locations.publishers' resource")
                publishers = locations.publishers()
                
                if hasattr(publishers, 'models'):
                    print("✅ Found 'projects.locations.publishers.models' resource")
                    models = publishers.models()
                    print(f"Models Resource Methods: {[m for m in dir(models) if not m.startswith('_')]}")
                else:
                    print("❌ 'models' NOT found on publishers")
            else:
                print("❌ 'publishers' NOT found on locations")
        else:
            print("❌ 'locations' NOT found on projects")
    else:
        print("❌ 'projects' NOT found on service")
    
except Exception as e:
    print(f"Error: {e}")
