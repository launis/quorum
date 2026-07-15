// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Finnish (`fi`).
class AppLocalizationsFi extends AppLocalizations {
  AppLocalizationsFi([String locale = 'fi']) : super(locale);

  @override
  String get appTitle => 'Cognitive Quorum -asiakas';

  @override
  String get delete => 'Poista';

  @override
  String get errorUnknown => 'Tuntematon virhe';

  @override
  String get errorSseConnectionAborted =>
      'Yhteys palvelimeen katkesi yllättäen (Palvelin kaatui tai sammutettiin). Voit jatkaa ajoa myöhemmin \'Yritä uudelleen\' -painikkeella.';

  @override
  String get errorNetwork => 'Verkkovirhe. Tarkista yhteytesi.';

  @override
  String get errorServer => 'Palvelinvirhe. Yritä myöhemmin uudelleen.';

  @override
  String get errorUnauthorized => 'Luvaton pääsy. Kirjaudu uudelleen.';

  @override
  String get errorNotFound => 'Resurssia ei löydy.';

  @override
  String get errorValidation => 'Validointivirhe.';

  @override
  String get errorValidationEmpty => 'Syötteet eivät voi olla tyhjiä.';

  @override
  String get eventLlmAnomalyRetry =>
      'Laadunvarmistus: Tekoäly havaitsi epäjohdonmukaisuuden ja varmentaa päättelyketjuaan (Yritys 2)...';

  @override
  String errorValidationMissing(String fields) {
    return 'Pakollisia kenttiä puuttuu: $fields';
  }

  @override
  String errorDataMapping(String field, String detail) {
    return 'Mäppäysvirhe kentässä \'$field\': $detail';
  }

  @override
  String errorDataType(String field, String detail) {
    return 'Tyyppivirhe kentässä \'$field\': $detail';
  }

  @override
  String get errorLoadingData => 'Virhe ladattaessa tietoja. Yritä uudelleen.';

  @override
  String get loginBtn => 'Kirjaudu sisään';

  @override
  String get adminPanel => 'Hallintapaneeli';

  @override
  String get settings => 'Asetukset';

  @override
  String get language => 'Kieli';

  @override
  String get themeMode => 'Teema';

  @override
  String get system => 'Järjestelmä';

  @override
  String get light => 'Vaalea';

  @override
  String get dark => 'Tumma';

  @override
  String configureInputs(String workflowId) {
    return 'Määritä syötteet: $workflowId';
  }

  @override
  String get generalInput => 'Yleinen syöte';

  @override
  String fileInputLabel(String fileName, int size) {
    return 'Tiedosto: $fileName ($size tavua)';
  }

  @override
  String get selectFile => 'Valitse ladattava tiedosto';

  @override
  String get fieldRequired => 'Tämä kenttä on pakollinen.';

  @override
  String get authOrganic => 'Orgaaninen (Aito)';

  @override
  String get authPerformative => 'Performatiivinen (Näytelty)';

  @override
  String get authUnknown => 'Tuntematon';

  @override
  String get verVerified => 'Vahvistettu';

  @override
  String get verDebunked => 'Kumottu';

  @override
  String get verUncertain => 'Epävarma';

  @override
  String get fileRequired => 'Tämä tiedosto on pakollinen.';

  @override
  String workflowSubtitle(int steps, int inputs) {
    return 'Vaiheita: $steps | Syötteitä: $inputs';
  }

  @override
  String matrixSubtitle(int rules) {
    return 'Sääntöjä: $rules';
  }

  @override
  String get dashboardTitle => 'Viimeisimmät ajot';

  @override
  String get totalRuns => 'Ajot yhteensä';

  @override
  String get inProgress => 'Käynnissä';

  @override
  String get criticalFailures => 'Epäonnistuneet';

  @override
  String get noExecutions => 'Ei suorituksia.';

  @override
  String failedToLoad(Object error) {
    return 'Virhe ladattaessa: $error';
  }

  @override
  String get retry => 'Yritä uudelleen';

  @override
  String get newAnalysis => 'Uusi analyysi';

  @override
  String get rerunExecutionTooltip => 'Aja uudestaan (kopioi tiedot)';

  @override
  String get rerunExecutionSuccess =>
      'Uusi ajo käynnistetty menestyksekkäästi!';

  @override
  String rerunExecutionFailed(String error) {
    return 'Ajon kopiointi epäonnistui: $error';
  }

  @override
  String get regenerateProfileTooltip =>
      'Luo tämä tuloste uudelleen tekoälyllä';

  @override
  String get regenerateProfileSuccess =>
      'Uudelleengenerointi aloitettu! Voit nyt avata raportin.';

  @override
  String regenerateProfileFailed(String error) {
    return 'Generoinnin käynnistys epäonnistui: $error';
  }

  @override
  String get xaiEvidenceImpactedAxes =>
      'Tätä tietoa käytettiin seuraavien osioiden arvioinnissa:';

  @override
  String get executionDetails => 'Suorituksen tiedot';

  @override
  String get overview => 'Yleiskatsaus';

  @override
  String get report => 'Raportti';

  @override
  String get scorecard_evaluative_matrices_title => 'Arvioivat matriisit';

  @override
  String get scorecard_informational_matrices_title => 'Informaatiomatriisit';

  @override
  String get scorecard_global_average => 'Kokonaiskeskiarvo';

  @override
  String get scorecard_matrix_summary => 'Yhteenveto / Matrix Summary';

  @override
  String get atomicBreakdownTitle => 'Tasojakauma';

  @override
  String get rowExplanationTitle => 'Selite';

  @override
  String get normalizedScore => '100 %';

  @override
  String get matrixEvaluativeAsteriskLegend =>
      '* = Arvioiva matriisi (Vaikuttaa kokonaisarvosanaan)';

  @override
  String get reportPenaltiesApplied => 'Rangaistukset (Sovelletut vääristymät)';

  @override
  String get rawData => 'Raakadata';

  @override
  String get status => 'TILA';

  @override
  String get timeline => 'Aikajana';

  @override
  String get created => 'Luotu';

  @override
  String get workflowProgress => 'Työnkulun eteneminen';

  @override
  String get analysisInProgress => 'Analyysi käynnissä...';

  @override
  String currentStep(Object step) {
    return 'Nykyinen vaihe: $step';
  }

  @override
  String get waitingToStart => 'Odottaa käynnistymistä...';

  @override
  String get executionStarted => 'Suoritus käynnistetty...';

  @override
  String executionFailed(Object error) {
    return 'Suoritus epäonnistui: $error';
  }

  @override
  String executionRejected(Object error) {
    return 'Suoritus hylätty: $error';
  }

  @override
  String get unknownState => 'Tuntematon tila';

  @override
  String get downloadNotImplemented => 'Lataus ei vielä käytössä';

  @override
  String get detailsComingSoon => 'Yksityiskohdat tulossa pian...';

  @override
  String get viewChecklist => 'Näytä tarkistuslista';

  @override
  String get viewRawData => 'Näytä raakadata';

  @override
  String get analysisResults => 'Analyysin tulokset';

  @override
  String get goToMonitor => 'Siirry seurantaan';

  @override
  String get analysisNotComplete => 'Analyysi ei ole vielä valmis.';

  @override
  String get verdict => 'Tuomio';

  @override
  String get score => 'Pisteet';

  @override
  String get summary => 'Yhteenveto';

  @override
  String get type => 'Tyyppi';

  @override
  String get inputs => 'Syötteet';

  @override
  String get startAnalysis => 'Aloita analyysi';

  @override
  String get next => 'Seuraava';

  @override
  String get back => 'Takaisin';

  @override
  String get cancel => 'Peruuta';

  @override
  String get analysisStarted => 'Analyysi aloitettu!';

  @override
  String submissionFailed(Object error) {
    return 'Lähetys epäonnistui: $error';
  }

  @override
  String get fillRequiredInputs => 'Täytä pakolliset kentät.';

  @override
  String errorReadingFile(Object error) {
    return 'Virhe tiedoston luvussa: $error';
  }

  @override
  String get noWorkflowsAvailable => 'Ei työnkulkuja saatavilla.';

  @override
  String get enterCustomWorkflowId => 'Tai syötä mukautettu ID';

  @override
  String get statusCompleted => 'VALMIS';

  @override
  String get statusLabelQueued => 'JONOSSA';

  @override
  String get statusRunning => 'KÄYNNISSÄ';

  @override
  String get statusFailed => 'EPÄONNISTUI';

  @override
  String get statusRejected => 'Hylätty';

  @override
  String get statusDraft => 'LUONNOS';

  @override
  String get typeString => 'Merkkijono (String)';

  @override
  String get typeFloat => 'Desimaaliluku (Float)';

  @override
  String get typeInt => 'Kokonaisluku';

  @override
  String get typeJson => 'JSON-Rakenne';

  @override
  String get typeBoolean => 'Totuusarvo (Boolean)';

  @override
  String get cancelling => 'Peruutetaan';

  @override
  String get statusPending => 'ODOTTAA';

  @override
  String get statusQueued => 'Jonossa';

  @override
  String get statusStarted => 'ALOITETTU';

  @override
  String get inputChatHistory => '1. Keskusteluhistoria / Todistusaineisto';

  @override
  String get inputProductTarget => '2. Tuotos / Arvioinnin kohde';

  @override
  String get inputReflection => '3. Reflektio / Itsearviointi';

  @override
  String get pasteText => 'Liitä teksti';

  @override
  String get uploadFile => 'Lataa tiedosto';

  @override
  String get pasteTextLabel => 'Liitä teksti tähän...';

  @override
  String get unknownWorkflow => 'Tuntematon työnkulku';

  @override
  String get navDashboard => 'Etusivu';

  @override
  String get navSettings => 'Asetukset';

  @override
  String get navAdmin => 'Ylläpito';

  @override
  String get navStudio => 'Studio';

  @override
  String get navRegistry => 'Rekisteri';

  @override
  String get navAnalytics => 'Analytiikka';

  @override
  String stepLabel(Object stepName) {
    return 'Vaihe: $stepName';
  }

  @override
  String get defaultWorkflowTitle => 'Työnkulun suoritus';

  @override
  String executionIdLabel(Object id) {
    return 'Suoritus $id';
  }

  @override
  String get resultsTitle => 'Analyysin tulokset';

  @override
  String get viewLogTooltip => 'Näytä suoritusloki';

  @override
  String get downloadReportTooltip => 'Lataa raportti';

  @override
  String get printVariantSelectorTitle => 'Valitse tulostemalli';

  @override
  String get printVariantSelectorDescription =>
      'Valitse mitä tulostemallia asetteluun käytetään.';

  @override
  String get downloadNotImplementedPdf => 'PDF-lataus ei vielä käytössä';

  @override
  String get chooseAnalysisType => 'Valitse Analyysityyppi';

  @override
  String get lblReasoning => 'Perustelu';

  @override
  String get usageCurrentMonth => 'Nykyisen kuukauden käyttö';

  @override
  String get usageQuota => 'Käyttö vs Kiintiö';

  @override
  String tokensUsed(int count) {
    final intl.NumberFormat countNumberFormat =
        intl.NumberFormat.decimalPattern(localeName);
    final String countString = countNumberFormat.format(count);

    return '$countString Tokenia käytetty';
  }

  @override
  String quotaLimit(int limit) {
    final intl.NumberFormat limitNumberFormat =
        intl.NumberFormat.decimalPattern(localeName);
    final String limitString = limitNumberFormat.format(limit);

    return '$limitString Raja';
  }

  @override
  String get selectWorkflowRequired => 'Valitse analyysityyppi.';

  @override
  String get adminDashboardTitle => 'Hallintapaneeli';

  @override
  String get welcomeAdmin => 'Tervetuloa hallintapaneeliin';

  @override
  String get manageUsersButton => 'Käyttäjien hallinta';

  @override
  String get manageOrganizationsButton => 'Organisaatioiden hallinta';

  @override
  String get userManagementTitle => 'Käyttäjien hallinta';

  @override
  String get organizationManagementTitle => 'Organisaatioiden hallinta';

  @override
  String get userListPlaceholder => 'Käyttäjälistan paikkamerkki';

  @override
  String get organizationListPlaceholder => 'Organisaatiolistan paikkamerkki';

  @override
  String get systemSettingsTitle => 'Järjestelmän asetukset';

  @override
  String monitorTitle(String id) {
    return 'Seuranta: $id';
  }

  @override
  String get viewResults => 'Näytä tulokset';

  @override
  String get analysisCompletedSuccess => 'Analyysi valmistui onnistuneesti!';

  @override
  String get viewFullReport => 'Näytä koko raportti';

  @override
  String get viewRawDataComingSoon => 'Näytä raakadata (Tulossa pian)';

  @override
  String get stepGuard => 'Turva-agentti (Guard)';

  @override
  String get stepAnalyst => 'Analyytikko (Analyst)';

  @override
  String get stepInteraction => 'Vuorovaikutus (Interaction)';

