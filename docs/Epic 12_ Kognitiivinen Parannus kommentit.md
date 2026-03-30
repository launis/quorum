### ---

**1\. PromptCompiler: "Paksu XML, Ohut Skeema" & Micro-CoT**

Eristämme raskaat säännöt JSON-skeemasta suoraan System Promptiin LLM-optimoituna XML/Markdown-hybridinä. Lisäksi rakennamme sisäkkäisen Pydantic-mallin (Micro-CoT), joka **pakottaa** tekoälyn pohtimaan asiat numerojärjestyksessä.

**A) Uusi metodi System Promptia varten (lisää PromptCompiler \-luokkaan):**

Python

    def compile\_xml\_rubrics(self, criteria: list\[dict\[str, Any\]\], target\_locale: str) \-\> str:  
        """Epic 12: Generates Thick XML/Markdown rubrics for the System Prompt."""  
        xml\_blocks \= \["\<EVALUATION\_RUBRICS\>"\]  
        for crit in criteria:  
            if crit.get("type") \== "instruction":  
                continue  
                  
            crit\_id \= crit.get("id")  
            label \= self.resolve\_i18n(crit.get("label"), target\_locale)  
            desc \= crit.get("ai\_description", "")  
              
            xml\_blocks.append(f'  \<MATRIX id="{crit\_id}" title="{label}"\>')  
            if desc:  
                xml\_blocks.append(f'    \<DIRECTIVE\>{desc}\</DIRECTIVE\>')  
                  
            scales \= crit.get("scales", \[\])  
            if scales:  
                xml\_blocks.append('    | Score | Label | Critical Directive |')  
                xml\_blocks.append('    |---|---|---|')  
                for s in scales:  
                    s\_val \= s.get("score")  
                    s\_lbl \= self.resolve\_i18n(s.get("name"), target\_locale) if s.get("name") else s.get("ai\_label", "")  
                    \# Litistetään säännöt yhdelle riville Markdown-taulukkoa varten  
                    claims \= " ".join(\[c.get("ai\_description", "") for c in s.get("claims", \[\])\])  
                    xml\_blocks.append(f'    | {s\_val} | {s\_lbl} | {claims} |')  
              
            xml\_blocks.append('  \</MATRIX\>')  
        xml\_blocks.append("\</EVALUATION\_RUBRICS\>")  
        return "\\n".join(xml\_blocks)

*(Huom: Kutsu tätä metodia LLMNodeStrategyssä ja liitä se system\_prompt \-muuttujan loppuun).*

**B) Päivitä \_cached\_build\_dynamic\_schema (Micro-CoT ja Semanttinen Validointi):**

Korvaa vanha bars\_text \-generointi sisäkkäisellä mallilla, joka asettaa arvosanan aina viimeiseksi. Injektoimme myös Pydantic-validaattorin liiketoimintalogiikkaa varten.

