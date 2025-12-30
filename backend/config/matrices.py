from typing import List, Dict
from backend.models.domain import EvaluationMatrixConfig, EvaluationCriterion

# --- 1. Standard Strategic Matrix (Driver vs. Passenger) ---
MATRIX_STANDARD_V1 = EvaluationMatrixConfig(
    name="Strategisen Ohjauksen Arviointimatriisi (Agency & Engineering)",
    description="Arvioi käyttäjän kykyä toimia prosessin Kuljettajana (Agency) ja hyödyntää tekoälyä teknisesti oikein (Engineering).",
    role_description="Toimit Strategisena Tuomarina. Arvioit käyttäjän `Agency`:a (Toimijuutta) eli kykyä ohjata tekoälyä tavoitteellisesti.",
    scale={"min": 1, "max": 4},
    criteria=[
        EvaluationCriterion(
            id="analyysi", # Maps to Agency/Strategy slot
            label="Strateginen Ohjaus (Agency)",
            instruction="Arvioi, onko prosessi suunniteltu (Arkkitehti/Kuski) vai reaktiivinen (Kartanlukija/Matkustaja).",
            anchors={
                "4": "Arkkitehti (Suunnittelee): Käyttäjä on purkanut ongelman osiin (Decomposition) ENNEN ensimmäistä promptia. Prosessi on suunniteltu ketju.",
                "3": "Kuski (Ohjaa): Käyttäjä tietää mitä haluaa ja asettaa reunaehdot. Korjaa suuntaa aktiivisesti, jos tekoäly poikkeaa.",
                "2": "Kartanlukija (Korjaa): Reaktiivinen toiminta. Epämääräinen aloitus, korjaa vasta jälkikäteen ('Ei noin, vaan näin').",
                "1": "Matkustaja (Tilaa): Passiivinen tilaaja. 'Tee essee aiheesta X'. Hyväksyy ensimmäisen version. Ulkoistaa ajattelun."
            }
        ),
        EvaluationCriterion(
            id="arviointi", # Maps to Engineering/Execution slot
            label="Tekninen Toteutus (Engineering)",
            instruction="Arvioi promptaustekniikoiden (Few-Shot, CoT, Roolitus) käyttöä.",
            anchors={
                "4": "Insinööri: Käyttää edistyneitä tekniikoita: Few-Shot, Chain-of-Thought, XML-tagit. Promptit ovat strukturoituja olioita.",
                "3": "Osaaja: Käyttää perustekniikoita: Roolitus, selkeät rajoitteet, kontekstin syöttö. Kieli on täsmällistä.",
                "2": "Keskusteleva: Käyttää luonnollista puhekieltä ('Voisitko...'). Promptit epätarkkoja.",
                "1": "Laiska (Lazy): Kirjoitusvirheitä, 'se juttu', pelkkiä avainsanoja. Luottaa tekoälyn 'mind reading' -kykyyn."
            }
        ),
        EvaluationCriterion(
            id="synteesi", # Maps to Falsification/Iteration slot
            label="Kriittinen Iteraatio (Falsification)",
            instruction="Arvioi käyttäjän kriittisyyttä tekoälyn tuotoksia kohtaan.",
            anchors={
                "4": "Adversariaalinen: Testaa rajoja ('Etsi virheet'). Spottaa faktavirheet ja pakottaa korjaamaan lähteisiin viitaten.",
                "3": "Korjaava: Huomaa selkeät virheet ja pyytää korjausta.",
                "2": "Hyväksyvä: Kehuu tekoälyä ('Hyvä!') vaikka vastauksessa olisi puutteita. Korjaukset vain tyylillisiä.",
                "1": "Sokea: Sokea luottamus. Kopioi hallusinaatiot suoraan lopputuotteeseen."
            }
        )
    ]
)

# --- 2. Cognitive Matrix (Bloom's Taxonomy) ---
MATRIX_COGNITIVE_V2 = EvaluationMatrixConfig(
    name="Kognitiivinen Arviointimatriisi (Bloom & Toulmin)",
    description="Arvioi ajattelun laatua Bloom:n taksonomian (Analyze, Evaluate, Create) ja Toulminin argumentaatiomallin kautta.",
    role_description="Toimit Kognitiivisena Tutkijana. Arvioit argumentaation rakenteellista ja älyllistä laatua.",
    scale={"min": 1, "max": 4},
    criteria=[
        EvaluationCriterion(
            id="analyysi",
            label="Analyysi ja Prosessin Tehokkuus (Bloom: Analyze)",
            instruction="Kyky pilkkoa monimutkainen tieto osiin ja tunnistaa syy-seuraussuhteet.",
            anchors={
                "4": "Prosessi on strateginen. Käyttäjä on purkanut ongelman osiin ja ohjannut tekoälyä ennaltaehkäisevästi. TAI Prosessi osoittaa poikkeuksellista ketteryyttä merkittävän oivalluksen kautta.",
                "3": "Prosessi on tehokas. Käyttäjä on tunnistanut ongelman ja ohjannut tekoälyä reaktiivisesti mutta johdonmukaisesti.",
                "2": "Prosessi on reaktiivinen. Käyttäjä reagoi vastauksiin ilman selkeää strategiaa. Iteraatioita ilman laadullista parannusta.",
                "1": "Prosessi on tehoton. Käyttäjä ei ole kyennyt ohjaamaan tekoälyä kohti tavoitetta."
            }
        ),
        EvaluationCriterion(
            id="arviointi",
            label="Arviointi ja Argumentaatio (Bloom: Evaluate; Toulmin)",
            instruction="Kyky esittää perusteltuja arvostelmia ja vertailla vaihtoehtoja kriteerien perusteella.",
            anchors={
                "4": "Poikkeuksellinen arviointikyky. Käyttäjä on haastanut tekoälyn päättelyä. Reflektio sisältää virheettömän argumentin.",
                "3": "Korkea arviointikyky. Käyttäjä on korjannut tuotoksia. Reflektio sisältää vahvan argumentin: Väite, Perusteet ja Oikeutus.",
                "2": "Perustason arviointikyky. Pieniä korjauksia. Reflektio sisältää argumentin aihion (Väite esitetty, perusteet heikkoja).",
                "1": "Ei arviointikykyä. Tekoälyn tuotokset käytetty sellaisenaan. Reflektio virheellinen tai harhaanjohtava."
            }
        ),
        EvaluationCriterion(
            id="synteesi",
            label="Synteesi ja Luovuus (Bloom: Create)",
            instruction="Kyky yhdistää elementtejä uudeksi kokonaisuudeksi.",
            anchors={
                "4": "Strateginen synteesi. Käyttäjä on luonut uutta, omaperäistä lisäarvoa, jota tekoäly ei ehdottanut.",
                "3": "Omaperäinen synteesi. Käyttäjä on parannellut tekoälyn tuotosta omalla perustellulla panoksellaan.",
                "2": "Kooste. Lopputuote on pääosin kooste tekoälyn materiaalista. Muutokset kielellisiä.",
                "1": "Kopio. Suora kopio tekoälyn tuottamasta materiaalista ilman omaa panosta."
            }
        )
    ]
)

# Registry for easy lookup
MATRICES = {
    "matrix_standard_v1": MATRIX_STANDARD_V1,
    "matrix_cognitive_v2": MATRIX_COGNITIVE_V2
}