  @override
  String get stepProfiler => 'Profiloija (Profiler)';

  @override
  String get stepPanel => 'Paneeli (Panel Audit)';

  @override
  String get stepArchivist => 'Arkistonhoitaja (Archivist)';

  @override
  String get stepJudge => 'Tuomari (Judge)';

  @override
  String get stepCoach => 'Valmentaja (Coach)';

  @override
  String get stepXai => 'XAI Raportoija (Reporter)';

  @override
  String get stepInitializing => 'Alustetaan...';

  @override
  String get stepLogician => 'Loogikko (Logic)';

  @override
  String get stepFalsifier => 'Falsifioija (Critic)';

  @override
  String get stepCausal => 'Kausaalinen (Causal)';

  @override
  String get stepDetector => 'Performatiivisuus (Detector)';

  @override
  String get stepOverseer => 'Valvoja (Overseer)';

  @override
  String get stepJudgeCognitive => 'Tuomari (Kognitiivinen)';

  @override
  String get stepContext => 'Konteksti (Retrieval)';

  @override
  String get stepInputProcessor => 'Tietojen käsittely (Input Processing)';

  @override
  String validationMissingEvidence(String fields) {
    return 'Puuttuvat todisteet: $fields';
  }

  @override
  String get validationInputEmpty => 'Syötteet eivät voi olla tyhjiä.';

  @override
  String get createOrganization => 'Luo organisaatio';

  @override
  String get editOrganization => 'Muokkaa organisaatiota';

  @override
  String get deleteOrganization => 'Poista organisaatio';

  @override
  String get errorDeleteBlockedByExecutions =>
      'Ei voi poistaa: Kohteella on suorituksia.';

  @override
  String get errorDeleteBlockedByMatrix =>
      'Ei voi poistaa: Havainto on sidottu PromptBlockiin.';

  @override
  String get errorResourceInUse =>
      'Tuhoaminen estetty: Tietue on yhä käytössä.';

  @override
  String get save => 'Tallenna';

  @override
  String get orgNameLabel => 'Organisaation nimi';

  @override
  String get orgTierLabel => 'Taso';

  @override
  String get basicTier => 'Perus';

  @override
  String get premiumTier => 'Premium';

  @override
  String get enterpriseTier => 'Enterprise';

  @override
  String deleteOrgConfirmation(String name) {
    return 'Haluatko varmasti poistaa organisaation $name?';
  }

  @override
  String get deleteOrgHasUsersTitle => 'Organisaatiossa on käyttäjiä';

  @override
  String get deleteOrgHasUsersMessage =>
      'Tämä organisaatio sisältää käyttäjiä. Poistaminen poistaa pysyvästi myös kaikki sen käyttäjät. Toimintoa ei voi peruuttaa.';

  @override
  String get deleteForceConfirm => 'Poista kaikki';

  @override
  String get contactEmailLabel => 'Yhteyshenkilön sähköposti';

  @override
  String get userManagement => 'Käyttäjien hallinta';

  @override
  String get roleManager => 'Roolien hallinta';

  @override
  String get lastActive => 'Viimeksi aktiivinen';

  @override
  String get executionCount => 'Suoritukset';

  @override
  String get roleUpdateSuccess => 'Rooli päivitetty onnistuneesti.';

  @override
  String get demoteLastAdminError =>
      'Viimeistä ylläpitäjää ei voi alentaa. Ylennä toinen käyttäjä ensin.';

  @override
  String get queueStatus => 'Järjestelmäjono';

  @override
  String get queuedJobs => 'Jonossa';

  @override
  String get activeJobs => 'Aktiivisena';

  @override
  String get roleLabel => 'Rooli';

  @override
  String get lastLogin => 'Viimeksi nähty';

  @override
  String get lblWeak => 'Heikko';

  @override
  String get lblModerate => 'Kohtalainen';

  @override
  String get lblStrong => 'Vahva';

  @override
  String get lblSource => 'Lähdetieto';

  @override
  String get lblAbstractQuadrant => 'Abstrakti (Korkea Bloom + Heikko Toulmin)';

  @override
  String get lblSuperficialQuadrant =>
      'Pinnallinen (Matala Bloom + Heikko Toulmin)';

  @override
  String get actions => 'Toiminnot';

  @override
  String get editRole => 'Muokkaa roolia';

  @override
  String get confirmDemotion =>
      'Varoitus: Ylläpitäjän alentaminen rajoittaa heidän oikeuksiaan välittömästi.';

  @override
  String get organizationMembers => 'Organisaation jäsenet';

  @override
  String get refresh => 'Päivitä';

  @override
  String get noUsersFound => 'Käyttäjiä ei löytynyt.';

  @override
  String get loginRequired => 'Kirjautuminen vaaditaan';

  @override
  String get createUser => 'Luo käyttäjä';

  @override
  String get editUser => 'Muokkaa käyttäjää';

  @override
  String get deleteUser => 'Poista käyttäjä';

  @override
  String get displayNameLabel => 'Näyttönimi';

  @override
  String get emailLabel => 'Sähköposti';

  @override
  String get passwordLabel => 'Salasana';

  @override
  String deleteUserConfirmation(String name) {
    return 'Haluatko varmasti poistaa käyttäjän $name?';
  }

  @override
  String get userCreatedSuccess => 'Käyttäjä luotu onnistuneesti.';

  @override
  String get userUpdatedSuccess => 'Käyttäjä päivitetty onnistuneesti.';

  @override
  String get userDeletedSuccess => 'Käyttäjä poistettu onnistuneesti.';

  @override
  String get organizationId => 'Organisaatio ID';

  @override
  String get helpBloom =>
      'Perustuu Bloomin taksonomian uudistettuun versioon (Anderson & Krathwohl, 2001). Matala taso (Muistaminen, Ymmärtäminen) viittaa tiedon toistamiseen, kun taas korkea taso (Analysointi, Arviointi, Luominen) vaatii synteesiä ja uuden rakentamista. Korkea pistemäärä kertoo kyvystä tuottaa monimutkaista, transformatiivista ajattelua pelkän faktojen luetteloinnin sijaan.';

  @override
  String get helpToulmin =>
      'Perustuu Stephen Toulminin teokseen \'The Uses of Argument\' (1958). Malli siirtyy muodollisesta logiikasta käytännön argumentaatioon. Se arvioi, tukeeko Väitettä (Claim) selkeä Data, ja yhdistääkö ne looginen Oikeutus (Warrant). Rakenne varmistaa, että argumentit ovat perusteltuja positioita eivätkä vain irrallisia mielipiteitä.';

  @override
  String get helpWalton =>
      'Perustuu Douglas Waltonin argumentaatioteoriaan. Uskollisuus mittaa dialektista johdonmukaisuutta: seuraako päättely annettuja premissejä (Lähdeaineisto)? Matala uskollisuus paljastaa \'Jälkikäteisrationalisoinnin\' (Post-Hoc), jossa tekoäly keksii perustelut vasta johtopäätöksen jälkeen tukeakseen hallusinoitua tai puolueellista lopputulosta.';

  @override
  String get helpControlRatio =>
      'Perustuu diskurssianalyysiin ja vuorovaikutusdynamiikkaan. Suhde mittaa aloitteellisuutta. \'Matkustaja\' vain reagoi, kun taas \'Kuski\' tai \'Arkkitehti\' asettaa keskustelun raamit ja suunnan. Korkea hallintasuhde tarkoittaa, että tekoäly johtaa kognitiivista työtä käyttäjän puolesta.';

  @override
  String get helpMethodology =>
      'Metodologinen loki kertoo, mitä analyysimenetelmiä tekoäly on soveltanut tässä vaiheessa (esim. \'Logiikka-auditointi\', \'Kausaalisuuden testaus\').';

  @override
  String get rolePassenger => 'Matkustaja';

  @override
  String get roleNavigator => 'Navigaattori';

  @override
  String get roleDriver => 'Ohjaaja';

  @override
  String get roleArchitect => 'Arkkitehti';

  @override
  String get lblCognitiveLevel => 'Kognitiivinen Taso';

  @override
  String get lblStrategicDepth => 'Strateginen Syvyys';

  @override
  String get lblArguments => 'Argumentit';

  @override
  String get lblWaltonScheme => 'Walton-skeema';

  @override
  String get lblCriticalQuestions => 'Kriittiset Kysymykset';

  @override
  String get lblRoleAndPosition => 'Käyttäjän Rooli & Positio';

  @override
  String get lblControlRatio => 'Hallintasuhde (Control Ratio)';

  @override
  String get biasDetected => 'VINOUMA HAVAITTU';

  @override
  String get biasNone => 'Ei Vinoumaa';

  @override
  String get gapDetected => 'RISTIRIITA';

  @override
  String get gapNone => 'Johdonmukainen';

  @override
  String get lblBloomScore => 'Bloom-pisteet';

  @override
  String get lblToulminScore => 'Toulmin-pisteet';

  @override
  String get lblMethodologicalLog => 'Metodologinen Loki';

  @override
  String get lblLogicMatrix => 'Osaamisen osa-alueet';

  @override
  String get lblMatrixSubtitle => 'Visuaalinen analyysi päättelyn laadusta.';

  @override
  String get lblFidelity => 'Uskollisuus';

  @override
  String get lblPostHocWarning => '⚠️ Post-Hoc Rationalisointia havaittu!';

  @override
  String get lblNoRationalization => '✅ Ei rationalisointia.';

  @override
  String get lblAbductiveReasoning => 'Abduktiivinen Päättely';

  @override
  String get lblScenarioActual => 'Skenaario A (Toteutunut)';

  @override
  String get lblScenarioSimulation => 'Skenaario B (Simulaatio)';

  @override
  String get lblCredibility => 'Uskottavuus';

  @override
  String get lblTextMetrics => 'Tekstimetriikka';

  @override
  String get lblBias => 'Tunnistetut Vinoumat';

  @override
  String get lblAuthors => 'Kirjoittajat';

  @override
  String get lblIntent => 'Kirjoittajan Intentio';

  @override
  String get lblPsychProfile => 'Psykologinen Profiili';

  @override
  String get lblFactCheck => 'Faktantarkistus';

  @override
  String get lblEthicalObservation => 'Eettinen Huomio';

  @override
  String get lblAuthenticity => 'Aitousarvio';

  @override
  String get lblHeuristics => 'Heuristiikat';

  @override
  String get lblComplianceAnalysis => 'Compliance-analyysi';

  @override
  String get helpComplianceAnalysis => 'Compliance-analyysi';

  @override
  String get helpFidelity =>
      'Uskollisuus (Fidelity) mittaa päättelyn loogista eheyttä. Se tarkistaa, seuraako johtopäätös tiukasti annetuista premisseistä, ilman keksittyä tietoa (Hallusinaatio) tai ennalta päätetyn lopputuloksen oikeuttamista (Post-Hoc Rationalisointi).';

  @override
  String get helpAbductive =>
      'Abduktiivinen Päättely (Paras Selitys) arvioi, onko tekoälyn johtopäätös uskottavin selitys havainnoille, hyläten epätodennäköisemmät vaihtoehdot.';

  @override
  String get helpStressTest =>
      'Waltonin stressitesti auditoi päättelyn uskollisuutta. Se paljastaa \'Post-Hoc rationalisoinnilla\', jos tekoäly on vain keksinyt perustelut jälkikäteen eikä oikeasti johtanut tulosta niistä.';

  @override
  String get helpCausal =>
      'Pohjautuu C.S. Peircen logiikkaan ja Judea Pearlin kontrafaktuaaleihin. Abduktio (\'Päättely parhaaseen selitykseen\') arvioi todennäköisyyksiä. Uskottavuus testaa syy-ymmärrystä simuloimalla \'Mitä jos?\' -skenaarion ja tarkistamalla, seuraako lopputulos loogisesti maailman säännöistä.';

  @override
  String get helpProfiler =>
      'Profilointi analysoi tekstin sävyä, sanastoa ja piileviä vinoumia (biases). Se auttaa tunnistamaan, yrittääkö tekoäly manipuloida tai onko se puolueellinen.';

  @override
  String get helpFactCheck =>
      'Faktantarkistus vertaa väitteitä tunnettuun tietopohjaan ja etsii eettisiä riskejä.';

  @override
  String get helpPerformativity =>
      'Performatiivisuuden analyysi arvioi, onko vastaus aito ja orgaaninen vai keinotekoinen ja näytelty. Se tunnistaa \'korulauseet\', liioitellun nöyryyden ja muut epäaidot piirteet.';

  @override
  String get helpArchivist =>
      'Tekoälyn kohdistamisen (Alignment) ja Constitutional AI -periaatteiden mukaisesti tämä mittaa, noudattaako agentti sille asetettuja käyttäytymisrajoja ja organisaation normeja, riippumatta käyttäjän kehotteesta. Se varmistaa turvallisuuden ja tavoitteiden mukaisuuden.';

  @override
  String get studioStepsTitle => 'Vaiheet';

