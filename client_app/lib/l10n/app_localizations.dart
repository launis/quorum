import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_fi.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
    : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
        delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
      ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('fi'),
  ];

  /// The title of the application
  ///
  /// In en, this message translates to:
  /// **'Cognitive Quorum Client'**
  String get appTitle;

  /// Text for the login button
  ///
  /// In en, this message translates to:
  /// **'Login'**
  String get loginBtn;

  /// Label for the admin panel
  ///
  /// In en, this message translates to:
  /// **'Admin Panel'**
  String get adminPanel;

  /// No description provided for @settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @themeMode.
  ///
  /// In en, this message translates to:
  /// **'Theme Mode'**
  String get themeMode;

  /// No description provided for @system.
  ///
  /// In en, this message translates to:
  /// **'System'**
  String get system;

  /// No description provided for @light.
  ///
  /// In en, this message translates to:
  /// **'Light'**
  String get light;

  /// No description provided for @dark.
  ///
  /// In en, this message translates to:
  /// **'Dark'**
  String get dark;

  /// Header for input configuration screen
  ///
  /// In en, this message translates to:
  /// **'Configure Inputs: {workflowId}'**
  String configureInputs(String workflowId);

  /// Label for generic text input
  ///
  /// In en, this message translates to:
  /// **'General Input'**
  String get generalInput;

  /// Label showing selected file details
  ///
  /// In en, this message translates to:
  /// **'File: {fileName} ({size} bytes)'**
  String fileInputLabel(String fileName, int size);

  /// Placeholder text for file picker
  ///
  /// In en, this message translates to:
  /// **'Select a file...'**
  String get selectFile;

  /// Validation error message
  ///
  /// In en, this message translates to:
  /// **'This field is required.'**
  String get fieldRequired;

  /// Validation error message for files
  ///
  /// In en, this message translates to:
  /// **'This file is required.'**
  String get fileRequired;

  /// No description provided for @dashboardTitle.
  ///
  /// In en, this message translates to:
  /// **'Recent Logic Executions'**
  String get dashboardTitle;

  /// No description provided for @totalRuns.
  ///
  /// In en, this message translates to:
  /// **'Total Runs'**
  String get totalRuns;

  /// No description provided for @inProgress.
  ///
  /// In en, this message translates to:
  /// **'In Progress'**
  String get inProgress;

  /// No description provided for @criticalFailures.
  ///
  /// In en, this message translates to:
  /// **'Critical Failures'**
  String get criticalFailures;

  /// No description provided for @noExecutions.
  ///
  /// In en, this message translates to:
  /// **'No executions found.'**
  String get noExecutions;

  /// No description provided for @failedToLoad.
  ///
  /// In en, this message translates to:
  /// **'Failed to load executions: {error}'**
  String failedToLoad(Object error);

  /// No description provided for @retry.
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get retry;

  /// No description provided for @newAnalysis.
  ///
  /// In en, this message translates to:
  /// **'New Analysis'**
  String get newAnalysis;

  /// No description provided for @executionDetails.
  ///
  /// In en, this message translates to:
  /// **'Execution Details'**
  String get executionDetails;

  /// No description provided for @overview.
  ///
  /// In en, this message translates to:
  /// **'Overview'**
  String get overview;

  /// No description provided for @report.
  ///
  /// In en, this message translates to:
  /// **'Report'**
  String get report;

  /// No description provided for @rawData.
  ///
  /// In en, this message translates to:
  /// **'Raw Data'**
  String get rawData;

  /// No description provided for @status.
  ///
  /// In en, this message translates to:
  /// **'STATUS'**
  String get status;

  /// No description provided for @timeline.
  ///
  /// In en, this message translates to:
  /// **'Timeline'**
  String get timeline;

  /// No description provided for @created.
  ///
  /// In en, this message translates to:
  /// **'Created'**
  String get created;

  /// No description provided for @workflowProgress.
  ///
  /// In en, this message translates to:
  /// **'Workflow Progress'**
  String get workflowProgress;

  /// No description provided for @analysisInProgress.
  ///
  /// In en, this message translates to:
  /// **'Analysis in progress...'**
  String get analysisInProgress;

  /// No description provided for @currentStep.
  ///
  /// In en, this message translates to:
  /// **'Current Step: {step}'**
  String currentStep(Object step);

  /// No description provided for @waitingToStart.
  ///
  /// In en, this message translates to:
  /// **'Waiting to start...'**
  String get waitingToStart;

  /// No description provided for @executionStarted.
  ///
  /// In en, this message translates to:
  /// **'Execution Started...'**
  String get executionStarted;

  /// No description provided for @executionFailed.
  ///
  /// In en, this message translates to:
  /// **'Execution Failed: {error}'**
  String executionFailed(Object error);

  /// No description provided for @unknownState.
  ///
  /// In en, this message translates to:
  /// **'Unknown State'**
  String get unknownState;

  /// No description provided for @downloadNotImplemented.
  ///
  /// In en, this message translates to:
  /// **'Download not implemented yet'**
  String get downloadNotImplemented;

  /// No description provided for @detailsComingSoon.
  ///
  /// In en, this message translates to:
  /// **'Details view coming soon...'**
  String get detailsComingSoon;

  /// No description provided for @viewChecklist.
  ///
  /// In en, this message translates to:
  /// **'View Checklist'**
  String get viewChecklist;

  /// No description provided for @viewRawData.
  ///
  /// In en, this message translates to:
  /// **'View Raw Data'**
  String get viewRawData;

  /// No description provided for @analysisResults.
  ///
  /// In en, this message translates to:
  /// **'Analysis Results'**
  String get analysisResults;

  /// No description provided for @goToMonitor.
  ///
  /// In en, this message translates to:
  /// **'Go to Monitor'**
  String get goToMonitor;

  /// No description provided for @analysisNotComplete.
  ///
  /// In en, this message translates to:
  /// **'Analysis is not complete yet.'**
  String get analysisNotComplete;

  /// No description provided for @verdict.
  ///
  /// In en, this message translates to:
  /// **'Verdict'**
  String get verdict;

  /// No description provided for @score.
  ///
  /// In en, this message translates to:
  /// **'Score'**
  String get score;

  /// No description provided for @summary.
  ///
  /// In en, this message translates to:
  /// **'Summary'**
  String get summary;

  /// No description provided for @type.
  ///
  /// In en, this message translates to:
  /// **'Type'**
  String get type;

  /// No description provided for @inputs.
  ///
  /// In en, this message translates to:
  /// **'Inputs'**
  String get inputs;

  /// No description provided for @startAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Start Analysis'**
  String get startAnalysis;

  /// No description provided for @next.
  ///
  /// In en, this message translates to:
  /// **'Next'**
  String get next;

  /// No description provided for @back.
  ///
  /// In en, this message translates to:
  /// **'Back'**
  String get back;

  /// No description provided for @cancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancel;

  /// No description provided for @analysisStarted.
  ///
  /// In en, this message translates to:
  /// **'Analysis Started!'**
  String get analysisStarted;

  /// No description provided for @submissionFailed.
  ///
  /// In en, this message translates to:
  /// **'Submission Failed: {error}'**
  String submissionFailed(Object error);

  /// No description provided for @fillRequiredInputs.
  ///
  /// In en, this message translates to:
  /// **'Please fill in required inputs.'**
  String get fillRequiredInputs;

  /// No description provided for @errorReadingFile.
  ///
  /// In en, this message translates to:
  /// **'Error reading file: {error}'**
  String errorReadingFile(Object error);

  /// No description provided for @noWorkflowsAvailable.
  ///
  /// In en, this message translates to:
  /// **'No workflows available for your account.'**
  String get noWorkflowsAvailable;

  /// No description provided for @enterCustomWorkflowId.
  ///
  /// In en, this message translates to:
  /// **'Or enter Custom Workflow ID'**
  String get enterCustomWorkflowId;

  /// No description provided for @statusCompleted.
  ///
  /// In en, this message translates to:
  /// **'COMPLETED'**
  String get statusCompleted;

  /// No description provided for @statusRunning.
  ///
  /// In en, this message translates to:
  /// **'RUNNING'**
  String get statusRunning;

  /// No description provided for @statusFailed.
  ///
  /// In en, this message translates to:
  /// **'FAILED'**
  String get statusFailed;

  /// No description provided for @statusRejected.
  ///
  /// In en, this message translates to:
  /// **'REJECTED'**
  String get statusRejected;

  /// No description provided for @statusPending.
  ///
  /// In en, this message translates to:
  /// **'PENDING'**
  String get statusPending;

  /// No description provided for @statusStarted.
  ///
  /// In en, this message translates to:
  /// **'STARTED'**
  String get statusStarted;

  /// No description provided for @inputChatHistory.
  ///
  /// In en, this message translates to:
  /// **'1. Chat History / Evidence (Chat Logs)'**
  String get inputChatHistory;

  /// No description provided for @inputProductTarget.
  ///
  /// In en, this message translates to:
  /// **'2. Product / Evaluation Target (Final Product)'**
  String get inputProductTarget;

  /// No description provided for @inputReflection.
  ///
  /// In en, this message translates to:
  /// **'3. Reflection / Self-Evaluation'**
  String get inputReflection;

  /// No description provided for @unknownWorkflow.
  ///
  /// In en, this message translates to:
  /// **'Unknown Workflow'**
  String get unknownWorkflow;

  /// No description provided for @navDashboard.
  ///
  /// In en, this message translates to:
  /// **'Dashboard'**
  String get navDashboard;

  /// No description provided for @navSettings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get navSettings;

  /// No description provided for @navAdmin.
  ///
  /// In en, this message translates to:
  /// **'Admin'**
  String get navAdmin;

  /// No description provided for @stepLabel.
  ///
  /// In en, this message translates to:
  /// **'Step: {stepName}'**
  String stepLabel(Object stepName);

  /// No description provided for @defaultWorkflowTitle.
  ///
  /// In en, this message translates to:
  /// **'Workflow Execution'**
  String get defaultWorkflowTitle;

  /// No description provided for @executionIdLabel.
  ///
  /// In en, this message translates to:
  /// **'Execution {id}'**
  String executionIdLabel(Object id);

  /// No description provided for @resultsTitle.
  ///
  /// In en, this message translates to:
  /// **'Analysis Results'**
  String get resultsTitle;

  /// No description provided for @viewLogTooltip.
  ///
  /// In en, this message translates to:
  /// **'View Execution Log'**
  String get viewLogTooltip;

  /// No description provided for @downloadReportTooltip.
  ///
  /// In en, this message translates to:
  /// **'Download Report'**
  String get downloadReportTooltip;

  /// No description provided for @downloadNotImplementedPdf.
  ///
  /// In en, this message translates to:
  /// **'Download PDF not implemented yet'**
  String get downloadNotImplementedPdf;

  /// No description provided for @chooseAnalysisType.
  ///
  /// In en, this message translates to:
  /// **'Choose Analysis Type'**
  String get chooseAnalysisType;

  /// No description provided for @usageCurrentMonth.
  ///
  /// In en, this message translates to:
  /// **'Current Month Usage'**
  String get usageCurrentMonth;

  /// No description provided for @usageQuota.
  ///
  /// In en, this message translates to:
  /// **'Usage vs Quota'**
  String get usageQuota;

  /// No description provided for @tokensUsed.
  ///
  /// In en, this message translates to:
  /// **'{count} Tokens Used'**
  String tokensUsed(int count);

  /// No description provided for @quotaLimit.
  ///
  /// In en, this message translates to:
  /// **'{limit} Limit'**
  String quotaLimit(int limit);

  /// No description provided for @selectWorkflowRequired.
  ///
  /// In en, this message translates to:
  /// **'Please select a workflow.'**
  String get selectWorkflowRequired;

  /// No description provided for @adminDashboardTitle.
  ///
  /// In en, this message translates to:
  /// **'Admin Dashboard'**
  String get adminDashboardTitle;

  /// No description provided for @welcomeAdmin.
  ///
  /// In en, this message translates to:
  /// **'Welcome to Admin Dashboard'**
  String get welcomeAdmin;

  /// No description provided for @manageUsersButton.
  ///
  /// In en, this message translates to:
  /// **'Manage Users'**
  String get manageUsersButton;

  /// No description provided for @manageOrganizationsButton.
  ///
  /// In en, this message translates to:
  /// **'Manage Organizations'**
  String get manageOrganizationsButton;

  /// No description provided for @userManagementTitle.
  ///
  /// In en, this message translates to:
  /// **'User Management'**
  String get userManagementTitle;

  /// No description provided for @organizationManagementTitle.
  ///
  /// In en, this message translates to:
  /// **'Organization Management'**
  String get organizationManagementTitle;

  /// No description provided for @userListPlaceholder.
  ///
  /// In en, this message translates to:
  /// **'User Management List Placeholder'**
  String get userListPlaceholder;

  /// No description provided for @organizationListPlaceholder.
  ///
  /// In en, this message translates to:
  /// **'Organization List Placeholder'**
  String get organizationListPlaceholder;

  /// No description provided for @systemSettingsTitle.
  ///
  /// In en, this message translates to:
  /// **'System Settings'**
  String get systemSettingsTitle;

  /// No description provided for @monitorTitle.
  ///
  /// In en, this message translates to:
  /// **'Monitor: {id}'**
  String monitorTitle(String id);

  /// No description provided for @viewResults.
  ///
  /// In en, this message translates to:
  /// **'View Results'**
  String get viewResults;

  /// No description provided for @analysisCompletedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Analysis Completed Successfully!'**
  String get analysisCompletedSuccess;

  /// No description provided for @viewFullReport.
  ///
  /// In en, this message translates to:
  /// **'View Full Report'**
  String get viewFullReport;

  /// No description provided for @viewRawDataComingSoon.
  ///
  /// In en, this message translates to:
  /// **'View Raw Data (Coming Soon)'**
  String get viewRawDataComingSoon;

  /// No description provided for @stepGuard.
  ///
  /// In en, this message translates to:
  /// **'Guard Agent (Safety)'**
  String get stepGuard;

  /// No description provided for @stepAnalyst.
  ///
  /// In en, this message translates to:
  /// **'Analyst Agent (Research)'**
  String get stepAnalyst;

  /// No description provided for @stepInteraction.
  ///
  /// In en, this message translates to:
  /// **'Interaction Analyst'**
  String get stepInteraction;

  /// No description provided for @stepProfiler.
  ///
  /// In en, this message translates to:
  /// **'Profiler Agent'**
  String get stepProfiler;

  /// No description provided for @stepPanel.
  ///
  /// In en, this message translates to:
  /// **'Panel Audit (Parallel)'**
  String get stepPanel;

  /// No description provided for @stepArchivist.
  ///
  /// In en, this message translates to:
  /// **'Archivist (History)'**
  String get stepArchivist;

  /// No description provided for @stepJudge.
  ///
  /// In en, this message translates to:
  /// **'Judge (Verdict)'**
  String get stepJudge;

  /// No description provided for @stepCoach.
  ///
  /// In en, this message translates to:
  /// **'Coach (Feedback)'**
  String get stepCoach;

  /// No description provided for @stepReporter.
  ///
  /// In en, this message translates to:
  /// **'Reporter (Final Report)'**
  String get stepReporter;

  /// No description provided for @stepInitializing.
  ///
  /// In en, this message translates to:
  /// **'Initializing...'**
  String get stepInitializing;

  /// Validation error for missing evidence fields
  ///
  /// In en, this message translates to:
  /// **'Missing required evidence: {fields}'**
  String validationMissingEvidence(String fields);

  /// No description provided for @validationInputEmpty.
  ///
  /// In en, this message translates to:
  /// **'Inputs cannot be empty.'**
  String get validationInputEmpty;

  /// No description provided for @errorUnknown.
  ///
  /// In en, this message translates to:
  /// **'Unknown error occurred.'**
  String get errorUnknown;

  /// No description provided for @errorNetwork.
  ///
  /// In en, this message translates to:
  /// **'Network error. Please check your connection.'**
  String get errorNetwork;

  /// No description provided for @errorServer.
  ///
  /// In en, this message translates to:
  /// **'Server error. Please try again later.'**
  String get errorServer;

  /// No description provided for @errorUnauthorized.
  ///
  /// In en, this message translates to:
  /// **'Unauthorized. Please log in again.'**
  String get errorUnauthorized;

  /// No description provided for @errorNotFound.
  ///
  /// In en, this message translates to:
  /// **'Resource not found.'**
  String get errorNotFound;

  /// No description provided for @errorValidation.
  ///
  /// In en, this message translates to:
  /// **'Validation failed.'**
  String get errorValidation;

  /// No description provided for @errorValidationEmpty.
  ///
  /// In en, this message translates to:
  /// **'Inputs cannot be empty.'**
  String get errorValidationEmpty;

  /// No description provided for @errorValidationMissing.
  ///
  /// In en, this message translates to:
  /// **'Missing required fields: {fields}'**
  String errorValidationMissing(Object fields);

  /// No description provided for @createOrganization.
  ///
  /// In en, this message translates to:
  /// **'Create Organization'**
  String get createOrganization;

  /// No description provided for @editOrganization.
  ///
  /// In en, this message translates to:
  /// **'Edit Organization'**
  String get editOrganization;

  /// No description provided for @deleteOrganization.
  ///
  /// In en, this message translates to:
  /// **'Delete Organization'**
  String get deleteOrganization;

  /// No description provided for @save.
  ///
  /// In en, this message translates to:
  /// **'Save'**
  String get save;

  /// No description provided for @orgNameLabel.
  ///
  /// In en, this message translates to:
  /// **'Organization Name'**
  String get orgNameLabel;

  /// No description provided for @orgTierLabel.
  ///
  /// In en, this message translates to:
  /// **'Tier'**
  String get orgTierLabel;

  /// No description provided for @basicTier.
  ///
  /// In en, this message translates to:
  /// **'Basic'**
  String get basicTier;

  /// No description provided for @premiumTier.
  ///
  /// In en, this message translates to:
  /// **'Premium'**
  String get premiumTier;

  /// No description provided for @enterpriseTier.
  ///
  /// In en, this message translates to:
  /// **'Enterprise'**
  String get enterpriseTier;

  /// No description provided for @deleteOrgConfirmation.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete {name}?'**
  String deleteOrgConfirmation(String name);

  /// No description provided for @deleteOrgHasUsersTitle.
  ///
  /// In en, this message translates to:
  /// **'Organization has users'**
  String get deleteOrgHasUsersTitle;

  /// No description provided for @deleteOrgHasUsersMessage.
  ///
  /// In en, this message translates to:
  /// **'This organization contains users. Deleting it will also permanently delete all its users. This action cannot be undone.'**
  String get deleteOrgHasUsersMessage;

  /// No description provided for @deleteForceConfirm.
  ///
  /// In en, this message translates to:
  /// **'Delete everything'**
  String get deleteForceConfirm;

  /// No description provided for @contactEmailLabel.
  ///
  /// In en, this message translates to:
  /// **'Contact Email'**
  String get contactEmailLabel;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'fi'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'fi':
      return AppLocalizationsFi();
  }

  throw FlutterError(
    'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
    'an issue with the localizations generation tool. Please file an issue '
    'on GitHub with a reproducible sample app and the gen-l10n configuration '
    'that was used.',
  );
}
