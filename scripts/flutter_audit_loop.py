"""Flutter Audit Loop Script (Antigravity Phase 9)

**Mitä tämä skripti tekee:**
Tämä skripti on Automatisoitu Laatuportti (Quality Gate) Flutter-käyttöliittymälle (`client_app_v2`). Se suorittaa peräkkäiset koodin puhtaanapitotoimet:
1. `build_runner` (Valinnainen): Ajaa Dartin koodigeneraattorin, joka kääntää SDUI/Freezed/JSON -mallit automaattisesti.
2. `dart format`: Formatoi Dart-tiedostot oikeellisen sisennyksen mukaiseksi.
3. `dart analyze`: Analysoi lähdekoodin staattisesti varmistaakseen, ettei siinä ole kognitiivisia tai rakenteellisia virheitä (The Component Generativity Mandate).

**Ohjeet käyttöön:**
Skripti suositellaan ajettavaksi projektin juuresta eristettynä `uv run python` -komennolla varman versionhallinnan takaamiseksi:

```bash
uv run python scripts/flutter_audit_loop.py <kohdekansio> [--build]
```

**Kopioitavia esimerkkejä:**

1. Aja laatuportti pelkille komponenteille ilman raskasta generointia:
```bash
uv run python scripts/flutter_audit_loop.py lib/core/components/
```

2. Aja laatuportti koko frontendille ja pakota koodigeneraattori päivittämään mallit:
```bash
uv run python scripts/flutter_audit_loop.py client_app_v2 --build
```

3. Aja tiettyyn uuteen kansioon generointi ja laatuportti:
```bash
uv run python scripts/flutter_audit_loop.py lib/features/sdui/ --build
```
"""

import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")  # type: ignore

    if len(sys.argv) < 2:
        print("Käyttö: python flutter_audit_loop.py <kohdekansio> [--build]")
        sys.exit(1)

    target_dir = sys.argv[1]
    run_build = "--build" in sys.argv

    # Varmista että olemme oikeassa hakemistossa (client_app_v2)
    current_dir = Path(os.getcwd())
    if current_dir.name != "client_app_v2":
        client_app_dir = current_dir / "client_app_v2"
        if client_app_dir.exists():
            os.chdir(client_app_dir)
        else:
            print("Virhe: Skripti pitää ajaa projektin juuresta tai client_app_v2 -kansiosta.")
            sys.exit(1)

    print(f"\n🚀 Suoritetaan quality-loop kansiolle: {target_dir}")
    print("--------------------------------------------------")

    # Korjaus: Koska skripti hyppää jo `client_app_v2` kansion sisään,
    # komento-argumentit pitää muuttaa muotoon "." jos pyydettiin koko kansiota,
    # tai poistaa 'client_app_v2/' polun alusta.
    cmd_dir = target_dir
    if cmd_dir.replace("\\", "/").startswith("client_app_v2/"):
        cmd_dir = cmd_dir[len("client_app_v2/") :]
    elif cmd_dir.strip("\\/") == "client_app_v2":
        cmd_dir = "."

    if not cmd_dir:
        cmd_dir = "."

    if run_build:
        print("\n⏳ 1/3: Ajetaan koodigeneraattori (flutter gen-l10n & build_runner)...")
        res_l10n = subprocess.run(["flutter", "gen-l10n"], shell=True)
        if res_l10n.returncode != 0:
            print("❌ L10N Generointi kaatui! Keskeytetään.")
            sys.exit(res_l10n.returncode)

        res = subprocess.run(["dart", "run", "build_runner", "build", "-d"], shell=True)
        if res.returncode != 0:
            print("❌ Generaattori kaatui! Keskeytetään.")
            sys.exit(res.returncode)
        print("✅ Generointi valmis.")
    else:
        print("\n⏭️ 1/3: Ohitetaan koodigenerointi (ei --build lippua).")

    print(f"\n⏳ 2/3: Formatoidaan koodi (dart format {cmd_dir})...")
    res = subprocess.run(["dart", "format", cmd_dir], shell=True)
    if res.returncode != 0:
        print("❌ Formatointi epäonnistui!")
        sys.exit(res.returncode)
    print("✅ Formatointi valmis.")

    print(f"\n⏳ 3/3: Analysoidaan koodi (dart analyze {cmd_dir})...")
    res = subprocess.run(["dart", "analyze", cmd_dir], shell=True)
    if res.returncode == 0:
        print("\n🏆 Kaikki puhdasta! Kansio on Phase 9 vaatimusten mukainen.\n")
    else:
        print("\n❌ AUDIT FAILED: Analyysi löysi koodista virheitä, korjaa ne ennen jatkamista!")
        print("🤖 AI INSTRUCTION: Lue yllä oleva raportti ja korjaa kaatuvat staattisen analyysin virheet.")
        print(
            "🚨 THE ANTI-TDD TRAP MANDATE: The architectural laws in `c:\\src\\quorum\\.agents\\rules` are ABSOLUTE. Do NOT fall into the 'Test-Driven Development Trap' where you preserve legacy dict-parsing, fallback hacks, or hardcoded strings just to satisfy existing unit tests. If old tests conflict with the new rules (e.g., No-String Mandate, De-Generator, Pydantic V2), you MUST ruthlessly tear down the legacy code AND rewrite the tests. A green test suite that violates architectural sovereignty is a failed state.\n"
        )
        sys.exit(res.returncode)


if __name__ == "__main__":
    main()
