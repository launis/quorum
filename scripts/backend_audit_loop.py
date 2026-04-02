import os
import subprocess
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Käyttö: python backend_audit_loop.py <kohdekansio> [--openapi] [--test]")
        sys.exit(1)

    target_dir = sys.argv[1]
    run_openapi = "--openapi" in sys.argv
    run_test = "--test" in sys.argv

    # Varmista että olemme oikeassa hakemistossa (projektin juuressa)
    current_dir = Path(os.getcwd())
    if current_dir.name == "scripts":
        os.chdir("..")
    elif not (current_dir / "backend_v2").exists():
        print("Virhe: Skripti pitää ajaa projektin juuresta (jossa backend_v2 sijaitsee).")
        sys.exit(1)

    print(f"\n🚀 Suoritetaan quality-loop kansiolle: {target_dir}")
    print("--------------------------------------------------")

    print("\n⏳ 1/3: Korjataan tiedostot (ruff check --fix)...")
    res = subprocess.run(["uv", "run", "ruff", "check", target_dir, "--fix"])
    if res.returncode != 0:
        print("❌ Ruff linter löysi automaattisesti korjaamattomia virheitä!")
        sys.exit(res.returncode)
    print("✅ Linttaus ja korjaus valmis.")

    print("\n⏳ 2/3: Formatoidaan koodi (ruff format)...")
    res = subprocess.run(["uv", "run", "ruff", "format", target_dir])
    if res.returncode != 0:
        print("❌ Ruff-formatointi epäonnistui!")
        sys.exit(res.returncode)
    print("✅ Formatointi valmis.")

    print("\n⏳ 3/3: Tyyppitarkastetaan koodi (mypy --strict)...")
    res = subprocess.run(["uv", "run", "mypy", target_dir, "--strict"])
    if res.returncode != 0:
        print("\n❌ MyPy löysi tyyppivirheitä! Korjaa The Universal Quality Gaten rikkomukset.\n")
        sys.exit(res.returncode)
    print("✅ Tyyppitarkastus läpäisty.")

    if run_openapi:
        print("\n⏳ Optio: Generoidaan OpenAPI-dokumentaatio (--openapi)...")
        res = subprocess.run(["uv", "run", "python", "backend_v2/scripts/generate_openapi.py"])
        if res.returncode != 0:
            print("❌ OpenAPI-luonti epäonnistui! Tarkista Pydantic mallit.")
            sys.exit(res.returncode)
        print("✅ OpenAPI-dokumentaatio päivitetty varmaotteisesti.")
        
    if run_test:
        print("\n⏳ Optio: Ajetaan Pytest-yksikkötestit (--test)...")
        res = subprocess.run(["uv", "run", "pytest", "backend_v2/tests/", "-v"])
        if res.returncode != 0:
            print("❌ Yksikkötestit epäonnistuivat!")
            sys.exit(res.returncode)
        print("✅ Yksikkötestit läpäisty.")

    print("\n🏆 Kaikki puhdasta! Backend-kansio on Phase 9 asennossa.\n")

if __name__ == "__main__":
    main()