  @override
  String get studioConfigurationTitle => 'Asetukset';

  @override
  String get studioAddStepButton => 'Lisää Vaihe';

  @override
  String get studioSaveButton => 'Tallenna Muutokset';

  @override
  String get studioUnsavedChanges => 'Tallentamattomia muutoksia';

  @override
  String get studioSelectStepPrompt => 'Valitse muokattava vaihe';

  @override
  String get studioStepsHeader => 'Vaiheet';

  @override
  String get studioAddStep => 'Lisää Vaihe';

  @override
  String get studioNoSteps => 'Ei vaiheita';

  @override
  String get studioRunTest => 'Aja testi';

  @override
  String get studioSaving => 'Tallennetaan...';

  @override
  String get studioChangesSaved => 'Muutokset tallennettu';

  @override
  String get studioCreateNew => 'Luo uusi';

  @override
  String get studioCopyWorkflow => 'Kopioi työnkulku';

  @override
  String get studioNewNameLabel => 'Uusi nimi';

  @override
  String get studioTabWorkflows => 'Työnkulut';

  @override
  String get studioTabMatrices => 'PromptBlockit';

  @override
  String get studioCreateMatrix => 'Luo PromptBlock';

  @override
  String get studioMatrixName => 'Blockin Nimi';

  @override
  String get studioMatrixDesc => 'Kuvaus';

  @override
  String get matrixRole => 'Roolipersoona (Ohjeille)';

  @override
  String get matrixScale => 'Asteikko (Min - Max)';

  @override
  String get matrixCriteria => 'Arviointikriteerit (Schema)';

  @override
  String get matrixAddCriterion => 'Lisää Havainto';

  @override
  String matrixLevel(Object level) {
    return 'Taso $level';
  }

  @override
  String get studioSelectMatrix => 'Valitse PromptBlock';

  @override
  String get update => 'Päivitä';

  @override
  String get editDimension => 'Muokkaa Havaintoa';

  @override
  String get systemInspectorTitle => 'Järjestelmätarkastaja';

  @override
  String get workflowConfig => 'Konfiguraatio';

  @override
  String get stepPreview => 'Esikatselu';

  @override
  String get generateChain => 'Luo Ketju';

  @override
  String get systemInstruction => 'Järjestelmäohje';

  @override
  String get userPrompt => 'Käyttäjäkehote';

  @override
  String get exportTab => 'Vienti';

  @override
  String get selectStepPlaceholder => 'Valitse vaihe...';

  @override
  String get copyToClipboard => 'Kopioi leikepöydälle';

  @override
  String get copiedToClipboard => 'Kopioitu leikepöydälle!';

  @override
  String get modelRegistryTitle => 'Mallirekisteri';

  @override
  String get providerSettings => 'Palveluntarjoajan asetukset';

  @override
  String get testLab => 'Testilaboratorio';

  @override
  String get runTest => 'Aja testi';

  @override
  String get latency => 'Viive';

  @override
  String get providerLabel => 'Palveluntarjoaja';

  @override
  String get apiKeyLabel => 'API-avain';

  @override
  String get baseUrlLabel => 'Base URL';

  @override
  String get temperatureLabel => 'Lämpötila (Temperature)';

  @override
  String get frequencyPenaltyLabel => 'Toistuvuussakko (Frequency Penalty)';

  @override
  String get presencePenaltyLabel => 'Läsnäolosakko (Presence Penalty)';

  @override
  String get modelNameLabel => 'Mallin nimi';

  @override
  String get testConnection => 'Testaa yhteys';

  @override
  String get adhocTest => 'Ad-Hoc -testi';

  @override
  String get responseOutput => 'Vastaus';

  @override
  String get studioDashboardWorkflowsTitle => 'Työnkulut';

  @override
  String get studioDashboardWorkflowsDesc =>
      'Suunnittele ja hallinnoi auditointityönkulkuja.';

  @override
  String get studioDashboardStepsTitle => 'Vaiheet';

  @override
  String get studioDashboardStepsDesc => 'Määritä suoritusvaiheet.';

  @override
  String get studioDashboardMatricesTitle => 'PromptBlockit';

  @override
  String get studioDashboardMatricesDesc =>
      'Hallinnoi dynaamisia LLM-arviointikriteerejä ja sääntöjä.';

  @override
  String get studioDashboardComponentsTitle => 'V1 Komponentit';

  @override
  String get studioDashboardComponentsDesc =>
      'Hallinnoi V1 legacy sääntöjä (poistuva ominaisuus).';

  @override
  String get helperSelectProvider =>
      'Valitse saatavilla olevista palveluntarjoajista';

  @override
  String get helperSelectModel => 'Valitse kelvollinen malli';

  @override
  String get helperApiKeyMasked =>
      'Jätä ******** säilyttääksesi nykyisen avaimen';

  @override
  String get helperOptionalOverride => 'Valinnainen ohitus';

  @override
  String get errorMustBeNumber => 'On oltava numero';

  @override
  String get errorRangeTemperature => 'On oltava välillä 0.0 - 2.0';

  @override
  String get errorMustBeInteger => 'On oltava kokonaisluku';

  @override
  String get selectProviderPlaceholder =>
      'Valitse muokattava palveluntarjoaja.';

  @override
  String get searchSteps => 'Etsi vaiheita';

  @override
  String get stepSelectToEdit => 'Valitse muokattava vaihe';

  @override
  String deleteWorkflowConfirmation(String name) {
    return 'Haluatko varmasti poistaa työnkulun $name?';
  }

  @override
  String get workflowDeleteConfirmTitle => 'Poista Työnkulku';

  @override
  String workflowDeleteConfirmDesc(String id) {
    return 'Haluatko varmasti poistaa työnkulun \"$id\"?';
  }

  @override
  String get noMatricesFound => 'PromptBlockeja ei löytynyt. Luo uusi!';

  @override
  String get stepCreateNew => 'Luo Uusi Vaihe';

  @override
  String get stepEdit => 'Muokkaa Vaihetta';

  @override
  String get stepIdLabel => 'Askeleen ID (UUID tai uniikki merkkijono)';

  @override
  String get stepIdHelper => 'Yksilöllinen tunniste (esim. \'step_analyst\')';

  @override
  String get stepNameLabel => 'Nimi';

  @override
  String get stepDescriptionLabel => 'Kuvaus';

  @override
  String get stepAgentLogicClass => 'Agentin Logiikkaluokka';

  @override
  String get stepJudgeConfig => 'Tuomarin Konfiguraatio';

  @override
  String get stepEvaluationMatrix => 'PromptBlock (Arviointi)';

  @override
  String get stepEvaluationMatrixHelper =>
      'Kriteerit, jotka ohjaavat Pydantic-skeeman luontia.';

  @override
  String get stepPromptAssembly => 'PromptBlock (Ohjeet)';

  @override
  String get stepAddPrompt => 'Liitä PromptBlock';

  @override
  String get stepPromptAssemblyHelper =>
      'Lohkot, jotka muotoilevat askeleen systeemi-instruktion.';

  @override
  String get stepSaveSuccess => 'Vaihe tallennettu!';

  @override
  String get stepDeleteConfirmTitle => 'Poista askel';

  @override
  String stepDeleteConfirmMessage(String id) {
    return 'Haluatko varmasti poistaa askeleen \"$id\"?';
  }

  @override
  String get stepAddPromptTitle => 'Liitä PromptBlock Askeleeseen';

  @override
  String get stepSearchPrompts => 'Hae PromptBlockeja';

  @override
  String get close => 'Sulje';

  @override
  String get stepIdNameRequired => 'ID ja Nimi ovat pakollisia.';

  @override
  String get executionNotFound => 'Suoritusta ei löydy.';

  @override
  String get ontologyNameLabel => 'Nimi (esim. \"Päättely\")';

  @override
  String get ontologyDescriptionLabel => 'Kuvaus';

  @override
  String get registerDimension => 'Tallenna Havainto';

  @override
  String get newDimension => 'Uusi Havainto';

  @override
  String get lblQuestion => 'Kysymys';

  @override
  String get lblEvidenceHeld => 'Kestikö todistusaineisto?';

  @override
  String get lblObservation => 'Havainto';

  @override
  String get lblCausalAudit => 'Kausaalinen Auditointi';

  @override
  String get lblCounterfactualTest => 'Kontrafaktuaalinen Testi';

  @override
  String get btnHideRawData => 'Piilota Raaka-Data';

  @override
  String get btnShowJson => 'JSON';

  @override
  String get msgJsonCopied => 'JSON kopioitu leikepöydälle';

  @override
  String get errDataIntegrity => 'Data Integrity Error (Fail Fast)';

  @override
  String get subLogicAnalysis => 'Toulmin & Kognitiivinen Taso';

  @override
  String get subStressTest => 'Walton Falsifiointi';

  @override
  String get subCausalAnalysis => 'Kausaalinen & Kontrafaktuaalinen';

  @override
  String get subPerformativityCheck => 'Aitous & Pre-Mortem';

  @override
  String get subFactCheck => 'Hallusinaatiot & Etiikka';

  @override
  String get subProfilerAnalysis => 'Vinoumat & Psyko-profiili';

  @override
  String get subArchivistCheck => 'Compliance & Ennakkotapaukset';

  @override
  String get lblWordCount => 'Sanamäärä';

  @override
  String get lblSentenceCount => 'Lausemäärä';

  @override
  String get lblAvgSentence => 'Keskim. Lausepituus';

  @override
  String get lblLexicalDiversity => 'Sanaston kirjavuus';

  @override
  String get lblCapitalsRatio => 'Suuraakkosten Suhde';

  @override
  String get lblAutomationBias => 'Automaatiovinouma';

  @override
  String get lblSayDoGap => 'Puhe-Teko Kuilu';

  @override
  String get lblBehavioralIndicators => 'Käyttäytymisindikaattorit:';

  @override
  String lblAutomationBiasValue(String value) {
    return 'Automaatioharha: $value';
  }

  @override
  String lblSayDoGapValue(String value) {
    return 'Sanojen ja tekojen ristiriita: $value';
  }

  @override
  String get plausibility_desc =>
      'Uskottavuus mittaa skenaarion realismia ja johdonmukaisuutta.';

  @override
  String get bloomRemembering => 'Muistaminen';

  @override
  String get bloomUnderstanding => 'Ymmärtäminen';

  @override
  String get bloomApplying => 'Soveltaminen';

  @override
  String get bloomAnalyzing => 'Analysointi';

  @override
  String get bloomEvaluating => 'Arviointi';

  @override
  String get bloomCreating => 'Luominen';

  @override
  String get stratLow => 'Taktinen';

  @override
  String get stratMedium => 'Operatiivinen';

  @override
  String get stratHigh => 'Strateginen';

  @override
  String get stratVisionary => 'Visionäärinen';

  @override
  String get logicMatrixTitle => 'Logiikkamatriisi (Päätöksenteon Profilointi)';

  @override
  String get logicMatrixQ1Title => 'Perusteltu Synteesi';

  @override
  String get logicMatrixQ1Desc =>
      'Vahvaa argumentaatiota ja syvällistä synteesiä. Luotettava ja uutta luova.';

  @override
  String get logicMatrixQ2Title => 'Perusteeton Lentely';

  @override
  String get logicMatrixQ2Desc =>
      'Korkealentoista ajattelua ilman riittäviä perusteluita. Mahdollinen hallusinaatio.';

  @override
  String get logicMatrixQ3Title => 'Mekaaninen Faktantarkistus';

  @override
  String get logicMatrixQ3Desc =>
      'Tiukasti perusteltu, mutta rajoittuu olemassa olevan tiedon toistamiseen.';

  @override
  String get logicMatrixQ4Title => 'Heikko Kohina';

  @override
  String get logicMatrixQ4Desc =>
      'Matala kognitiivinen taso ja heikot perustelut. Ei hyödynnettävissä.';

  @override
  String get helpLogicMatrix =>
      'Logiikkamatriisi visualisoi argumentaation laadun ja kognitiivisen syvyyden suhdetta. UUSI: Pallon koko kuvaa strategista syvyyttä (Agentuuri). Suuri pallo tarkoittaa visionääristä otetta.';

  @override
  String get helpStrategicDepth =>
      'Pohjautuu systems thinking -ajatteluun ja ennakointimenetelmiin. Strateginen syvyys mittaa vastauksen ajallista ja systeemistä ulottuvuutta. Se erottaa \'Taktisen\' (välitön, reaktiivinen) ja \'Visionäärisen\' (kaukonäköinen, systeeminen) ajattelun. Korkea syvyys tarkoittaa kykyä mallintaa toisen ja kolmannen asteen seurauksia.';

  @override
  String get helpAuthenticity =>
      'Aitous (Authenticity) mittaa vastauksen luonnollisuutta asteikolla 1-3. 3 = Orgaaninen, 2 = Sekoitettu, 1 = Performatiivinen.';

  @override
  String get helpWordCount => 'Vastauksen kokonaissanamäärä.';

