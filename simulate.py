from backend_v2.utils.math_utils import calculate_progressive_dampening_score, calculate_waterfall_floor, calculate_weighted_score
stats = {
    1.0: {'hits': 10, 'total': 15}, # 66%
    2.0: {'hits': 5, 'total': 10},  # 50%
    3.0: {'hits': 2, 'total': 10},  # 20%
    4.0: {'hits': 8, 'total': 10},  # 80%
    5.0: {'hits': 10, 'total': 10}  # 100%
}
d_score = calculate_progressive_dampening_score(stats, 1.0, 5.0)
w_score = calculate_weighted_score(stats, 1.0, 5.0)
f_score = calculate_waterfall_floor(stats, 1.0, 0.75)

print('\n=== SIMULAATIO (XAI JUSTIFICATION) ===\n')
print('### Kognitiivisen diagnostiikkamallin (CDM) erittely:')
mod = 1.0
for lvl, s in stats.items():
    hr = s['hits'] / s['total']
    if lvl == 1.0:
        mod = hr
        print(f"- **Taso {lvl}:** {s['hits']}/{s['total']} ({int(hr*100)}% - Kognitiivinen virta: {mod:.2f})")
    else:
        status = "Osumat virtasivat täysimääräisesti läpi" if hr >= 1.0 else ("Osumia vaimennettiin virran mukaisesti" if hr >= 0.7 else "Kognitiivinen virta heikkenee merkittävästi")
        print(f"- **Taso {lvl}:** {s['hits']}/{s['total']} ({int(hr*100)}% - {status} ({hr:.2f}))")
        mod *= hr

print('\n**Vertailutiedot (Shadow-laskenta):**')
print(f"1. *Raaka painotettu keskiarvo:* {w_score:.2f} (Kaikki osumat linearisesti)")
print(f"2. *Vanha vesiputouslattia:* {f_score:.1f} (Katkaisukohta)")
diff = w_score - d_score
if diff > 0.5:
    print(f"-> Puutteet perustason vakuuttavuudessa vaimentavat lopullista tulosta merkittävästi (-{diff:.2f}).")
print(f"**Lopullinen CDM-Arvosana:** {d_score:.2f}\n")
