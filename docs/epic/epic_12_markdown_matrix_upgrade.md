# Epic 12: Cognitive Context & Markdown Matrix Upgrade

**Tavoitetila:** Vuoden 2026 Enterprise-tason AI-analyysien osumatarkkuuden maksimointi, hallusinaatioiden minimointi ja huomiomekanismin (Attention) hallinta. Siirtyminen raakatekstistä puhtaaseen kone-optimoituun Markdown/XML-kontekstiin sekä kognitiivisen prosessin pakottaminen "System 2" -ajatteluun (Micro-CoT ja luonnollinen itseparantuminen).

## 1. Tausta: Arkkitehtuurin Kognitiiviset Pullonkaulat

Modernit laajat kielimallit (LLM), kuten Gemini 2.5 Pro ja Claude 3.5, kärsivät "Lost in the Middle" -ilmiöstä lukiessaan raakataulukoita tai pitkiä sääntöjä. Vaikka Quorumin Pydantic V2 Strict Mode -arkkitehtuuri on ohjelmallisesti vahva, pelkkä JSON-pohjainen lähestymistapa kohtaa kaksi kriittistä pullonkaulaa siirryttäessä kognitiiviseen kyvykkyyteen:

1.  **Schema Bloat (Skeeman ylikuormitus):** Kun satojen rivien pituiset arviointiasteikot ja säännöt pakotetaan suoraan Pydantic-skeeman `description`-kenttiin, LLM:n resursseja tuhlataan väärin. Mallit on opetettu lukemaan JSON-skeemoja tulosteen muotoilua varten, ei niinkään monimutkaisen liiketoimintalogiikan sisäistämiseen.
2.  **Attention Dilution (Huomion laimeneminen):** DAGExecutorin syöttäessä edellisten askelten historiaa massiivisena, sisäkkäisenä JSONina (`{"steps": {"outputs": {...}}}`), syntyy liikaa syntaktista kohinaa (aaltosulkeita) varsinaisen merkityksen ympärille, mikä syö LLM:n rajallista huomiokykyä.

Tämän Epic 12 -päivityksen ydin on **Signaali-kohinasuhteen (SNR) maksimoiminen**. Emme enää toivo LLM:n ymmärtävän arkkitehtuuria; pakotamme sen ymmärtämään sen siirtämällä säännöt optimaaliseen muotoon ja rakentamalla "kognitiivisen suppilon".

---

## 2. Kooditason Muutokset (Zero-Deploy)

Kaikki muutokset tapahtuvat puhtaasti backendin moottoreissa (`PromptCompiler`, `DAGExecutor`, `LLMClient`), täysin ilman tarvetta UI-päivityksille (eli vältetään "Deploy"-syklit).

### Vaihe 1: `PromptCompiler` – Semantiikan ja Skeeman Täydellinen Erottaminen

**A) "Paksu XML, Ohut Skeema" -arkkitehtuuri**
Matriisien BARS-sääntöjä (Behaviorally Anchored Rating Scales) ei enää renderöidä Pydantic-mallin sisään. PromptCompiler jakaa vastuun:
*   **System Prompt:** Renderöi matriisit puhtaana XML/Markdown-hybridinä. LLM:t ymmärtävät 2D-rakenteita (Markdown-taulukot) ja XML-hierarkiaa natiivisti valtavasti paremmin kuin JSON-avaimien sisään tungettua tekstiä.
*   **Ohut Skeema (`build_dynamic_schema`):** Pydantic-skeemasta tulee höyhenenkevyt. Määritykset (descriptions) toimivat vain magneettisina osoittimina matriisiin.

**Uusi metodi XML-renderöinnille (lisätään `PromptCompiler` -luokkaan):**
```python
    def compile_xml_rubrics(self, criteria: list[dict[str, Any]], target_locale: str) -> str:
        """Epic 12: Generates Thick XML/Markdown rubrics for the System Prompt."""
        xml_blocks = ["<EVALUATION_RUBRICS>"]
        for crit in criteria:
            if crit.get("type") == "instruction":
                continue
                
            crit_id = crit.get("id")
            label = self.resolve_i18n(crit.get("label"), target_locale)
            desc = crit.get("ai_description", "")
            
            xml_blocks.append(f'  <MATRIX id="{crit_id}" title="{label}">')
            if desc:
                xml_blocks.append(f'    <DIRECTIVE>{desc}</DIRECTIVE>')
                
            scales = crit.get("scales", [])
            if scales:
                xml_blocks.append('    | Score | Label | Critical Directive |')
                xml_blocks.append('    |---|---|---|')
                for s in scales:
                    s_val = s.get("score")
                    s_lbl = self.resolve_i18n(s.get("name"), target_locale) if s.get("name") else s.get("ai_label", "")
                    # Litistetään säännöt yhdelle riville Markdown-taulukkoa varten
                    claims = " ".join([c.get("ai_description", "") for c in s.get("claims", [])])
                    xml_blocks.append(f'    | {s_val} | {s_lbl} | {claims} |')
            
            xml_blocks.append('  </MATRIX>')
        xml_blocks.append("</EVALUATION_RUBRICS>")
        return "\n".join(xml_blocks)
```
*(Huom: Kutsu tätä metodia `LLMNodeStrategy`ssä ja liitä se `system_prompt` -muuttujan loppuun).*

