from google.cloud import aiplatform_v1beta1
from google.api_core.client_options import ClientOptions
import os

def list_gemini_models(project_id, location="europe-north1"):
    # 1. Määritä API-endpoint valitulle lokaatiolle
    api_endpoint = f"{location}-aiplatform.googleapis.com"
    client_options = ClientOptions(api_endpoint=api_endpoint)

    # 2. Luo Model Garden -asiakas (BETA)
    # Käytetään suoraa importtia paketista (ei services-polkua, joka on hauras)
    client = aiplatform_v1beta1.ModelGardenServiceClient(client_options=client_options)

    # 3. Määritä parent
    parent = "publishers/google"

    print(f"Haetaan Gemini-malleja lokaatiosta: {location} (Project: {project_id}) [API: v1beta1]...\n")
    # Debug:
    # print("Methods:", [m for m in dir(client) if "list" in m])

    try:
        # 4. Tee haku suoraan argumenteilla
        # Beta-versiossa metodi on varmasti list_publisher_models
        response = client.list_publisher_models(parent=parent)

        found_models = []

        for model in response:
            # Mallin resurssinimi on muotoa: publishers/google/models/gemini-1.5-pro
            model_id = model.name.split('/')[-1]
            
            # 5. Suodatetaan lista (näytetään vain Gemini-mallit)
            if "gemini" in model_id.lower():
                found_models.append(model_id)
                print(f"Model ID: {model_id}")

        if not found_models:
            print("Ei löytynyt malleja hakusanalla 'gemini'.")
            
    except Exception as e:
        print(f"Virhe haettaessa malleja: {e}")

if __name__ == "__main__":
    # Aseta credentials polku koodissa varmuuden vuoksi, jos env ei ole vielä ladattu
    if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service-account.json"
    
    list_gemini_models("cognitive-quorum", "europe-west4")
