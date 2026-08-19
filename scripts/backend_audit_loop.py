"""Backend Audit Loop Script (Antigravity Phase 9)

**Mitä tämä skripti tekee:**
Tämä skripti on Automatisoitu Laatuportti (Quality Gate) Python-backendille. Se suorittaa kolmivaiheisen putken:
1. `ruff check --fix`: Etsii asennointivirheitä ja pyrkii korjaamaan ne automaattisesti.
2. `ruff format`: Formatoi koodin täysin standardien mukaiseksi.
3. `mypy --strict`: Suorittaa ankaran tyyppitarkastuksen The Universal Quality Gaten mukaisesti.
Lisäksi skripti voi päivittää OpenAPI-skeemat ja ajaa yksikkötestit tiukalla (30%) kattavuusvaatimuksella.

**Ohjeet käyttöön:**
Suorita skripti projektin juuressa eristettynä `uv run python` -komennolla:

```bash
uv run python scripts/backend_audit_loop.py <kohdekansio_tai_tiedosto> [--openapi] [--test]
```

**Kopioitavia esimerkkejä:**

1. Tarkista ja korjaa yksittäinen tiedosto:
```bash
uv run python scripts/backend_audit_loop.py backend_v2/hooks/synthesis.py
```

2. Tarkista koko reititin-kansio ja aja samalla testit:
```bash
uv run python scripts/backend_audit_loop.py backend_v2/ --test
```

3. Aja laatuportti ytimeen ja luo uusi OpenAPI-spesifikaatio:
```bash
uv run python scripts/backend_audit_loop.py backend_v2/ --openapi
```
"""

import os
import re
import subprocess
import sys
from pathlib import Path

# Force pure Python Protobuf implementation to prevent duplicate descriptor pool crashes in Python 3.14+
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Force UTF-8 encoding for stdout to support emojis on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_tests_with_strict_coverage(target: str) -> None:
    print("🚀 Verifying Strict 90% TDD Coverage...")

    # Convert file path to dotted module path for accurate coverage (e.g. backend_v2/services/execution.py -> backend_v2.services.execution)
    if target.endswith(".py"):
        if target.replace("\\", "/").startswith("scripts/"):
            cov_target = target.replace("\\", "/").split("/")[-1].replace(".py", "")
        elif target.replace("\\", "/").endswith("/__init__.py"):
            cov_target = target.replace("\\", "/").removesuffix("/__init__.py").replace("/", ".")
        else:
            cov_target = target.replace("\\", "/").replace(".py", "").replace("/", ".")
    else:
        cov_target = target

    if target.endswith(".py"):
        parts = target.replace("\\", "/").split("/")
        if parts[-1].startswith("test_") or "tests" in parts:
            test_path = target.replace("\\", "/")
        else:
            parts[-1] = "test_" + parts[-1]
            if parts[0] == "backend_v2":
                test_path = "backend_v2/tests/unit/" + "/".join(parts[1:])
                if not os.path.exists(test_path):
                    flat_path = "backend_v2/tests/unit/" + parts[-1]
                    if os.path.exists(flat_path):
                        test_path = flat_path
            else:
                test_path = "backend_v2/tests/unit/" + "/".join(parts)
                if not os.path.exists(test_path):
                    test_path = "tests/" + "/".join(parts)
                if not os.path.exists(test_path):
                    flat_path = "tests/" + parts[-1]
                    if os.path.exists(flat_path):
                        test_path = flat_path
                    elif os.path.exists("backend_v2/tests/unit/scripts/test_audit_verification_scripts.py"):
                        test_path = "backend_v2/tests/unit/scripts/test_audit_verification_scripts.py"

        # 1. Ajetaan Pytest ja kerätään kattavuusdata (ei kaatumista fail-underiin vielä)
        cmd = [
            "uv",
            "run",
            "python",
            "-c",
            f"import sys\ntry: import numpy\nexcept ImportError: pass\nimport pytest\nsys.exit(pytest.main(['{test_path}', '-v', '--tb=short', '--cov={cov_target}', '--cov-fail-under=0']))",
        ]
        print("Executing:", " ".join(cmd))
        result = subprocess.run(cmd)

        # 2. Ajetaan Coverage Report, joka filtteröi laatuportin vaatimuksen KOSKEMAAN VAIN tätä kyseistä tiedostoa
        if result.returncode == 0:
            target_name = os.path.basename(target)  # esim. synthesis.py
            coverage_cmd = ["uv", "run", "coverage", "report", f"--include=*{target_name}", "--fail-under=90", "-m"]
            result = subprocess.run(coverage_cmd)
    else:
        parts = target.replace("\\", "/").strip("/").split("/")
        if "tests" in parts:
            test_path = target.replace("\\", "/")
        else:
            if parts[0] == "backend_v2":
                test_path = "backend_v2/tests/unit/" + "/".join(parts[1:])
            else:
                if parts == ["."]:
                    test_path = "backend_v2/tests/"
                else:
                    test_path = "tests/" + "/".join(parts)

        test_paths_list = test_path.split()
        args = test_paths_list + [
            "-v",
            "--tb=short",
            f"--cov={cov_target}",
            "--cov-fail-under=90",
            "--cov-report=term-missing",
        ]

        cmd = [
            "uv",
            "run",
            "python",
            "-c",
            f"import sys\ntry: import numpy\nexcept ImportError: pass\nimport pytest\nsys.exit(pytest.main({args}))",
        ]
        result = subprocess.run(cmd)

    if result.returncode != 0:
        print("\n❌ AUDIT FAILED: Testeissä oli virheitä TAI testikattavuus ei ole 90%.")
        print(
            "🤖 AI INSTRUCTION: Lue yllä oleva raportti ja korjaa joko kaatuvat testit (-v tai --tb=short kertoo syyn) TAI lisää testejä puuttuville riveille (Miss-sarake)."
        )
        print(
            "🚨 THE ANTI-TDD TRAP MANDATE: The architectural laws in `c:\\src\\quorum\\.agents\\rules` are ABSOLUTE. Do NOT fall into the 'Test-Driven Development Trap' where you preserve legacy dict-parsing, fallback hacks, or hardcoded strings just to satisfy existing unit tests. If old tests conflict with the new rules (e.g., No-String Mandate, De-Generator, Pydantic V2), you MUST ruthlessly tear down the legacy code AND rewrite the tests. A green test suite that violates architectural sovereignty is a failed state."
        )
        sys.exit(result.returncode)
    else:
        print("\n✅ Strict 90% Coverage Target Met.")


