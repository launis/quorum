import json
import os
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from google.oauth2 import service_account
from dotenv import load_dotenv

def parse_pasted_chat_with_vertex(raw_paste: str, project_id: str, location: str = "europe-west1") -> dict:
    """
    Ottaa vastaan asiakkaan käyttöliittymään liittämän (paste) sotkuisen raakatekstin
    ja käyttää Geminiä sen muuttamiseksi puhtaaksi, analyysivalmiiksi JSON-dataksi.
    """
    
    # Ladataan ympäristömuuttujat .env -tiedostosta
    load_dotenv()
    
    # Etsitään service-account.json polkua .env:stä (tai vakiopolkuna)
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not creds_path or not os.path.exists(creds_path):
         creds_path = os.path.join(os.getcwd(), "service-account.json")
    
    # 1. Alusta Vertex AI Service Accountilla
    if os.path.exists(creds_path):
        credentials = service_account.Credentials.from_service_account_file(creds_path)
        vertexai.init(project=project_id, location=location, credentials=credentials)
    else:
        # Fallback lokaaliin auth-ympäristöön
        vertexai.init(project=project_id, location=location)
        
    # Käytetään Gemini 1.5 Flash -mallia: Täydellinen, nopea ja kustannustehokas datan erotteluun
    model = GenerativeModel("gemini-2.5-pro")
    
    # KRIITTINEN KOHTA: Pakotetaan malli vastaamaan pelkällä JSON:illa.
    # Lämpötila (temperature) 0.0 varmistaa, että tekoäly käyttäytyy kuin robotti:
    # se ei hallusinoi tai keksi omiaan, vaan ainoastaan poimii faktat tekstistä.
    generation_config = GenerationConfig(
        response_mime_type="application/json",
        temperature=0.0,
    )
    
    # 2. Määritellään tiukka ohjeistus (System Prompt)
    prompt = f"""
    Olet datanlouhinta-asiantuntija. Tehtäväsi on ottaa vastaan käyttäjän selaimesta 
    kopioima (copy-paste) sotkuinen raakateksti, joka on peräisin tekoälykeskustelusta 
    (esim. ChatGPT, Gemini tai Claude).

    SÄÄNNÖT:
    1. Erottele tekstistä ihmisen (User) ja tekoälyn (AI) viestit.
    2. Jätä täysin huomiotta kaikki käyttöliittymän roskateksti (esim. "Regenerate", "Copy code", aikaleimat, "Was this response better or worse?", sivuvalikot, profiilien nimet).
    3. Palauta data TÄSMÄLLEEN alla olevassa JSON-muodossa.

    Odotettu JSON-rakenne:
    {{
      "conversation": [
        {{
          "order": 1,
          "role": "User",
          "text": "Käyttäjän viestin sisältö tähän"
        }},
        {{
          "order": 2,
          "role": "AI",
          "text": "Tekoälyn vastaus tähän"
        }}
      ]
    }}

    Tässä on käsiteltävä raakateksti:
    <raakateksti>
    {raw_paste}
    </raakateksti>
    """
    
    try:
        # 3. Kutsutaan mallia
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # 4. Koska pakotimme mime-tyypin, vastaus on suoraan jäsenneltävissä Python-sanakirjaksi
        parsed_data = json.loads(response.text)
        return parsed_data
        
    except json.JSONDecodeError as e:
        print(f"❌ Gemini ei palauttanut validia JSON:ia: {e}")
        return {}
    except Exception as e:
        print(f"❌ Virhe Vertex AI -yhteydessä: {e}")
        return {}

# ==========================================
# KÄYTTÖLIITTYMÄ (Tkinter)
# ==========================================
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading

def run_ui():
    load_dotenv()
    default_project = os.getenv("GOOGLE_CLOUD_PROJECT", "cognitive-quorum")
    default_location = os.getenv("VERTEX_LOCATION", "europe-north1")
    
    def process_text():
        raw_text = text_area.get("1.0", tk.END).strip()
        if not raw_text:
            messagebox.showwarning("Varoitus", "Tekstikenttä on tyhjä!")
            return
            
        project_id = project_entry.get().strip()
        location_id = location_entry.get().strip()
        
        if not project_id:
            messagebox.showwarning("Varoitus", "Syötä GCP Projektin ID!")
            return
            
        result_area.delete("1.0", tk.END)
        result_area.insert(tk.END, "⏳ Käsitellään pyyntöä Geminillä, odota hetki...\n")
        
        # Poistetaan nappi käytöstä suorituksen ajaksi
        btn.config(state=tk.DISABLED)
        
        def run_inference():
            try:
                print(f"[DEBUG] Aloitetaan jäsennys. Projekti: {project_id}, Sijainti: {location_id}")
                print(f"[DEBUG] Tekstin pituus: {len(raw_text)} merkkiä.")
                valmis_data = parse_pasted_chat_with_vertex(raw_text, project_id, location_id)
                
                # Takaisin UI-säikeeseen
                root.after(0, update_ui_success, valmis_data)
            except Exception as e:
                print(f"[DEBUG] Exception kaapattu lankasta: {e}")
                import traceback
                traceback.print_exc()
                root.after(0, update_ui_error, str(e))
                
        def update_ui_success(valmis_data):
            btn.config(state=tk.NORMAL)
            result_area.delete("1.0", tk.END)
            if valmis_data:
                result_area.insert(tk.END, "✅ ONNISTUI! Puhdistettu JSON:\n\n")
                result_area.insert(tk.END, json.dumps(valmis_data, indent=2, ensure_ascii=False))
                print("[DEBUG] Jäsennys valmis ja tulostettu käyttöliittymään.")
            else:
                result_area.insert(tk.END, "❌ Jäsentäminen epäonnistui tai palautti tyhjää.\nTarkista terminaalin virheet.")
                print("[DEBUG] Jäsennys palautti tyhjän tuloksen.")
                
        def update_ui_error(error_msg):
            btn.config(state=tk.NORMAL)
            result_area.delete("1.0", tk.END)
            result_area.insert(tk.END, f"❌ Virhe ajon aikana:\n{error_msg}")
            
        # Käynnistetään taustasäie
        print("[DEBUG] Käynnistetään taustasäie Vertex AI -pyynnölle.")
        threading.Thread(target=run_inference, daemon=True).start()

    root = tk.Tk()
    root.title("Tekoälykeskustelun Jäsennin (Gemini 2.5 Pro)")
    root.geometry("800x750")
    
    # Yläpalkki: Configs
    top_frame = tk.Frame(root)
    top_frame.pack(pady=10, padx=10, fill=tk.X)
    
    tk.Label(top_frame, text="Project ID:").pack(side=tk.LEFT)
    project_entry = tk.Entry(top_frame, width=30)
    project_entry.pack(side=tk.LEFT, padx=5)
    project_entry.insert(0, default_project)
    
    tk.Label(top_frame, text="Location:").pack(side=tk.LEFT, padx=(10, 0))
    location_entry = tk.Entry(top_frame, width=15)
    location_entry.pack(side=tk.LEFT, padx=5)
    location_entry.insert(0, default_location)
    
    # Syöttökenttä (Kopioitu teksti)
    tk.Label(root, text="1. Liitä (Copy-Paste) raakateksti tähän:").pack(anchor=tk.W, padx=10, pady=(10, 0))
    text_area = scrolledtext.ScrolledText(root, height=12)
    text_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    # Suoritusnappi
    btn = tk.Button(root, text="2. Jäsennä JSON-muotoon", command=process_text, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
    btn.pack(pady=10)
    
    # Tuloskenttä (JSON)
    tk.Label(root, text="Tulokset (Puhdas JSON):").pack(anchor=tk.W, padx=10)
    result_area = scrolledtext.ScrolledText(root, height=15, bg="#f4f4f4")
    result_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    run_ui()