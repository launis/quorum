Tämä suunnittelemamme Admin Studion (Epic 7\) uudistus koskettaa suoraan projektisi hakemistorakenteessa olevia tiedostoja. Jaottelu osuu täydellisesti nykyiseen backend\_v2/api/routers/studio/ ja client\_app\_v2/lib/features/studio/ \-hakemistoihin.

Tässä on tarkka kartoitus siitä, mihin Python- ja Riverpod/Flutter-tiedostoihin kukin osio liittyy, ja mitä niissä pitää muuttaa:

## **1\. Järjestelmä (System Config: Model Registry & MCP Gateways)**

Tässä jaetaan nykyinen "järjestelmäasetukset" tekoälymalleihin ja työkalureitityksiin.

* **Python (Backend):**  
  * backend\_v2/api/routers/studio/model\_registry.py (Tänne jäävät LLM-mallien reitit).  
  * backend\_v2/api/routers/studio/system\_configs.py (Tänne luodaan uudet CRUD-reitit MCP Gateways \-määrityksille).  
  * backend\_v2/models/v2\_core.py (Pydantic-mallien päivitys tukemaan MCP-rajapintojen tallennusta).  
* **Riverpod / Flutter:**  
  * client\_app\_v2/lib/features/studio/controllers/model\_registry\_controller.dart (Vastaa mallien tilanhallinnasta).  
  * client\_app\_v2/lib/features/studio/views/model\_registry\_view.dart (Jaetaan Master-listaksi ja Detail-editoriksi).  
  * *Uusi tiedosto:* Esim. mcp\_gateway\_controller.dart ja mcp\_gateway\_view.dart tarvitaan työkaluille.

## **2\. Kognitio (Prompt Blocks & BARS)**

Tässä erotetaan asennepromptit ja matriisit (category\_id: "matrix") toisistaan UI-tasolla.

* **Python (Backend):**  
  * backend\_v2/api/routers/studio/prompt\_blocks.py (API-reitit ohjeille ja matriiseille).  
  * backend\_v2/services/studio.py (Tänne lisätään logiikka, joka osaa palauttaa erikseen filtteröidyt listat matriiseille ja perusprompteille listanäkymiä varten).  
* **Riverpod / Flutter:**  
  * client\_app\_v2/lib/features/studio/views/prompt\_block\_builder\_view.dart (Refaktoroidaan Master-Detail \-malliseksi teksti/markdown-ohjeille).  
  * client\_app\_v2/lib/features/studio/views/widgets/scale\_editor\_modal.dart ja row\_editor\_modal.dart (Nämä liitetään uuteen dedikoituun BARS/Matrix-editorinäkymään).

## **3\. Työvaiheet (Steps)**

Tässä lisätään Hookien ja ohjeiden (Prompt Blocks) hallinta yksittäisille askelille.

* **Python (Backend):**  
  * backend\_v2/api/routers/studio/steps.py (CRUD-reitit työvaiheille).  
  * backend\_v2/core/hook\_registry.py (Backendin pitää tarjota GET /api/v2/studio/hooks rajapinta, joka palauttaa dynaamisen listan kaikista käytettävissä olevista pre\_hooks ja post\_hooks arvoista UI:n pudotusvalikkoa varten).  
* **Riverpod / Flutter:**  
  * client\_app\_v2/lib/features/studio/views/step\_builder\_view.dart (Muutetaan siten, että pre\_hooks ja post\_hooks valitaan Enum/Multi-select \-komponentilla, ja prompt\_blocks on Drag & Drop \-lista).

## **4\. Esityskerros (Layouts)**

Output Profiles muuttuu suoremmaksi Layouts-hallinnaksi.

* **Python (Backend):**  
  * backend\_v2/api/routers/output\_profiles.py  
* **Riverpod / Flutter:**  
  * client\_app\_v2/lib/features/studio/controllers/output\_profile\_controller.dart  
  * client\_app\_v2/lib/features/studio/views/output\_profile\_list\_view.dart (Master-lista).  
  * client\_app\_v2/lib/features/studio/views/output\_profile\_crud\_view.dart ja profile\_editor\_view.dart (Detail-näkymä, jossa suoraan hallitaan arvoja SDUI-malleille kuten ScoreCard, DataTable).

## **5\. Työnkulut (Workflows)**

Raskain editori, jossa Stepit ketjutetaan DAG:iksi.

* **Python (Backend):**  
  * backend\_v2/api/routers/studio/workflows.py  
  * backend\_v2/services/orchestrator/dag\_compiler.py (Tämä luokka suorittaa tallennushetkellä "Dry Run" \-preflight-validoinnin, tarkistaen Kahnin algoritmilla ettei UI:sta lähetetyssä verkossa ole silmukoita).  
* **Riverpod / Flutter:**  
  * client\_app\_v2/lib/features/studio/controllers/blueprint\_editor\_controller.dart (Tilanhallinta Workflowin muokkaukselle).  
  * client\_app\_v2/lib/features/studio/views/workflow\_builder\_view.dart (Työnkulkujen listaus ja CRUD).  
  * client\_app\_v2/lib/features/studio/views/blueprint\_editor\_view.dart (Itse DAG-rakentaja, jossa valitaan Stepit ja määritellään niiden reititykset / Cascading Dropdowns).  
  * client\_app\_v2/lib/features/studio/views/widgets/expected\_input\_editor\_box.dart (Työnkulun odotettujen syötteiden dynaaminen lista).

## **Ylätason Navigaatio (Sivupalkki)**

* client\_app\_v2/lib/features/shell/presentation/widgets/admin\_sidebar.dart  
  Tähän tiedostoon päivitetään uusi 5-osainen päävalikkorakenne, joka reitittää yllä mainittuihin Master-listoihin (GoRouterin avulla).