def main() -> None:
    targets = []
    run_openapi = False
    run_test = False

    for arg in sys.argv[1:]:
        if arg == "--openapi":
            run_openapi = True
        elif arg == "--test":
            run_test = True
        else:
            targets.append(arg)

    if not targets:
        print("Käyttö: python backend_audit_loop.py <kohdekansio_tai_tiedostot...> [--openapi] [--test]")
        sys.exit(1)

    # Varmista että olemme oikeassa hakemistossa (projektin juuressa)
    current_dir = Path(os.getcwd())
    if current_dir.name == "scripts":
        os.chdir("..")
    elif not (current_dir / "backend_v2").exists():
        print("Virhe: Skripti pitää ajaa projektin juuresta (jossa backend_v2 sijaitsee).")
        sys.exit(1)

    targets_str = ", ".join(targets)
    print(f"\n🚀 Suoritetaan quality-loop kohteille: {targets_str}")
    print("--------------------------------------------------")

    print("\n⏳ 1/5: Korjataan tiedostot (ruff check --fix)...")
    res = subprocess.run(["uv", "run", "ruff", "check", *targets, "--fix", "--extend-ignore=E501"])
    if res.returncode != 0:
        print("❌ Ruff linter löysi automaattisesti korjaamattomia virheitä!")
        sys.exit(res.returncode)
    print("✅ Linttaus ja korjaus valmis.")

    print("\n⏳ 2/5: Formatoidaan koodi (ruff format)...")
    res = subprocess.run(["uv", "run", "ruff", "format", *targets])
    if res.returncode != 0:
        print("❌ Ruff-formatointi epäonnistui!")
        sys.exit(res.returncode)
    print("✅ Formatointi valmis.")

    print("\n⏳ 3/5: Tyyppitarkastetaan koodi (mypy --strict)...")
    res = subprocess.run(["uv", "run", "mypy", *targets, "--strict"])
    if res.returncode != 0:
        print("\n❌ MyPy löysi tyyppivirheitä! Korjaa The Universal Quality Gaten rikkomukset.\n")
        sys.exit(res.returncode)
    print("✅ Tyyppitarkastus läpäisty.")

    print("\n⏳ 4/5: Validoidaan UI-mallineet (Jinja Dumb Painter Enforcement)...")
    jinja_dir = Path("backend_v2/templates")
    dumb_painter_pattern = re.compile(r"\|\s*(default|d)\s*\(|\.get\s*\(")
    if jinja_dir.exists():
        for jinja_file in jinja_dir.rglob("*.jinja2"):
            try:
                content = jinja_file.read_text(encoding="utf-8")
                if dumb_painter_pattern.search(content):
                    print(f"\n❌ UI-mallineen validointi epäonnistui tiedostossa {jinja_file.name}!")
                    print("   Löydettiin kielletty dumb-painter lauseke: `| default` tai `.get`.")
                    print("   UI-mallineiden tulee olla täysin passiivisia (Strict ICU Markdown Parity).")
                    sys.exit(1)
            except Exception as e:
                print(f"Varoitus: Ei voitu lukea tiedostoa {jinja_file.name}: {e}")
    print("✅ UI-mallineet validoitu.")

    print("\n⏳ 5/5: Validoidaan Seed Data (Dry-Run)...")
    res = subprocess.run(["uv", "run", "python", "backend_v2/seed/run_seed.py", "local", "--dry-run"])
    if res.returncode != 0:
        print("\n❌ Seed Data Dry-Run epäonnistui! Pydantic mallien muutokset rikkovat SSOT JSON -tiedoston.\n")
        sys.exit(res.returncode)
    print("✅ Seed Data integroitu ja validoitu.")

    if run_openapi:
        print("\n⏳ Optio: Generoidaan OpenAPI-dokumentaatio (--openapi)...")
        res = subprocess.run(["uv", "run", "python", "backend_v2/scripts/generate_openapi.py"])
        if res.returncode != 0:
            print("❌ OpenAPI-luonti epäonnistui! Tarkista Pydantic mallit.")
            sys.exit(res.returncode)
        print("✅ OpenAPI-dokumentaatio päivitetty varmaotteisesti.")

    if run_test:
        print("\n⏳ Optio: Ajetaan Pytest-yksikkötestit ja Coverage (--test)...")
        for target in targets:
            print(f"\n🏃 Ajetaan testit kohteelle: {target}")
            run_tests_with_strict_coverage(target)
        print("✅ Yksikkötestit läpäisty.")

    print("\n🏆 Kaikki puhdasta! Kohteet ovat Phase 9 asennossa.\n")


if __name__ == "__main__":
    main()
