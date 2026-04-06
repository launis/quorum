import os
import subprocess
import sys
from pathlib import Path

def run_tests_with_strict_coverage(target):
    print("🚀 Verifying Strict 30% TDD Coverage...")
    
    # Use directory for pytest-cov to harvest data without PyO3 collision/path bugs
    cov_target = os.path.dirname(target) if target.endswith(".py") else target
    if not cov_target: cov_target = target
    
    if target.endswith(".py"):
        parts = target.replace("\\", "/").split("/")
        parts[-1] = "test_" + parts[-1]
        test_path = "tests/" + "/".join(parts)
        
        # 1. Ajetaan Pytest ja kerätään kattavuusdata (ei kaatumista fail-underiin vielä)
        cmd = ["uv", "run", "pytest", test_path, "-v", "--tb=short", f"--cov={cov_target}"]
        result = subprocess.run(cmd)
        
        # 2. Ajetaan Coverage Report, joka filtteröi laatuportin vaatimuksen KOSKEMAAN VAIN tätä kyseistä tiedostoa
        if result.returncode == 0:
            target_name = os.path.basename(target) # esim. synthesis.py
            coverage_cmd = ["uv", "run", "coverage", "report", f"--include=*{target_name}", "--fail-under=30", "-m"]
            result = subprocess.run(coverage_cmd)
    else:
        cmd = ["uv", "run", "pytest", "-v", "--tb=short", f"--cov={cov_target}", "--cov-fail-under=30", "--cov-report=term-missing"]
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
