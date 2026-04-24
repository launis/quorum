# EPIC 37: Enforce Mandatory Micro-CoT in Dynamic Schemas

**Status:** REJECTED / INVALIDATED
**Objective:** Sementoi "Micro-CoT" (Chain-of-Thought) -harkintakenttä. 

## HYLÄTTY (Invalidated)
Tämä Epic luotiin tekoälyn tekemän väärän oletuksen perusteella. Oletuksena oli, että Pydantic-malli pyytäisi AI:lta suoraan `score` (pisteet) -kenttää, jolloin ilman erillistä `justification`-kenttää malli joutuisi arvaamaan numeron.

Todellisuudessa Quorumin arkkitehtuuri käyttää **Atom Flattening** -mekanismia (`Epic 27 Telemetry`). Matemaattisia pisteitä **ei koskaan** kysytä suoraan tekoälyltä! Tekoäly palauttaa ainoastaan `AtomResponse`-objekteja, joissa on JO sisäänrakennettuna tiukka Micro-CoT -rakenne: `quote -> reasoning -> boolean`. Backendin deterministinen koodi (ei AI) laskee lopulliset pisteet näiden `boolean`-kenttien pohjalta.

Koska pisteytys on täysin irrotettu dynaamisista laajennoksista (kuten `justification`), tekoälyn laskentatehoa ei voida vahingossa "rampauttaa" UI-konfiguraatiolla. Arkkitehtuuri on siis jo nyt turvallinen. Tämä Epic on tarpeeton.
