# Arkkitehtuurisuunnitelma: Normalisoitu Sääntökanta (SSOT)

## Tavoite
Jokainen sääntö, mandaatti ja määritelmä on olemassa vain yhdessä paikassa, ja ne injektoidaan dynaamisesti agenttien kehotteisiin. Tämä poistaa päällekkäisyydet ja varmistaa johdonmukaisuuden.

## 1. Datan Atomisointi (`data/fragments/`)
Sen sijaan, että meillä on yksi iso `MASTER_INSTRUCTIONS` -tekstiblobbi, pilkkoisimme sen pieniin, itsenäisiin JSON/YAML-tiedostoihin:

*   `rules.json`: Lista säännöistä (id, text, category).
*   `mandates.json`: Lista mandaateista.
*   `protocols.json`: Protokollat (RFI, Skeemavalidointi).
*   `methods.json`: Menetelmät (Metodologinen Loki, RegEx).

### Esimerkki (`rules.json`):
```json
[
  {
    "id": "RULE_1",
    "name": "Haurauden Tunnustus",
    "content": "Kirjaa XAI-analyysiin Systeeminen Epävarmuus.",
    "applies_to": ["ALL"]
  },
  {
    "id": "RULE_9",
    "name": "Eettinen Tarkastus",
    "content": "Valvo eettisiä periaatteita.",
    "applies_to": ["FACT_CHECKER", "JUDGE"]
  }
]
```

## 2. Dynaaminen Kehotteiden Generointi (Jinja2)
Käyttäisimme Jinja2-templatingia (jota käytämme jo raportoinnissa) myös kehotteiden (prompts) rakentamiseen.

### Esimerkki (`templates/prompt_analyst.j2`):
```jinja2
VAIHE 2: ANALYYTIKKO-AGENTTI
...
TEHTÄVÄT:
{% for method in methods if 'ANALYST' in method.applies_to %}
{{ loop.index }}. {{ method.content }}
{% endfor %}

NOUDATA SEURAAVIA SÄÄNTÖJÄ:
{% for rule in rules if 'ANALYST' in rule.applies_to or 'ALL' in rule.applies_to %}
- {{ rule.id }}: {{ rule.content }}
{% endfor %}
```

## 3. Hyödyt
*   **Ylläpidettävyys**: Jos sääntö 4 muuttuu, muokkaat sitä vain yhdessä paikassa (`rules.json`), ja se päivittyy automaattisesti kaikkiin agentteihin, jotka sitä käyttävät.
*   **Johdonmukaisuus**: Ei enää "copy-paste" -virheitä, joissa yhdellä agentilla on vanha versio säännöstä.
*   **Modulaarisuus**: Uusien agenttien luominen on nopeaa, kun voi vain "poimia" tarvittavat säännöt ja menetelmät kirjastosta.

## 4. Toteutus
Tämä vaatisi `seeder.py`:n uudelleenkirjoittamista niin, että se lukee nämä fragmentit ja "kokoaa" lopulliset prompt-tekstit ennen tietokantaan tallennusta.
