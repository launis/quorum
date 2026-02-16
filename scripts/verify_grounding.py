import vertexai
from vertexai.generative_models import GenerativeModel, Tool
import os
from dotenv import load_dotenv

# 1. Ladataan ympäristömuuttujat
load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "cognitive-quorum")
LOCATION = os.getenv("VERTEX_LOCATION", "europe-north1")

# Käytetään modernia Gemini 2.0 -mallia
MODEL_ID = "gemini-2.0-flash-001" 

def test_grounding():
    print(f"🚀 Testataan Vertex AI Groundingia (Project: {PROJECT_ID}, Model: {MODEL_ID})...")
    
    try:
        # 2. Alustus
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        # 3. Määritellään työkalu (KORJAUS)
        # Käytetään Tool.from_dict -metodia, jotta voimme pakottaa
        # uuden API:n vaatiman 'google_search' -rakenteen.
        print("🔧 Luodaan työkalu käyttäen 'google_search' -kenttää...")
        
        google_search_tool = Tool.from_dict({
            "google_search": {} 
        })
        
        # 4. Ladataan malli
        model = GenerativeModel(MODEL_ID) 
        
        # 5. Kysytään kysymys
        prompt = "Kuka voitti viimeisimmän jääkiekon maailmanmestaruuden ja millä tuloksella?"
        print(f"\nKysymys: '{prompt}'")
        print("Haetaan vastausta Googlen avulla...\n")

        response = model.generate_content(
            prompt,
            tools=[google_search_tool],
            generation_config={
                "temperature": 0.0
            }
        )
        
        # 6. Tulostetaan vastaus
        print("--- VASTAUS ---")
        try:
            print(response.text)
        except ValueError:
            print("(Vastaus estettiin turvasyistä tai oli tyhjä)")
        
        # 7. Tulostetaan lähteet
        print("\n--- LÄHTEET (Grounding Metadata) ---")
        if response.candidates and response.candidates[0].grounding_metadata:
            metadata = response.candidates[0].grounding_metadata
            
            if metadata.search_entry_point:
                print(f"Haku tehty: {metadata.search_entry_point.rendered_content}")
            
            found_sources = False
            if metadata.grounding_chunks:
                for chunk in metadata.grounding_chunks:
                    if chunk.web:
                        print(f"✅ Lähde: {chunk.web.title} ({chunk.web.uri})")
                        found_sources = True
            
            if not found_sources:
                print("⚠️ Ei suoria verkkolähteitä vastauksessa.")
            else:
                print("\n✅ TESTI LÄPI: Grounding toimii!")
        else:
            print("⚠️ Ei metadataa saatavilla.")

    except Exception as e:
        print(f"\n❌ VIRHE: {e}")

if __name__ == "__main__":
    test_grounding()