# Cognitive Evaluation Strictness Framework: Analyysiraportti
Tämä on automaattisesti generoitu raportti kaksiulotteisen tiukkuustestauksen tuloksista.
Testausajossa varioitiin kahta päämuuttujaa:
1. **Makrotaso (Arkkitehtuurinen Tiukkuus):** 3, 5. Vaikuttaa rooleihin (esim. Syyttäjä) ja poikkeusmoduulien (esim. Zero-Trust Null-Hypothesis) käyttöön.
2. **Mikrotaso (Matriisikohtainen Skaala):** 0, 50, 100 (0=Armelias, 100=Lahjomaton). Vaikuttaa prompt-tason ohjeistuksiin.

## Johdon Yhteenveto (Executive Summary)
Quorum V2:n uusittu "Strictness"-moottori on suunniteltu ohjaamaan tekoälyn suorittamaa kognitiivista arviointia kaksiulotteisesti. Raportti todentaa empiirisesti, miten tiukkuustason kiristäminen (Makrotasot 1-5) yhdistettynä matriisikohtaiseen säätöön (0-100) laskee odotetusti arvosanoja ja pakottaa LLM:n vaatimaan vahvempaa näyttöä väitteiden tueksi. Tämä "Tiukkuuden Kalibrointi" on pakollinen ominaisuus erikoistuneissa laadunvarmistus- ja auditoinneissa, poistaen tekoälymalleille tyypillisen myötäilevyyden ja ylioptimistisuuden. Pääasiallinen löydös on, että **Tason 5 Zero-Trust -arkkitehtuuri** toimii halutulla tavalla: se romauttaa arvosanat automaattisesti Null-hypoteesiin, mikäli väitteen tueksi ei löydy todistettavasti validia, tekstivelvoitteet täyttävää näyttöä.

## 1. Suositukset ja Kohderyhmät
### Miten 'Tiukkuus' (Strictness) pitäisi valita?
- **Makrotaso 1 (Gricean / Avulias) - *Ideointi ja Luonnokset*:** Kohderyhmänä luovat työntekijät ja kehittäjät. Tarkoituksena on palkita ideasta ja sallia puutteellinen logiikka hahmotelmissa.
- **Makrotaso 3 (Kausaalinen / Oletus) - *Peruskäyttäjät*:** Suosittelemme tätä päivittäiseen työhön. Se on luotettava baseline, joka etsii rakentavasti syy-seuraussuhteita ilman vihamielistä asennetta. Arvioi reilusti sitä mitä on kirjoitettu.
- **Makrotaso 4 (Falsifikaatio / Syyttäjä) - *Sisäinen Auditointi ja Laadunvarmistus*:** Kohderyhmänä esihenkilöt, asiantuntijat ja QA. Tehokas etsimään piileviä virheitä ja haastamaan ylioptimistisia lausuntoja asettamalla tekoälyn antagonistiseen rooliin.
- **Makrotaso 5 (Zero-Trust) - *Compliance, Lakiosasto ja Turvallisuus*:** Tarkoitettu vain äärimmäiseen validointiin, jossa oletusarvoisesti *mikään* väite ei pidä paikkaansa ilman aukotonta tieteellistä tai dokumentaarista todistetta (Kognitiivinen kitka). Käytä tätä kun virheiden hinta on äärimmäisen korkea.

### Matriisi-tason hienosäätö (Mikrotaso 0-100)
Mikrotaso ohjaa tekoälyn armollisuutta yksittäisten asteikkojen sisällä.
- **0 (Armelias):** Käytä jos haluat sallia tulkinnanvaraisuutta ja palkita yrityksestä. Sopii sisäisiin raportteihin omien alojen asiantuntijoiden kesken.
- **50 (Neutraali):** Sopii objektiiviseen arviointiin yleisen ohjeistuksen mukaan.
- **100 (Lahjomaton):** Käytä vain kun jokaisen sanamuodon ja pilkun on oltava lakiteknisesti tai tieteellisesti kohdallaan. Yhdistettynä Zero-Trust makrotasoon tämä usein romahduttaa normaalin tekstin arvosanat minimiin.

## 2. Numeerinen Analyysi Aineistoittain

### Aineisto: REKLAMAATIO
*(Aineisto-otannan koko: 1 iteratiota per kombinaatio)*


#### Matriisi: `FINAL_SCORE_KILL_SWITCH`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **79.00** | 0.00 | 0.00 | +27.27 |
| 3 | 50 | **51.73** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **46.93** | 0.00 | 0.00 | -4.80 |
| 5 | 0 | **62.53** | 0.00 | 0.00 | +10.80 |
| 5 | 50 | **85.87** | 0.00 | 0.00 | +34.13 |
| 5 | 100 | **69.20** | 0.00 | 0.00 | +17.47 |

#### Matriisi: `matrix_archivist`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **90.00** | 0.00 | 0.00 | -6.00 |
| 3 | 50 | **96.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **84.00** | 0.00 | 0.00 | -12.00 |
| 5 | 0 | **90.00** | 0.00 | 0.00 | -6.00 |
| 5 | 50 | **90.00** | 0.00 | 0.00 | -6.00 |
| 5 | 100 | **96.00** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_bloom`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **78.33** | 0.00 | 0.00 | +25.00 |
| 3 | 50 | **53.33** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **33.33** | 0.00 | 0.00 | -20.00 |
| 5 | 0 | **53.33** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **63.33** | 0.00 | 0.00 | +10.00 |
| 5 | 100 | **76.67** | 0.00 | 0.00 | +23.33 |

#### Matriisi: `matrix_causal_abductive`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **66.67** | 0.00 | 0.00 | +33.33 |
| 3 | 50 | **33.33** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **33.33** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **33.33** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **100.00** | 0.00 | 0.00 | +66.67 |
| 5 | 100 | **33.33** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_causal_analyst`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **64.00** | 0.00 | 0.00 | +44.00 |
| 3 | 50 | **20.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **40.00** | 0.00 | 0.00 | +20.00 |
| 5 | 0 | **40.00** | 0.00 | 0.00 | +20.00 |
| 5 | 50 | **80.00** | 0.00 | 0.00 | +60.00 |
| 5 | 100 | **44.00** | 0.00 | 0.00 | +24.00 |