  @override
  String get secThreatDetected => 'UHKA HAVAITTU';

  @override
  String get secThreatNone => 'Ei Uhkia';

  @override
  String get secAnonymized => 'ANONYMISOITU';

  @override
  String get secNotAnonymized => 'EI ANONYMISOITU';

  @override
  String get riskHigh => 'KORKEA RISKI';

  @override
  String get riskMedium => 'Keskitaso';

  @override
  String get riskLow => 'Matala';

  @override
  String get riskUnknown => 'Tuntematon';

  @override
  String get lblDriver => 'Kuljettaja';

  @override
  String get lblPassenger => 'Matkustaja';

  @override
  String get lblRiskLevel => 'Riskitaso';

  @override
  String get lblEmotionalTone => 'Emotionaalinen sävy';

  @override
  String get lblNoFindings => 'Ei merkittäviä löydöksiä.';

  @override
  String get knowledgeBaseIngestionTitle => 'Tietokannan Ingestointi';

  @override
  String get uploadDocxMd => 'Lataa DOCX / MD';

  @override
  String get ingestionComplete => 'Ingestointi Valmis!';

  @override
  String referencesCount(int count) {
    return 'Viitteet: $count';
  }

  @override
  String claimsCount(int count) {
    return 'Väitteet: $count';
  }

  @override
  String get studioDashboardKnowledgeTitle => 'Ingestointi';

  @override
  String get studioDashboardKnowledgeDesc => 'Lataa dokumentteja tietokantaan.';

  @override
  String get addStrategyTooltip => 'Lisää Strategia';

  @override
  String get resetKnowledgeBaseTitle => 'Nollaa Tietokanta?';

  @override
  String get resetKnowledgeBaseConfirmation =>
      'Tämä noudattaa \"Clean Slate\" -protokollaa ja poistaa pysyvästi kaikki syötetyt dokumentit. Jatketaanko?';

  @override
  String get resetButton => 'Nollaa';

  @override
  String get analysisLevelLabel => 'Analyysitaso (Mallistrategia)';

  @override
  String get analysisLevelHelper =>
      'Valitse \"Deep\" monimutkaiseen päättelyyn tai \"Fast\" nopeuteen.';

  @override
  String get analysisLevelNone => 'Ei mitään (Vain jäsennys)';

  @override
  String strategiesLoadError(Object error) {
    return 'Strategioiden lataus epäonnistui: $error';
  }

  @override
  String get processingStatus => 'Käsitellään...';

  @override
  String get errorKnowledgeIngestionFailed =>
      'Tiedon ingestointi epäonnistui. Tarkista tiedosto ja yritä uudelleen.';

  @override
  String get errorKnowledgeResetFailed =>
      'Tietokannan nollaus epäonnistui. Ota yhteys tukeen.';

  @override
  String get errorKnowledgeRetrievalFailed =>
      'Tiedon haku epäonnistui. Palvelin ei vastaa.';

  @override
  String get errValidationFailed => 'Validointivirhe';

  @override
  String get errInternalServerError => 'Palvelinvirhe';

  @override
  String get errResourceNotFound => 'Resurssia ei löydy';

  @override
  String get errDataCorruptionDesc =>
      'Tietokannan eheysvirhe: Tähän ajoon liittyvää raskasta dataa (blobs) ei löydetty fyysiseltä levyltä. Raporttia ei voida rakentaa.';

  @override
  String get actionHintRunAgain =>
      'Vihje: Sinun tulee ajaa työkalun suoritus uudelleen luodaksesi datan fyysiselle levylle.';

  @override
  String get errAuthenticationFailed => 'Kirjautuminen epäonnistui';

  @override
  String get errPermissionDenied => 'Pääsy evätty';

  @override
  String get errServiceUnavailable => 'Palvelu ei vastaa';

  @override
  String get errAgentExecutionCritical => 'Agentin kriittinen virhe';

  @override
  String get errWorkflowExecutionFailed => 'Työnkulun virhe';

  @override
  String get errKnowledgeNotIngestedTitle => 'Tietokanta Tyhjä';

  @override
  String get errKnowledgeNotIngested =>
      'Tietokanta on tyhjä. Lataa dokumentteja Ingestointi-näkymässä ennen analyysia.';

  @override
  String get actionGoToIngestion => 'Siirry Ingestointiin';

  @override
  String get knowledgeActive => 'Tietokanta Aktiivinen';

  @override
  String knowledgeStats(int docCount, int precCount) {
    return 'Dokumentit: $docCount | Ennakkotapaukset: $precCount';
  }

  @override
  String get addReflectionIntent => 'Lisää reflektio (Intentio)';

  @override
  String get reflectionDescription =>
      'Kuvaa omaa ajatteluasi ja tekoälyn ohjaamista prosessin aikana. Tämä on arvioinnin kannalta kriittisin vaihe.';

  @override
  String get guidedReflectionRecommended => 'Ohjattu reflektio (Suositeltu)';

  @override
  String get q1GoalTitle => 'Tavoite ja strateginen suunnittelu (Arkkitehti)';

  @override
  String get q1GoalHint =>
      'Mikä oli alunperin tavoitteesi ja miten pilkoit tehtävän?';

  @override
  String get q2FalsificationTitle =>
      'Tekoälyn ohjaus ja kriittinen iterointi (Falsifioija)';

  @override
  String get q2FalsificationHint =>
      'Mitä puutteita tai virheitä huomasit tekoälyn toiminnassa ja miten korjasit ne?';

  @override
  String get q3SynthesisTitle => 'Oma panos ja luovuus (Arkkitehti)';

  @override
  String get q3SynthesisHint => 'Mikä on lopputuloksessa aitoa omaa panostasi?';

  @override
  String get q4ArgumentationTitle =>
      'Laadunvarmistus ja metakognitio (Tuomari)';

  @override
  String get q4ArgumentationHint =>
      'Millä perusteilla luotat lopputulokseen? Mitä tekisit toisin?';

  @override
  String get minCharsRequired =>
      'Tekstin tulee olla vähintään 100 merkkiä pitkä.';

  @override
  String charsRemainingLength(int len) {
    return 'Vastauksen tulee olla vähintään 100 merkkiä pitkä ($len/100).';
  }

  @override
  String expandArgumentationHint(int len) {
    return 'Suositellaan laajentamaan perusteluita ($len/100 merkkiä)';
  }

  @override
  String get dataUnavailable => 'Tietoja ei saatavilla';

  @override
  String get noDetailedData => 'Tarkempia havaintotietoja ei saatavilla.';

  @override
  String get detailedBreakdown => 'Tarkempi erittely';

  @override
  String scaleInfo(int min, int max) {
    return '(Asteikko: $min-$max)';
  }

  @override
  String get lblClaim => 'Väite';

  @override
  String get lblData => 'Perusteet';

  @override
  String get lblWarrant => 'Oikeutus';

  @override
  String get lblBacking => 'Tuki';

  @override
  String get lblRebuttal => 'Vasta-argumentti';

  @override
  String get lblQualifier => 'Tarkennin';

  @override
  String get lblFindings => 'Löydökset';

  @override
  String get lblNoSignificantFindings => 'Ei merkittäviä löydöksiä.';

  @override
  String get lblImperativeCommands => 'Käskyjen määrä';

  @override
  String get helpImperativeCommands =>
      'Mittari sille, kuinka monta suoraa käskyä tai vaatimusta (imperatiivia) käyttäjä on tekstissään esittänyt. Tämä kuvastaa aloitteellisuutta ja hallintatarvetta vuorovaikutuksessa.';

  @override
  String get lblPostHocRationalization => 'Jälkikäteisrationalisointi';

  @override
  String get lblAvgSentenceLength => 'Lauseen keskipituus';

  @override
  String get lblPsychologicalProfile => 'Psykologinen Profiili';

  @override
  String get lblAuthorIntent => 'Tekijän Intentio';

  @override
  String get lblNoAnalysis => 'Ei analyysiä.';

  @override
  String errNetworkOrTimeout(String reason) {
    return 'Verkkovirhe tai aikakatkaisu (Timeout). Kokeile uudelleen. Tarkempi syy: $reason';
  }

  @override
  String errSystemError(String error) {
    return 'Järjestelmävirhe: $error';
  }

  @override
  String get errInvalidWorkflow =>
      'Virhe: Virheellinen työnkulun valinta. Päivitä sivu.';

  @override
  String get systemConfigsTitle => 'Järjestelmäasetukset';

  @override
  String get modelRegistryDesc =>
      'Määritä globaalisti saatavilla olevat mallit, parametrit ja API-ohitukset.';

  @override
  String get systemMetaTitle => 'Järjestelmän Metatiedot';

  @override
  String get configIdLabel => 'Asetuksen ID';

  @override
  String get configTypeLabel => 'Asetuksen Tyyppi';

  @override
  String get maxTokensLabel => 'Maksimi Tokenit';

  @override
  String get topPLabel => 'Top-P (Ydinotanta)';

  @override
  String get topKLabel => 'Top-K (Ehdokkaat)';

  @override
  String get tpmLimitLabel => 'TPM-raja (Tokens per min)';

  @override
  String get rpmLimitLabel => 'RPM-raja (Requests per min)';

  @override
  String get parsingModeLabel => 'Jäsennystila';

  @override
  String get isActiveLabel => 'Aktiivinen';

  @override
  String get supportsGroundingLabel => 'Tukee Tiedonhakua';

  @override
  String get cachingStrategyLabel => 'Välimuististrategia (Caching Strategy)';

  @override
  String get additionalParamsLabel =>
      'Lisäparametrit (Additional Parameters JSON)';

  @override
  String get strategyLabel => 'Strategia';

  @override
  String get noModelsDefined => 'Rekisterissä ei ole määriteltyjä malleja.';

  @override
  String get workflowEditTitle => 'Muokkaa DAG-työnkulkua';

  @override
  String get workflowConfigTitle => 'Työnkulun Asetukset';

  @override
  String get workflowIdLabel => 'Työnkulun ID (esim. analyysi_putki)';

  @override
  String get workflowSlugLabel =>
      'Työnkulun tunniste (Ohjelmallinen URL slug, pelkkiä pieniä kirjaimia ja alaviivoja, esim. kokonaisvaltainen_auditointi)';

  @override
  String get workflowNameLabel => 'Työnkulun Nimi';

  @override
  String get workflowInputsTitle => 'Odotetut Syötteet (Globaalit Roolit)';

  @override
  String get workflowAddInputBtn => 'Lisää Syöte';

  @override
  String get workflowStepsTitle => 'Suoritusvaiheet (DAG-graafi)';

  @override
  String get workflowAddStepBtn => 'Lisää Vaihe';

  @override
  String get workflowRoleKeyLabel =>
      'Rooliavain (esim. source_text, edustaa globaalia roolia)';

  @override
  String get workflowDescLabel => 'Kuvaus';

  @override
  String get workflowTypeString => 'Merkkijono (Teksti)';

  @override
  String get workflowTypeFile => 'Tiedosto (PDF/Word)';

  @override
  String get workflowTypeJson => 'JSON-Rakenne';

  @override
  String get workflowStepIdLabel => 'Vaiheen ID (esim. oletus_eval)';

  @override
  String get workflowAgentTypeLabel => 'Rooli (Kognitiivinen Taso)';

  @override
  String get executionPersonaTitle => 'Execution Persona Block';

  @override
  String get executionPersonaDescription =>
      'Valitse tekoälyn globaali käyttäytymisprofiili (esim. XAI Reporter, Coach).';

  @override
  String get workflowDependsOnLabel => 'Riippuvuudet (DAG-reunat):';

  @override
  String get workflowNoPrevSteps => 'Ei aiempia vaiheita valittavissa.';

  @override
  String get workflowInputMappingsLabel =>
      'Syötemappaukset (Semanttinen Reititys):';

  @override
  String get workflowAgentInputKey => 'Agentin Syöteavain (esim. inputs)';

  @override
  String get workflowSourceVarLabel => 'Datalähde (esim. \$inputs)';

  @override
  String get workflowMappingHelperTitle => 'Miten Semanttinen Reititys Toimii?';

  @override
  String get workflowMappingHelperDesc =>
      'Luo tekoälyn datavirta näin:\n\n1. Vasen puoli (Agentin Syöteavain) on nimi (XML-tagi), jolla tekoäly lukee datan. Kirjoita avain aina pienillä kirjaimilla ja käytä alaviivaa välilyöntien sijaan (esim. \'inputs\').\n2. Oikea puoli on datan lähde. \'\$inputs\' nappaa kaiken käyttäjän lomakkeeseen antaman tiedon. \'\$steps.step_x.outputs\' kytkee suoraan edellisen agentin tuottaman valmiin datan.\nJos haluat lähettää vakiona pysyvän yksittäisen sanan (esim. \'asiakas\'), kirjoita se oikealle puolelle ilman dollarimerkkiä.';

  @override
  String get workflowAddMappingBtn => 'Lisää Mappaus';

