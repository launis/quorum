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
  String get selectFile => 'Valitse tiedosto...';

  @override
  String get fieldRequired => 'Tämä kenttä on pakollinen.';

  @override
  String get fileRequired => 'Tämä tiedosto on pakollinen.';

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
  String get executionDetails => 'Suorituksen tiedot';

  @override
  String get overview => 'Yleiskatsaus';

  @override
  String get report => 'Raportti';

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
  String get statusRunning => 'KÄYNNISSÄ';

  @override
  String get statusFailed => 'EPÄONNISTUI';

  @override
  String get statusRejected => 'HYLÄTTY';

  @override
  String get statusPending => 'ODOTTAA';

  @override
  String get statusStarted => 'ALOITETTU';

  @override
  String get inputChatHistory => '1. Keskusteluhistoria / Todistusaineisto';

  @override
  String get inputProductTarget => '2. Tuotos / Arvioinnin kohde';

  @override
  String get inputReflection => '3. Reflektio / Itsearviointi';

  @override
  String get unknownWorkflow => 'Tuntematon työnkulku';

  @override
  String get navDashboard => 'Etusivu';

  @override
  String get navSettings => 'Asetukset';

  @override
  String get navAdmin => 'Ylläpito';

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
  String get downloadNotImplementedPdf => 'PDF-lataus ei vielä käytössä';

  @override
  String get chooseAnalysisType => 'Valitse analyysin tyyppi';
}
