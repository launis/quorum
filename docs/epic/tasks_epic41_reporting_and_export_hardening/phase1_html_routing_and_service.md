# Phase 1: HTML Routing & Zero-Compromise Service Hardening

## Tavoite
Lisätään backendin ydin-API:in virallinen tuki HTML-pohjaiselle renderöinnille (`format=html`) PDF-tulosteen rinnalle. Tällä taklataan lokaalin Weasyprint-ajoympäristön (GTK3) hauraus Windows-ympäristöissä täysin ilman "purkkaskriptejä", noudattaen Quorumin "Code is Truth" -standardeja.

## Architectural Invariants (Must Follow)
- **Rule 1: Anemic Routers:** Reitittimiin (`backend_v2/api/`) EI SAA kirjoittaa bisneslogiikkaa. Ydinlogiikan on oltava Service-kerroksessa.
- **Rule 2: No Silent Failures:** Try-except -lohkot eivät saa olla tyhjiä (ei `except Exception: pass`). Kaikki virheet on logitettava natiivisti (`logger.error`) ja nostettava `AppException` (RFC 7807) virheinä.
- **Rule 3: Opaque Stripe ID Pattern:** Älä käytä järjestelmässä tai testeissä `target_locale` tai muita satunnaisia dict-hakuja suoraan `metadata`-olioista ilman Fallbackia, vaan käytä vain määriteltyjä Pydantic-attribuutteja.
- **Rule 4: Pydantic Namespace Collisions:** Pydantic-skeemoja ei saa määritellä `routers/` kansioiden sisällä.

## Target Files (Modify)
1. `c:\src\quorum\backend_v2\services\execution.py`
   - Lisää uusi ehto `elif fmt == "html":`
   - Ota talteen Pydantic-varmennettu `dto`, muodosta renderöity HTML-malli suoraan Jinja2-ympäristöstä ja palauta se merkkijonona / tiedostotulosteena.
2. `c:\src\quorum\backend_v2\services\pdf_generator.py`
   - Eriytä HTML-renderöinti (`weasyprint.HTML(string=html_content)`) siten, että HTML-tulostevaiheesta (Jinja2) voidaan palauttaa suoraan raaka HTML erillisen `generate_execution_html` -metodin kautta, jota `execution.py` kutsuu.

## Context Files (Read-Only)
- `c:\src\quorum\backend_v2\templates\report_template.jinja2`
- `c:\src\quorum\backend_v2\models\v2_core.py`

## Verification & Quality Gate Plan
- Varmista, että uudet metodit ja reititykset sisältävät tyyppivihjeet.
- Aja Ruff: `uv run ruff check backend_v2/services/execution.py backend_v2/services/pdf_generator.py --fix`
- Aja MyPy: `uv run mypy --strict backend_v2/services/execution.py backend_v2/services/pdf_generator.py`
- Luo tai päivitä olemassa oleva unit-testi HTML-palautukselle. Aja: `uv run pytest backend_v2/tests/test_pdf_generator.py -v`