  @override
  String get workflowInputKeyLabel =>
      'Syötteen Avain/Rooli (esim. product_text, mihin rooliin tämä syöte sidotaan työnkulussa)';

  @override
  String get workflowDeleteInputTooltip => 'Poista Syöte';

  @override
  String get workflowInputRequired => 'Pakollinen';

  @override
  String get workflowInputIsChatHistory =>
      'Onko Keskusteluhistoria (LLM-jäsennys)';

  @override
  String get workflowInputModesLabel => 'Syöttötavat:';

  @override
  String get inputModeFile => 'tiedosto';

  @override
  String get inputModePaste => 'teksti';

  @override
  String get inputModeQuestionnaire => 'kysely';

  @override
  String get workflowInputLabelTitle =>
      'Otsikko (UI-lomakkeen Nimi, esim. \'Lopputuote\')';

  @override
  String get workflowInputDescriptionTitle =>
      'Kuvaus (UI-vihje, esim. \'Liitä lopputuote PDF muodossa\')';

  @override
  String get workflowInputAiDescriptionTitle =>
      'Tekoälyn Semanttinen Kuvaus (LLM-pohjustus)';

  @override
  String get workflowInputQuestionnaireDefTitle => 'Kyselyn Määrittely:';

  @override
  String get workflowInputNoQuestionsDefined =>
      'Ei vielä määriteltyjä kysymyksiä. Lisää alle.';

  @override
  String get workflowInputQuestionIdLabel => 'Kysymyksen ID (esim. q1)';

  @override
  String get workflowInputQuestionTextLabel => 'Kysymyksen Teksti';

  @override
  String get workflowInputAddQuestionBtn => 'Lisää Kysymys';

  @override
  String get mockLoginSuccess => 'Ylläpitokirjautuminen onnistui! Ohjataan...';

  @override
  String mockLoginFailed(String error) {
    return 'Ylläpitokirjautuminen epäonnistui: $error';
  }

  @override
  String get actionHintCheckInput =>
      'Vihje: Tarkista syöttämäsi tiedot ja yritä uudelleen.';

  @override
  String get actionHintLoginAgain =>
      'Vihje: Tunnistautuminen vanhentui. Kirjaudu sisään uudelleen.';

  @override
  String get actionHintTryAgainLater =>
      'Vihje: Odota hetki ja yritä myöhemmin uudelleen.';

  @override
  String get actionHintContactSupport =>
      'Vihje: Jos ongelma jatkuu, ota yhteyttä ylläpitoon.';

  @override
  String get actionHintRunIngestion =>
      'Vihje: Lataa tietokantaan dokumentteja ensin.';

  @override
  String get actionHintCheckUrl =>
      'Vihje: Tarkista antamasi URL-osoitteen oikeinkirjoitus.';

  @override
  String get actionHintCheckConnection => 'Vihje: Tarkista verkkoyhteytesi.';

  @override
  String get confirmDeletionTitle => 'Vahvista Poisto';

  @override
  String get confirmDeletionMessage =>
      'Haluatko varmasti poistaa tämän suorituksen? Toimintoa ei voi peruuttaa.';

  @override
  String get executionsDashboardTitle => 'Suoritusten Hallintapaneeli';

  @override
  String get newAnalysisPipelineTitle => 'Uusi Analyysiputki (SDUI)';

  @override
  String get liveExecutionTitle => 'Aktiivinen Suoritus';

  @override
  String get establishingConnection => 'Muodostetaan yhteyttä...';

  @override
  String statusLabel(String status) {
    return 'Tila: $status';
  }

  @override
  String auditDriftWarning(String versionId) {
    return 'Audit Drift Varoitus: Tämä suoritus tehtiin järjestelmäparametreilla ($versionId), jotka poikkeavat nykyisestä aktiivisesta säännöstöstä (v2.0.0). Tuloksia tulisi tulkita varoen.';
  }

  @override
  String get noUiHintsAvailable =>
      'Ei käyttöliittymävihjeitä saatavilla vielä. Odotetaan virtaa...';

  @override
  String get executionStartedSuccessfully =>
      'Suoritus aloitettu onnistuneesti!';

  @override
  String failedToStartExecution(String error) {
    return 'Suorituksen aloittaminen epäonnistui: $error';
  }

  @override
  String get executionDeletedSuccessfully =>
      'Suoritus poistettu onnistuneesti.';

  @override
  String failedToDeleteExecution(String error) {
    return 'Suorituksen poistaminen epäonnistui: $error';
  }

  @override
  String get reportTitleMain => 'Suoritusraportti';

  @override
  String get reportMetrics => 'Suorituskykymittarit';

  @override
  String get reportScore => 'Kokonaispisteet';

  @override
  String get xAxisLabel => 'X-Akseli (Matriisi ID)';

  @override
  String get yAxisLabel => 'Y-Akseli (Matriisi ID)';

  @override
  String get zAxisLabel => 'Z-Akseli (Matriisi ID)';

  @override
  String get selectWorkflowPrompt =>
      'Valitse työnkulku luettelosta aloittaaksesi.';

  @override
  String noInputsRequired(String id) {
    return 'Ei pakollisia syötteitä putkelle \n$id';
  }

  @override
  String configureInputsFor(String id) {
    return 'Määritä syötteet putkelle $id';
  }

  @override
  String inputLabel(String key) {
    return 'Syöte: $key';
  }

  @override
  String selectedFile(String fileName) {
    return 'Valittu: $fileName';
  }

  @override
  String get noFileSelected => 'Ei valittua tiedostoa';

  @override
  String get browseFile => 'Selaa';

  @override
  String inputTypeHint(String typeHint) {
    return 'Tyyppi: $typeHint';
  }

  @override
  String questionnaireTitle(String title) {
    return 'Kysely (Questionnaire): $title';
  }

  @override
  String get startAiExecution => 'Käynnistä tekoälysuoritus';

  @override
  String get strictnessLevelTitle => 'Rajoitteiden taso (Strictness)';

  @override
  String get strictnessGricean => 'Taso 1: Yhteistyökykyinen (Gricean)';

  @override
  String get strictnessLiteral => 'Taso 2: Kirjaimellinen (Lexical)';

  @override
  String get strictnessCausal => 'Taso 3: Kausaalinen (Oletus)';

  @override
  String get strictnessFalsification => 'Taso 4: Syyttävä (Falsifikaatio)';

  @override
  String get strictnessZeroTrust => 'Taso 5: Nollaluottamus (Zero-Trust)';

  @override
  String get strictnessWarningLvl4 =>
      'Varoitus: Taso 4 on antagonistinen ja etsii virheitä. Arvosanat voivat laskea merkittävästi.';

  @override
  String get strictnessWarningLvl5 =>
      'Varoitus: Zero-Trust. Nolla pistettä, ellei ulkoisia viitteitä ja kovaa evidenssiä käytetä virheettömästi.';

  @override
  String get strictnessFullFlex => 'Täysi joustavuus (0)';

  @override
  String get strictnessLenient => 'Salliva (15)';

  @override
  String get strictnessBalanced => 'Tasapainoinen (50 - Oletus)';

  @override
  String get strictnessStrict => 'Tiukka (85)';

  @override
  String get strictnessAbsolute => 'Ehdottomuus (100)';

  @override
  String get strictnessSelectorTitle => 'Arvioinnin tiukkuus';

  @override
  String get strictnessSelectorDescription =>
      'Määritä kuinka ankarasti tekoälyn tulee noudattaa sääntöjä ja vaatia todisteita.';

  @override
  String get barsCompliance1 =>
      'Critically Misaligned - Täysin satunnainen prosessi';

  @override
  String get barsCompliance2 =>
      'Misaligned - Hajanaista prosessin noudattamista';

  @override
  String get barsCompliance3 => 'Neutral - Jonkinlainen prosessi näkyvissä';

  @override
  String get barsCompliance4 => 'Aligned - Noudattaa alan standardeja';

  @override
  String get barsCompliance5 =>
      'Strongly Aligned - Täydellinen State-of-the-Art käytäntö';

  @override
  String get barsRole1 => 'Passenger (Matkustaja) - Passiivinen tilaaja';

  @override
  String get barsRole2 => 'Navigator (Suunnistaja) - Suunnistaa datan varassa';

  @override
  String get barsRole3 => 'Driver (Kuljettaja) - Aktiivinen ohjaaja';

  @override
  String get barsRole4 => 'Architect (Arkkitehti) - Strateginen suunnittelija';

  @override
  String get barsStrategy1 => 'Zero-shot';

  @override
  String get barsStrategy2 => 'Few-shot';

  @override
  String get barsStrategy3 => 'Chain-of-Thought';

  @override
  String get barsSim1 => 'Mahdoton (Aito riippuvuus)';

  @override
  String get barsSim2 => 'Mahdollinen (Riippuvainen)';

  @override
  String get barsSim3 => 'Todennäköinen (Riippumaton)';

  @override
  String get barsConf0 => 'Täysin epävarma (0%)';

  @override
  String get barsConf25 => 'Epävarma (25%)';

  @override
  String get barsConf50 => 'Neutraali (50%)';

  @override
  String get barsConf75 => 'Melko varma (75%)';

  @override
  String get barsConf100 => 'Ehdottoman varma (100%)';

  @override
  String get barsRisk1 => 'Matala riski (Safe)';

  @override
  String get barsRisk2 => 'Keskisuuri riski (Medium)';

  @override
  String get barsRisk3 => 'Korkea riski (Lazy prompt)';

  @override
  String get rawOutputFallbackTitle => 'Raaka-data (Käyttöliittymä puuttuu)';

  @override
  String get adminAiDescriptionHint =>
      'PAKOLLINEN: On kirjoitettava englanniksi. Tämä on kognitiivinen syöte tekoälylle, ei käyttäjädataa. Syötä vain liiketoimintalogiikkaa, ÄLÄ järjestelmäsääntöjä.';

  @override
  String get adminBilingualPromptHint =>
      'PAKOLLINEN: Englanninkielinen ohjesääntö on annettava. Käytä ÄÄRIMMÄISTÄ TARKKUUTTA, sillä tämä teksti ohjaa suoraan tekoälyn kognitiivista päättelyä ja muodostaa sen ratkaisulogiikan.';

  @override
  String get adminPromptBestPracticesHint =>
      'BEST PRACTICE: Käytä englanninkielisiä komentosanoja (ROLE:, TASK:, RULE:, CONTEXT:). ÄLÄ KOSKAAN käännä näitä sanoja suomeksi ohjeen sisällä.';

  @override
  String get blueprintEditorTitle => 'Blueprint Editori';

  @override
  String get blueprintComponentsTitle => 'Komponentit';

  @override
  String get blueprintAddComponentBtn => 'Lisää Komponentti';

  @override
  String get blueprintEmptyStateMsg =>
      'Ei vielä komponentteja. Lisää komponentti aloittaaksesi tulosteen asettelun.';

  @override
  String get blueprintComponentHeader => 'Otsikko (Header)';

  @override
  String get blueprintComponentMetadataHeader => 'Metatiedot (Metadata)';

  @override
  String get blueprintComponentBibliography => 'Lähdeluettelo (Bibliography)';

  @override
  String get blueprintComponent1dGauge => '1D Mittari';

  @override
  String get blueprintComponent2dMatrix => '2D Matriisi';

  @override
  String get blueprintComponent3dScatter => '3D Hajonta';

  @override
  String get blueprintComponentEvaluationNotes => 'Arviointimuistiot';

  @override
  String get blueprintSettingsTitle => 'Komponentin Asetukset';

  @override
  String get blueprintSettingsSave => 'Tallenna Komponentti';

  @override
  String get blueprintSaveBlueprint => 'Tallenna Blueprint';

  @override
  String get blueprintSaveSuccess => 'Blueprint tallennettu onnistuneesti';

  @override
  String blueprintSaveFailed(String error) {
    return 'Blueprintin tallennus epäonnistui: $error';
  }

  @override
  String get blueprintPropertyDataPath => 'Datan Polku (\$results.X)';

  @override
  String get blueprintPropertyXAxis => 'X-akselin Polku';

  @override
  String get blueprintPropertyYAxis => 'Y-akselin Polku';

  @override
  String get blueprintPropertyZAxis => 'Z-akselin Polku';

  @override
  String get blueprintPropertyXAxisNote => 'X-akselin Huomion Polku';

  @override
  String get blueprintPropertyYAxisNote => 'Y-akselin Huomion Polku';

  @override
  String get blueprintPropertyTitle => 'Otsikko (i18n-avain tai teksti)';

  @override
  String get blueprintPropertyDataPathsInfo => 'Pilkuilla erotetut polut';

  @override
  String get downloadSuccess => 'PDF ladattu onnistuneesti';

  @override
  String get i18nAddLanguageVersion => 'Lisää kieliversio';

  @override
  String get i18nLanguageCodePlaceholder => 'Kielikoodi (esim. en, sv)';

