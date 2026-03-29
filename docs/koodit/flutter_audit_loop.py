import subprocess
import sys
import os
from pathlib import Path

def main():
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

    if run_build:
        print("\n⏳ 1/3: Ajetaan koodigeneraattori (build_runner)...")
        res = subprocess.run(["dart", "run", "build_runner", "build", "-d"], shell=True)
        if res.returncode != 0:
            print("❌ Generaattori kaatui! Keskeytetään.")
            sys.exit(res.returncode)
        print("✅ Generointi valmis.")
    else:
        print("\n⏭️ 1/3: Ohitetaan koodigenerointi (ei --build lippua).")

    print(f"\n⏳ 2/3: Formatoidaan koodi (dart format {target_dir})...")
    res = subprocess.run(["dart", "format", target_dir], shell=True)
    if res.returncode != 0:
        print("❌ Formatointi epäonnistui!")
        sys.exit(res.returncode)
    print("✅ Formatointi valmis.")

    print(f"\n⏳ 3/3: Analysoidaan koodi (dart analyze {target_dir})...")
    res = subprocess.run(["dart", "analyze", target_dir], shell=True)
    if res.returncode == 0:
        print("\n🏆 Kaikki puhdasta! Kansio on Phase 9 vaatimusten mukainen.\n")
    else:
        print("\n❌ Analyysi löysi koodista virheitä, korjaa ne ennen jatkamista!\n")
        sys.exit(res.returncode)

if __name__ == "__main__":
    main()
