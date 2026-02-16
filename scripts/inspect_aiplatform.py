
try:
    from google.cloud import aiplatform_v1
    print("✅ Imported aiplatform_v1")
    print(f"Dir: {dir(aiplatform_v1)[:20]}...")
    
    if hasattr(aiplatform_v1, 'ListPublisherModelsRequest'):
        print("✅ ListPublisherModelsRequest found at top level")
    else:
        print("❌ ListPublisherModelsRequest NOT found at top level")
        
    if hasattr(aiplatform_v1, 'types'):
        print("✅ types found")
        if hasattr(aiplatform_v1.types, 'ListPublisherModelsRequest'):
            print("✅ ListPublisherModelsRequest found in types")
        else:
            print("❌ ListPublisherModelsRequest NOT found in types")
            
except ImportError as e:
    print(f"❌ ImportError: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
