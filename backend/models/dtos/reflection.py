from pydantic import BaseModel, ConfigDict, Field


class GuidedReflectionDTO(BaseModel):
    """Data Transfer Object for Guided Reflection form inputs."""

    q1_goal: str | None = Field(
        default=None,
        description=(
            "Tavoite ja strateginen suunnittelu: Mikä oli alkuperäinen tavoitteesi, "
            "ja miten jaoit laajan ongelman pienempiin osiin ennen ensimmäistäkään "
            "tekoälylle annettua kehotetta?"
        ),
    )
    q2_falsification: str | None = Field(
        default=None,
        description=(
            "Tekoälyn ohjaus ja kriittinen iterointi: Mitä puutteita, virheitä tai "
            "hallusinaatioita havaitsit tekoälyn vastauksissa prosessin aikana, "
            "ja miten ohjasit tekoälyä korjaamaan ne?"
        ),
    )
    q3_synthesis: str | None = Field(
        default=None,
        description=(
            "Oma panos ja luovuus: Mikä on lopullisessa työssä puhtaasti omaa, "
            "inhimillistä lisäarvoasi?"
        ),
    )
    q4_argumentation: str | None = Field(
        default=None,
        description=(
            "Laadunvarmistus ja metakognitio: Millä perusteilla arvioit lopputuloksen "
            "olevan laadukas ja luotettava? Jos tekisit tehtävän uudelleen, "
            "mitä tekisit toisin?"
        ),
    )

    model_config = ConfigDict(strict=True)
