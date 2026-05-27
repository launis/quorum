import json

# The 17 oscillating atoms from 11.md
# The historically oscillating atoms with high frequency of mismatches (>= 4 out of 19 runs)
high_entropy_ids = {
    # Alkuperäiset
    "tda_bce60530213249dd",
    "tda_545bffdc85a31f0e",
    "tda_f142c3fa1d08cc2d",
    "tda_247927c98b0c46f8",
    "tda_bdbdc546677cc222",
    "tda_55dfd9cb0adec620",
    "tda_2303fd9ca0b0fa67",
    "tda_8b1717b2ca9f25e2",
    "tda_c74c4367acc028cf",
    "tda_8f668ea29869ba8b",
    "tda_9ab273ce743ac29e",
    "tda_8c7b6a9f0d8e411b",
    "tda_c6bcce2b818718a1",
    "tda_ade6cbd3f956fa67",
    "tda_32ee0cac79ad098e",
    "tda_6bf0433f60924302",
    "tda_80c038ed35173cb4",
    
    # Uudet historiallisesti epävakaat (esiintymiskerrat >= 5)
    "tda_d0b6789c895808eb", # 6 kertaa (31.6%) Mustavalkoinen ajattelu / dikotomia
    "tda_3d3f1162d2ff1558", # 6 kertaa (31.6%) Rajoitusten sivuuttaminen
    "tda_50d614006cd53384", # 5 kertaa (26.3%) Absoluuttiset tilajulistukset
    "tda_31ae4494272845fe", # 5 kertaa (26.3%) Siltaussäännöt / warrantit
    "tda_2aec15ab07984f4d", # 5 kertaa (26.3%) Ennusteet / 100% varmuus
    "tda_cee9db6717cdafb7", # 5 kertaa (26.3%) Riskien purkaminen datalla
    "tda_c1a05b0ce5f88033", # 5 kertaa (26.3%) Vaihtoehtoiset mallit ilman kumoamista
    "tda_d204baf0bdf74ff7", # 5 kertaa (26.3%) Syntaktiset ankkurit rajoituksille
    
    # Uudet historiallisesti epävakaat (esiintymiskerrat = 4, 21.1%)
    "tda_03419e9a41f304ce", # Vähättelevät ilmaukset ilman viitteitä
    "tda_6be555cac0b9115b", # Proseduraaliset merkitsijät ilman päättelyä
    "tda_aa54c6b40e9c4160", # Persoonattomat kappaleet vs yrityksemme
    "tda_073aecbc29db5fc9", # Arkkitehtoniset rakennuspiirustukset
    "tda_d335b4457e3e4ac7", # Ajatuksen pysäyttävät kliseet
    "tda_fbd90f9c0f2247ed", # Vasta-argumentit citations-ehdolla
    "tda_4fa47fd622e62e0d", # Viralliset citation-viitteet standardeihin
    "tda_b7ce46fc627dbc7e", # Episteemisen nöyryyden vaatimukset
    "tda_c45a513f2e724e06", # Absoluuttisen varmuuden julistukset ilman dataa
    "tda_61c1b43bc6f5406f", # Teorian uutuustarkastelu dialogissa
    "tda_2dabbdba90a549ae", # Akateemiset viittaukset metodologioihin
    "tda_be74d9af83716dcc", # Käyttäjän retroaktiiviset väitteet intentiosta
    "tda_569f87a921a2fb69", # Muokkauskomennot listassa A ja B
    "tda_b8c1d460ccfd9ae4", # Rinnakkaiset käsitteet ilman relaatioverbiä
    "tda_25973a87867690b7", # Yksisuuntaiset komennot (Single-path)
    "tda_5f71c2e291f1ae4e"  # Kausaalipäättely ilman polkua
}

seed_path = "backend_v2/seed/seed_data.json"
with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

modified_count = 0

for block in data.get("prompt_blocks", []):
    for scale in block.get("scales", []):
        for claim in scale.get("claims", []):
            for tda in claim.get("tda_assertions", []):
                tda_id = tda.get("tda_id")
                if tda_id in high_entropy_ids:
                    tda["high_entropy"] = True
                    modified_count += 1
                else:
                    tda["high_entropy"] = False

print(f"Parsed seed_data.json. Modified {modified_count} out of {len(high_entropy_ids)} targeted high entropy assertions.")

with open(seed_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Saved updated seed_data.json cleanly.")
