import vertexai.generative_models as stable
import inspect

print("--- VERTEX AI DIAGNOSTIIKKA ---")

# 1. Etsitään "Search" tai "Retrieval" -sanoja stable-versiosta
print("\n🔎 Etsitään luokkia moduulista 'vertexai.generative_models':")
found = False
for name, obj in inspect.getmembers(stable):
    if "Search" in name or "Retrieval" in name or "Grounding" in name:
        print(f"   ✅ LÖYTYI: {name} ({type(obj)})")
        found = True

# 2. Tarkistetaan onko 'grounding'-alimoduulia
if hasattr(stable, 'grounding'):
    print("\n🔎 Tutkitaan alimoduulia 'vertexai.generative_models.grounding':")
    for name, obj in inspect.getmembers(stable.grounding):
        if "Search" in name or "Retrieval" in name:
            print(f"   ✅ LÖYTYI: {name}")
            found = True
else:
    print("\n❌ Alimoduulia 'grounding' ei löytynyt suoraan.")

# 3. Tarkistetaan Tool-luokan metodit
if hasattr(stable, 'Tool'):
    print("\n🔧 Tool-luokan metodit (factory methods):")
    for name, _ in inspect.getmembers(stable.Tool):
        if name.startswith("from_"):
            print(f"   - {name}")

if not found:
    print("\n⚠️ Yhtään Search-luokkaa ei löytynyt. Kokeillaan preview-puolta...")
    try:
        import vertexai.preview.generative_models as preview
        for name, obj in inspect.getmembers(preview):
            if "Search" in name or "Retrieval" in name:
                print(f"   ✅ PREVIEW LÖYTÖ: {name}")
    except ImportError:
        print("   ❌ Preview-moduulia ei voitu ladata.")

print("\n--- LOPPU ---")