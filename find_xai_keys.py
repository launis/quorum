import json

try:
    with open('c:\\src\\quorum\\OMAT_AJOTIEDOT.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print("Mistä etsitään XAI-Raportoijan ulostuloja ja tunnisteita:\n")
    
    # Etsi kaikki sp_-alkuiset tai muuten merkittävät tunnisteet koko JSON:sta.
    found_keys = []
    
    def search_dict(d, path=""):
        if isinstance(d, dict):
            for k, v in d.items():
                new_path = f"{path}.{k}" if path else k
                if "XAI" in str(k) or "xai" in str(k).lower() or str(k).startswith("sp_") or "falsification" in str(k).lower() or "risk_flag" in str(k).lower():
                    found_keys.append(f"Mielenkiintoinen AVAIN löytyi: {new_path}")
                if "XAI" in str(v) or "xai" in str(v).lower() or "falsification" in str(v).lower() or "risk_flag" in str(v).lower():
                    if isinstance(v, str) and len(v) < 100:
                        found_keys.append(f"Mielenkiintoinen ARVO löytyi ({new_path}): {v}")
                
                search_dict(v, new_path)
        elif isinstance(d, list):
            for i, item in enumerate(d):
                search_dict(item, f"{path}[{i}]")

    search_dict(data)
    
    if found_keys:
        for f in found_keys:
            print(f)
    else:
        print("Hakusanat eivät tuottaneet yhtään osumaa koko tiedostossa. Ajo (exe_...) ei välttämättä ajanut XAI-raportoijaa tai avainsanoja ei ole tässä ajossa.")
            
except Exception as e:
    print(f"Virhe: {e}")