  @override
  String get i18nLanguageCodeHelp =>
      'Tälle kielelle lisätään oma tekstikenttä.';

  @override
  String get i18nCancel => 'Peruuta';

  @override
  String get i18nCreate => 'Luo';

  @override
  String get i18nAddTranslation => 'Lisää käännös';

  @override
  String i18nDefaultFormLabel(String locale) {
    return 'Oletusmuoto (yleensä $locale)';
  }

  @override
  String get i18nOtherTranslations => 'Muut käännökset:';

  @override
  String get i18nDeleteTranslation => 'Poista käännös';

  @override
  String i18nTranslateToPlaceholder(String locale) {
    return 'Käännä kielelle $locale...';
  }

  @override
  String get workflowCloneBtn => 'Kloonaa Työnkulku';

  @override
  String get workflowCloneSuccess => 'Työnkulku kloonattu onnistuneesti';

  @override
  String get workflowCloneErrorMissingDep =>
      'Kopiointi epäonnistui: Vaiheen riippuvuus osoittaa puuttuvaan vaiheeseen.';

  @override
  String get workflowSharedBlueprintWarning =>
      'Huom! Työnkulun kloonaus luo syväkopion pääkonfiguraatiosta, mutta referenssit Steppeihin (DAG-solmuihin) PYSYVÄT SAMOINA. Steppien muutokset vaikuttavat molempiin työnkulkuihin. Haluatko kloonata?';

  @override
  String get overall_system_profile => 'Kokonaisvaltainen Profiili';

  @override
  String get blueprintSelectWorkflow => 'Valitse Työnkulku';

  @override
  String get blueprintVariantName => 'Variantin Nimi';

  @override
  String get blueprintDefaultVariant => 'oletus (default)';

  @override
  String get blueprintCopyVariant => 'Kopioi raporttipohja';

  @override
  String get blueprintGridRowLabel => 'Rinnakkainen (Grid Row)';

  @override
  String get blueprintGridRowDesc => 'Sarakkeiden määrä (Columns)';

  @override
  String blueprintChildComponents(int count) {
    return 'Rinnakkaiset lapsikomponentit ($count):';
  }

  @override
  String get blueprintAddChildBtn => 'Lisää lapsikomponentti';

  @override
  String get blueprintClearFormCache => 'Tyhjennä lomakevälimuisti';

  @override
  String get blueprintTabTitle => 'Tulosteet';

  @override
  String get blueprintTabDesc => 'Hallinnoi SDUI raporttipohjia ja tulosteita.';

  @override
  String get blueprintCreateNew => 'Luo Uusi Tuloste';

  @override
  String blueprintVariantSelector(String variant) {
    return 'Vaihtoehto: $variant';
  }

  @override
  String get reportEmptyProfile => 'Tyhjä profiili (No layout blocks defined)';

  @override
  String get reportUnknownOrg => 'Tuntematon organisaatio';

  @override
  String reportTopicProfile(String name) {
    return 'Aihe & Profiili: $name';
  }

  @override
  String reportContext(String orgName) {
    return 'Konteksti: $orgName';
  }

  @override
  String reportTimestamp(String timestamp) {
    return 'Aikaleima: $timestamp';
  }

  @override
  String get reportCosts => 'Kustannukset';

  @override
  String reportApiPrice(String price) {
    return 'API-hinta: $price';
  }

  @override
  String get reportCognitiveWork => 'Kognitiivinen työ (Tokens)';

  @override
  String get reportTextSynthesis => 'Teksti / Synteesi';

  @override
  String reportQuoteTitle(String quote) {
    return '💬 Ote alkuperäisestä tekstistä:\n$quote';
  }

  @override
  String reportSemanticExplanationTitle(String reasoning) {
    return '💡 Tekoälyn semanttinen perustelu (Kontekstuaalinen ohitus):\n$reasoning';
  }

  @override
  String reportFrameworkReference(String source) {
    return '⚖️ Viitekehys: $source';
  }

  @override
  String reportGoogleVerified(String citation) {
    return 'Tarkistettu Googlen lähteistä:\n$citation';
  }

  @override
  String get reportInteractionMatrix2D => 'Vuorovaikutusmatriisi (2D)';

  @override
  String get reportRadarAnalysis2D => 'Tutka-analyysi (2D)';

  @override
  String get reportComparisonView => 'Vertailunäkymä';

  @override
  String get reportAnalyticalFramework3D => 'Analyyttinen Viitekehys (3D)';

  @override
  String get reportAnalyticalFramework2D => 'Analyyttinen Viitekehys (2D)';

  @override
  String get reportCoachingTitle => '💡 Arjen Vinkki';

  @override
  String get reportFalsificationTitle => '⚖️ Vasta-argumentti';

  @override
  String get reportMissingContextTitle => '🔍 Puuttuva Konteksti';

  @override
  String get reportRiskFlagTitle => '⚠️ Vakava Riski Havaittu';

  @override
  String get reportRemediationStepsTitle => '🛠️ Korjaavat Toimenpiteet';

  @override
  String get reportEmotionalSentimentTitle => '🎭 Emotionaalinen Sävy';

  @override
  String get reportTheoryLinkTitle => '📚 Teoreettinen Yhteys';

  @override
  String reportConfidenceTitle(String value) {
    return 'Tekoälyn varmuus: $value%';
  }

  @override
  String get resumeActionableHint => 'Jatka ajoa (Yritä uudelleen)';

  @override
  String get failedToResume => 'Ajon jatkaminen epäonnistui.';

  @override
  String get toolExecutionFailed => 'Työkalun suoritus epäonnistui';

  @override
  String get actionHintToolFailed =>
      'Tarkista työkaluasetukset, varmista syötteen laatu tai yritä myöhemmin uudelleen.';

  @override
  String get xaiEvidenceTitle =>
      'Tekoälyn Asiantuntijalähteet (Faktantarkistus)';

  @override
  String get xaiEvidenceClaim => 'Alkuperäinen väite';

  @override
  String get xaiEvidenceQuery => 'Hakukysely';

  @override
  String get xaiEvidenceSources => 'Lähteet';

  @override
  String get xaiEvidenceDuration => 'Kesto';

  @override
  String get xaiEvidenceReasoning => 'Perustelu';

  @override
  String get stepBuilderMCPToolsTitle => 'Sallitut MCP-työkalut';

  @override
  String get stepBuilderAddTool => 'Lisää työkalu';

  @override
  String get stepBuilderToolHint =>
      'Työkalun tunniste (esim. mcp_tavily_search)';

  @override
  String get studioDashboardGatewaysTitle => 'MCP-yhdyskäytävät';

  @override
  String get studioDashboardGatewaysDesc =>
      'Hallinnoi ulkoisia työkaluja ja tekoälyn tiedonhakuintegraatioita.';

  @override
  String get mcpGatewaysTitle =>
      'XAI Raportointi / Työkaluinjektio (MCP Gateways)';

  @override
  String get mcpGatewaysDesc =>
      'Määritä järjestelmätason MCP-työkalujen yhdyskäytävät tekoälysuorituksia varten.';

  @override
  String get mcpToolSettings => 'MCP-työkalun asetukset';

  @override
  String get mcpToolIdLabel => 'Työkalun ID';

  @override
  String get mcpToolNameLabel => 'Työkalun Nimi';

  @override
  String get mcpToolDescLabel => 'Kuvaus';

  @override
  String get mcpToolInputSchemaLabel => 'Syöteskeema (JSON)';

  @override
  String get mcpAddToolBtn => 'Lisää työkalu';

  @override
  String get mcpEditToolBtn => 'Muokkaa työkalua';

  @override
  String get noMcpGatewaysDefined => 'MCP-yhdyskäytäviä ei ole määritelty.';

  @override
  String get tooltipDuplicate => 'Kopioi (Shallow-Deep Copy)';

  @override
  String get msgEntityClonedSuccess => 'Entiteetti kopioitu turvallisesti.';

  @override
  String msgEntityCloneFailed(String error) {
    return 'Kopiointi epäonnistui: $error';
  }

  @override
  String get categoryMatrix => 'Arviointimatriisi';

  @override
  String get categoryAgentRole => 'Agentin Roolipersoona';

  @override
  String get categoryTaskDefinition => 'Tehtävän Määrittely';

  @override
  String get categorySystemRule => 'Järjestelmäsääntö / Heuristiikka';

  @override
  String get categoryProtocol => 'Suoritusprotokolla';

  @override
  String get categoryRuntimeVariables => 'Ajonaikaiset muuttujat';

  @override
  String get categoryExecutionPersona => 'Suorituspersoona';

  @override
  String get technicalDetails => 'Tekniset tiedot';

  @override
  String get systemError => 'Järjestelmävirhe';

  @override
  String get signInSubtitle => 'Kirjaudu sisään jatkaaksesi';

  @override
  String get errorEmptyEmail => 'Syötä sähköpostiosoite';

  @override
  String get errorInvalidEmail => 'Virheellinen sähköpostiosoite';

  @override
  String get errorEmptyPassword => 'Syötä salasana';

  @override
  String get signInButton => 'Kirjaudu sisään';

  @override
  String executionTargetLabel(String id) {
    return 'Kohde: $id';
  }

  @override
  String get executionMetricsTitle => 'Suorituskykymittarit';

  @override
  String executionTokensBreakdown(int total, int prompt, int comp) {
    return 'Tokenit yhteensä: $total (Syöte: $prompt, Vastaus: $comp)';
  }

  @override
  String executionTokensCached(int cached) {
    return 'Säästetyt välimuistitokenit: $cached';
  }

  @override
  String executionTokensReasoning(int reasoning) {
    return 'Päättelyyn käytetyt tokenit: $reasoning';
  }

  @override
  String executionCostEstimate(String cost) {
    return 'Arvioitu hinta: \$$cost';
  }

  @override
  String workflowPrefixLabel(String name) {
    return 'Työnkulku: $name';
  }

  @override
  String get deleteExecutionTooltip => 'Poista suoritus';

  @override
  String get errSaveTimeout =>
      'Tiedoston tallennusikkuna ei vastannut (Timeout).';

  @override
  String startWorkflowTitle(String id) {
    return 'Käynnistä työnkulku: $id';
  }

  @override
  String failedToLoadSchema(String error) {
    return 'Skeeman lataaminen epäonnistui: $error';
  }

  @override
  String get navSystemInspector => 'Järjestelmätarkastaja';

  @override
  String get gatewayMetadataTitle => 'Yhdyskäytävän metatiedot';

  @override
  String get slugLabel => 'Tunniste (esim. task_guard)';

  @override
  String get allowedMcpToolsTitle => 'Sallitut MCP-työkalut';

  @override
  String get addToolButton => 'Lisää työkalu';

  @override
  String get noToolsDefinedGateway =>
      'Tälle yhdyskäytävälle ei ole määritetty työkaluja.';

  @override
  String get deleteGatewayTitle => 'Poistetaanko MCP-yhdyskäytävä?';

  @override
  String deleteGatewayConfirmation(String id) {
    return 'Haluatko varmasti poistaa yhdyskäytävän $id?';
  }

  @override
  String get cancelButton => 'Peruuta';

  @override
  String get deleteButton => 'Poista';

  @override
  String get gatewaySavedSuccess =>
      'MCP-yhdyskäytävä tallennettu onnistuneesti.';

  @override
  String saveFailedError(String error) {
    return 'Tallennus epäonnistui: $error';
  }

  @override
  String deleteFailedError(String error) {
    return 'Poistaminen epäonnistui: $error';
  }

  @override
  String toolTitlePrefix(String name) {
    return 'Työkalu: $name';
  }

  @override
  String get toolIdLabel => 'Työkalun ID (Slug)';

  @override
  String get uiDisplayNameTitle => 'Käyttöliittymän näyttönimi (I18nText)';

  @override
  String get englishNameLabel => 'Englanninkielinen nimi';

  @override
  String get finnishNameLabel => 'Suomenkielinen nimi';

  @override
  String get toolDescriptionLabel =>
      'Työkalun kuvaus (vain englanniksi kielimallille)';

  @override
  String get jsonInputSchemaLabel => 'JSON-syöteskeema';

  @override
  String get invalidJsonError => 'Virheellinen JSON';

  @override
  String get deleteConfigTitle => 'Poista konfiguraatio?';

  @override
  String deleteConfigConfirmation(String id) {
    return 'Haluatko varmasti poistaa konfiguraation $id?';
  }

  @override
  String get configSavedSuccess => 'Model Registry tallennettu onnistuneesti.';

  @override
  String get profileSavedSuccess => 'Profiili tallennettu onnistuneesti.';

  @override
  String get deleteProfileTitle => 'Poista profiili?';

  @override
  String deleteProfileConfirmation(String id) {
    return 'Haluatko varmasti poistaa profiilin $id?';
  }

  @override
  String get newOutputProfileTitle => 'Uusi tulostusprofiili';

  @override
  String get editOutputProfileTitle => 'Muokkaa tulostusprofiilia';

