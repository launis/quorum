# P5: Retry-logiikan vahvistus

## Tavoite
Vähentää `[SYSTEM ERROR: LLM Unable to verify.]` -timeout/rate limit -kaatumisia nostamalla Fail-Fast -luupin sallittujen uudelleenyritysten määrää.

## Toimenpiteet
1. Etsi ympäristömuuttujista tai konfiguraatiosta (`settings.py` tms.) vakio, joka määrittää maksimi retry-yritykset (esim. `FAIL_FAST_MAX_RETRIES`).
2. Nosta tämä arvo 1:stä arvoon 2 tai 3, jotta transientit verkko-ongelmat eivät kaada koko ajoa turhaan.

## Säännöt ja Rajoitteet
- Yksinkertainen konfiguraatiomuutos, aja auditoinnit ja varmista ettei se riko asynkronisten jonojen odotuksia.