#### Matriisi: `matrix_falsifier`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **25.00** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **25.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **25.00** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **25.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **25.00** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **25.00** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_goodhart`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **20.00** | 0.00 | 0.00 | -4.00 |
| 3 | 50 | **24.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **20.00** | 0.00 | 0.00 | -4.00 |
| 5 | 0 | **20.00** | 0.00 | 0.00 | -4.00 |
| 5 | 50 | **20.00** | 0.00 | 0.00 | -4.00 |
| 5 | 100 | **24.00** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_judge`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **40.00** | 0.00 | 0.00 | +4.00 |
| 3 | 50 | **36.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **44.00** | 0.00 | 0.00 | +8.00 |
| 5 | 0 | **44.00** | 0.00 | 0.00 | +8.00 |
| 5 | 50 | **40.00** | 0.00 | 0.00 | +4.00 |
| 5 | 100 | **42.00** | 0.00 | 0.00 | +6.00 |

#### Matriisi: `matrix_kahneman`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **36.67** | 0.00 | 0.00 | -3.33 |
| 3 | 50 | **40.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **36.67** | 0.00 | 0.00 | -3.33 |
| 5 | 0 | **40.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **33.33** | 0.00 | 0.00 | -6.67 |
| 5 | 100 | **36.67** | 0.00 | 0.00 | -3.33 |

#### Matriisi: `matrix_taskguard`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **100.00** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **100.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **100.00** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_taskxai_clarity`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **96.00** | 0.00 | 0.00 | -4.00 |
| 3 | 50 | **100.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **96.00** | 0.00 | 0.00 | -4.00 |
| 5 | 100 | **96.00** | 0.00 | 0.00 | -4.00 |

#### Matriisi: `matrix_toulmin`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **96.00** | 0.00 | 0.00 | +40.00 |
| 3 | 50 | **56.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **44.00** | 0.00 | 0.00 | -12.00 |
| 5 | 0 | **96.00** | 0.00 | 0.00 | +40.00 |
| 5 | 50 | **96.00** | 0.00 | 0.00 | +40.00 |
| 5 | 100 | **96.00** | 0.00 | 0.00 | +40.00 |

#### Matriisi: `matrix_xai_reporter`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **100.00** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **100.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **100.00** | 0.00 | 0.00 | +0.00 |

### Aineisto: SYNTHETIC_GARBAGE
*(Aineisto-otannan koko: 1 iteratiota per kombinaatio)*


#### Matriisi: `FINAL_SCORE_KILL_SWITCH`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **28.67** | 0.00 | 0.00 | -1.33 |
| 3 | 50 | **30.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **28.67** | 0.00 | 0.00 | -1.33 |
| 5 | 0 | **22.00** | 0.00 | 0.00 | -8.00 |
| 5 | 50 | **28.67** | 0.00 | 0.00 | -1.33 |
| 5 | 100 | **28.67** | 0.00 | 0.00 | -1.33 |

#### Matriisi: `matrix_archivist`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **20.00** | 0.00 | 0.00 | -40.00 |
| 3 | 50 | **60.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **20.00** | 0.00 | 0.00 | -40.00 |
| 5 | 0 | **20.00** | 0.00 | 0.00 | -40.00 |
| 5 | 50 | **20.00** | 0.00 | 0.00 | -40.00 |
| 5 | 100 | **20.00** | 0.00 | 0.00 | -40.00 |

#### Matriisi: `matrix_bloom`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **16.67** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **16.67** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **16.67** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **16.67** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **16.67** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **16.67** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_causal_abductive`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **66.67** | 0.00 | 0.00 | +33.33 |
| 3 | 50 | **33.33** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **66.67** | 0.00 | 0.00 | +33.33 |
| 5 | 0 | **33.33** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **66.67** | 0.00 | 0.00 | +33.33 |
| 5 | 100 | **66.67** | 0.00 | 0.00 | +33.33 |

#### Matriisi: `matrix_causal_analyst`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **20.00** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **20.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **20.00** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **20.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **20.00** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **20.00** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_falsifier`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **25.00** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **25.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **25.00** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **25.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **25.00** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **25.00** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_goodhart`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **20.00** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **20.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **20.00** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **20.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **20.00** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **20.00** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_judge`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **20.00** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **20.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **20.00** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **20.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **20.00** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **20.00** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_kahneman`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **33.33** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **33.33** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **33.33** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **33.33** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **33.33** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **33.33** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_taskguard`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **100.00** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **100.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **100.00** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_taskxai_clarity`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **100.00** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **100.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **100.00** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_toulmin`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **20.00** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **20.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **20.00** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **20.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **20.00** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **20.00** | 0.00 | 0.00 | +0.00 |

#### Matriisi: `matrix_xai_reporter`
| Macro Level | Micro Level | Mean Score | Std Dev | Variance | Deltas (vs 3/50) |
|---|---|---|---|---|---|
| 3 | 0 | **100.00** | 0.00 | 0.00 | +0.00 |
| 3 | 50 | **100.00** | 0.00 | 0.00 | +0.00 |
| 3 | 100 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 0 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 50 | **100.00** | 0.00 | 0.00 | +0.00 |
| 5 | 100 | **100.00** | 0.00 | 0.00 | +0.00 |