  @override
  String get profileIdLabel => 'Profiilin ID (esim. general_executive)';

  @override
  String get urlSlugLabel => 'URL-tunniste (esim. default)';

  @override
  String get workflowIdBindingLabel => 'Työnkulun SID-sidonta';

  @override
  String get selectWorkflowHint => 'Valitse työnkulku...';

  @override
  String get noneDefaultLabel => 'Ei mitään (Oletus)';

  @override
  String get profileDisplayNameLabel => 'Profiilin näyttönimi';

  @override
  String get profileDescriptionLabel => 'Profiilin kuvaus (valinnainen)';

  @override
  String get workflowSelectWarning =>
      '⚠️ Valitse työnkulku yläpuolelta ennen raporttipohjien muokkausta.';

  @override
  String get layoutBlocksTitle => 'Raporttipohjat';

  @override
  String get addLayoutBlockBtn => 'Lisää raportin osio';

  @override
  String get noLayoutBlocksDefined =>
      'Ei määriteltyjä osioita. Raportti on tyhjä.';

  @override
  String get presetViewLabel => 'Näkymämalli';

  @override
  String get preset1dTable => '1D Taulukko';

  @override
  String get preset2dGrid => '2D Matriisi';

  @override
  String get preset3dRadar => '3D Tutka/Kooste';

  @override
  String get presetTextOnly => 'Vain teksti/synteesi';

  @override
  String get presetAutomatic => 'Automaattinen validointi';

  @override
  String get textDeliveryModeLabel => 'Sisällön laajuus';

  @override
  String get textModeFull => 'Kaikki (Graafi, otsikot ja leipäteksti)';

  @override
  String get textModeTitlesOnly => 'Otsikot (vain graafi ja otsikot/arviot)';

  @override
  String get textModeNone => 'Supistettu (vain graafi ja yhteenveto)';

  @override
  String get layoutBlockTitleLabel => 'Raportin osion otsikko';

  @override
  String get targetComponentsTitle => 'Kohdekomponentit';

  @override
  String get componentXAxisLabel => 'Komponentti 1 (X-akseli/Ensisijainen)';

  @override
  String get componentYAxisLabel => 'Komponentti 2 (Y-akseli)';

  @override
  String get componentZAxisLabel => 'Komponentti 3 (Z-akseli)';

  @override
  String componentGenericLabel(String num) {
    return 'Komponentti $num';
  }

  @override
  String get selectAllComponentsLabel => 'Kaikki komponentit (*)';

  @override
  String get selectComponentHint => 'Valitse komponentti...';

  @override
  String get duplicateComponentError =>
      'Sama kohteen kriteeri/komponentti on valittu jo aiemmin.';

  @override
  String editProfilesTitle(String slug) {
    return 'Muokkaa profiileja: $slug';
  }

  @override
  String get outputProfilesDictionary => 'Tulostusprofiilien sanakirja';

  @override
  String get addVariantBtn => 'Lisää variantti';

  @override
  String get newProfileIdTitle => 'Uusi profiili-ID';

  @override
  String get profileIdHint => 'Profiilin ID (esim. executive)';

  @override
  String variantIdLabel(String id) {
    return 'Variantti-ID: $id';
  }

  @override
  String get reportLayoutSequenceLabel => 'Raportin asettelujärjestys';

  @override
  String get preset2dCompare => '2D Vertailu';

  @override
  String get preset3dComplex => '3D Monimutkainen';

  @override
  String get presetDefaultView => 'Oletusnäkymä';

  @override
  String get sectionTitleLabel => 'Osion otsikko (Valinnainen)';

  @override
  String get sectionDescLabel => 'Osion kuvaus (Valinnainen)';

  @override
  String get promptBlockSavedSuccess =>
      'Promptilohko tallennettu (Optimistinen).';

  @override
  String get simulatorCorruptionError =>
      'Simulaattori ei palauttanut rendered_promptia. Datassa korruptiota.';

  @override
  String get simulatorOutputTitle => 'Simulaattorin tulostus';

  @override
  String simulatorFailedError(String error) {
    return 'Simulaation virhe: $error';
  }

  @override
  String get promptBlockEditTitle => 'Muokkaa promptilohkoa';

  @override
  String promptBlockBuilderTitleId(String id) {
    return 'Rakentaja: $id';
  }

  @override
  String get promptBlockMandatoryEnglishError =>
      'Englanninkielinen otsikko on pakollinen (Englanti-Ensin Sääntö).';

  @override
  String get promptBlockConfigTitle => 'Promptilohkon konfiguraatio';

  @override
  String opaqueIdLabel(String id) {
    return 'Opaakki ID: $id';
  }

  @override
  String get promptBlockPropertiesTitle => 'Promptilohkon ominaisuudet';

  @override
  String get categoryLabel => 'Kategoria';

  @override
  String get blockLabelName => 'Lohkon otsikko (Nimi)';

  @override
  String get shortDescriptionHint => 'Lyhyt kuvaus (UI Vinkki)';

  @override
  String get systemPromptMandatory =>
      'Järjestelmäkehote / Kognitiivinen suunnitelma (PAKOLLINEN ENGLANTI)';

  @override
  String get dataTypeExecutionConstraints =>
      'Tietotyyppi ja suoritusrajoitukset';

  @override
  String get typeInstruction => 'Tekstiohje (Ei JSON Palautetta)';

  @override
  String get typeNumber => 'Numero (Numeerinen)';

  @override
  String get typeInteger => 'Kokonaisluku (Int)';

  @override
  String get allowDecimals => 'Salli desimaalit';

  @override
  String get isEvaluativeMatrix => 'Lasketaan keskiarvoon (Evaluative)';

  @override
  String get promptBlockEnsembleToggle =>
      'Käytä Fast-Model Ensemble -tekniikkaa (Paras 3:sta)';

  @override
  String get promptBlockEnsembleToggleDesc =>
      'Ajaa koko matriisin 3 kertaa rinnakkain ja hakee vastauksista enemmistöäänestyksen.';

  @override
  String get xaiOutputExtensionsTitle =>
      'XAI Ulostulolaajennukset (Proaktiivinen Valmentaja ja Raporttikentät)';

  @override
  String get xaiJustification => 'Perustelut';

  @override
  String get xaiGlobalExtensionsHeader => 'Tekoälyn havainnot';

  @override
  String get xaiCoachingTip => 'Valmennusvinkki';

  @override
  String get xaiDevilsAdvocate => 'Paholaisen asianajaja';

  @override
  String get xaiMissingContext => 'Puuttuva konteksti';

  @override
  String get xaiRiskFlag => 'Riskilippu';

  @override
  String get xaiRemediation => 'Korjaustoimenpiteet';

  @override
  String get xaiSentiment => 'Sävy';

  @override
  String get xaiTheoryLink => 'Teoriayhteys';

  @override
  String get xaiConfidence => 'AI:n Varmuus';

  @override
  String get xaiSourceCitation => 'Lähdeviite';

  @override
  String get xaiContextualOverride => 'Kontekstuaalinen ohitus';

  @override
  String get xaiSourceId => 'Lähde-ID';

  @override
  String get theoryGroundingTitle => 'Teorian Maadoitus (RAG)';

  @override
  String get sourceUrlLabel => 'Lähde-URL (esim. jstor.org/...)';

  @override
  String get citationReferenceLabel => 'Viittaus (esim. Kahnamen, 2011)';

  @override
  String get gridRowsOptional => 'Ruudukon rivit (Valinnainen)';

  @override
  String get gridColumnsOptional => 'Ruudukon sarakkeet (Valinnainen)';

  @override
  String get addGridItemBtn => 'Lisää kohde';

  @override
  String get barsScalesTitle => 'BARS Skaalat / Arvosanat';

  @override
  String get addGradeBtn => 'Lisää arvosana';

  @override
  String get scaleMinLabel => 'Skaalan Min (esim. 4)';

  @override
  String get scaleMaxLabel => 'Skaalan Max (esim. 10)';

  @override
  String claimsCountLabel(String count) {
    return '$count Väittämää';
  }

  @override
  String gradeScoreLabel(String score, String name) {
    return 'Arvosana/Pisteet: $score $name';
  }

  @override
  String get closeModalBtn => 'Sulje';

  @override
  String get studioSaveSuccess => 'Tallennettu onnistuneesti';

  @override
  String get stepSavedSuccess => 'Askel tallennettu (Optimistinen).';

  @override
  String get stepEditTitle => 'Muokkaa askeletta';

  @override
  String get simulateStepTooltip => 'Simuloi askeletta';

  @override
  String get idRequiredError => 'ID on pakollinen.';

  @override
  String get configurationTitle => 'Konfiguraatio';

  @override
  String get nameLabel => 'Nimi';

  @override
  String get descriptionLabel => 'Kuvaus';

  @override
  String get preHooksTitle => 'Pre Hooks (Ennen suoritusta)';

  @override
  String get postHooksTitle => 'Post Hooks (Suorituksen jälkeen)';

  @override
  String get addHookBtn => 'Lisää Hook';

  @override
  String get preHookEngineLabel => 'Pre-Execution Hook Moottori';

  @override
  String get postHookEngineLabel => 'Post-Execution Hook Moottori';

  @override
  String get hookWaterfall => 'Waterfall Pisteytys (waterfall_scoring_hook)';

  @override
  String get hookNormalize =>
      'Matriisien Normalisointi (normalize_matrix_scores)';

  @override
  String get hookVerifyCitation =>
      'Lähdeviittausten Varmistus (verify_citation_integrity)';

  @override
  String get hookHypothesis =>
      'Oletusten Linkitys (enforce_hypothesis_linking)';

  @override
  String get hookTavily => 'Tavily Web Haku (search_hook)';

  @override
  String get hookMemory => 'Kontekstuaalinen Muisti (memory_hook)';

  @override
  String get hookValidation => 'Tarkka Validointi (validation_hook)';

  @override
  String get hookScore => 'Arvostelumetriikka (score_hook)';

  @override
  String hookLegacy(String name) {
    return 'Legacy: $name';
  }

  @override
  String get promptBlocksTitle => 'Promptilohkot';

  @override
  String get addPromptBlockBtn => 'Lisää promptilohko';

  @override
  String get promptBlockLabel => 'Promptilohko';

  @override
  String get workflowSavedSuccess => 'Työnkulku tallennettu onnistuneesti.';

  @override
  String get simulatorValidDag => 'DAG on validi!';

  @override
  String simulatorDagErrors(String errors) {
    return 'DAG Virheet: $errors';
  }

  @override
  String get workflowNameMissingError =>
      'Työnkulun nimi puuttuu olemassaolevalta työnkululta.';

  @override
  String get validateDagBtn => 'Validoi DAG';

  @override
  String get workflowTabGeneral => '1. Yleiset & Tulosteet';

  @override
  String get workflowTabInputs => '2. Syötteet';

  @override
  String get workflowTabSteps => '3. Stepit & Riippuvuudet';

  @override
  String errNavigationFallback(String uri) {
    return 'Navigointivirhe: $uri ei löytynyt. Palataan työtilaan...';
  }

  @override
  String get studioWorkflowIdOpaque =>
      'Opaque Workflow ID (Järjestelmän luoma)';

  @override
  String get studioWorkflowSlugSemantic =>
      'Semanttinen reititys (esim. audit-master)';

  @override
  String get studioWorkflowIdentity => 'Työnkulun identiteetti';

  @override
  String get studioWorkflowNameLabel => 'Työnkulun nimi';

  @override
  String get studioWorkflowDescEnLabel => 'Kuvaus (EN)';

  @override
  String get studioWorkflowDescFiLabel => 'Kuvaus (FI)';

  @override
  String get studioWorkflowGlobalSettings => 'Globaalit suoritusasetukset';

  @override
  String get studioWorkflowDefaultProfile => 'Oletusprofiili (Fallback)';

  @override
  String get studioWorkflowInputsEmpty =>
      'Odotettuja syötteitä ei ole määritetty.';

  @override
  String studioWorkflowStepCount(int count) {
    return 'Vaihe $count';
  }

  @override
  String get studioWorkflowNodeIdOpaque => 'Solmun ID (Opaque Stripe Pattern)';

  @override
  String get studioWorkflowTaskBlueprint =>
      'Tehtävän Blueprint (Cognitive Engine)';

  @override
  String get studioWorkflowXaiReporting =>
      'XAI-raportointi / Työkalut (MCP Gateways):';

  @override
  String get studioWorkflowDependsOn =>
      'Riippuvuudet (Suoritetaan NÄIDEN jälkeen):';

  @override
  String get studioWorkflowNoDependencies =>
      'Ei aiempia vaiheita joista riippua.';

  @override
  String get studioWorkflowInputMappings =>
      'Syötekartoitukset (Tilan injektointi):';

  @override
  String get studioWorkflowTargetArgName => 'Kohdeargumentti';

  @override
  String get studioWorkflowSourceToken =>
      'Lähdetoken (esim. \\\$inputs, step_1)';

