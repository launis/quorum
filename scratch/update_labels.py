import json

mapping = {
    "Episteeminen Nöyryys": {"new_label": "Oman tiedon rajat", "desc": "Arvioi kykyäsi tunnistaa, mitä et tiedä. Se varoittaa liiallisesta varmuudesta asioissa, jotka ovat todellisuudessa epävarmoja."},
    "Kausaalinen ja Abduktiivinen Integriteetti": {"new_label": "Päättelyn rehellisyys", "desc": "Varmistaa, että johtopäätöksesi ovat syntyneet aidon analyysin tuloksena, eivätkä ne ole vain keksittyjä selityksiä lopputulokselle."},
    "Kahnemanin Kaksoisprosessiteoria": {"new_label": "Harkintakyky", "desc": "Seuraa, käytätkö nopeaa intuitiota (Systeemi 1) vai hidasta, kriittistä harkintaa (Systeemi 2). Tavoitteena on välttää hätäisiä johtopäätöksiä."},
    "Toulminin Argumentaatiomalli": {"new_label": "Väitteiden perustelu", "desc": "Kertoo, kuinka taitavasti perustelet asiasi. Se seuraa, onko esittämilläsi väitteillä selkeä looginen pohja."},
    "Falsifioinnin Auditointi": {"new_label": "Itsensä haastaminen", "desc": "Mittaa haluasi etsiä virheitä omista ajatuksistasi. Se arvioi, yritätkö aktiivisesti todistaa omat väitteesi vääriksi vahvistaaksesi niitä."},
    "Kausaalisuuden Analyysi": {"new_label": "Syy-seuraussuhteet", "desc": "Arvioi kykyäsi ymmärtää, mikä johtaa mihinkin. Se mittaa, kuinka hyvin hallitset monimutkaisia ketjuja, joissa yksi asia vaikuttaa toiseen."},
    "Arkistointistandardien Auditointi": {"new_label": "Ohjeiden noudattaminen", "desc": "Seuraa, kuinka hyvin pysyt sovituissa raameissa ja parhaissa käytännöissä työn aikana."},
    "Selitettävyys ja Läpinäkyvyys": {"new_label": "Avoimuus", "desc": "Mittaa, kuinka helposti raporttisi logiikka on ulkopuolisen seurattavissa ja kuinka hyvin olet avannut käytetyt lähteet."},
    "Bloomin Taksonomia": {"new_label": "Luovuus ja syvyys", "desc": "Mittaa, kuinka syvälle pureudut aiheeseen. Korkeimmalla tasolla et vain toista tietoa, vaan luot tekoälyn avulla täysin uusia näkökulmia."},
    "Ylituomari": {"new_label": "Prosessiomistajuus", "desc": "Tämä kuvaa sitä, kuinka vahvasti otat vastuun koko ketjusta ja ohjaat työtä alusta loppuun."},
    "Performatiivisuus ja Goodhartin Laki": {"new_label": "Aktiivinen ohjaus", "desc": "Arvioi, oletko prosessin johtaja vai pelkkä matkustaja. Se mittaa, kuinka aktiivisesti ohjaat tekoälyä kohti tavoitetta."},
    "XAI-Raportoija": {"new_label": "Luottamusarvio", "desc": "Arvioi tekoälyn suositusten läpinäkyvyyttä ja selitettävyyttä luottamuksen rakentamiseksi."},
    "Turvallisuus- ja Etiikkasuodatin": {"new_label": "Vastuullisuus", "desc": "Varmistaa, ettei tekoälyä käytetä tavalla, joka tuottaa perusteetonta tai riskialtista tietoa."},
    "Vastuullisuus": {"new_label": "Vastuullisuus", "desc": "Varmistaa, ettei tekoälyä käytetä tavalla, joka tuottaa perusteetonta tai riskialtista tietoa."}
}

file_path = 'backend_v2/seed/seed_data.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

updated_count = 0
for block in data.get('prompt_blocks', []):
    label_fi = block.get('label', {}).get('translations', {}).get('fi', '')
    
    # Try exact match first
    matched_key = None
    if label_fi in mapping:
        matched_key = label_fi
    else:
        # fuzzy match if there's minor differences or already renamed
        for k in mapping.keys():
            if k.lower() in label_fi.lower() or label_fi.lower() in k.lower():
                matched_key = k
                break
                
    if matched_key:
        v = mapping[matched_key]
        # Only update if not already updated
        if "(" not in label_fi:
            # We want "New Label (Old Label)" format
            # Let's clean up the old label (e.g. if it was "Vastuullisuus", it maps to Vastuullisuus)
            original_title = matched_key if matched_key != "Vastuullisuus" else "Turvallisuus- ja Etiikkasuodatin"
            new_title = f"{v['new_label']} ({original_title})"
            
            block['label']['translations']['fi'] = new_title
            
            if 'description' not in block or block['description'] is None:
                block['description'] = {'default_locale': 'fi', 'translations': {}}
            block['description']['translations']['fi'] = v['desc']
            updated_count += 1
            print(f"Updated {matched_key} -> {new_title}")

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Total updated: {updated_count}")