**B) Pakotettu Kognitiivinen Järjestys (Micro-CoT)**
Estetään LLM:n "Post-Hoc Fallacy", jossa se antaa nopean arvauksen tuottaessaan auto-regressiivisesti kohdan `score: 4` ja keksii perustelun `_justification` vasta sen jälkeen. Pydantic-malleista (`create_model`) rakennetaan matriisikohtaiset sisäkkäiset mallit pakottamaan hidas "System 2" -päättely:

**Päivitä `_cached_build_dynamic_schema` sisällyttämään Semanttinen Validointi:**
```python
        # PromptCompiler._cached_build_dynamic_schema sisällä (for crit in criteria: -luupissa)
        from pydantic import model_validator
        
        # ... (id ja label haku)
        
        # Epic 12: Micro-CoT sisäkkäiset kentät
        sub_fields = {}
        
        if "citation" in extensions:
            sub_fields["step_1_evidence_quote"] = (str | None, Field(
                default=None, description="EXACT verbatim quote from user input. Return null if none exists."
            ))
            
        if "falsification" in extensions:
            sub_fields["step_2_falsification"] = (str, Field(
                ..., description="Devil's advocate argument. Why might your initial assumption be wrong?"
            ))
            
        if "justification" in extensions:
            sub_fields["step_3_logical_friction"] = (str, Field(
                ..., description=f"Detailed reasoning bridging the evidence to <MATRIX id='{crit_id}'>."
            ))
            
        # ARVOSANA ON AINA VIIMEISENÄ (Estää Post-Hoc Fallacyn)
        sub_fields["step_4_final_score"] = (value_type, Field(
            ..., description=f"Numeric score strictly mapped to <MATRIX id='{crit_id}'> in the system prompt."
        ))

        # Epic 12: Liiketoimintalogiikan validointi (Semantic Self-Healing)
        def validate_logic(cls, values):
            score = values.get("step_4_final_score")
            quote = values.get("step_1_evidence_quote")
            # SÄÄNTÖ: Korkea arvosana vaatii aina empiirisen todisteen raakadatasta
            if score is not None and score >= 4 and not quote:
                raise ValueError(
                    f"CRITICAL LOGICAL ERROR: You assigned a high score ({score}) for '{crit_id}', "
                    f"but failed to provide a verbatim 'step_1_evidence_quote'. "
                    f"You MUST find an exact quote from the text or lower the score immediately."
                )
            return values

        # Luodaan sisäkkäinen malli
        NestedModel = create_model(
            f"{crit_id}_Evaluation",
            __config__=ConfigDict(extra="forbid", strict=True),
            __validators__={"logic_check": model_validator(mode="before")(validate_logic)},
            **sub_fields
        )
        
        fields[crit_id] = (NestedModel, Field(..., description=f"Evaluation object for {label}"))
```

### Vaihe 2: `DAGExecutor` – Semanttinen Tilan Karsinta ja Litistäminen

Kun työnkulku etenee, aiemmat askeleet tuottavat valtavasti kontekstia. Nykytilan JSON-dumppi varastaa arvokasta prosessointikapasiteettia signaalin hukkuessa.
**Päivitä `_extract_value_from_state` litistämään Pydantic-tulosteet puhtaaksi Markdowniksi:**
```python
        if isinstance(current, dict):
            # Epic 12: Flatten nested JSON into LLM-friendly Markdown
            formatted = []
            for k, v in current.items():
                formatted.append(f"<prior_step_context source=\"{str(k).upper()}\">")
                if isinstance(v, dict):
                    # Puretaan uusi Micro-CoT rakenne nätiksi listaksi
                    target_dict = v.get("outputs", v) if "outputs" in v else v
                    for sub_k, sub_v in target_dict.items():
                        if isinstance(sub_v, dict):
                            formatted.append(f"### {str(sub_k).upper()}")
                            for micro_k, micro_v in sub_v.items():
                                # Siivotaan kognitiiviset etuliitteet pois luettavuuden vuoksi
                                clean_key = str(micro_k).replace("step_1_", "").replace("step_2_", "").replace("step_3_", "").replace("step_4_", "").replace("_", " ").title()
                                formatted.append(f"- **{clean_key}:** {micro_v}")
                        else:
                            formatted.append(f"- **{str(sub_k).title()}:** {sub_v}")
                else:
                    formatted.append(str(v))
                formatted.append("</prior_step_context>\n")
            return "\n".join(formatted).strip()
```

### Vaihe 3: `LLMClient` – Looginen Itseparantuminen (Semantic Self-Healing)

