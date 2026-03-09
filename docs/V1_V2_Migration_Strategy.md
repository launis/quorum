# V1 -> V2 Migraation Sääntökirja

Tämä sääntökirja tiivistää lyhyesti ja selkeästi säännöt, joilla V1-arkkitehtuurin tietorakenteet muutetaan siistittyyn V2-muotoon.

## Pääperiaate: 3 Tasoa

V2-arkkitehtuuri koostuu kolmesta selkeästä tasosta: Palikat (`prompt_blocks`), Tehtävät (`task_blueprints`) ja Työnkulut (`workflows`).

---

### 1. Palikat: Matriisit ja Komponentit (V1) ➔ Prompt Blocks (V2)
V1:n monimutkaiset ja erilliset `matrices`- ja `components`-rakenteet yhdistetään yhdeksi ainoaksi tauluksi: **`prompt_blocks`**.

*   Ei ole erillisiä "Agentteja". Pelkät rooli- tai ohjetekstit (esim. "Olet tuomari") tallennetaan tänne muotoon `type: "instruction"`.
*   Tieteelliset arviointimatriisit (BARS, Toulmin) asuvat myös täällä, varustettuna `scales`-asteikoilla.

**Esimerkki (Prompt Block):**
```json
{
  "id": "matrix_toulmin",
  "category_id": "scientific_theory",
  "type": "string",
  "label": { "default_locale": "fi", "translations": { "fi": "Toulminin Argumentaatio" } },
  "description": { "default_locale": "fi", "translations": { "fi": "Puro argumentti osiin..." } }
}
```

---

### 2. Tehtävät: Steps (V1) ➔ Task Blueprints (V2)
V1:n monimutkaiset askeleet pelkistetään **`task_blueprints`** -malleiksi. 
Task Blueprint on pelkkä "resepti". Sen päätehtävä on **sisältää linkit prompt blocks -tauluun**. Se yhdistää halutun ohjeistuksen ja mittarit yhdeksi kokonaisuudeksi.

**Esimerkki (Task Blueprint):**
```json
{
  "id": "task_judge",
  "name": { "default_locale": "fi", "translations": { "fi": "Tuomarin Arviointi" } },
  "prompt_blocks": [
    "block_judge_role",       // Viittaus rooliohjeeseen
    "matrix_toulmin",         // Viittaus argumentaatiomatriisiin
    "matrix_kahneman"         // Viittaus ajattelunopeusmatriisiin
  ]
}
```

---

### 3. Reititin: Workflows (V1) ➔ Workflows (V2)
Työnkulut (Workflows) ovat V2:ssa pelkistettyjä reitittimiä. Ne sisältävät lähinnä:
1.  **Input / Output**: Miten askeleet linkitetään toisiinsa (Mistä data tulee, mihin se menee).
2.  **Solmut (Steps)**: Linkit `task_blueprints` -slugeihin.
3.  **Mallin kohdistus (MANDATE)**: **Tämä on ainut paikka, missä päätetään tekoälymallin strategia (esim. "käytä isoa OpenAI-mallia" tai "käytä nopeaa Googlea").** Globaali `model_registry` opettaa järjestelmälle vain mitä malleja on olemassa, mutta lopullinen tekoälymallin *kohdistus* tehdään aina Workflowssa!

**Esimerkki (Workflow askeleineen):**
```json
{
  "id": "workflow_courtroom_30",
  "name": { "default_locale": "fi", "translations": { "fi": "Courtroom 3.0" } },
  "expected_inputs": {
    "chat_log": "string"
  },
  "steps": [
    {
      "id": "step_node_1",
      "task_blueprint": "task_judge",
      "input_mappings": {
        "context": "$inputs.chat_log"
      },
      "model_strategy": "advanced_reasoning" // Mallin kohdistus tapahtuu täällä!
    }
  ]
}
```

---

## Yhteenveto Työnjaosta

| V1 Rakenne | V2 Nimitys | Mitä se tekee käytännössä V2:ssa? |
| :--- | :--- | :--- |
| `Component` / `Matrix` | **`Prompt Blocks`** | Sisältää ohjetekstin tai numeerisen BARS-kriteeristön. Tämä on matalimman tason palikka. |
| `Step` | **`Task Blueprints`** | Listaa suoraan (viittaa slugilla) niihin Palikoihin (`prompt_blocks`), joita tässä tehtävässä käytetään. |
| `Workflow` | **`Workflows`** | Kytkee Tehtävät (`task_blueprints`) peräkkäin, syöttää askeleelle oikeat Inputit, ja **valitsee tekoälymallin**. |