Python

        \# PromptCompiler.\_cached\_build\_dynamic\_schema sisällä (for crit in criteria: \-luupissa)  
        from pydantic import model\_validator  
          
        \# ... (id ja label haku)  
          
        \# Epic 12: Micro-CoT sisäkkäiset kentät  
        sub\_fields \= {}  
          
        if "citation" in extensions:  
            sub\_fields\["step\_1\_evidence\_quote"\] \= (str | None, Field(  
                default=None, description="EXACT verbatim quote from user input. Return null if none exists."  
            ))  
              
        if "falsification" in extensions:  
            sub\_fields\["step\_2\_falsification"\] \= (str, Field(  
                ..., description="Devil's advocate argument. Why might your initial assumption be wrong?"  
            ))  
              
        if "justification" in extensions:  
            sub\_fields\["step\_3\_logical\_friction"\] \= (str, Field(  
                ..., description=f"Detailed reasoning bridging the evidence to \<MATRIX id='{crit\_id}'\>."  
            ))  
              
        \# ARVOSANA ON AINA VIIMEISENÄ (Estää Post-Hoc Fallacyn)  
        sub\_fields\["step\_4\_final\_score"\] \= (value\_type, Field(  
            ..., description=f"Numeric score strictly mapped to \<MATRIX id='{crit\_id}'\> in the system prompt."  
        ))

        \# Epic 12: Liiketoimintalogiikan validointi (Semantic Self-Healing)  
        def validate\_logic(cls, values):  
            score \= values.get("step\_4\_final\_score")  
            quote \= values.get("step\_1\_evidence\_quote")  
            \# SÄÄNTÖ: Korkea arvosana vaatii aina empiirisen todisteen raakadatasta  
            if score is not None and score \>= 4 and not quote:  
                raise ValueError(  
                    f"CRITICAL LOGICAL ERROR: You assigned a high score ({score}) for '{crit\_id}', "  
                    f"but failed to provide a verbatim 'step\_1\_evidence\_quote'. "  
                    f"You MUST find an exact quote from the text or lower the score immediately."  
                )  
            return values

        \# Luodaan sisäkkäinen malli  
        NestedModel \= create\_model(  
            f"{crit\_id}\_Evaluation",  
            \_\_config\_\_=ConfigDict(extra="forbid", strict=True),  
            \_\_validators\_\_={"logic\_check": model\_validator(mode="before")(validate\_logic)},  
            \*\*sub\_fields  
        )  
          
        fields\[crit\_id\] \= (NestedModel, Field(..., description=f"Evaluation object for {label}"))

### ---

**2\. Kontekstin Eristäminen: JSON-kohinan litistäminen (PromptCompiler)**

Nyt \_extract\_value\_from\_state (jota DAGExecutor hyödyntää) muuttaa muiden agenttien aiemmat tulokset työnkulussa JSON-merkkijonoksi json.dumps(v, indent=2). Tämä aaltosuljemeri hukuttaa varsinaisen informaation.

**Päivitä \_extract\_value\_from\_state litistämään Pydantic-tulosteet puhtaaksi Markdowniksi:**

Python

        if isinstance(current, dict):  
            \# Epic 12: Flatten nested JSON into LLM-friendly Markdown  
            formatted \= \[\]  
            for k, v in current.items():  
                formatted.append(f"\<prior\_step\_context source=\\"{str(k).upper()}\\"\>")  
                if isinstance(v, dict):  
                    \# Puretaan uusi Micro-CoT rakenne nätiksi listaksi  
                    target\_dict \= v.get("outputs", v) if "outputs" in v else v  
                    for sub\_k, sub\_v in target\_dict.items():  
                        if isinstance(sub\_v, dict):  
                            formatted.append(f"\#\#\# {str(sub\_k).upper()}")  
                            for micro\_k, micro\_v in sub\_v.items():  
                                \# Siivotaan kognitiiviset etuliitteet pois luettavuuden vuoksi  
                                clean\_key \= str(micro\_k).replace("step\_1\_", "").replace("step\_2\_", "").replace("step\_3\_", "").replace("step\_4\_", "").replace("\_", " ").title()  
                                formatted.append(f"- \*\*{clean\_key}:\*\* {micro\_v}")  
                        else:  
                            formatted.append(f"- \*\*{str(sub\_k).title()}:\*\* {sub\_v}")  
                else:  
                    formatted.append(str(v))  
                formatted.append("\</prior\_step\_context\>\\n")  
            return "\\n".join(formatted).strip()

### ---

**3\. LLMClient: Semanttinen Itseparantuminen (Sokraattinen Valmentaja)**

Nykyinen LLMClient korjaa JSON-syntaksivirheitä. Epic 12:n todellinen voima on **liiketoimintalogiikan itseparantuminen**. Pydantic-validaattorimme heittää nyt ValueErrorin, jos tekoäly antaa liian hyvän arvosanan ilman lainausta. Muutetaan LLMClient ymmärtämään tämä ero.