Nykyinen `LLMClient` osaa korjata syntaksivirheitä. Pydantic-validaattorimme heittää nyt `ValueErrorin`, jos tekoäly antaa liian hyvän arvosanan ilman empiiristä lainausta. Muutetaan `LLMClient` ymmärtämään tämä ero.

**Päivitä `run_structured_task` -metodin poikkeuskäsittely:**
```python
                except (json.JSONDecodeError, pydantic.ValidationError) as schema_err:
                    if attempt == max_retries - 1:
                        # ... (vanha error logiikka) ...

                    error_str = str(schema_err)
                    # Tunnistetaan onko kyse meidän asettamasta loogisesta virheestä
                    is_logical_error = "CRITICAL LOGICAL ERROR" in error_str or "Value error" in error_str
                    error_msg = schema_err.json() if isinstance(schema_err, pydantic.ValidationError) else error_str

                    if is_logical_error:
                        logger.warning("[LLMClient] Semantic Logic Error detected. Triggering Socratic Self-Healing.")
                        correction_prompt = (
                            f"\n\n[SYSTEM: STRICT LOGICAL COMPLIANCE REQUIRED]\n"
                            f"Your JSON structure was correct, but your logic failed the architectural validation:\n"
                            f"--- VALIDATION ERROR ---\n{error_msg}\n------------------------\n"
                            f"ACTION: You MUST engage System 2 thinking. Correct your cognitive logic. "
                            f"If you cannot provide empirical evidence, you MUST lower your score to match reality. Do not guess."
                        )
                    else:
                        logger.warning("[LLMClient] Structural Schema Error detected. Triggering Syntax Self-Healing.")
                        correction_prompt = (
                            f"\n\n[SYSTEM: SELF-HEALING CORRECTION - STRUCTURAL]\n"
                            f"Validation errors:\n{error_msg}\n"
                            f"ACTION: Please correct the JSON output to strictly match the requested schema types."
                        )

                    # Syötetään palaute takaisin mallille
                    failed_content = getattr(response, "content", "EMPTY_CONTENT") if response else "EMPTY_CONTENT"
                    current_prompt += f"\n\n{failed_content}{correction_prompt}"

                    final_messages.append({"role": "assistant", "content": failed_content})
                    final_messages.append({"role": "user", "content": correction_prompt})
```

### Vaihe 4: `InputProcessingHook` – Syötteen Kognitiivinen Eristäminen (The "Pre-Flight" Boundary)

Tekoälyn ei koskaan pitäisi joutua tekemään ETL-työtä kalliilla huomiolaskennallaan. Kaikki data litistetään 100% puhtaaksi Markdowniksi `input_processing.py` -hookissa *ennen* kognitiivista moottoria:

1. **Kyselylomakkeiden Blockquote-eristys:** Estää Prompt Injectionin ja erottaa käyttäjän tekstin järjestelmän puheesta LLM:lle.
   ```python
                   elif str(q_key).startswith("a"):
                       # Epic 12: Isolate user input with blockquotes
                       markdown_parts.append(f"> **A:** {val}\n")
   ```

2. **PDF-purku (`pymupdf4llm`):** Vaihdetaan purku suoraan markdowniksi, jolloin PDF:n omat taulukot ja otsikot säilyvät täydellisesti LLM:lle luettavassa muodossa:
   ```python
   def _extract_pdf(file_bytes: bytes) -> str:
       import pymupdf4llm # Vaatii: pip install pymupdf4llm
       doc = fitz.open(stream=file_bytes, filetype="pdf")
       md_text = pymupdf4llm.to_markdown(doc)
       doc.close()
       return md_text.strip()
   ```

---

## 3. DoD (Definition of Done)

* [ ] `PromptCompiler`: Yhdistää säännöt vahvaan kone-optimoituun eristettyyn XML-kontekstiin huomion laimenemisen (Lost in the middle) välttämiseksi.
* [ ] `PromptCompiler`: Rakentaa `create_model` dynaamiseen validointiin tiukan "Micro-CoT" Pydantic -järjestyksen (`1_evidence_quote` -> `4_final_score`), pakottaen LLM:n argumentoimaan itsensä kohti tulosta.
* [ ] `DAGExecutor`: Litistää muiden agenttien aiemmat JSON-tulokset historiasta luonnolliseksi `<prior_step_context>` Markdowniksi, poistaen synteettisen kohinan (Attention Dilution -ratkaisu).
* [ ] `LLMClient`: Hyödyntää `@model_validator`-logiikkaa dynaamisesti luoduissa skeemoissa ja kykenee antamaan loogisen/sokraattisen korjausviestin malleille ("Semantic Self-Healing").
* [ ] `InputProcessingHook`: Käsittelee PDF-tiedostot puhtaana Markdownina (`pymupdf4llm`), eristää kyselylomakkeet Blockquote-rakenteilla ja muuntaa chattidatan raskaasta JSONista semanttiseksi Transcript-markdowniksi välittömästi Pre-Flight-vaiheessa.
