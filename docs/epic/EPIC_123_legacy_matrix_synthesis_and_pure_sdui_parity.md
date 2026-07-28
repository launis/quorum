# EPIC 123: Legacy Matrix Synthesis and Pure SDUI Parity

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
>
> Implementing Server-Driven UI (SDUI) effectively in 2025-2026 requires a mature architectural pattern centered on "Design-First Contracts." Industry best practices emphasize avoiding deep nesting and data-model dependency on the client. Instead, the backend must construct explicit UI component blocks (e.g., `AlertBlock`, `QuoteBlock`) rather than transmitting flat string properties (like `coaching: "Do this"`). This "demand-driven" approach ensures the client acts strictly as a "Dumb Painter", rendering the payload blindly, which guarantees 100% deterministic pixel-parity across Flutter apps and generated PDFs while preventing "re-hydration churn".

---

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective
Restore the rich synthesis styling and XAI output extensions (e.g., "Arjen Vinkki", "Vasta-argumentti", Jargon Ratio) that existed prior to Epic 110/122, ensuring complete visual parity between the interactive Flutter UI and the generated PDF report.

### Problem Statement
During the implementation of Epic 111 (Dumb Painter SDUI) and Epic 122 (Legacy Parity Output Profile), the hardcoded HTML logic responsible for styling Matrix extensions in `report_template.jinja2` was removed to enforce the strict ICU Markdown Parity rule. Furthermore, backend mapping for these extensions was flattened. As a result, the premium colored boxes and AI-generated synthesis text vanished from the final outputs. 

The challenge is to bring these rich visual elements back WITHOUT violating the new SDUI architecture. We cannot revert to "duct tape" hardcoded HTML or Flutter-side string-parsing.

### Strategic Scope
This Epic achieves visual restoration through **pure dynamic SDUI**. The backend (`blueprint.py`) will transform flat string properties extracted by the AI into a structured `inner_sdui_blocks` array (utilizing existing models like `AnySduiBlock`). Both the Flutter frontend and the PDF Jinja template will simply execute their standard generic SDUI rendering pipelines over these inner blocks.

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **Hardcoded Extension Rendering Logic**: Any remaining Flutter code attempting to parse `coaching` or `falsification` strings to render specific UI containers will be INTENTIONALLY DROPPED in favor of the `SduiRenderer`.
- **Emoji Injection**: Hardcoded emojis in `extension_labels` will be purged to ensure clean, professional strings. 

### Retained SSOT Invariants (What We Will RETAIN)
- **`SduiBlockDTO` / `AnySduiBlock`** (`@[c:\src\quorum\backend_v2\models\view\sdui.py]`): The backend and frontend will strictly utilize the existing sealed polymorphic models. No new parallel schemas will be introduced.
- **Strict ICU Markdown Parity**: The PDF template (`@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`) will remain devoid of manual HTML formatting for specific data fields, relying entirely on the `render_sdui_blocks()` macro.

### Compliance & Modernity Gates
| Gate | Status |
|---|---|
| Pydantic V2 `ConfigDict(strict=True, extra='forbid')` | ✅ Inherited via `V2CoreBase` |
| Cross-Domain DTO Parity | ✅ Backend `MatrixScorecardRowDTO` syncs with Flutter Freezed model |
| Fail-Fast SDUI Serialization | ✅ `SduiRenderer` consumes strictly typed `SduiBlockDTO`s |
| Zero Duct Tape Rule | ✅ No client-side conditional styling based on magic keys |
| RFC-7807 Dual-Reporting | ✅ Maintained during pipeline hydration |