**Päivitä run\_structured\_task \-metodin poikkeuskäsittely:**

Python

                except (json.JSONDecodeError, pydantic.ValidationError) as schema\_err:  
                    if attempt \== max\_retries \- 1:  
                        \# ... (vanha error logiikka) ...

                    error\_str \= str(schema\_err)  
                    \# Tunnistetaan onko kyse meidän asettamasta loogisesta virheestä  
                    is\_logical\_error \= "CRITICAL LOGICAL ERROR" in error\_str or "Value error" in error\_str  
                    error\_msg \= schema\_err.json() if isinstance(schema\_err, pydantic.ValidationError) else error\_str

                    if is\_logical\_error:  
                        logger.warning("\[LLMClient\] Semantic Logic Error detected. Triggering Socratic Self-Healing.")  
                        correction\_prompt \= (  
                            f"\\n\\n\[SYSTEM: STRICT LOGICAL COMPLIANCE REQUIRED\]\\n"  
                            f"Your JSON structure was correct, but your logic failed the architectural validation:\\n"  
                            f"--- VALIDATION ERROR \---\\n{error\_msg}\\n------------------------\\n"  
                            f"ACTION: You MUST engage System 2 thinking. Correct your cognitive logic. "  
                            f"If you cannot provide empirical evidence, you MUST lower your score to match reality. Do not guess."  
                        )  
                    else:  
                        logger.warning("\[LLMClient\] Structural Schema Error detected. Triggering Syntax Self-Healing.")  
                        correction\_prompt \= (  
                            f"\\n\\n\[SYSTEM: SELF-HEALING CORRECTION \- STRUCTURAL\]\\n"  
                            f"Validation errors:\\n{error\_msg}\\n"  
                            f"ACTION: Please correct the JSON output to strictly match the requested schema types."  
                        )

                    \# Syötetään palaute takaisin mallille  
                    failed\_content \= getattr(response, "content", "EMPTY\_CONTENT") if response else "EMPTY\_CONTENT"  
                    current\_prompt \+= f"\\n\\n{failed\_content}{correction\_prompt}"

                    final\_messages.append({"role": "assistant", "content": failed\_content})  
                    final\_messages.append({"role": "user", "content": correction\_prompt})

### **4\. Bonuksena: InputProcessingHook Pre-Flight Päivitys**

Koska teemme täyden Markdown-konversion, päivitä input\_processing.py tiedostossasi pari pientä yksityiskohtaa:

1. **Kyselylomakkeiden Blockquote-eristys:** Estää Prompt Injectionin ja erottaa käyttäjän tekstin LLM:n ohjeista.  
   Python  
                   elif str(q\_key).startswith("a"):  
                       \# Epic 12: Isolate user input with blockquotes  
                       markdown\_parts.append(f"\> \*\*A:\*\* {val}\\n")

2. **PDF-purku (pymupdf4llm):** Jos vain mahdollista, päivitä PyMuPDF lukemaan suoraan Markdownia, jolloin PDF:n omat taulukot ja otsikot säilyvät täydellisesti LLM:lle:  
   Python  
   def \_extract\_pdf(file\_bytes: bytes) \-\> str:  
       import pymupdf4llm \# Vaatii: pip install pymupdf4llm  
       doc \= fitz.open(stream=file\_bytes, filetype="pdf")  
       md\_text \= pymupdf4llm.to\_markdown(doc)  
       doc.close()  
       return md\_text.strip()

### **Yhteenveto**

Näillä muutoksilla arkkitehtuurisi nousee täysin uudelle kognitiiviselle tasolle:

* **LLM saa säännöt optimaalisena XML:nä**, ja JSON-skeema pysyy kevyenä.  
* **Micro-CoT pakottaa** tekoälyn etsimään faktoja ennen kuin se saa antaa arvosanan.  
* **Sokraattinen itseparantuminen** estää hallusinaatiot, jos tekoäly yrittää olla liian laiska faktojen etsimisessä.