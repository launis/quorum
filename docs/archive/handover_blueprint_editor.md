# System Context & Handover (Quorum V2)

**Current Status:**
Olemme saaneet valmiiksi SDUI (Server-Driven UI) renderöinnit. Backendin PDF-engine ja Flutter-klientin widgetit ovat nyt täydellisessä 1:1 pariteetissa. Viimeisimpänä korjasimme Scatter3D- ja Matrix2D-komponenttien typografian (X/Y/Z akselien nimien ja otsikoiden splittaus) sekä selitelaatikoiden (`x/y/z_axis_note`) viennin onnistuneesti läpi.

Kytkimme myös backendin `V2CoreBase` -päämalliin Pydanticin `extra="forbid"` -tilan päälle ("The Pydantic Purity Mandate"). Tämä tarkoittaa, että backend noudattaa ehdotonta Fail-Fast -periaatetta: jos Flutter lähettää yksikään ylimääräisen tulkitsemattoman kentän payloadissa, koko API-kutsu kaatuu heti 422 ValidationErroriin.

**Tämän päivän tavoite:**
Rakennamme Admin Studion Render Blueprint -editorin näyttöön `client_app_v2/lib/features/studio/views/blueprint_editor_view.dart`.

**Lähtötilanne:**
- Tiedosto on olemassa, mutta se on tällä hetkellä vain hyvin yksinkertainen placeholder/prototyyppi ("näytöllä on paikka, ei muuta").
- Sen tehtävänä on antaa pääkäyttäjän rakentaa raahaamalla ja pudottamalla (tai dynaamisen lomakkeen avulla) työnkulun raportti-layout, joka tallennetaan `RenderBlueprint`-rakenteena (lista `components` -kartoituksia, kuten `1d_gauge`, `2d_matrix`, `3d_scatter`, jne.).
- UI:n tilanhallinta tapahtuu Riverpodilla (`blueprintEditorControllerProvider`). Koska kyseessä on Zero-Codegen SDUI, tilaa pidetään tyypillisesti `Map<String, dynamic>` mudossa ennen backendille lähetystä.

**Reunaehdot:**
1. Pidä mielessä backendin `extra="forbid"`. UI:n generoiman JSON-rakenteen on vastattava **millintarkasti** `backend_v2/models/v2_core.py` tiedoston `BlueprintComponentType` -malleja (esim. ei ylimääräisiä `flutter_internal_id` kenttiä lähetysvaiheessa).
2. Noudata olemassa olevaa Riverpod 3.0 ja Optimistic UI -arkkitehtuuria.
3. Ei kovakoodattuja UI-merkkijonoja. Käytä lokalisaatiota (AppLocalizations).

Tehtävä: Lue `blueprint_editor_view.dart` ja `blueprint_editor_controller.dart` läpi ymmärtääksesi nykytilan, ja laadi suunnitelma (implementation_plan.md) siitä, miten toteutamme uudet konfiguraatiolomakkeet (esim. Matrix ja Scatter3D datakentille).