### Producer-Consumer Integration Check
| Producer | Consumer | Contract |
|---|---|---|
| Backend `blueprint.py` | `MatrixScorecardRowDTO.inner_sdui_blocks` | Transforms AI strings into `list[AnySduiBlock]` (e.g. `AlertBlock`) |
| Backend `MatrixScorecardRowDTO` | Flutter `matrix_row_item_widget.dart` | Pipes `innerSduiBlocks` array to `SduiRenderer` |
| Backend `MatrixScorecardRowDTO` | Jinja `report_template.jinja2` | Passes `inner_sdui_blocks` to `render_sdui_blocks()` macro |

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Database Seed Restoration
- **Target**: @[c:\src\quorum\backend_v2\seed\seed_data.json#L7900-L11000]
- Locate the first `text_only` layout named `"YHTEENVETO"` in the `holistic_audit` profile.
- Restore its `synthesis.system_prompt` to the original XML prompt and `synthesis.preamble_text` to the rich default ("Raportti tekoälytaidoistasi...").
- For matrix layouts (`2d_compare`, `3d_matrix`) with synthesis, explicitly set `"row_explanations_block_id": "sp_row_explanations"`.
- Strip all emojis from `extension_labels` (e.g., `"💡 ARJEN VINKKI"` -> `"ARJEN VINKKI"`).

### Phase 2: Backend SDUI Hydration
- **Target**: `@[c:\src\quorum\backend_v2\services\blueprint.py]` & `@[c:\src\quorum\backend_v2\models\v2_core.py]`
- Update `MatrixScorecardRowDTO` to include `inner_sdui_blocks: list[AnySduiBlock] = Field(default_factory=list)`.
- In `blueprint.py`, during matrix extraction, transform string fields (`coaching`, `falsification`) into `AlertBlock` models. **CRITICAL ARCHITECTURE INVARIANT**: Do NOT hardcode Finnish strings or emojis like `"**💡 Arjen Vinkki:**"` in Python. You MUST dynamically read the localized label from the matrix's `extension_labels` mapping (e.g., `extension_labels.get("coaching", "Coaching")`). Emojis are purposefully stripped because the `AlertBlock` `severity` parameter (e.g., `info`) will command the Flutter frontend to render the appropriate native icon automatically.
- Implement `_hydrate_printable_sources_block` and `_hydrate_jargon_ratio_block`, converting them into `SduiBlockDTO` structures rather than raw strings.
- Verify the `variance_validation` extension correctly populates `grouped_extensions`.

### Phase 3: Frontend & PDF Rendering Parity
- **Target Flutter**: `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\matrix_row_item_widget.dart]`
- **Target Jinja**: `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`
- Update the Flutter Freezed model for `MatrixScorecardRowDTO` to accept `innerSduiBlocks`.
- In Flutter, pass `row.innerSduiBlocks` directly to the `SduiRenderer` within the expandable container.
- Ensure `SduiAlertBoxWidget` correctly parses and paints all required severities (`info`, `error`, `success`, `warning`) utilizing dynamic colors from the theme.
- In Jinja, invoke `{{ render_sdui_blocks(axis.inner_sdui_blocks) }}` inside the matrix layout loop.

### Phase 4: Verification & E2E Integration Gate
- Execute `backend_audit_loop.py` to ensure schema integrity and routing.
- Execute `flutter_audit_loop.py --build` to synchronize Freezed DTOs and verify widget compilation.
- Perform a live database seed and generate a holistic audit report to verify visual parity.

### Phase 5: Multilingual & Localization (i18n) Verification
To guarantee complete multilingual support across all textual generation sources, the implementation MUST adhere to the following routing:
- **Database Source (`extension_labels`)**: Because `AlertBlock.text` expects a `str`, `blueprint.py` MUST resolve the `I18nText` object from `extension_labels` using the current Execution's `target_language` before injecting it into the SDUI block (e.g., `label = ext_labels[type].get_translation(execution.target_language)`).
- **Prompt Directory Features (`models/prompts`)**: If any textual prefixes (e.g., "Jargon Ratio:") are injected via static prompt configurations, the backend MUST utilize the localized properties matching the `target_language` rather than hardcoding.
- **Flutter Translations (`AppLocalizations`)**: If standard UI text requires client-side localization, the backend may transmit a predefined translation key (e.g., `xai_ext_coaching_fallback`) within `AlertBlock.text`. The Flutter `SduiAlertBoxWidget` must be updated to gracefully attempt `AppLocalizations.of(context)` resolution for the string; if a translation exists, it renders the localized string, otherwise it renders the raw string provided by the backend.
- **LLM Prompt Generation (`linguistic_directives.py`)**: If the AI prompt itself is directed to generate the explanations or text (e.g., matrix synthesis), it MUST NOT use hardcoded natural language instructions (e.g., "Please write in Finnish"). Instead, the prompt MUST strictly utilize the `<linguistic_context>` XML pattern defined in `backend_v2/models/prompts/linguistic_directives.py`, ensuring the LLM dynamically respects the `target_locale` across all generated string fields.
- **Dynamic Enums and Roles (e.g., "Käyttäjän Rooli")**: Any dynamic labels referring to system states, user classifications, or assigned roles (such as the "Arkkitehti" role in the output summary) MUST be mapped and retrieved dynamically through the system's official Enum definitions and their corresponding translation functions. Hardcoding such classification strings in templates, LLM prompts, or synthesis outputs is strictly forbidden.
- **Strict Extension Generation (`EXTENSION_ANCHORING_MANDATE`)**: The generation of these extensions (such as remediation_steps) is governed strictly by the `EXTENSION_ANCHORING_MANDATE` in `global_mandates.py`. The LLM MUST anchor every extension to the raw input data, ensuring the content is a directly actionable consequence of the data rather than generic theoretical advice.

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- [ ] Matrix extensions (Arjen Vinkki, jne.) are transmitted exclusively as `SduiBlockDTO` objects.
- [ ] Zero hardcoded HTML exists in `report_template.jinja2` for specific matrix extensions.
- [ ] Zero hardcoded string parsing exists in Flutter UI for specific matrix extensions.
- [ ] The generated PDF and Flutter UI display identical, visually rich colored boxes.
- [ ] The "Jargon Ratio" and "Tulostettavat Lähteet" blocks render flawlessly.
- [ ] Python Pydantic models and Dart Freezed models are mathematically aligned and pass automated audits.

### Automated Unit Tests
- `uv run python scripts/backend_audit_loop.py backend_v2/seed/seed_data.json`
- `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/widgets --build`

### MANDATORY Final E2E REST API Verification Gate
```powershell
$env:RUN_LIVE_E2E="true"
uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 5. Expected Output & Test Fixture Payload

This section defines the exact target payload expected after implementation. **This identical JSON structure MUST be utilized as the baseline mock fixture in both Backend and Frontend automated tests** (e.g., `test_blueprint.py` and `matrix_scorecard_dto_test.dart`) to guarantee the polymorphic `inner_sdui_blocks` deserializer handles the SDUI mapping correctly alongside legacy string fields. The example below represents the complete top-level `ReportView` payload to illustrate how the matrix sits within the broader ecosystem of summaries, graphs, and citations.

```json
{
  "view_id": "exe_1c38d59faaa94ae1aa48c3b9ba464c78",
  "title": "KOKONAISVALTAINEN AUDITOINTI",
  "status_theme": "success",
  "metrics": {
    "kokonaiskeskiarvo": "19.30/100",
    "radar_chart_data": {
      "labels": ["Episteeminen Nöyryys", "Harkintakyky", "Päättelyn rehellisyys"],
      "datasets": [{"label": "Tulos", "data": [29.0, 15.0, 15.0]}]
    }
  },
  "system_notification": null,
  "references": [],
  "sections": [
    {
      "id": "sec_summary",
      "type": "HEADER",
      "title": "Yhteenveto",
      "data": {
        "content": "**Raportti tekoälytaidoistasi**\n\nTämä raportti analysoi tapaasi hyödyntää tekoälyä ja auttaa sinua kehittymään sen strategiseksi ohjaajaksi. Arvioinnissa keskitytään kolmeen osa-alueeseen:\n- **Oivalluskyky**: Pureudutko syvälle aiheeseen vai jäätkö pintatasolle?\n- **Logiikka ja päättely**: Miten perustelet väitteesi ja haastat tekoälyn vastauksia?\n- **Luotettavuus**: Miten hallitset prosessia ja sen läpinäkyvyyttä?\n\nKäyttäjän Rooli: **Arkkitehti**."
      }
    },
    {
      "id": "sec_scorecard",
      "type": "SCORE_CARD",
      "title": "YHTEENVETO / MATRIX SUMMARY",
      "data": {
        "preset_view": "3d_matrix",
        "title": {
          "fi": "Yhteenveto / Matrix Summary",
          "en": "Matrix Summary"
        },
        "description": {
          "fi": "Arvioinnin yksityiskohtainen pisteytys ja erittely osa-alueittain.",
          "en": "Detailed scoring and breakdown by dimension."
        },
        "is_synthesis_enabled": true,
        "synthesis_blocks": [
          {
            "block_type": "paragraph",
            "text": "Osoitat poikkeuksellista kykyä jäsentää monimutkaisia ongelmia ja ohjata tekoälyä systemaattisella, iteratiivisella prosessilla.",
            "exact_quotes": [],
            "citations": []
          }
        ],
        "axes": [
          {
            "block_id": "mat_episteeminen_noyryys",
            "name": "Oman tiedon rajat (Episteeminen Nöyryys)",
            "label_i18n": {
              "fi": "Oman tiedon rajat",
              "en": "Epistemic Humility"
            },
            "description": "Arvioi kykyäsi tunnistaa, mitä et tiedä. Se varoittaa liiallisesta varmuudesta asioissa, jotka ovat todellisuudessa epävarmoja.",
            "score": 29.0,
            "scale_min": 0.0,
            "scale_max": 100.0,
            "coaching": "Käyttäjä rakentaa kehotteen, joka pakottaa mallin itsekritiikkiin, mutta ei kuitenkaan haasta mallin esittämiä ehdottomia väitteitä tai kritiikittömästi esitettyjä lähteitä.",
            "inner_sdui_blocks": [
              {
                "block_type": "alert_box",
                "severity": "info",
                "text": "**💡 ARJEN VINKKI:**\n\nKun tekoäly tarjoaa spesifejä lähteitä, kuten tutkimuksia, on kriittisen tärkeää yrittää validoida ne ulkoisella hakukoneella. Tämä auttaa erottamaan aidot lähteet uskottavasti kuulostavista keksinnöistä.",
                "exact_quotes": [],
                "citations": []
              },
              {
                "block_type": "alert_box",
                "severity": "warning",
                "text": "**⚠️ VASTA-ARGUMENTTI:**\n\nVäite, että prosessi oli täysin turvallinen, voidaan kumota osoittamalla, että tekoäly tuotti todennäköisesti keksittyjä lähdeviitteitä. Ilman kriittistä käyttäjää virheellinen tieto olisi päätynyt lopputulokseen.",
                "exact_quotes": [],
                "citations": []
              },
              {
                "block_type": "alert_box",
                "severity": "success",
                "text": "**🛠️ KORJAAVAT TOIMENPITEET:**\n\n- Ota käyttöön pysyvä käytäntö, jossa kaikki tekoälyn tuottamat faktaväitteet ja lähteet tarkistetaan ulkoisesta, luotettavasta lähteestä.\n- Käytä \"paholaisen asianajaja\" -tyyppisiä kehotteita systemaattisesti monimutkaisissa tehtävissä paljastaaksesi piilevät oletukset ja heikkoudet.\n- Lisää kaikkiin lähdeviittauksiin automaattinen huomautus, joka kehottaa käyttäjää tarkistamaan tiedon oikeellisuuden ulkoisesta lähteestä.\n- Integroi proaktiivisesti \"mahdolliset riskit ja rajoitukset\" -osio kaikkiin suosituksiin, jotta itsekritiikki on sisäänrakennettu ominaisuus eikä vaadi erillistä kehotetta.",
                "exact_quotes": [],
                "citations": []
              }
            ]
          }
        ]
      }
    }
  ]
}
```
