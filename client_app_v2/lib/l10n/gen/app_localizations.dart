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
/// import 'gen/app_localizations.dart';
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

  /// No description provided for @delete.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get delete;

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
  /// **'Select a file to upload'**
  String get selectFile;

  /// Validation error message
  ///
  /// In en, this message translates to:
  /// **'This field is required.'**
  String get fieldRequired;

  /// No description provided for @authOrganic.
  ///
  /// In en, this message translates to:
  /// **'Organic (Authentic)'**
  String get authOrganic;

  /// No description provided for @authPerformative.
  ///
  /// In en, this message translates to:
  /// **'Performative (Staged)'**
  String get authPerformative;

  /// No description provided for @authUnknown.
  ///
  /// In en, this message translates to:
  /// **'Unknown'**
  String get authUnknown;

  /// No description provided for @verVerified.
  ///
  /// In en, this message translates to:
  /// **'Verified'**
  String get verVerified;

  /// No description provided for @verDebunked.
  ///
  /// In en, this message translates to:
  /// **'Debunked'**
  String get verDebunked;

  /// No description provided for @verUncertain.
  ///
  /// In en, this message translates to:
  /// **'Uncertain'**
  String get verUncertain;

  /// Validation error message for files
  ///
  /// In en, this message translates to:
  /// **'This file is required.'**
  String get fileRequired;

  /// Subtitle showing workflow step and input counts
  ///
  /// In en, this message translates to:
  /// **'Steps: {steps} | Inputs: {inputs}'**
  String workflowSubtitle(int steps, int inputs);

  /// Subtitle showing matrix strictness and rule counts
  ///
  /// In en, this message translates to:
  /// **'Strictness: {strictness} | Rules: {rules}'**
  String matrixSubtitle(int strictness, int rules);

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

  /// No description provided for @executionRejected.
  ///
  /// In en, this message translates to:
  /// **'Execution Rejected: {error}'**
  String executionRejected(Object error);

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
  /// **'Submission failed: {error}'**
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

  /// No description provided for @cancelling.
  ///
  /// In en, this message translates to:
  /// **'Cancelling'**
  String get cancelling;

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

  /// No description provided for @pasteText.
  ///
  /// In en, this message translates to:
  /// **'Paste Text'**
  String get pasteText;

  /// No description provided for @uploadFile.
  ///
  /// In en, this message translates to:
  /// **'Upload File'**
  String get uploadFile;

  /// No description provided for @pasteTextLabel.
  ///
  /// In en, this message translates to:
  /// **'Paste text here...'**
  String get pasteTextLabel;

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

  /// No description provided for @navStudio.
  ///
  /// In en, this message translates to:
  /// **'Studio'**
  String get navStudio;

  /// No description provided for @navRegistry.
  ///
  /// In en, this message translates to:
  /// **'Registry'**
  String get navRegistry;

  /// No description provided for @navAnalytics.
  ///
  /// In en, this message translates to:
  /// **'Analytics'**
  String get navAnalytics;

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

  /// No description provided for @stepXai.
  ///
  /// In en, this message translates to:
  /// **'XAI Reporter (Final Report)'**
  String get stepXai;

  /// No description provided for @stepInitializing.
  ///
  /// In en, this message translates to:
  /// **'Initializing...'**
  String get stepInitializing;

  /// No description provided for @stepLogician.
  ///
  /// In en, this message translates to:
  /// **'Logic Audit (Logician)'**
  String get stepLogician;

  /// No description provided for @stepFalsifier.
  ///
  /// In en, this message translates to:
  /// **'Critical Audit (Falsifier)'**
  String get stepFalsifier;

  /// No description provided for @stepCausal.
  ///
  /// In en, this message translates to:
  /// **'Causal Audit (Causal)'**
  String get stepCausal;

  /// No description provided for @stepDetector.
  ///
  /// In en, this message translates to:
  /// **'Illusion Audit (Detector)'**
  String get stepDetector;

  /// No description provided for @stepOverseer.
  ///
  /// In en, this message translates to:
  /// **'Overseer (Fact)'**
  String get stepOverseer;

  /// No description provided for @stepJudgeCognitive.
  ///
  /// In en, this message translates to:
  /// **'Judge (Cognitive)'**
  String get stepJudgeCognitive;

  /// No description provided for @stepContext.
  ///
  /// In en, this message translates to:
  /// **'Context Retrieval'**
  String get stepContext;

  /// No description provided for @stepInputProcessor.
  ///
  /// In en, this message translates to:
  /// **'Input Processing'**
  String get stepInputProcessor;

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
  /// **'Unknown error'**
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

  /// No description provided for @errorLoadingData.
  ///
  /// In en, this message translates to:
  /// **'Error loading data. Please try again.'**
  String get errorLoadingData;

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

  /// No description provided for @errorDeleteBlockedByExecutions.
  ///
  /// In en, this message translates to:
  /// **'Cannot delete: Item has active executions.'**
  String get errorDeleteBlockedByExecutions;

  /// No description provided for @errorDeleteBlockedByMatrix.
  ///
  /// In en, this message translates to:
  /// **'Cannot delete: Observation is bound to a PromptBlock.'**
  String get errorDeleteBlockedByMatrix;

  /// No description provided for @errorResourceInUse.
  ///
  /// In en, this message translates to:
  /// **'Cannot delete: Record is still in use.'**
  String get errorResourceInUse;

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

  /// No description provided for @userManagement.
  ///
  /// In en, this message translates to:
  /// **'User Management'**
  String get userManagement;

  /// No description provided for @roleManager.
  ///
  /// In en, this message translates to:
  /// **'Role Manager'**
  String get roleManager;

  /// No description provided for @lastActive.
  ///
  /// In en, this message translates to:
  /// **'Last Active'**
  String get lastActive;

  /// No description provided for @executionCount.
  ///
  /// In en, this message translates to:
  /// **'Executions'**
  String get executionCount;

  /// No description provided for @roleUpdateSuccess.
  ///
  /// In en, this message translates to:
  /// **'Role updated successfully.'**
  String get roleUpdateSuccess;

  /// No description provided for @demoteLastAdminError.
  ///
  /// In en, this message translates to:
  /// **'Cannot demote the last Admin. Promote another user first.'**
  String get demoteLastAdminError;

  /// No description provided for @queueStatus.
  ///
  /// In en, this message translates to:
  /// **'System Queue'**
  String get queueStatus;

  /// No description provided for @queuedJobs.
  ///
  /// In en, this message translates to:
  /// **'Queued'**
  String get queuedJobs;

  /// No description provided for @activeJobs.
  ///
  /// In en, this message translates to:
  /// **'Active'**
  String get activeJobs;

  /// No description provided for @roleLabel.
  ///
  /// In en, this message translates to:
  /// **'Role'**
  String get roleLabel;

  /// No description provided for @lastLogin.
  ///
  /// In en, this message translates to:
  /// **'Last seen'**
  String get lastLogin;

  /// No description provided for @lblWeak.
  ///
  /// In en, this message translates to:
  /// **'Weak'**
  String get lblWeak;

  /// No description provided for @lblModerate.
  ///
  /// In en, this message translates to:
  /// **'Moderate'**
  String get lblModerate;

  /// No description provided for @lblStrong.
  ///
  /// In en, this message translates to:
  /// **'Strong'**
  String get lblStrong;

  /// No description provided for @lblSource.
  ///
  /// In en, this message translates to:
  /// **'Source'**
  String get lblSource;

  /// No description provided for @lblAbstractQuadrant.
  ///
  /// In en, this message translates to:
  /// **'Abstract (High Bloom + Low Toulmin)'**
  String get lblAbstractQuadrant;

  /// No description provided for @lblSuperficialQuadrant.
  ///
  /// In en, this message translates to:
  /// **'Superficial (Low Bloom + Low Toulmin)'**
  String get lblSuperficialQuadrant;

  /// No description provided for @actions.
  ///
  /// In en, this message translates to:
  /// **'Actions'**
  String get actions;

  /// No description provided for @editRole.
  ///
  /// In en, this message translates to:
  /// **'Edit Role'**
  String get editRole;

  /// No description provided for @confirmDemotion.
  ///
  /// In en, this message translates to:
  /// **'Warning: Demoting an Admin limits their access immediately.'**
  String get confirmDemotion;

  /// No description provided for @organizationMembers.
  ///
  /// In en, this message translates to:
  /// **'Organization Members'**
  String get organizationMembers;

  /// No description provided for @refresh.
  ///
  /// In en, this message translates to:
  /// **'Refresh'**
  String get refresh;

  /// No description provided for @noUsersFound.
  ///
  /// In en, this message translates to:
  /// **'No users found.'**
  String get noUsersFound;

  /// No description provided for @loginRequired.
  ///
  /// In en, this message translates to:
  /// **'Login Required'**
  String get loginRequired;

  /// No description provided for @createUser.
  ///
  /// In en, this message translates to:
  /// **'Create User'**
  String get createUser;

  /// No description provided for @editUser.
  ///
  /// In en, this message translates to:
  /// **'Edit User'**
  String get editUser;

  /// No description provided for @deleteUser.
  ///
  /// In en, this message translates to:
  /// **'Delete User'**
  String get deleteUser;

  /// No description provided for @displayNameLabel.
  ///
  /// In en, this message translates to:
  /// **'Display Name'**
  String get displayNameLabel;

  /// No description provided for @emailLabel.
  ///
  /// In en, this message translates to:
  /// **'Email'**
  String get emailLabel;

  /// No description provided for @passwordLabel.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get passwordLabel;

  /// No description provided for @deleteUserConfirmation.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete {name}?'**
  String deleteUserConfirmation(String name);

  /// No description provided for @userCreatedSuccess.
  ///
  /// In en, this message translates to:
  /// **'User created successfully.'**
  String get userCreatedSuccess;

  /// No description provided for @userUpdatedSuccess.
  ///
  /// In en, this message translates to:
  /// **'User updated successfully.'**
  String get userUpdatedSuccess;

  /// No description provided for @userDeletedSuccess.
  ///
  /// In en, this message translates to:
  /// **'User deleted successfully.'**
  String get userDeletedSuccess;

  /// No description provided for @organizationId.
  ///
  /// In en, this message translates to:
  /// **'Organization ID'**
  String get organizationId;

  /// No description provided for @helpBloom.
  ///
  /// In en, this message translates to:
  /// **'Based on the Revised Bloom\'s Taxonomy (Anderson & Krathwohl, 2001), this metric evaluates the cognitive complexity of the output. It distinguishes between lower-order thinking (Remembering, Understanding) and higher-order skills (Applying, Analyzing, Evaluating, Creating). High scores indicate the agent is not just retrieving facts but synthesizing new information.'**
  String get helpBloom;

  /// No description provided for @helpToulmin.
  ///
  /// In en, this message translates to:
  /// **'Derived from Stephen Toulmin\'s \'The Uses of Argument\' (1958), this model moves beyond formal logic to practical argumentation. It assesses whether the Claim is supported by Data and connected via a Warrant. This structure ensures that arguments are not just assertions but reasoned positions.'**
  String get helpToulmin;

  /// No description provided for @helpWalton.
  ///
  /// In en, this message translates to:
  /// **'Based on Douglas Walton\'s Argumentation Schemes, Fidelity measures dialectical consistency. It checks if the reasoning strictly adheres to the provided premises (Source Data) or if the agent engages in \'Post-Hoc Rationalization\'—inventing justifications after the fact to support a hallucinated or biased conclusion.'**
  String get helpWalton;

  /// No description provided for @helpControlRatio.
  ///
  /// In en, this message translates to:
  /// **'Based on Discourse Analysis and Interaction Dynamics, this ratio measures the balance of initiative. A \'Passenger\' merely responds (reactive), while a \'Driver\' or \'Architect\' sets the frame and direction of the conversation (proactive). High control indicates the AI is leading the cognitive work.'**
  String get helpControlRatio;

  /// No description provided for @helpMethodology.
  ///
  /// In en, this message translates to:
  /// **'The Methodological Log tells what analysis methods the AI has applied in this phase (e.g. \'Logic Audit\', \'Causality Testing\').'**
  String get helpMethodology;

  /// No description provided for @rolePassenger.
  ///
  /// In en, this message translates to:
  /// **'Passenger'**
  String get rolePassenger;

  /// No description provided for @roleNavigator.
  ///
  /// In en, this message translates to:
  /// **'Navigator'**
  String get roleNavigator;

  /// No description provided for @roleDriver.
  ///
  /// In en, this message translates to:
  /// **'Driver'**
  String get roleDriver;

  /// No description provided for @roleArchitect.
  ///
  /// In en, this message translates to:
  /// **'Architect'**
  String get roleArchitect;

  /// No description provided for @lblCognitiveLevel.
  ///
  /// In en, this message translates to:
  /// **'Cognitive Level'**
  String get lblCognitiveLevel;

  /// No description provided for @lblStrategicDepth.
  ///
  /// In en, this message translates to:
  /// **'Strategic Depth'**
  String get lblStrategicDepth;

  /// No description provided for @lblArguments.
  ///
  /// In en, this message translates to:
  /// **'Arguments'**
  String get lblArguments;

  /// No description provided for @lblWaltonScheme.
  ///
  /// In en, this message translates to:
  /// **'Walton Scheme'**
  String get lblWaltonScheme;

  /// No description provided for @lblCriticalQuestions.
  ///
  /// In en, this message translates to:
  /// **'Critical Questions'**
  String get lblCriticalQuestions;

  /// No description provided for @lblRoleAndPosition.
  ///
  /// In en, this message translates to:
  /// **'User Role & Position'**
  String get lblRoleAndPosition;

  /// No description provided for @lblControlRatio.
  ///
  /// In en, this message translates to:
  /// **'Control Ratio'**
  String get lblControlRatio;

  /// No description provided for @biasDetected.
  ///
  /// In en, this message translates to:
  /// **'BIAS DETECTED'**
  String get biasDetected;

  /// No description provided for @biasNone.
  ///
  /// In en, this message translates to:
  /// **'No Bias'**
  String get biasNone;

  /// No description provided for @gapDetected.
  ///
  /// In en, this message translates to:
  /// **'GAP DETECTED'**
  String get gapDetected;

  /// No description provided for @gapNone.
  ///
  /// In en, this message translates to:
  /// **'Consistent'**
  String get gapNone;

  /// No description provided for @lblBloomScore.
  ///
  /// In en, this message translates to:
  /// **'Bloom Score'**
  String get lblBloomScore;

  /// No description provided for @lblToulminScore.
  ///
  /// In en, this message translates to:
  /// **'Toulmin Score'**
  String get lblToulminScore;

  /// No description provided for @lblMethodologicalLog.
  ///
  /// In en, this message translates to:
  /// **'Methodological Log'**
  String get lblMethodologicalLog;

  /// No description provided for @lblLogicMatrix.
  ///
  /// In en, this message translates to:
  /// **'Logic Matrix'**
  String get lblLogicMatrix;

  /// No description provided for @lblMatrixSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Visual analysis of reasoning quality.'**
  String get lblMatrixSubtitle;

  /// No description provided for @lblFidelity.
  ///
  /// In en, this message translates to:
  /// **'Reasoning Fidelity'**
  String get lblFidelity;

  /// No description provided for @lblPostHocWarning.
  ///
  /// In en, this message translates to:
  /// **'⚠️ Post-Hoc Rationalization detected!'**
  String get lblPostHocWarning;

  /// No description provided for @lblNoRationalization.
  ///
  /// In en, this message translates to:
  /// **'✅ No rationalization.'**
  String get lblNoRationalization;

  /// No description provided for @lblAbductiveReasoning.
  ///
  /// In en, this message translates to:
  /// **'Abductive Reasoning'**
  String get lblAbductiveReasoning;

  /// No description provided for @lblScenarioActual.
  ///
  /// In en, this message translates to:
  /// **'Scenario A (Actual)'**
  String get lblScenarioActual;

  /// No description provided for @lblScenarioSimulation.
  ///
  /// In en, this message translates to:
  /// **'Scenario B (Simulation)'**
  String get lblScenarioSimulation;

  /// No description provided for @lblCredibility.
  ///
  /// In en, this message translates to:
  /// **'Credibility'**
  String get lblCredibility;

  /// No description provided for @lblTextMetrics.
  ///
  /// In en, this message translates to:
  /// **'Text Metrics'**
  String get lblTextMetrics;

  /// No description provided for @lblBias.
  ///
  /// In en, this message translates to:
  /// **'Identified Biases'**
  String get lblBias;

  /// No description provided for @lblAuthors.
  ///
  /// In en, this message translates to:
  /// **'Authors'**
  String get lblAuthors;

  /// No description provided for @lblIntent.
  ///
  /// In en, this message translates to:
  /// **'Author Intent'**
  String get lblIntent;

  /// No description provided for @lblPsychProfile.
  ///
  /// In en, this message translates to:
  /// **'Psychological Profile'**
  String get lblPsychProfile;

  /// No description provided for @lblFactCheck.
  ///
  /// In en, this message translates to:
  /// **'Fact Check'**
  String get lblFactCheck;

  /// No description provided for @lblEthicalObservation.
  ///
  /// In en, this message translates to:
  /// **'Ethical Observation'**
  String get lblEthicalObservation;

  /// No description provided for @lblAuthenticity.
  ///
  /// In en, this message translates to:
  /// **'Authenticity Assessment'**
  String get lblAuthenticity;

  /// No description provided for @lblHeuristics.
  ///
  /// In en, this message translates to:
  /// **'Heuristics'**
  String get lblHeuristics;

  /// No description provided for @lblComplianceAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Compliance Analysis'**
  String get lblComplianceAnalysis;

  /// No description provided for @helpComplianceAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Compliance Analysis'**
  String get helpComplianceAnalysis;

  /// No description provided for @helpFidelity.
  ///
  /// In en, this message translates to:
  /// **'Fidelity measures the logical consistency of the argument. It checks if the conclusion follows strictly from the premises, without inventing new information (Hallucination) or justifying a pre-decided conclusion (Post-Hoc Rationalization).'**
  String get helpFidelity;

  /// No description provided for @helpAbductive.
  ///
  /// In en, this message translates to:
  /// **'Abductive Reasoning (Inference to Best Explanation) evaluates if the AI\'s conclusion is the most plausible explanation for the observations, rejecting less likely alternatives.'**
  String get helpAbductive;

  /// No description provided for @helpStressTest.
  ///
  /// In en, this message translates to:
  /// **'Walton\'s stress test audits the fidelity of reasoning. It reveals \'Post-Hoc rationalization\' if the AI has merely invented justifications afterwards and did not actually derive the result from them.'**
  String get helpStressTest;

  /// No description provided for @helpCausal.
  ///
  /// In en, this message translates to:
  /// **'Rooted in C.S. Peirce\'s logic of \'Inference to the Best Explanation\', Abductive reasoning infers the most likely cause. Plausibility, grounded in Counterfactual theories (e.g. Judea Pearl), tests causal understanding by simulating \'What If?\' scenarios to check logical consistency.'**
  String get helpCausal;

  /// No description provided for @helpProfiler.
  ///
  /// In en, this message translates to:
  /// **'Profiling analyzes text tone, vocabulary, and latent biases. It helps identify if the AI is attempting to manipulate or is biased.'**
  String get helpProfiler;

  /// No description provided for @helpFactCheck.
  ///
  /// In en, this message translates to:
  /// **'Fact Check compares claims against a known knowledge base and scans for ethical risks.'**
  String get helpFactCheck;

  /// No description provided for @helpPerformativity.
  ///
  /// In en, this message translates to:
  /// **'Performativity analysis evaluates whether the response is authentic and organic or artificial and staged. It detects \'purple prose\', excessive humility, and other inauthentic traits.'**
  String get helpPerformativity;

  /// No description provided for @helpArchivist.
  ///
  /// In en, this message translates to:
  /// **'In the context of AI Alignment and Constitutional AI, Compliance measures the agent\'s adherence to defined behavioral constraints (The Constitution) and organizational norms, ensuring safety and goal alignment regardless of the user\'s prompt.'**
  String get helpArchivist;

  /// No description provided for @studioStepsTitle.
  ///
  /// In en, this message translates to:
  /// **'Steps'**
  String get studioStepsTitle;

  /// No description provided for @studioConfigurationTitle.
  ///
  /// In en, this message translates to:
  /// **'Configuration'**
  String get studioConfigurationTitle;

  /// No description provided for @studioAddStepButton.
  ///
  /// In en, this message translates to:
  /// **'Add Step'**
  String get studioAddStepButton;

  /// No description provided for @studioSaveButton.
  ///
  /// In en, this message translates to:
  /// **'Save Changes'**
  String get studioSaveButton;

  /// No description provided for @studioUnsavedChanges.
  ///
  /// In en, this message translates to:
  /// **'Unsaved changes'**
  String get studioUnsavedChanges;

  /// No description provided for @studioSelectStepPrompt.
  ///
  /// In en, this message translates to:
  /// **'Select a step to configure'**
  String get studioSelectStepPrompt;

  /// No description provided for @studioStepsHeader.
  ///
  /// In en, this message translates to:
  /// **'Steps'**
  String get studioStepsHeader;

  /// No description provided for @studioAddStep.
  ///
  /// In en, this message translates to:
  /// **'Add Step'**
  String get studioAddStep;

  /// No description provided for @studioNoSteps.
  ///
  /// In en, this message translates to:
  /// **'No steps defined'**
  String get studioNoSteps;

  /// No description provided for @studioRunTest.
  ///
  /// In en, this message translates to:
  /// **'Run Test'**
  String get studioRunTest;

  /// No description provided for @studioSaving.
  ///
  /// In en, this message translates to:
  /// **'Saving...'**
  String get studioSaving;

  /// No description provided for @studioChangesSaved.
  ///
  /// In en, this message translates to:
  /// **'Changes saved'**
  String get studioChangesSaved;

  /// No description provided for @studioCreateNew.
  ///
  /// In en, this message translates to:
  /// **'Create New'**
  String get studioCreateNew;

  /// No description provided for @studioCopyWorkflow.
  ///
  /// In en, this message translates to:
  /// **'Copy Workflow'**
  String get studioCopyWorkflow;

  /// No description provided for @studioNewNameLabel.
  ///
  /// In en, this message translates to:
  /// **'New Name'**
  String get studioNewNameLabel;

  /// No description provided for @studioTabWorkflows.
  ///
  /// In en, this message translates to:
  /// **'Workflows'**
  String get studioTabWorkflows;

  /// No description provided for @studioTabMatrices.
  ///
  /// In en, this message translates to:
  /// **'PromptBlocks'**
  String get studioTabMatrices;

  /// No description provided for @studioCreateMatrix.
  ///
  /// In en, this message translates to:
  /// **'Create PromptBlock'**
  String get studioCreateMatrix;

  /// No description provided for @studioMatrixName.
  ///
  /// In en, this message translates to:
  /// **'Block Name'**
  String get studioMatrixName;

  /// No description provided for @studioMatrixDesc.
  ///
  /// In en, this message translates to:
  /// **'Description'**
  String get studioMatrixDesc;

  /// No description provided for @matrixRole.
  ///
  /// In en, this message translates to:
  /// **'Role Persona (For Instructions)'**
  String get matrixRole;

  /// No description provided for @matrixScale.
  ///
  /// In en, this message translates to:
  /// **'Scale (Min - Max)'**
  String get matrixScale;

  /// No description provided for @matrixCriteria.
  ///
  /// In en, this message translates to:
  /// **'Criteria (Schema)'**
  String get matrixCriteria;

  /// No description provided for @matrixAddCriterion.
  ///
  /// In en, this message translates to:
  /// **'Add Observation'**
  String get matrixAddCriterion;

  /// No description provided for @matrixLevel.
  ///
  /// In en, this message translates to:
  /// **'Level {level}'**
  String matrixLevel(Object level);

  /// No description provided for @studioSelectMatrix.
  ///
  /// In en, this message translates to:
  /// **'Select PromptBlock'**
  String get studioSelectMatrix;

  /// No description provided for @update.
  ///
  /// In en, this message translates to:
  /// **'Update'**
  String get update;

  /// No description provided for @editDimension.
  ///
  /// In en, this message translates to:
  /// **'Edit Observation'**
  String get editDimension;

  /// No description provided for @systemInspectorTitle.
  ///
  /// In en, this message translates to:
  /// **'System Inspector'**
  String get systemInspectorTitle;

  /// No description provided for @workflowConfig.
  ///
  /// In en, this message translates to:
  /// **'Config'**
  String get workflowConfig;

  /// No description provided for @stepPreview.
  ///
  /// In en, this message translates to:
  /// **'Preview'**
  String get stepPreview;

  /// No description provided for @generateChain.
  ///
  /// In en, this message translates to:
  /// **'Generate Chain'**
  String get generateChain;

  /// No description provided for @systemInstruction.
  ///
  /// In en, this message translates to:
  /// **'System Instruction'**
  String get systemInstruction;

  /// No description provided for @userPrompt.
  ///
  /// In en, this message translates to:
  /// **'User Prompt'**
  String get userPrompt;

  /// No description provided for @exportTab.
  ///
  /// In en, this message translates to:
  /// **'Export'**
  String get exportTab;

  /// No description provided for @selectStepPlaceholder.
  ///
  /// In en, this message translates to:
  /// **'Select a step...'**
  String get selectStepPlaceholder;

  /// No description provided for @copyToClipboard.
  ///
  /// In en, this message translates to:
  /// **'Copy to Clipboard'**
  String get copyToClipboard;

  /// No description provided for @copiedToClipboard.
  ///
  /// In en, this message translates to:
  /// **'Copied to Clipboard!'**
  String get copiedToClipboard;

  /// No description provided for @modelRegistryTitle.
  ///
  /// In en, this message translates to:
  /// **'Model Registry'**
  String get modelRegistryTitle;

  /// No description provided for @providerSettings.
  ///
  /// In en, this message translates to:
  /// **'Provider Settings'**
  String get providerSettings;

  /// No description provided for @testLab.
  ///
  /// In en, this message translates to:
  /// **'Test Laboratory'**
  String get testLab;

  /// No description provided for @runTest.
  ///
  /// In en, this message translates to:
  /// **'Run Test'**
  String get runTest;

  /// No description provided for @latency.
  ///
  /// In en, this message translates to:
  /// **'Latency'**
  String get latency;

  /// No description provided for @providerLabel.
  ///
  /// In en, this message translates to:
  /// **'Provider'**
  String get providerLabel;

  /// No description provided for @apiKeyLabel.
  ///
  /// In en, this message translates to:
  /// **'API Key'**
  String get apiKeyLabel;

  /// No description provided for @baseUrlLabel.
  ///
  /// In en, this message translates to:
  /// **'Base URL'**
  String get baseUrlLabel;

  /// No description provided for @temperatureLabel.
  ///
  /// In en, this message translates to:
  /// **'Temperature'**
  String get temperatureLabel;

  /// No description provided for @modelNameLabel.
  ///
  /// In en, this message translates to:
  /// **'Model Name'**
  String get modelNameLabel;

  /// No description provided for @testConnection.
  ///
  /// In en, this message translates to:
  /// **'Test Connection'**
  String get testConnection;

  /// No description provided for @adhocTest.
  ///
  /// In en, this message translates to:
  /// **'Ad-Hoc Test'**
  String get adhocTest;

  /// No description provided for @responseOutput.
  ///
  /// In en, this message translates to:
  /// **'Response Output'**
  String get responseOutput;

  /// No description provided for @studioDashboardWorkflowsTitle.
  ///
  /// In en, this message translates to:
  /// **'Workflows'**
  String get studioDashboardWorkflowsTitle;

  /// No description provided for @studioDashboardWorkflowsDesc.
  ///
  /// In en, this message translates to:
  /// **'Design and manage audit workflows.'**
  String get studioDashboardWorkflowsDesc;

  /// No description provided for @studioDashboardStepsTitle.
  ///
  /// In en, this message translates to:
  /// **'Steps'**
  String get studioDashboardStepsTitle;

  /// No description provided for @studioDashboardStepsDesc.
  ///
  /// In en, this message translates to:
  /// **'Configure execution steps.'**
  String get studioDashboardStepsDesc;

  /// No description provided for @studioDashboardMatricesTitle.
  ///
  /// In en, this message translates to:
  /// **'PromptBlocks'**
  String get studioDashboardMatricesTitle;

  /// No description provided for @studioDashboardMatricesDesc.
  ///
  /// In en, this message translates to:
  /// **'Manage dynamic LLM evaluation schema and instructions.'**
  String get studioDashboardMatricesDesc;

  /// No description provided for @studioDashboardComponentsTitle.
  ///
  /// In en, this message translates to:
  /// **'V1 Components'**
  String get studioDashboardComponentsTitle;

  /// No description provided for @studioDashboardComponentsDesc.
  ///
  /// In en, this message translates to:
  /// **'Manage legacy V1 rules (deprecation pending).'**
  String get studioDashboardComponentsDesc;

  /// No description provided for @helperSelectProvider.
  ///
  /// In en, this message translates to:
  /// **'Select from available providers'**
  String get helperSelectProvider;

  /// No description provided for @helperSelectModel.
  ///
  /// In en, this message translates to:
  /// **'Select valid model for provider'**
  String get helperSelectModel;

  /// No description provided for @helperApiKeyMasked.
  ///
  /// In en, this message translates to:
  /// **'Leave as ******** to keep existing key'**
  String get helperApiKeyMasked;

  /// No description provided for @helperOptionalOverride.
  ///
  /// In en, this message translates to:
  /// **'Optional override'**
  String get helperOptionalOverride;

  /// No description provided for @errorMustBeNumber.
  ///
  /// In en, this message translates to:
  /// **'Must be a number'**
  String get errorMustBeNumber;

  /// No description provided for @errorRangeTemperature.
  ///
  /// In en, this message translates to:
  /// **'Must be between 0.0 and 2.0'**
  String get errorRangeTemperature;

  /// No description provided for @errorMustBeInteger.
  ///
  /// In en, this message translates to:
  /// **'Must be an integer'**
  String get errorMustBeInteger;

  /// No description provided for @selectProviderPlaceholder.
  ///
  /// In en, this message translates to:
  /// **'Select a provider to configure.'**
  String get selectProviderPlaceholder;

  /// No description provided for @searchSteps.
  ///
  /// In en, this message translates to:
  /// **'Search Steps'**
  String get searchSteps;

  /// No description provided for @stepSelectToEdit.
  ///
  /// In en, this message translates to:
  /// **'Select a step to edit'**
  String get stepSelectToEdit;

  /// No description provided for @deleteWorkflowConfirmation.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete {name}?'**
  String deleteWorkflowConfirmation(String name);

  /// No description provided for @noMatricesFound.
  ///
  /// In en, this message translates to:
  /// **'No PromptBlocks found. Create one!'**
  String get noMatricesFound;

  /// No description provided for @stepCreateNew.
  ///
  /// In en, this message translates to:
  /// **'Create New Step'**
  String get stepCreateNew;

  /// No description provided for @stepEdit.
  ///
  /// In en, this message translates to:
  /// **'Edit Step'**
  String get stepEdit;

  /// No description provided for @stepIdLabel.
  ///
  /// In en, this message translates to:
  /// **'Step ID'**
  String get stepIdLabel;

  /// No description provided for @stepIdHelper.
  ///
  /// In en, this message translates to:
  /// **'Unique identifier (e.g. \'step_analyst\')'**
  String get stepIdHelper;

  /// No description provided for @stepNameLabel.
  ///
  /// In en, this message translates to:
  /// **'Name'**
  String get stepNameLabel;

  /// No description provided for @stepDescriptionLabel.
  ///
  /// In en, this message translates to:
  /// **'Description'**
  String get stepDescriptionLabel;

  /// No description provided for @stepAgentLogicClass.
  ///
  /// In en, this message translates to:
  /// **'Agent Logic Class'**
  String get stepAgentLogicClass;

  /// No description provided for @stepJudgeConfig.
  ///
  /// In en, this message translates to:
  /// **'Judge Configuration'**
  String get stepJudgeConfig;

  /// No description provided for @stepEvaluationMatrix.
  ///
  /// In en, this message translates to:
  /// **'PromptBlock (Evaluation)'**
  String get stepEvaluationMatrix;

  /// No description provided for @stepEvaluationMatrixHelper.
  ///
  /// In en, this message translates to:
  /// **'The criteria used for schema generation.'**
  String get stepEvaluationMatrixHelper;

  /// No description provided for @stepPromptAssembly.
  ///
  /// In en, this message translates to:
  /// **'PromptBlock (Instructions)'**
  String get stepPromptAssembly;

  /// No description provided for @stepAddPrompt.
  ///
  /// In en, this message translates to:
  /// **'Attach PromptBlock'**
  String get stepAddPrompt;

  /// No description provided for @stepPromptAssemblyHelper.
  ///
  /// In en, this message translates to:
  /// **'Blocks that shape the step\'s system instruction.'**
  String get stepPromptAssemblyHelper;

  /// No description provided for @stepSaveSuccess.
  ///
  /// In en, this message translates to:
  /// **'Step saved!'**
  String get stepSaveSuccess;

  /// No description provided for @stepDeleteConfirmTitle.
  ///
  /// In en, this message translates to:
  /// **'Confirm Delete'**
  String get stepDeleteConfirmTitle;

  /// No description provided for @stepDeleteConfirmMessage.
  ///
  /// In en, this message translates to:
  /// **'Delete step \'{id}\'?'**
  String stepDeleteConfirmMessage(String id);

  /// No description provided for @stepAddPromptTitle.
  ///
  /// In en, this message translates to:
  /// **'Attach PromptBlock to Step'**
  String get stepAddPromptTitle;

  /// No description provided for @stepSearchPrompts.
  ///
  /// In en, this message translates to:
  /// **'Search PromptBlocks'**
  String get stepSearchPrompts;

  /// No description provided for @close.
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get close;

  /// No description provided for @stepIdNameRequired.
  ///
  /// In en, this message translates to:
  /// **'ID and Name are required.'**
  String get stepIdNameRequired;

  /// No description provided for @executionNotFound.
  ///
  /// In en, this message translates to:
  /// **'Execution Not Found'**
  String get executionNotFound;

  /// No description provided for @ontologyNameLabel.
  ///
  /// In en, this message translates to:
  /// **'Name (e.g. \"Reasoning\")'**
  String get ontologyNameLabel;

  /// No description provided for @ontologyDescriptionLabel.
  ///
  /// In en, this message translates to:
  /// **'Description'**
  String get ontologyDescriptionLabel;

  /// No description provided for @registerDimension.
  ///
  /// In en, this message translates to:
  /// **'Register Observation'**
  String get registerDimension;

  /// No description provided for @newDimension.
  ///
  /// In en, this message translates to:
  /// **'New Observation'**
  String get newDimension;

  /// No description provided for @lblQuestion.
  ///
  /// In en, this message translates to:
  /// **'Question'**
  String get lblQuestion;

  /// No description provided for @lblEvidenceHeld.
  ///
  /// In en, this message translates to:
  /// **'Evidence Held?'**
  String get lblEvidenceHeld;

  /// No description provided for @lblObservation.
  ///
  /// In en, this message translates to:
  /// **'Observation'**
  String get lblObservation;

  /// No description provided for @lblCausalAudit.
  ///
  /// In en, this message translates to:
  /// **'Causal Audit'**
  String get lblCausalAudit;

  /// No description provided for @lblCounterfactualTest.
  ///
  /// In en, this message translates to:
  /// **'Counterfactual Test'**
  String get lblCounterfactualTest;

  /// No description provided for @btnHideRawData.
  ///
  /// In en, this message translates to:
  /// **'Hide Raw Data'**
  String get btnHideRawData;

  /// No description provided for @btnShowJson.
  ///
  /// In en, this message translates to:
  /// **'JSON'**
  String get btnShowJson;

  /// No description provided for @msgJsonCopied.
  ///
  /// In en, this message translates to:
  /// **'JSON copied to clipboard'**
  String get msgJsonCopied;

  /// No description provided for @errDataIntegrity.
  ///
  /// In en, this message translates to:
  /// **'Data Integrity Error (Fail Fast)'**
  String get errDataIntegrity;

  /// No description provided for @subLogicAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Toulmin & Cognitive Level'**
  String get subLogicAnalysis;

  /// No description provided for @subStressTest.
  ///
  /// In en, this message translates to:
  /// **'Walton Falsification'**
  String get subStressTest;

  /// No description provided for @subCausalAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Causal & Counterfactual'**
  String get subCausalAnalysis;

  /// No description provided for @subPerformativityCheck.
  ///
  /// In en, this message translates to:
  /// **'Authenticity & Pre-Mortem'**
  String get subPerformativityCheck;

  /// No description provided for @subFactCheck.
  ///
  /// In en, this message translates to:
  /// **'Hallucinations & Ethics'**
  String get subFactCheck;

  /// No description provided for @subProfilerAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Biases & Psycho-profile'**
  String get subProfilerAnalysis;

  /// No description provided for @subArchivistCheck.
  ///
  /// In en, this message translates to:
  /// **'Compliance & Precedents'**
  String get subArchivistCheck;

  /// No description provided for @lblWordCount.
  ///
  /// In en, this message translates to:
  /// **'Word Count'**
  String get lblWordCount;

  /// No description provided for @lblSentenceCount.
  ///
  /// In en, this message translates to:
  /// **'Sentence Count'**
  String get lblSentenceCount;

  /// No description provided for @lblAvgSentence.
  ///
  /// In en, this message translates to:
  /// **'Avg Sentence'**
  String get lblAvgSentence;

  /// No description provided for @lblLexicalDiversity.
  ///
  /// In en, this message translates to:
  /// **'Lexical Diversity'**
  String get lblLexicalDiversity;

  /// No description provided for @lblCapitalsRatio.
  ///
  /// In en, this message translates to:
  /// **'Capitals Ratio'**
  String get lblCapitalsRatio;

  /// No description provided for @lblAutomationBias.
  ///
  /// In en, this message translates to:
  /// **'Automation Bias'**
  String get lblAutomationBias;

  /// No description provided for @lblSayDoGap.
  ///
  /// In en, this message translates to:
  /// **'Say-Do Gap'**
  String get lblSayDoGap;

  /// No description provided for @lblBehavioralIndicators.
  ///
  /// In en, this message translates to:
  /// **'Behavioral Indicators:'**
  String get lblBehavioralIndicators;

  /// No description provided for @lblAutomationBiasValue.
  ///
  /// In en, this message translates to:
  /// **'Automation Bias: {value}'**
  String lblAutomationBiasValue(String value);

  /// No description provided for @lblSayDoGapValue.
  ///
  /// In en, this message translates to:
  /// **'Say-Do Gap: {value}'**
  String lblSayDoGapValue(String value);

  /// No description provided for @plausibility_desc.
  ///
  /// In en, this message translates to:
  /// **'Plausibility measures scenario realism and consistency.'**
  String get plausibility_desc;

  /// No description provided for @bloomRemembering.
  ///
  /// In en, this message translates to:
  /// **'Remembering'**
  String get bloomRemembering;

  /// No description provided for @bloomUnderstanding.
  ///
  /// In en, this message translates to:
  /// **'Understanding'**
  String get bloomUnderstanding;

  /// No description provided for @bloomApplying.
  ///
  /// In en, this message translates to:
  /// **'Applying'**
  String get bloomApplying;

  /// No description provided for @bloomAnalyzing.
  ///
  /// In en, this message translates to:
  /// **'Analyzing'**
  String get bloomAnalyzing;

  /// No description provided for @bloomEvaluating.
  ///
  /// In en, this message translates to:
  /// **'Evaluating'**
  String get bloomEvaluating;

  /// No description provided for @bloomCreating.
  ///
  /// In en, this message translates to:
  /// **'Creating'**
  String get bloomCreating;

  /// No description provided for @stratLow.
  ///
  /// In en, this message translates to:
  /// **'Tactical'**
  String get stratLow;

  /// No description provided for @stratMedium.
  ///
  /// In en, this message translates to:
  /// **'Operational'**
  String get stratMedium;

  /// No description provided for @stratHigh.
  ///
  /// In en, this message translates to:
  /// **'Strategic'**
  String get stratHigh;

  /// No description provided for @stratVisionary.
  ///
  /// In en, this message translates to:
  /// **'Visionary'**
  String get stratVisionary;

  /// No description provided for @logicMatrixTitle.
  ///
  /// In en, this message translates to:
  /// **'Logic Matrix (Decision Profiling)'**
  String get logicMatrixTitle;

  /// No description provided for @logicMatrixQ1Title.
  ///
  /// In en, this message translates to:
  /// **'Grounded Synthesis'**
  String get logicMatrixQ1Title;

  /// No description provided for @logicMatrixQ1Desc.
  ///
  /// In en, this message translates to:
  /// **'Strong argumentation and deep synthesis. Reliable and innovative.'**
  String get logicMatrixQ1Desc;

  /// No description provided for @logicMatrixQ2Title.
  ///
  /// In en, this message translates to:
  /// **'Unwarranted Ideation'**
  String get logicMatrixQ2Title;

  /// No description provided for @logicMatrixQ2Desc.
  ///
  /// In en, this message translates to:
  /// **'High-level thinking without sufficient warrants. Potential hallucination.'**
  String get logicMatrixQ2Desc;

  /// No description provided for @logicMatrixQ3Title.
  ///
  /// In en, this message translates to:
  /// **'Pedantic Fact-telling'**
  String get logicMatrixQ3Title;

  /// No description provided for @logicMatrixQ3Desc.
  ///
  /// In en, this message translates to:
  /// **'Strictly warranted, but limited to repeating existing knowledge.'**
  String get logicMatrixQ3Desc;

  /// No description provided for @logicMatrixQ4Title.
  ///
  /// In en, this message translates to:
  /// **'Weak Assertions'**
  String get logicMatrixQ4Title;

  /// No description provided for @logicMatrixQ4Desc.
  ///
  /// In en, this message translates to:
  /// **'Low cognitive level and weak warrants. Not actionable.'**
  String get logicMatrixQ4Desc;

  /// No description provided for @helpLogicMatrix.
  ///
  /// In en, this message translates to:
  /// **'The Logic Matrix visualizes the relationship between argumentation quality and cognitive depth. NEW: Bubble size represents Strategic Depth (Agency). Large bubble implies visionary approach.'**
  String get helpLogicMatrix;

  /// No description provided for @helpStrategicDepth.
  ///
  /// In en, this message translates to:
  /// **'Drawing on Systems Thinking and Foresight methodologies, Strategic Depth measures the temporal and systemic scope of the response. It contrasts \'Tactical\' (immediate, reactive) thinking with \'Visionary\' (long-term, systemic) thinking, evaluating the agent\'s ability to model second- and third-order consequences.'**
  String get helpStrategicDepth;

  /// No description provided for @helpAuthenticity.
  ///
  /// In en, this message translates to:
  /// **'Authenticity measures the naturalness of the response on a scale of 1-3. 3 = Organic, 2 = Mixed, 1 = Performative.'**
  String get helpAuthenticity;

  /// No description provided for @helpWordCount.
  ///
  /// In en, this message translates to:
  /// **'Total word count of the response.'**
  String get helpWordCount;

  /// No description provided for @secThreatDetected.
  ///
  /// In en, this message translates to:
  /// **'THREAT DETECTED'**
  String get secThreatDetected;

  /// No description provided for @secThreatNone.
  ///
  /// In en, this message translates to:
  /// **'No Threats'**
  String get secThreatNone;

  /// No description provided for @secAnonymized.
  ///
  /// In en, this message translates to:
  /// **'ANONYMIZED'**
  String get secAnonymized;

  /// No description provided for @secNotAnonymized.
  ///
  /// In en, this message translates to:
  /// **'NOT ANONYMIZED'**
  String get secNotAnonymized;

  /// No description provided for @riskHigh.
  ///
  /// In en, this message translates to:
  /// **'HIGH RISK'**
  String get riskHigh;

  /// No description provided for @riskMedium.
  ///
  /// In en, this message translates to:
  /// **'Medium Risk'**
  String get riskMedium;

  /// No description provided for @riskLow.
  ///
  /// In en, this message translates to:
  /// **'Low Risk'**
  String get riskLow;

  /// No description provided for @riskUnknown.
  ///
  /// In en, this message translates to:
  /// **'Unknown Risk'**
  String get riskUnknown;

  /// No description provided for @lblDriver.
  ///
  /// In en, this message translates to:
  /// **'Driver'**
  String get lblDriver;

  /// No description provided for @lblPassenger.
  ///
  /// In en, this message translates to:
  /// **'Passenger'**
  String get lblPassenger;

  /// No description provided for @lblRiskLevel.
  ///
  /// In en, this message translates to:
  /// **'Risk Level'**
  String get lblRiskLevel;

  /// No description provided for @lblEmotionalTone.
  ///
  /// In en, this message translates to:
  /// **'Emotional Tone'**
  String get lblEmotionalTone;

  /// No description provided for @lblNoFindings.
  ///
  /// In en, this message translates to:
  /// **'No significant findings.'**
  String get lblNoFindings;

  /// No description provided for @knowledgeBaseIngestionTitle.
  ///
  /// In en, this message translates to:
  /// **'Knowledge Base Ingestion'**
  String get knowledgeBaseIngestionTitle;

  /// No description provided for @uploadDocxMd.
  ///
  /// In en, this message translates to:
  /// **'Upload DOCX / MD'**
  String get uploadDocxMd;

  /// No description provided for @ingestionComplete.
  ///
  /// In en, this message translates to:
  /// **'Ingestion Complete!'**
  String get ingestionComplete;

  /// No description provided for @referencesCount.
  ///
  /// In en, this message translates to:
  /// **'References: {count}'**
  String referencesCount(int count);

  /// No description provided for @claimsCount.
  ///
  /// In en, this message translates to:
  /// **'Claims: {count}'**
  String claimsCount(int count);

  /// No description provided for @studioDashboardKnowledgeTitle.
  ///
  /// In en, this message translates to:
  /// **'Ingestion'**
  String get studioDashboardKnowledgeTitle;

  /// No description provided for @studioDashboardKnowledgeDesc.
  ///
  /// In en, this message translates to:
  /// **'Upload documents to Knowledge Base.'**
  String get studioDashboardKnowledgeDesc;

  /// No description provided for @addStrategyTooltip.
  ///
  /// In en, this message translates to:
  /// **'Add Strategy'**
  String get addStrategyTooltip;

  /// No description provided for @resetKnowledgeBaseTitle.
  ///
  /// In en, this message translates to:
  /// **'Reset Knowledge Base?'**
  String get resetKnowledgeBaseTitle;

  /// No description provided for @resetKnowledgeBaseConfirmation.
  ///
  /// In en, this message translates to:
  /// **'This will adhere to the \"Clean Slate\" protocol and permanently delete all ingested documents. Continue?'**
  String get resetKnowledgeBaseConfirmation;

  /// No description provided for @resetButton.
  ///
  /// In en, this message translates to:
  /// **'Reset'**
  String get resetButton;

  /// No description provided for @analysisLevelLabel.
  ///
  /// In en, this message translates to:
  /// **'Analysis Level (Model Strategy)'**
  String get analysisLevelLabel;

  /// No description provided for @analysisLevelHelper.
  ///
  /// In en, this message translates to:
  /// **'Select \"Deep\" for complex reasoning or \"Fast\" for speed.'**
  String get analysisLevelHelper;

  /// No description provided for @analysisLevelNone.
  ///
  /// In en, this message translates to:
  /// **'None (Parsing Only)'**
  String get analysisLevelNone;

  /// No description provided for @strategiesLoadError.
  ///
  /// In en, this message translates to:
  /// **'Failed to load strategies: {error}'**
  String strategiesLoadError(Object error);

  /// No description provided for @processingStatus.
  ///
  /// In en, this message translates to:
  /// **'Processing...'**
  String get processingStatus;

  /// No description provided for @errorKnowledgeIngestionFailed.
  ///
  /// In en, this message translates to:
  /// **'Knowledge ingestion failed. Check file and try again.'**
  String get errorKnowledgeIngestionFailed;

  /// No description provided for @errorKnowledgeResetFailed.
  ///
  /// In en, this message translates to:
  /// **'Knowledge base reset failed. Contact support.'**
  String get errorKnowledgeResetFailed;

  /// No description provided for @errorKnowledgeRetrievalFailed.
  ///
  /// In en, this message translates to:
  /// **'Knowledge retrieval failed. Server unresponsive.'**
  String get errorKnowledgeRetrievalFailed;

  /// No description provided for @errValidationFailed.
  ///
  /// In en, this message translates to:
  /// **'Validation Failed'**
  String get errValidationFailed;

  /// No description provided for @errInternalServerError.
  ///
  /// In en, this message translates to:
  /// **'Internal Server Error'**
  String get errInternalServerError;

  /// No description provided for @errResourceNotFound.
  ///
  /// In en, this message translates to:
  /// **'Resource Not Found'**
  String get errResourceNotFound;

  /// No description provided for @errAuthenticationFailed.
  ///
  /// In en, this message translates to:
  /// **'Authentication Failed'**
  String get errAuthenticationFailed;

  /// No description provided for @errPermissionDenied.
  ///
  /// In en, this message translates to:
  /// **'Permission Denied'**
  String get errPermissionDenied;

  /// No description provided for @errServiceUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Service Unavailable'**
  String get errServiceUnavailable;

  /// No description provided for @errAgentExecutionCritical.
  ///
  /// In en, this message translates to:
  /// **'Agent Execution Critical'**
  String get errAgentExecutionCritical;

  /// No description provided for @errWorkflowExecutionFailed.
  ///
  /// In en, this message translates to:
  /// **'Workflow Execution Failed'**
  String get errWorkflowExecutionFailed;

  /// No description provided for @errKnowledgeNotIngestedTitle.
  ///
  /// In en, this message translates to:
  /// **'Knowledge Base Empty'**
  String get errKnowledgeNotIngestedTitle;

  /// No description provided for @errKnowledgeNotIngested.
  ///
  /// In en, this message translates to:
  /// **'Knowledge Base is empty. Please upload documents in the Ingestion view before running analysis.'**
  String get errKnowledgeNotIngested;

  /// No description provided for @actionGoToIngestion.
  ///
  /// In en, this message translates to:
  /// **'Go to Ingestion'**
  String get actionGoToIngestion;

  /// No description provided for @knowledgeActive.
  ///
  /// In en, this message translates to:
  /// **'Knowledge Base Active'**
  String get knowledgeActive;

  /// No description provided for @knowledgeStats.
  ///
  /// In en, this message translates to:
  /// **'Documents: {docCount} | Precedents: {precCount}'**
  String knowledgeStats(int docCount, int precCount);

  /// No description provided for @addReflectionIntent.
  ///
  /// In en, this message translates to:
  /// **'Add reflection (Intent)'**
  String get addReflectionIntent;

  /// No description provided for @reflectionDescription.
  ///
  /// In en, this message translates to:
  /// **'Describe your own reasoning and how you guided the AI during the process. This is the most critical phase for evaluation.'**
  String get reflectionDescription;

  /// No description provided for @guidedReflectionRecommended.
  ///
  /// In en, this message translates to:
  /// **'Guided reflection (Recommended)'**
  String get guidedReflectionRecommended;

  /// No description provided for @q1GoalTitle.
  ///
  /// In en, this message translates to:
  /// **'Goal and strategic planning (Architect)'**
  String get q1GoalTitle;

  /// No description provided for @q1GoalHint.
  ///
  /// In en, this message translates to:
  /// **'What was your original goal and how did you break down the task?'**
  String get q1GoalHint;

  /// No description provided for @q2FalsificationTitle.
  ///
  /// In en, this message translates to:
  /// **'AI steering and critical iteration (Falsifier)'**
  String get q2FalsificationTitle;

  /// No description provided for @q2FalsificationHint.
  ///
  /// In en, this message translates to:
  /// **'What shortcomings or errors did you notice in the AI\'s response and how did you correct them?'**
  String get q2FalsificationHint;

  /// No description provided for @q3SynthesisTitle.
  ///
  /// In en, this message translates to:
  /// **'Own contribution and creativity (Architect)'**
  String get q3SynthesisTitle;

  /// No description provided for @q3SynthesisHint.
  ///
  /// In en, this message translates to:
  /// **'What is genuinely your own human contribution in the final product?'**
  String get q3SynthesisHint;

  /// No description provided for @q4ArgumentationTitle.
  ///
  /// In en, this message translates to:
  /// **'Quality assurance and metacognition (Judge)'**
  String get q4ArgumentationTitle;

  /// No description provided for @q4ArgumentationHint.
  ///
  /// In en, this message translates to:
  /// **'On what grounds do you trust the outcome? What would you do differently?'**
  String get q4ArgumentationHint;

  /// No description provided for @minCharsRequired.
  ///
  /// In en, this message translates to:
  /// **'Text must be at least 100 characters long.'**
  String get minCharsRequired;

  /// No description provided for @charsRemainingLength.
  ///
  /// In en, this message translates to:
  /// **'Answer must be at least 100 characters ({len}/100).'**
  String charsRemainingLength(int len);

  /// No description provided for @expandArgumentationHint.
  ///
  /// In en, this message translates to:
  /// **'It is recommended to expand your reasoning ({len}/100 chars)'**
  String expandArgumentationHint(int len);

  /// No description provided for @dataUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Data unavailable'**
  String get dataUnavailable;

  /// No description provided for @noDetailedData.
  ///
  /// In en, this message translates to:
  /// **'No detailed observation data available.'**
  String get noDetailedData;

  /// No description provided for @detailedBreakdown.
  ///
  /// In en, this message translates to:
  /// **'Detailed Breakdown'**
  String get detailedBreakdown;

  /// No description provided for @scaleInfo.
  ///
  /// In en, this message translates to:
  /// **'(Scale: {min}-{max})'**
  String scaleInfo(int min, int max);

  /// No description provided for @lblClaim.
  ///
  /// In en, this message translates to:
  /// **'Claim'**
  String get lblClaim;

  /// No description provided for @lblData.
  ///
  /// In en, this message translates to:
  /// **'Data'**
  String get lblData;

  /// No description provided for @lblWarrant.
  ///
  /// In en, this message translates to:
  /// **'Warrant'**
  String get lblWarrant;

  /// No description provided for @lblBacking.
  ///
  /// In en, this message translates to:
  /// **'Backing'**
  String get lblBacking;

  /// No description provided for @lblRebuttal.
  ///
  /// In en, this message translates to:
  /// **'Rebuttal'**
  String get lblRebuttal;

  /// No description provided for @lblQualifier.
  ///
  /// In en, this message translates to:
  /// **'Qualifier'**
  String get lblQualifier;

  /// No description provided for @lblFindings.
  ///
  /// In en, this message translates to:
  /// **'Findings'**
  String get lblFindings;

  /// No description provided for @lblNoSignificantFindings.
  ///
  /// In en, this message translates to:
  /// **'No significant findings.'**
  String get lblNoSignificantFindings;

  /// No description provided for @lblImperativeCommands.
  ///
  /// In en, this message translates to:
  /// **'Imperative Commands'**
  String get lblImperativeCommands;

  /// No description provided for @helpImperativeCommands.
  ///
  /// In en, this message translates to:
  /// **'A metric that measures how many direct commands or demands (imperatives) the user made in their text. This indicates initiative and the need for control in the interaction.'**
  String get helpImperativeCommands;

  /// No description provided for @lblPostHocRationalization.
  ///
  /// In en, this message translates to:
  /// **'Post-Hoc Rationalization'**
  String get lblPostHocRationalization;

  /// No description provided for @lblReasoning.
  ///
  /// In en, this message translates to:
  /// **'Reasoning'**
  String get lblReasoning;

  /// No description provided for @lblAvgSentenceLength.
  ///
  /// In en, this message translates to:
  /// **'Average Sentence Length'**
  String get lblAvgSentenceLength;

  /// No description provided for @lblPsychologicalProfile.
  ///
  /// In en, this message translates to:
  /// **'Psychological Profile'**
  String get lblPsychologicalProfile;

  /// No description provided for @lblAuthorIntent.
  ///
  /// In en, this message translates to:
  /// **'Author Intent'**
  String get lblAuthorIntent;

  /// No description provided for @lblNoAnalysis.
  ///
  /// In en, this message translates to:
  /// **'No analysis.'**
  String get lblNoAnalysis;

  /// No description provided for @errNetworkOrTimeout.
  ///
  /// In en, this message translates to:
  /// **'Network error or timeout. Please try again. Reason: {reason}'**
  String errNetworkOrTimeout(String reason);

  /// No description provided for @errSystemError.
  ///
  /// In en, this message translates to:
  /// **'System error: {error}'**
  String errSystemError(String error);

  /// No description provided for @errInvalidWorkflow.
  ///
  /// In en, this message translates to:
  /// **'Error: Invalid Workflow Selection. Please refresh.'**
  String get errInvalidWorkflow;

  /// No description provided for @systemConfigsTitle.
  ///
  /// In en, this message translates to:
  /// **'System Configs'**
  String get systemConfigsTitle;

  /// No description provided for @modelRegistryDesc.
  ///
  /// In en, this message translates to:
  /// **'Configure globally available models, LLM parameters and API overrides.'**
  String get modelRegistryDesc;

  /// No description provided for @systemMetaTitle.
  ///
  /// In en, this message translates to:
  /// **'System Meta'**
  String get systemMetaTitle;

  /// No description provided for @configIdLabel.
  ///
  /// In en, this message translates to:
  /// **'Config ID'**
  String get configIdLabel;

  /// No description provided for @configTypeLabel.
  ///
  /// In en, this message translates to:
  /// **'Config Type'**
  String get configTypeLabel;

  /// No description provided for @maxTokensLabel.
  ///
  /// In en, this message translates to:
  /// **'Max Tokens'**
  String get maxTokensLabel;

  /// No description provided for @topPLabel.
  ///
  /// In en, this message translates to:
  /// **'Top-P (Nucleus Sampling)'**
  String get topPLabel;

  /// No description provided for @tpmLimitLabel.
  ///
  /// In en, this message translates to:
  /// **'TPM Limit (Tokens/Min)'**
  String get tpmLimitLabel;

  /// No description provided for @rpmLimitLabel.
  ///
  /// In en, this message translates to:
  /// **'RPM Limit (Requests/Min)'**
  String get rpmLimitLabel;

  /// No description provided for @parsingModeLabel.
  ///
  /// In en, this message translates to:
  /// **'Parsing Mode'**
  String get parsingModeLabel;

  /// No description provided for @isActiveLabel.
  ///
  /// In en, this message translates to:
  /// **'Is Active'**
  String get isActiveLabel;

  /// No description provided for @supportsGroundingLabel.
  ///
  /// In en, this message translates to:
  /// **'Supports Grounding'**
  String get supportsGroundingLabel;

  /// No description provided for @strategyLabel.
  ///
  /// In en, this message translates to:
  /// **'Strategy'**
  String get strategyLabel;

  /// No description provided for @noModelsDefined.
  ///
  /// In en, this message translates to:
  /// **'No models defined in registry.'**
  String get noModelsDefined;

  /// No description provided for @workflowEditTitle.
  ///
  /// In en, this message translates to:
  /// **'Edit DAG Workflow'**
  String get workflowEditTitle;

  /// No description provided for @workflowConfigTitle.
  ///
  /// In en, this message translates to:
  /// **'Workflow Configuration'**
  String get workflowConfigTitle;

  /// No description provided for @workflowIdLabel.
  ///
  /// In en, this message translates to:
  /// **'Workflow ID (e.g. analysis_pipeline)'**
  String get workflowIdLabel;

  /// No description provided for @workflowNameLabel.
  ///
  /// In en, this message translates to:
  /// **'Workflow Name'**
  String get workflowNameLabel;

  /// No description provided for @workflowInputsTitle.
  ///
  /// In en, this message translates to:
  /// **'Expected Inputs (Global Roles)'**
  String get workflowInputsTitle;

  /// No description provided for @workflowAddInputBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Input'**
  String get workflowAddInputBtn;

  /// No description provided for @workflowStepsTitle.
  ///
  /// In en, this message translates to:
  /// **'Execution Steps (DAG Graph)'**
  String get workflowStepsTitle;

  /// No description provided for @workflowAddStepBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Step'**
  String get workflowAddStepBtn;

  /// No description provided for @workflowRoleKeyLabel.
  ///
  /// In en, this message translates to:
  /// **'Role Key (e.g. source_text)'**
  String get workflowRoleKeyLabel;

  /// No description provided for @workflowDescLabel.
  ///
  /// In en, this message translates to:
  /// **'Description'**
  String get workflowDescLabel;

  /// No description provided for @workflowTypeString.
  ///
  /// In en, this message translates to:
  /// **'String (Text)'**
  String get workflowTypeString;

  /// No description provided for @workflowTypeFile.
  ///
  /// In en, this message translates to:
  /// **'File (PDF/Word)'**
  String get workflowTypeFile;

  /// No description provided for @workflowTypeJson.
  ///
  /// In en, this message translates to:
  /// **'JSON Struct'**
  String get workflowTypeJson;

  /// No description provided for @workflowStepIdLabel.
  ///
  /// In en, this message translates to:
  /// **'Step ID (e.g. initial_eval)'**
  String get workflowStepIdLabel;

  /// No description provided for @workflowAgentTypeLabel.
  ///
  /// In en, this message translates to:
  /// **'Role (Cognitive Strategy)'**
  String get workflowAgentTypeLabel;

  /// No description provided for @workflowDependsOnLabel.
  ///
  /// In en, this message translates to:
  /// **'Depends On (DAG Edges):'**
  String get workflowDependsOnLabel;

  /// No description provided for @workflowNoPrevSteps.
  ///
  /// In en, this message translates to:
  /// **'No previous steps available.'**
  String get workflowNoPrevSteps;

  /// No description provided for @workflowInputMappingsLabel.
  ///
  /// In en, this message translates to:
  /// **'Input Mappings (Semantic Routing):'**
  String get workflowInputMappingsLabel;

  /// No description provided for @workflowAgentInputKey.
  ///
  /// In en, this message translates to:
  /// **'Agent Input Key (e.g. source_text)'**
  String get workflowAgentInputKey;

  /// No description provided for @workflowSourceVarLabel.
  ///
  /// In en, this message translates to:
  /// **'Source Var (e.g. \$inputs.data)'**
  String get workflowSourceVarLabel;

  /// No description provided for @workflowAddMappingBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Mapping'**
  String get workflowAddMappingBtn;

  /// No description provided for @workflowInputKeyLabel.
  ///
  /// In en, this message translates to:
  /// **'Input Key/Role (e.g. product_text)'**
  String get workflowInputKeyLabel;

  /// No description provided for @workflowDeleteInputTooltip.
  ///
  /// In en, this message translates to:
  /// **'Delete Input'**
  String get workflowDeleteInputTooltip;

  /// No description provided for @workflowInputRequired.
  ///
  /// In en, this message translates to:
  /// **'Required'**
  String get workflowInputRequired;

  /// No description provided for @workflowInputIsChatHistory.
  ///
  /// In en, this message translates to:
  /// **'Is Chat History (LLM Parse)'**
  String get workflowInputIsChatHistory;

  /// No description provided for @workflowInputModesLabel.
  ///
  /// In en, this message translates to:
  /// **'Input Modes:'**
  String get workflowInputModesLabel;

  /// No description provided for @inputModeFile.
  ///
  /// In en, this message translates to:
  /// **'file'**
  String get inputModeFile;

  /// No description provided for @inputModePaste.
  ///
  /// In en, this message translates to:
  /// **'paste'**
  String get inputModePaste;

  /// No description provided for @inputModeQuestionnaire.
  ///
  /// In en, this message translates to:
  /// **'questionnaire'**
  String get inputModeQuestionnaire;

  /// No description provided for @workflowInputLabelTitle.
  ///
  /// In en, this message translates to:
  /// **'Label (UI Form Title)'**
  String get workflowInputLabelTitle;

  /// No description provided for @workflowInputDescriptionTitle.
  ///
  /// In en, this message translates to:
  /// **'Description (UI Hint)'**
  String get workflowInputDescriptionTitle;

  /// No description provided for @workflowInputAiDescriptionTitle.
  ///
  /// In en, this message translates to:
  /// **'AI Semantic Description (For LLM Grounding)'**
  String get workflowInputAiDescriptionTitle;

  /// No description provided for @workflowInputQuestionnaireDefTitle.
  ///
  /// In en, this message translates to:
  /// **'Questionnaire Definition:'**
  String get workflowInputQuestionnaireDefTitle;

  /// No description provided for @workflowInputNoQuestionsDefined.
  ///
  /// In en, this message translates to:
  /// **'No questions defined yet. Add one below.'**
  String get workflowInputNoQuestionsDefined;

  /// No description provided for @workflowInputQuestionIdLabel.
  ///
  /// In en, this message translates to:
  /// **'Question ID (e.g. q1)'**
  String get workflowInputQuestionIdLabel;

  /// No description provided for @workflowInputQuestionTextLabel.
  ///
  /// In en, this message translates to:
  /// **'Question Text'**
  String get workflowInputQuestionTextLabel;

  /// No description provided for @workflowInputAddQuestionBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Question'**
  String get workflowInputAddQuestionBtn;

  /// No description provided for @mockLoginSuccess.
  ///
  /// In en, this message translates to:
  /// **'Mock Login Successful! Redirecting...'**
  String get mockLoginSuccess;

  /// No description provided for @mockLoginFailed.
  ///
  /// In en, this message translates to:
  /// **'Mock login failed. Verify user data: {error}'**
  String mockLoginFailed(String error);

  /// No description provided for @actionHintCheckInput.
  ///
  /// In en, this message translates to:
  /// **'Hint: Please check your input and try again.'**
  String get actionHintCheckInput;

  /// No description provided for @actionHintLoginAgain.
  ///
  /// In en, this message translates to:
  /// **'Hint: Session expired. Please log in again.'**
  String get actionHintLoginAgain;

  /// No description provided for @actionHintTryAgainLater.
  ///
  /// In en, this message translates to:
  /// **'Hint: Server error. Please wait a moment and try again.'**
  String get actionHintTryAgainLater;

  /// No description provided for @actionHintContactSupport.
  ///
  /// In en, this message translates to:
  /// **'Hint: If the issue persists, contact support.'**
  String get actionHintContactSupport;

  /// No description provided for @actionHintRunIngestion.
  ///
  /// In en, this message translates to:
  /// **'Hint: Please upload documents to the Knowledge Base first.'**
  String get actionHintRunIngestion;

  /// No description provided for @actionHintCheckUrl.
  ///
  /// In en, this message translates to:
  /// **'Hint: Please verify the spelling of the URL.'**
  String get actionHintCheckUrl;

  /// No description provided for @actionHintCheckConnection.
  ///
  /// In en, this message translates to:
  /// **'Hint: Please check your network connection.'**
  String get actionHintCheckConnection;

  /// No description provided for @confirmDeletionTitle.
  ///
  /// In en, this message translates to:
  /// **'Confirm Deletion'**
  String get confirmDeletionTitle;

  /// No description provided for @confirmDeletionMessage.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete this execution? This action cannot be undone.'**
  String get confirmDeletionMessage;

  /// No description provided for @executionsDashboardTitle.
  ///
  /// In en, this message translates to:
  /// **'Executions Dashboard'**
  String get executionsDashboardTitle;

  /// No description provided for @newAnalysisPipelineTitle.
  ///
  /// In en, this message translates to:
  /// **'New Analysis Pipeline (SDUI)'**
  String get newAnalysisPipelineTitle;

  /// No description provided for @liveExecutionTitle.
  ///
  /// In en, this message translates to:
  /// **'Live Execution'**
  String get liveExecutionTitle;

  /// No description provided for @establishingConnection.
  ///
  /// In en, this message translates to:
  /// **'Establishing connection...'**
  String get establishingConnection;

  /// No description provided for @statusLabel.
  ///
  /// In en, this message translates to:
  /// **'Status: {status}'**
  String statusLabel(String status);

  /// No description provided for @auditDriftWarning.
  ///
  /// In en, this message translates to:
  /// **'Audit Drift Warning: This execution was completed with system parameters ({versionId}) that differ from the current active ruleset (v2.0.0). Results should be interpreted with caution.'**
  String auditDriftWarning(String versionId);

  /// No description provided for @noUiHintsAvailable.
  ///
  /// In en, this message translates to:
  /// **'No UI hints available yet. Waiting for stream...'**
  String get noUiHintsAvailable;

  /// No description provided for @executionStartedSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Execution started successfully!'**
  String get executionStartedSuccessfully;

  /// No description provided for @failedToStartExecution.
  ///
  /// In en, this message translates to:
  /// **'Failed to start execution: {error}'**
  String failedToStartExecution(String error);

  /// No description provided for @executionDeletedSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Execution deleted successfully.'**
  String get executionDeletedSuccessfully;

  /// No description provided for @failedToDeleteExecution.
  ///
  /// In en, this message translates to:
  /// **'Failed to delete execution: {error}'**
  String failedToDeleteExecution(String error);

  /// No description provided for @selectWorkflowPrompt.
  ///
  /// In en, this message translates to:
  /// **'Select a workflow from the list to begin.'**
  String get selectWorkflowPrompt;

  /// No description provided for @noInputsRequired.
  ///
  /// In en, this message translates to:
  /// **'No inputs strictly required for \n{id}'**
  String noInputsRequired(String id);

  /// No description provided for @configureInputsFor.
  ///
  /// In en, this message translates to:
  /// **'Configure Inputs for {id}'**
  String configureInputsFor(String id);

  /// No description provided for @inputLabel.
  ///
  /// In en, this message translates to:
  /// **'Input: {key}'**
  String inputLabel(String key);

  /// No description provided for @selectedFile.
  ///
  /// In en, this message translates to:
  /// **'Selected: {fileName}'**
  String selectedFile(String fileName);

  /// No description provided for @noFileSelected.
  ///
  /// In en, this message translates to:
  /// **'No file selected'**
  String get noFileSelected;

  /// No description provided for @browseFile.
  ///
  /// In en, this message translates to:
  /// **'Browse'**
  String get browseFile;

  /// No description provided for @inputTypeHint.
  ///
  /// In en, this message translates to:
  /// **'Type: {typeHint}'**
  String inputTypeHint(String typeHint);

  /// No description provided for @questionnaireTitle.
  ///
  /// In en, this message translates to:
  /// **'Questionnaire: {title}'**
  String questionnaireTitle(String title);

  /// No description provided for @startAiExecution.
  ///
  /// In en, this message translates to:
  /// **'Start AI Execution'**
  String get startAiExecution;

  /// No description provided for @barsCompliance1.
  ///
  /// In en, this message translates to:
  /// **'Critically Misaligned - Completely random process'**
  String get barsCompliance1;

  /// No description provided for @barsCompliance2.
  ///
  /// In en, this message translates to:
  /// **'Misaligned - Scattered process adherence'**
  String get barsCompliance2;

  /// No description provided for @barsCompliance3.
  ///
  /// In en, this message translates to:
  /// **'Neutral - Some process visible'**
  String get barsCompliance3;

  /// No description provided for @barsCompliance4.
  ///
  /// In en, this message translates to:
  /// **'Aligned - Adheres to industry standards'**
  String get barsCompliance4;

  /// No description provided for @barsCompliance5.
  ///
  /// In en, this message translates to:
  /// **'Strongly Aligned - Perfect State-of-the-Art practice'**
  String get barsCompliance5;

  /// No description provided for @barsRole1.
  ///
  /// In en, this message translates to:
  /// **'Passenger - Passive requester'**
  String get barsRole1;

  /// No description provided for @barsRole2.
  ///
  /// In en, this message translates to:
  /// **'Navigator - Navigates existing data'**
  String get barsRole2;

  /// No description provided for @barsRole3.
  ///
  /// In en, this message translates to:
  /// **'Driver - Active director'**
  String get barsRole3;

  /// No description provided for @barsRole4.
  ///
  /// In en, this message translates to:
  /// **'Architect - Strategic planner'**
  String get barsRole4;

  /// No description provided for @barsStrategy1.
  ///
  /// In en, this message translates to:
  /// **'Zero-shot'**
  String get barsStrategy1;

  /// No description provided for @barsStrategy2.
  ///
  /// In en, this message translates to:
  /// **'Few-shot'**
  String get barsStrategy2;

  /// No description provided for @barsStrategy3.
  ///
  /// In en, this message translates to:
  /// **'Chain-of-Thought'**
  String get barsStrategy3;

  /// No description provided for @barsSim1.
  ///
  /// In en, this message translates to:
  /// **'Impossible (True dependence)'**
  String get barsSim1;

  /// No description provided for @barsSim2.
  ///
  /// In en, this message translates to:
  /// **'Possible (Dependent)'**
  String get barsSim2;

  /// No description provided for @barsSim3.
  ///
  /// In en, this message translates to:
  /// **'Probable (Independent)'**
  String get barsSim3;

  /// No description provided for @barsConf0.
  ///
  /// In en, this message translates to:
  /// **'Completely uncertain (0%)'**
  String get barsConf0;

  /// No description provided for @barsConf25.
  ///
  /// In en, this message translates to:
  /// **'Uncertain (25%)'**
  String get barsConf25;

  /// No description provided for @barsConf50.
  ///
  /// In en, this message translates to:
  /// **'Neutral (50%)'**
  String get barsConf50;

  /// No description provided for @barsConf75.
  ///
  /// In en, this message translates to:
  /// **'Fairly certain (75%)'**
  String get barsConf75;

  /// No description provided for @barsConf100.
  ///
  /// In en, this message translates to:
  /// **'Absolutely certain (100%)'**
  String get barsConf100;

  /// No description provided for @barsRisk1.
  ///
  /// In en, this message translates to:
  /// **'Low risk (Safe)'**
  String get barsRisk1;

  /// No description provided for @barsRisk2.
  ///
  /// In en, this message translates to:
  /// **'Medium risk (Warning)'**
  String get barsRisk2;

  /// No description provided for @barsRisk3.
  ///
  /// In en, this message translates to:
  /// **'High risk (Lazy prompt)'**
  String get barsRisk3;

  /// No description provided for @rawOutputFallbackTitle.
  ///
  /// In en, this message translates to:
  /// **'Raw Output (UI Missing)'**
  String get rawOutputFallbackTitle;
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
