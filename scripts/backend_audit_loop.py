import os
import subprocess
import sys
from pathlib import Path

def run_tests_with_strict_coverage(target):
    print("🚀 Verifying Strict 30% TDD Coverage...")
    # NOTE: tests are in backend_v2/tests path, but we evaluate coverage across backend_v2 packages
    # target passed in sys.argv[1] is usually backend_v2 or backend_v2/something
    cmd = ["uv", "run", "pytest", "-v", "--tb=short", f"--cov={target}", "--cov-fail-under=30", "--cov-report=term-missing"]
    
    # Anna pytestin tulostaa suoraan konsoliin, jotta värit ja selkeät virheilmoitukset näkyvät heti
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("\n❌ AUDIT FAILED: Testeissä oli virheitä TAI testikattavuus ei ole 30%.")
        print("🤖 AI INSTRUCTION: Lue yllä oleva raportti ja korjaa joko kaatuvat testit (-v tai --tb=short kertoo syyn) TAI lisää testejä puuttuville riveille (Miss-sarake).")
        sys.exit(result.returncode)
    else:
        print("\n✅ Strict 30% Coverage Target Met.")

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
        print("\n⏳ Optio: Ajetaan Pytest-yksikkötestit ja Coverage (--test)...")
        run_tests_with_strict_coverage(target_dir)
        print("✅ Yksikkötestit läpäisty.")

    print("\n🏆 Kaikki puhdasta! Backend-kansio on Phase 9 asennossa.\n")

if __name__ == "__main__":
    main()