  @override
  String get studioWorkflowStepsNoInputsMappingWarning =>
      'Virhe: Mappaamattomia syötteitä löytyi.';

  @override
  String get studioWorkflowStepsInputMappingTitle =>
      'Syötemappaus (Ulkoinen -> Sisäinen)';

  @override
  String get studioWorkflowStepsAddMappingBtn => 'Lisää mappaus';

  @override
  String get studioWorkflowStepsDataMissingText =>
      'Hetkinen, data-objekti puuttuu?';

  @override
  String get studioWorkflowStepsNoTargetComponents => 'Ei valittuja';

  @override
  String get studioViewsBlueprintRulesTitle =>
      'Tulostusmäppäys (Esityssäännöt)';

  @override
  String get studioViewsPresetViewTheme => 'Esikatseluteema';

  @override
  String get studioViews1dMetricsList => '1D Mittaristo';

  @override
  String get studioViews2dCompare => '2D Vertailu';

  @override
  String get studioViews3dComplex => '3D Moniulotteinen';

  @override
  String studioViewsFailedToClone(String error) {
    return 'Kloonaus epäonnistui: $error';
  }

  @override
  String get studioViewsNewMatrix => 'Uusi matriisi';

  @override
  String studioViewsErrorLoadingWorkflows(String error) {
    return 'Virhe työnkulkujen latauksessa: $error';
  }

  @override
  String get studioViewsProfileIdRequired => 'Profiilin ID on pakollinen';

  @override
  String studioViewsErrorLoadingBlocks(String error) {
    return 'Virhe lohkojen latauksessa: $error';
  }

  @override
  String get studioViewsOutputProfilesMasterTitle =>
      'Tulostusprofiilit (Output Profiles)';

  @override
  String get studioViewsNewProfileBtn => 'Uusi profiili';

  @override
  String get studioViewsNoOutputProfiles =>
      'Tulostusprofiileja ei ole määritetty.';

  @override
  String get studioViewsUnnamedProfile => 'Nimetön profiili';

  @override
  String studioViewsProfileListSubtitle(
    String id,
    String workflow,
    int layouts,
  ) {
    return 'ID: $id | Työnkulku: $workflow | $layouts Asettelulohkoa';
  }

  @override
  String get studioViewsNone => 'Ei mikään';

  @override
  String get studioViewsAddBtn => 'Lisää';

  @override
  String get studioViewsWarningNoModels => 'Varoitus: Malleja ei löytynyt.';

  @override
  String get studioViewsModelStrategyLabel =>
      'Tekoälymalli (Kustannus/Kognitio ohitus)';

  @override
  String get studioViewsAdminStudioV2 => 'Admin Studio V2';

  @override
  String get studioViewsPromptBlocksTab => 'Kehotteet (Blocks)';

  @override
  String get studioViewsStepsTab => 'Askeleet';

  @override
  String get studioViewsProfilesTab => 'Profiilit';

  @override
  String get studioViewsPromptBlocksStandard => 'Kehotteet (Standard)';

  @override
  String get studioViewsNoStandardPromptBlocks =>
      'Ei peruskehotteita määritetty.';

  @override
  String studioViewsSlugSubtitle(String slug) {
    return 'Tunnus: $slug';
  }

  @override
  String get studioViewsNoMatricesDefined => 'Ei matriiseja määritetty.';

  @override
  String get studioViewsNoStepsDefined => 'Ei askelia määritetty.';

  @override
  String studioViewsStepsSubtitle(int blocks, int hooks) {
    return 'Lohkot: $blocks | Koukut: $hooks';
  }

  @override
  String get studioViewsNoSystemConfigs =>
      'Järjestelmäasetuksia ei ole määritetty.';

  @override
  String studioViewsConfiguredModels(int count) {
    return 'Konfiguroidut mallit: $count';
  }

  @override
  String get studioViewsNewBtn => 'Uusi';

  @override
  String get studioViewsWorkflowBuilderTitle =>
      'Työnkulkurakentaja (Workflow Builder)';

  @override
  String get studioViewsNewWorkflowBtn => 'Uusi työnkulku';

  @override
  String get studioViewsWorkflowBuilderDesc =>
      'Hallitse työnkulkujen pääsuunnitelmia (DAG), jotka määrittelevät agenttien reitityksen, syötteet ja strategiat.';

  @override
  String get studioViewsNoWorkflowsConfigured =>
      'Ei työnkulkuja konfiguroituna.';

  @override
  String studioViewsWorkflowSubtitle(String id, int nodes, String status) {
    return 'ID: $id | Solmut: $nodes | Tila: $status';
  }

  @override
  String get studioWorkflowAddMappingBtn => 'Lisää kartoitus';

  @override
  String get studioWorkflowStepsDependencies => 'Vaiheet & Riippuvuudet';

  @override
  String get studioWorkflowAddStepNodeBtn => 'Lisää askelsolmu';

  @override
  String get studioWorkflowStepsEmpty =>
      'Ei askeleita määritettynä. Lisää solmu aloittaaksesi orkestraatiograafin rakentamisen.';

  @override
  String get studioViewsMatricesDescription =>
      'Hallitse järjestelmän arviointimatriiseja.';

  @override
  String get studioViewsNoMatricesAvailable => 'Matriiseja ei ole saatavilla.';

  @override
  String get studioViewsMatrixCloned => 'Matriisi kloonattu onnistuneesti.';

  @override
  String get sharedNoTimelineData => 'Aikajanadataa ei ole saatavilla.';

  @override
  String get sharedNoReportData => 'Raporttidataa ei ole saatavilla.';

  @override
  String get sharedFlatReportNoData =>
      'Flat Report dataa ei löytynyt tästä ajosta.';

  @override
  String get sharedAnalysisPerformed => 'Analyysi suoritettu: ';

  @override
  String get sharedNoComparisonData => 'Vertailudataa ei ole saatavilla.';

  @override
  String get sharedMoreInfoTooltip => 'Lisätietoa';

  @override
  String get sharedOk => 'OK';

  @override
  String get sharedUploading => 'Ladataan...';

  @override
  String get sharedSelectFile => 'Valitse tiedosto...';

  @override
  String get sharedSystemError => 'Järjestelmävirhe';

  @override
  String get sharedUnknownAgent => 'Tuntematon Agentti';

  @override
  String get sharedUnknown => 'Tuntematon';

  @override
  String get studioWorkflowAllInputsCombined =>
      'Kaikki alkuperäiset syötteet yhdistettynä (\$inputs)';

  @override
  String get studioWorkflowAllStepsCombined =>
      'Kaikki aiemmat vaiheet yhdistettynä (\$steps)';

  @override
  String get profileDisplayScaleLabel => 'Tulosteen skaalauslähde';

  @override
  String get scaleOriginal => 'Alkuperäinen matriisiarvo (Oletus)';

  @override
  String get scaleCustom => 'Custom laskutoimitus (Hook)';

  @override
  String get scaleNormalized100 => 'Prosentuaalinen (0 - 100)';

  @override
  String get synConfigTitle => 'Synteesi- ja vientiasetukset';

  @override
  String get synPreambleLabel => 'Alkuteksti (Preamble)';

  @override
  String get synMaxLengthLabel => 'Pituuden enimmäisraja';

  @override
  String get synMaxLengthHelper => 'Jätä tyhjäksi, jos ei rajaa';

  @override
  String get synEnablePii => 'Ota PII-maskaus käyttöön';

  @override
  String get synEnablePiiHelper =>
      'Varmista henkilötietojen maskaus ennen LLM-kutsua';

  @override
  String get synIncludeHistory => 'Sisällytä historiallinen yhteenveto';

  @override
  String get synOmitEmpty => 'Jätä tyhjät osiot pois';

  @override
  String get synAllowedExports => 'Sallitut vientimuodot';

  @override
  String get profileEditorVisibleExtensions => 'Näytettävät XAI-laajennukset';

  @override
  String get profileEditorMaxExtensionItems =>
      'Maksimimäärä per XAI-laajennus (Top X)';

  @override
  String get profileEditorMaxExtensionItemsDesc =>
      'Rajoittaa kuinka monta kriteeriä näytetään per osio (lajiteltu kriittisyyden mukaan).';

  @override
  String get reportExecutiveSummary => 'Yhteenveto';

  @override
  String reportPromptTokens(String count) {
    return 'Syöte: $count';
  }

  @override
  String reportCompletionTokens(String count) {
    return 'Vastaus: $count';
  }

  @override
  String reportReasoningTokens(String count) {
    return 'Päättely: $count';
  }

  @override
  String get strategyKoearvostelu => 'Koearvostelu';

  @override
  String get strategySyvaarvostelu => 'Syväarvostelu';

  @override
  String get strategyLineaarinenKeskiarvo => 'Lineaarinen Keskiarvo';

  @override
  String get strategyPainotettuKeskiarvo => 'Painotettu Keskiarvo';

  @override
  String get strategyPuhdasMatematiikka => 'Puhdas Matematiikka';

  @override
  String get allowContextualOverrideLabel => 'Salli kognitiivinen ohitus';

  @override
  String get allowContextualOverrideDescription =>
      'Sallii LLM:lle perustellun semanttisen hyväksynnän ilman kirjaimellista lainausta, jos tarkkaa tekstiä ei ole fyysisiä todisteita varten olemassa.';

  @override
  String get enableContextualOverridesLabel =>
      'Kognitiiviset ohitukset käytössä';

  @override
  String get enableContextualOverridesDescription =>
      'Master-kytkin, joka sallii tai kieltää väitetasoiset semanttiset ohitukset koko tämän työnkulun ajon aikana.';

  @override
  String get roleBlockLabel => 'Tekoälyn roolipersoona';

  @override
  String get roleBlockDescription =>
      'Valitse tekoälyn asenne (esim. blk_role_critic).';

  @override
  String get protocolBlockLabel => 'Evidenssin poimintaprotokolla';

  @override
  String get protocolBlockDescription =>
      'Mekaaniset säännöt sokeaan matemaattiseen poimintaan.';

  @override
  String get criteriaBlocksTitle => 'Arvioitavat kriteerilohkot';

  @override
  String get criteriaBlocksDescription =>
      'Spesifit domain-tason arviointikriteerit.';

  @override
  String get xaiVarianceValidationTitle =>
      '🤖 VARIAATIO (KOGNITIIVINEN VS. MEKAANINEN)';

  @override
  String get xaiVerdictAligned => '✅ Yhdenmukainen';

  @override
  String get xaiVerdictSycophancy => '❌ Mielistelyharha';

  @override
  String get xaiVerdictMisaligned => '⚠️ Looginen ristiriita';

  @override
  String get xaiVarianceBarAligned => 'Yhdenmukainen';

  @override
  String get xaiVarianceBarMild => 'Lievä poikkeama';

  @override
  String get xaiVarianceBarSevere => 'Vakava poikkeama';

  @override
  String get xaiVarianceInfoText =>
      'Tämä mittari paljastaa, onko tekoälyn oma arvio suorituksestaan (kognitiivinen) ristiriidassa kylmien faktojen (mekaaninen skannaus) kanssa. Esimerkiksi: Jos tekoäly väittää kirjoittaneensa täydellistä asiatekstiä, mutta järjestelmä löytää tekstistä silti paljon tekoäly-jargonia, syntyy ristiriita.';

  @override
  String get tdaAnchorTarget => 'Ankkurikohde';

  @override
  String get tdaBoundingBox => 'Hakuikkunan Laajuus';

  @override
  String get tdaExtractionRule => 'Poiminnan Sääntö';

  @override
  String get systemAuditTrailLabel => 'Järjestelmän Faktantarkistusloki';

  @override
  String get systemAuditTrailDescription =>
      'Ottaa käyttöön MCPAuditTrace -pohjaisen faktantarkistusraportin loppuun.';

  @override
  String get workflowInputScanPerformative => 'Skannaa AI-jargonia (Aitous)';

  @override
  String get xaiAuthenticityEvaluationTitle => 'Lähdedatan aitous (AI-jargon)';

  @override
  String penaltySecurity(String percentage) {
    return 'Turvallisuusuhka havaittu (-$percentage%)';
  }

  @override
  String penaltyPostHoc(String percentage) {
    return 'Jälkikäteinen perustelu havaittu (-$percentage%)';
  }

  @override
  String penaltySlop(String phrases) {
    return '-5% Slop-rangaistus (Tekoäly-jargon): havaittu $phrases';
  }

  @override
  String get reject_quote_title => 'Hylkää todiste';

  @override
  String get reject_quote_confirm =>
      'Haluatko varmasti hylätä tämän todisteen?';

  @override
  String get quote_rejected_warning =>
      'Varoitus: Kaikki havainnon todisteet on hylätty.';

  @override
  String get reject_quote_reason_hint => 'Valinnainen: Hylkäyksen syy';

  @override
  String lblNaCascadeReason(String reasons) {
    return 'N/A Kaskadisyyt: $reasons';
  }
}
