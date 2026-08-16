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

  /// No description provided for @errorUnknown.
  ///
  /// In en, this message translates to:
  /// **'Unknown error'**
  String get errorUnknown;

  /// No description provided for @errorSseConnectionAborted.
  ///
  /// In en, this message translates to:
  /// **'Connection dropped unexpectedly (Server crashed or shut down). You can safely resume the execution using the \'Try again\' button.'**
  String get errorSseConnectionAborted;

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

  /// Message shown when the AI self-correction circuit breaker triggers
  ///
  /// In en, this message translates to:
  /// **'Quality Assurance: The AI detected an inconsistency and is verifying its reasoning (Attempt 2)...'**
  String get eventLlmAnomalyRetry;

  /// No description provided for @errorValidationMissing.
  ///
  /// In en, this message translates to:
  /// **'Missing required fields: {fields}'**
  String errorValidationMissing(String fields);

  /// No description provided for @sduiMetadataCosts.
  ///
  /// In en, this message translates to:
  /// **'Meta Costs'**
  String get sduiMetadataCosts;

  /// No description provided for @sduiMetadataTokens.
  ///
  /// In en, this message translates to:
  /// **'Meta Tokens'**
  String get sduiMetadataTokens;

  /// No description provided for @errorDataMapping.
  ///
  /// In en, this message translates to:
  /// **'Mapping Error in field \'{field}\': {detail}'**
  String errorDataMapping(String field, String detail);

  /// No description provided for @errorDataType.
  ///
  /// In en, this message translates to:
  /// **'Type Error in field \'{field}\': {detail}'**
  String errorDataType(String field, String detail);

  /// No description provided for @errorLoadingData.
  ///
  /// In en, this message translates to:
  /// **'Error loading data. Please try again.'**
  String get errorLoadingData;

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

  /// Subtitle showing matrix rule counts
  ///
  /// In en, this message translates to:
  /// **'Rules: {rules}'**
  String matrixSubtitle(int rules);

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

  /// No description provided for @rerunExecutionTooltip.
  ///
  /// In en, this message translates to:
  /// **'Re-run this analysis (clones data)'**
  String get rerunExecutionTooltip;

  /// No description provided for @rerunExecutionSuccess.
  ///
  /// In en, this message translates to:
  /// **'New analysis spawned successfully!'**
  String get rerunExecutionSuccess;

  /// No description provided for @rerunExecutionFailed.
  ///
  /// In en, this message translates to:
  /// **'Cloning failed: {error}'**
  String rerunExecutionFailed(String error);

  /// No description provided for @regenerateProfileTooltip.
  ///
  /// In en, this message translates to:
  /// **'Regenerate only this report via AI'**
  String get regenerateProfileTooltip;

  /// No description provided for @regenerateProfileSuccess.
  ///
  /// In en, this message translates to:
  /// **'Regeneration scheduled! You can now open the report.'**
  String get regenerateProfileSuccess;

  /// No description provided for @regenerateProfileFailed.
  ///
  /// In en, this message translates to:
  /// **'Failed to restart generation: {error}'**
  String regenerateProfileFailed(String error);

  /// No description provided for @xaiEvidenceImpactedAxes.
  ///
  /// In en, this message translates to:
  /// **'This information was used in evaluating the following axes:'**
  String get xaiEvidenceImpactedAxes;

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

  /// No description provided for @scorecard_evaluative_matrices_title.
  ///
  /// In en, this message translates to:
  /// **'Evaluative Matrices'**
  String get scorecard_evaluative_matrices_title;

  /// No description provided for @scorecard_informational_matrices_title.
  ///
  /// In en, this message translates to:
  /// **'Informational Matrices'**
  String get scorecard_informational_matrices_title;

  /// No description provided for @scorecard_global_average.
  ///
  /// In en, this message translates to:
  /// **'Global Average'**
  String get scorecard_global_average;

  /// No description provided for @scorecard_matrix_summary.
  ///
  /// In en, this message translates to:
  /// **'Matrix Summary'**
  String get scorecard_matrix_summary;

  /// No description provided for @atomicBreakdownTitle.
  ///
  /// In en, this message translates to:
  /// **'Level Breakdown'**
  String get atomicBreakdownTitle;

  /// No description provided for @rowExplanationTitle.
  ///
  /// In en, this message translates to:
  /// **'Explanation'**
  String get rowExplanationTitle;

  /// No description provided for @normalizedScore.
  ///
  /// In en, this message translates to:
  /// **'100 %'**
  String get normalizedScore;

  /// No description provided for @matrixEvaluativeAsteriskLegend.
  ///
  /// In en, this message translates to:
  /// **'* = Evaluative Matrix (Impacts global score)'**
  String get matrixEvaluativeAsteriskLegend;

  /// No description provided for @matrixOverrideAsteriskLegend.
  ///
  /// In en, this message translates to:
  /// **'** = Contextual override allowed'**
  String get matrixOverrideAsteriskLegend;

  /// No description provided for @reportPenaltiesApplied.
  ///
  /// In en, this message translates to:
  /// **'Penalties (Applied Biases)'**
  String get reportPenaltiesApplied;

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

  /// No description provided for @statusLabelQueued.
  ///
  /// In en, this message translates to:
  /// **'QUEUED'**
  String get statusLabelQueued;

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
  /// **'Rejected'**
  String get statusRejected;

  /// No description provided for @statusDraft.
  ///
  /// In en, this message translates to:
  /// **'DRAFT'**
  String get statusDraft;

  /// No description provided for @typeString.
  ///
  /// In en, this message translates to:
  /// **'String'**
  String get typeString;

  /// No description provided for @typeFloat.
  ///
  /// In en, this message translates to:
  /// **'Float'**
  String get typeFloat;

  /// No description provided for @typeInt.
  ///
  /// In en, this message translates to:
  /// **'Integer (Whole Number)'**
  String get typeInt;

  /// No description provided for @typeJson.
  ///
  /// In en, this message translates to:
  /// **'JSON'**
  String get typeJson;

  /// No description provided for @typeBoolean.
  ///
  /// In en, this message translates to:
  /// **'Boolean'**
  String get typeBoolean;

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

  /// No description provided for @statusQueued.
  ///
  /// In en, this message translates to:
  /// **'Queued'**
  String get statusQueued;

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

  /// No description provided for @printVariantSelectorTitle.
  ///
  /// In en, this message translates to:
  /// **'Select Print Variant'**
  String get printVariantSelectorTitle;

  /// No description provided for @printVariantSelectorDescription.
  ///
  /// In en, this message translates to:
  /// **'Choose a variant for this execution report.'**
  String get printVariantSelectorDescription;

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

  /// No description provided for @lblReasoning.
  ///
  /// In en, this message translates to:
  /// **'Reasoning'**
  String get lblReasoning;

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
  /// **'Competency Areas'**
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

  /// No description provided for @frequencyPenaltyLabel.
  ///
  /// In en, this message translates to:
  /// **'Frequency Penalty'**
  String get frequencyPenaltyLabel;

  /// No description provided for @presencePenaltyLabel.
  ///
  /// In en, this message translates to:
  /// **'Presence Penalty'**
  String get presencePenaltyLabel;

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

  /// No description provided for @workflowDeleteConfirmTitle.
  ///
  /// In en, this message translates to:
  /// **'Delete Workflow'**
  String get workflowDeleteConfirmTitle;

  /// No description provided for @workflowDeleteConfirmDesc.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete workflow \"{id}\"?'**
  String workflowDeleteConfirmDesc(String id);

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
  /// **'Step ID (UUID or Unique String)'**
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
  /// **'Delete Step'**
  String get stepDeleteConfirmTitle;

  /// No description provided for @stepDeleteConfirmMessage.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete step \"{id}\"?'**
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

  /// No description provided for @errDataCorruptionDesc.
  ///
  /// In en, this message translates to:
  /// **'Data integrity error: The heavy data file associated with this record could not be found on the physical disk. A report cannot be generated.'**
  String get errDataCorruptionDesc;

  /// No description provided for @actionHintRunAgain.
  ///
  /// In en, this message translates to:
  /// **'Hint: You must execute this analysis again to generate new data.'**
  String get actionHintRunAgain;

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

  /// No description provided for @topKLabel.
  ///
  /// In en, this message translates to:
  /// **'Top-K (Candidates)'**
  String get topKLabel;

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

  /// No description provided for @cachingStrategyLabel.
  ///
  /// In en, this message translates to:
  /// **'Caching Strategy'**
  String get cachingStrategyLabel;

  /// No description provided for @additionalParamsLabel.
  ///
  /// In en, this message translates to:
  /// **'Additional Parameters (JSON)'**
  String get additionalParamsLabel;

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

  /// No description provided for @workflowSlugLabel.
  ///
  /// In en, this message translates to:
  /// **'Workflow Identifier (URL slug, lowercase and underscores only, e.g., holistic_audit)'**
  String get workflowSlugLabel;

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
  /// **'Role Key (e.g. source_text, represents a global role)'**
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

  /// No description provided for @executionPersonaTitle.
  ///
  /// In en, this message translates to:
  /// **'Execution Persona Block'**
  String get executionPersonaTitle;

  /// No description provided for @executionPersonaDescription.
  ///
  /// In en, this message translates to:
  /// **'Select the global behavioral profile for the AI (e.g. XAI Reporter, Coach).'**
  String get executionPersonaDescription;

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
  /// **'Agent Input Key (e.g. inputs)'**
  String get workflowAgentInputKey;

  /// No description provided for @workflowSourceVarLabel.
  ///
  /// In en, this message translates to:
  /// **'Data Source (e.g. \$inputs)'**
  String get workflowSourceVarLabel;

  /// No description provided for @workflowMappingHelperTitle.
  ///
  /// In en, this message translates to:
  /// **'How does Semantic Routing work?'**
  String get workflowMappingHelperTitle;

  /// No description provided for @workflowMappingHelperDesc.
  ///
  /// In en, this message translates to:
  /// **'1. Left side (Agent Input Key) is the XML tag name the AI will use to read the data. In V2 Architecture, it is almost always just the word \'inputs\' (lower_snake_case).\n2. Right side is the data source. \'\$inputs\' captures all values provided by the user in the form. \'\$steps.step_x.outputs\' directly connects the previous agent\'s output as an input here.\nTo pass a hardcoded rule (e.g. the word \'doctor\'), simply type it on the right side without a dollar sign.'**
  String get workflowMappingHelperDesc;

  /// No description provided for @workflowAddMappingBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Mapping'**
  String get workflowAddMappingBtn;

  /// No description provided for @workflowInputKeyLabel.
  ///
  /// In en, this message translates to:
  /// **'Input Key/Role (e.g. product_text, the role this input binds to in the workflow)'**
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
  /// **'Label (UI Form Title, e.g. \'Final Product\')'**
  String get workflowInputLabelTitle;

  /// No description provided for @workflowInputDescriptionTitle.
  ///
  /// In en, this message translates to:
  /// **'Description (UI Hint, e.g. \'Paste the final product in PDF format\')'**
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
  /// **'Hint: Please wait a moment and try again.'**
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

  /// No description provided for @reportTitleMain.
  ///
  /// In en, this message translates to:
  /// **'Execution Report'**
  String get reportTitleMain;

  /// No description provided for @reportMetrics.
  ///
  /// In en, this message translates to:
  /// **'Performance Metrics'**
  String get reportMetrics;

  /// No description provided for @reportScore.
  ///
  /// In en, this message translates to:
  /// **'Total Score'**
  String get reportScore;

  /// No description provided for @xAxisLabel.
  ///
  /// In en, this message translates to:
  /// **'X-Axis (Matrix ID)'**
  String get xAxisLabel;

  /// No description provided for @yAxisLabel.
  ///
  /// In en, this message translates to:
  /// **'Y-Axis (Matrix ID)'**
  String get yAxisLabel;

  /// No description provided for @zAxisLabel.
  ///
  /// In en, this message translates to:
  /// **'Z-Axis (Matrix ID)'**
  String get zAxisLabel;

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

  /// No description provided for @strictnessLevelTitle.
  ///
  /// In en, this message translates to:
  /// **'Strictness Level'**
  String get strictnessLevelTitle;

  /// No description provided for @strictnessGricean.
  ///
  /// In en, this message translates to:
  /// **'Level 1: Cooperative (Gricean)'**
  String get strictnessGricean;

  /// No description provided for @strictnessLiteral.
  ///
  /// In en, this message translates to:
  /// **'Level 2: Literal (Lexical)'**
  String get strictnessLiteral;

  /// No description provided for @strictnessCausal.
  ///
  /// In en, this message translates to:
  /// **'Level 3: Causal (Default)'**
  String get strictnessCausal;

  /// No description provided for @strictnessFalsification.
  ///
  /// In en, this message translates to:
  /// **'Level 4: Adversarial (Falsification)'**
  String get strictnessFalsification;

  /// No description provided for @strictnessZeroTrust.
  ///
  /// In en, this message translates to:
  /// **'Level 5: Zero-Trust'**
  String get strictnessZeroTrust;

  /// No description provided for @strictnessWarningLvl4.
  ///
  /// In en, this message translates to:
  /// **'Warning: Level 4 is adversarial and searches for flaws. Expect significantly lower scores.'**
  String get strictnessWarningLvl4;

  /// No description provided for @strictnessWarningLvl5.
  ///
  /// In en, this message translates to:
  /// **'Warning: Zero-Trust. Zero points unless external frameworks and hard evidence are used flawlessly.'**
  String get strictnessWarningLvl5;

  /// No description provided for @strictnessFullFlex.
  ///
  /// In en, this message translates to:
  /// **'Full Flexibility (0)'**
  String get strictnessFullFlex;

  /// No description provided for @strictnessLenient.
  ///
  /// In en, this message translates to:
  /// **'Lenient (15)'**
  String get strictnessLenient;

  /// No description provided for @strictnessBalanced.
  ///
  /// In en, this message translates to:
  /// **'Balanced (50 - Default)'**
  String get strictnessBalanced;

  /// No description provided for @strictnessStrict.
  ///
  /// In en, this message translates to:
  /// **'Strict (85)'**
  String get strictnessStrict;

  /// No description provided for @strictnessAbsolute.
  ///
  /// In en, this message translates to:
  /// **'Absolute Strictness (100)'**
  String get strictnessAbsolute;

  /// No description provided for @strictnessSelectorTitle.
  ///
  /// In en, this message translates to:
  /// **'Evaluation Strictness'**
  String get strictnessSelectorTitle;

  /// No description provided for @strictnessSelectorDescription.
  ///
  /// In en, this message translates to:
  /// **'Define how rigorously the AI must enforce rules and validate evidence.'**
  String get strictnessSelectorDescription;

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

  /// No description provided for @adminAiDescriptionHint.
  ///
  /// In en, this message translates to:
  /// **'MANDATORY: Must be written in English. Cognitive prompt, not user data. Only input business logic, NOT system rules.'**
  String get adminAiDescriptionHint;

  /// No description provided for @adminBilingualPromptHint.
  ///
  /// In en, this message translates to:
  /// **'MANDATORY: English translation required. Use EXTREME PRECISION. This text directly dictates the AI\'s cognitive reasoning and structural rules.'**
  String get adminBilingualPromptHint;

  /// No description provided for @adminPromptBestPracticesHint.
  ///
  /// In en, this message translates to:
  /// **'BEST PRACTICE: Use command keywords like ROLE:, TASK:, RULE: and CONTEXT:. NEVER translate these keywords into Finnish inside the text.'**
  String get adminPromptBestPracticesHint;

  /// No description provided for @blueprintEditorTitle.
  ///
  /// In en, this message translates to:
  /// **'Blueprint Editor'**
  String get blueprintEditorTitle;

  /// No description provided for @blueprintComponentsTitle.
  ///
  /// In en, this message translates to:
  /// **'Components'**
  String get blueprintComponentsTitle;

  /// No description provided for @blueprintAddComponentBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Component'**
  String get blueprintAddComponentBtn;

  /// No description provided for @blueprintEmptyStateMsg.
  ///
  /// In en, this message translates to:
  /// **'No components added yet. Add a component to start building the report.'**
  String get blueprintEmptyStateMsg;

  /// No description provided for @blueprintComponentHeader.
  ///
  /// In en, this message translates to:
  /// **'Header'**
  String get blueprintComponentHeader;

  /// No description provided for @blueprintComponentMetadataHeader.
  ///
  /// In en, this message translates to:
  /// **'Metadata Header'**
  String get blueprintComponentMetadataHeader;

  /// No description provided for @blueprintComponentBibliography.
  ///
  /// In en, this message translates to:
  /// **'Bibliography'**
  String get blueprintComponentBibliography;

  /// No description provided for @blueprintComponent1dGauge.
  ///
  /// In en, this message translates to:
  /// **'1D Gauge'**
  String get blueprintComponent1dGauge;

  /// No description provided for @blueprintComponent2dMatrix.
  ///
  /// In en, this message translates to:
  /// **'2D Matrix'**
  String get blueprintComponent2dMatrix;

  /// No description provided for @blueprintComponent3dScatter.
  ///
  /// In en, this message translates to:
  /// **'3D Scatter'**
  String get blueprintComponent3dScatter;

  /// No description provided for @blueprintComponentEvaluationNotes.
  ///
  /// In en, this message translates to:
  /// **'Evaluation Notes'**
  String get blueprintComponentEvaluationNotes;

  /// No description provided for @blueprintSettingsTitle.
  ///
  /// In en, this message translates to:
  /// **'Component Settings'**
  String get blueprintSettingsTitle;

  /// No description provided for @blueprintSettingsSave.
  ///
  /// In en, this message translates to:
  /// **'Save Component'**
  String get blueprintSettingsSave;

  /// No description provided for @blueprintSaveBlueprint.
  ///
  /// In en, this message translates to:
  /// **'Save Blueprint'**
  String get blueprintSaveBlueprint;

  /// No description provided for @blueprintSaveSuccess.
  ///
  /// In en, this message translates to:
  /// **'Blueprint saved successfully'**
  String get blueprintSaveSuccess;

  /// No description provided for @blueprintSaveFailed.
  ///
  /// In en, this message translates to:
  /// **'Failed to save blueprint: {error}'**
  String blueprintSaveFailed(String error);

  /// No description provided for @blueprintPropertyDataPath.
  ///
  /// In en, this message translates to:
  /// **'Data Path (\$results.X)'**
  String get blueprintPropertyDataPath;

  /// No description provided for @blueprintPropertyXAxis.
  ///
  /// In en, this message translates to:
  /// **'X Axis Path'**
  String get blueprintPropertyXAxis;

  /// No description provided for @blueprintPropertyYAxis.
  ///
  /// In en, this message translates to:
  /// **'Y Axis Path'**
  String get blueprintPropertyYAxis;

  /// No description provided for @blueprintPropertyZAxis.
  ///
  /// In en, this message translates to:
  /// **'Z Axis Path'**
  String get blueprintPropertyZAxis;

  /// No description provided for @blueprintPropertyXAxisNote.
  ///
  /// In en, this message translates to:
  /// **'X Axis Note Path'**
  String get blueprintPropertyXAxisNote;

  /// No description provided for @blueprintPropertyYAxisNote.
  ///
  /// In en, this message translates to:
  /// **'Y Axis Note Path'**
  String get blueprintPropertyYAxisNote;

  /// No description provided for @blueprintPropertyTitle.
  ///
  /// In en, this message translates to:
  /// **'Title (i18n Key or Text)'**
  String get blueprintPropertyTitle;

  /// No description provided for @blueprintPropertyDataPathsInfo.
  ///
  /// In en, this message translates to:
  /// **'Comma-separated paths'**
  String get blueprintPropertyDataPathsInfo;

  /// No description provided for @downloadSuccess.
  ///
  /// In en, this message translates to:
  /// **'PDF Downloaded Successfully'**
  String get downloadSuccess;

  /// No description provided for @i18nAddLanguageVersion.
  ///
  /// In en, this message translates to:
  /// **'Add Language Version'**
  String get i18nAddLanguageVersion;

  /// No description provided for @i18nLanguageCodePlaceholder.
  ///
  /// In en, this message translates to:
  /// **'Language Code (e.g., en, sv)'**
  String get i18nLanguageCodePlaceholder;

  /// No description provided for @i18nLanguageCodeHelp.
  ///
  /// In en, this message translates to:
  /// **'An inline editor box will be added for this language.'**
  String get i18nLanguageCodeHelp;

  /// No description provided for @i18nCancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get i18nCancel;

  /// No description provided for @i18nCreate.
  ///
  /// In en, this message translates to:
  /// **'Create'**
  String get i18nCreate;

  /// No description provided for @i18nAddTranslation.
  ///
  /// In en, this message translates to:
  /// **'Add Translation'**
  String get i18nAddTranslation;

  /// No description provided for @i18nDefaultFormLabel.
  ///
  /// In en, this message translates to:
  /// **'Default Form ({locale} usually expected)'**
  String i18nDefaultFormLabel(String locale);

  /// No description provided for @i18nOtherTranslations.
  ///
  /// In en, this message translates to:
  /// **'Other Translations:'**
  String get i18nOtherTranslations;

  /// No description provided for @i18nDeleteTranslation.
  ///
  /// In en, this message translates to:
  /// **'Delete translation'**
  String get i18nDeleteTranslation;

  /// No description provided for @i18nTranslateToPlaceholder.
  ///
  /// In en, this message translates to:
  /// **'Translate to {locale}...'**
  String i18nTranslateToPlaceholder(String locale);

  /// No description provided for @workflowCloneBtn.
  ///
  /// In en, this message translates to:
  /// **'Clone Workflow'**
  String get workflowCloneBtn;

  /// No description provided for @workflowCloneSuccess.
  ///
  /// In en, this message translates to:
  /// **'Workflow Cloned successfully'**
  String get workflowCloneSuccess;

  /// No description provided for @workflowCloneErrorMissingDep.
  ///
  /// In en, this message translates to:
  /// **'Clone failed: Step dependency points to a non-existent step.'**
  String get workflowCloneErrorMissingDep;

  /// No description provided for @workflowSharedBlueprintWarning.
  ///
  /// In en, this message translates to:
  /// **'Cloning a workflow will create a deep copy of the workflow configuration, but it will STILL reference the same Steps (DAG Nodes) by ID. If you edit a Step, it will be edited for both workflows. Are you sure you want to clone?'**
  String get workflowSharedBlueprintWarning;

  /// No description provided for @overall_system_profile.
  ///
  /// In en, this message translates to:
  /// **'Overall System Profile'**
  String get overall_system_profile;

  /// No description provided for @blueprintSelectWorkflow.
  ///
  /// In en, this message translates to:
  /// **'Select Workflow'**
  String get blueprintSelectWorkflow;

  /// No description provided for @blueprintVariantName.
  ///
  /// In en, this message translates to:
  /// **'Variant Name'**
  String get blueprintVariantName;

  /// No description provided for @blueprintDefaultVariant.
  ///
  /// In en, this message translates to:
  /// **'default'**
  String get blueprintDefaultVariant;

  /// No description provided for @blueprintCopyVariant.
  ///
  /// In en, this message translates to:
  /// **'Copy Blueprint'**
  String get blueprintCopyVariant;

  /// No description provided for @blueprintGridRowLabel.
  ///
  /// In en, this message translates to:
  /// **'Grid Row'**
  String get blueprintGridRowLabel;

  /// No description provided for @blueprintGridRowDesc.
  ///
  /// In en, this message translates to:
  /// **'Number of columns'**
  String get blueprintGridRowDesc;

  /// No description provided for @blueprintChildComponents.
  ///
  /// In en, this message translates to:
  /// **'Parallel child components ({count}):'**
  String blueprintChildComponents(int count);

  /// No description provided for @blueprintAddChildBtn.
  ///
  /// In en, this message translates to:
  /// **'Add child component'**
  String get blueprintAddChildBtn;

  /// No description provided for @blueprintClearFormCache.
  ///
  /// In en, this message translates to:
  /// **'Clear Form Cache'**
  String get blueprintClearFormCache;

  /// No description provided for @blueprintTabTitle.
  ///
  /// In en, this message translates to:
  /// **'Blueprints'**
  String get blueprintTabTitle;

  /// No description provided for @blueprintTabDesc.
  ///
  /// In en, this message translates to:
  /// **'Manage SDUI report layouts and printouts.'**
  String get blueprintTabDesc;

  /// No description provided for @blueprintCreateNew.
  ///
  /// In en, this message translates to:
  /// **'Create New Blueprint'**
  String get blueprintCreateNew;

  /// No description provided for @blueprintVariantSelector.
  ///
  /// In en, this message translates to:
  /// **'Variant: {variant}'**
  String blueprintVariantSelector(String variant);

  /// No description provided for @reportEmptyProfile.
  ///
  /// In en, this message translates to:
  /// **'Empty profile (No layout blocks defined)'**
  String get reportEmptyProfile;

  /// No description provided for @reportUnknownOrg.
  ///
  /// In en, this message translates to:
  /// **'Unknown organization'**
  String get reportUnknownOrg;

  /// No description provided for @reportTopicProfile.
  ///
  /// In en, this message translates to:
  /// **'Topic & Profile: {name}'**
  String reportTopicProfile(String name);

  /// No description provided for @reportContext.
  ///
  /// In en, this message translates to:
  /// **'Context: {orgName}'**
  String reportContext(String orgName);

  /// No description provided for @reportTimestamp.
  ///
  /// In en, this message translates to:
  /// **'Timestamp: {timestamp}'**
  String reportTimestamp(String timestamp);

  /// No description provided for @reportCosts.
  ///
  /// In en, this message translates to:
  /// **'Costs'**
  String get reportCosts;

  /// No description provided for @reportApiPrice.
  ///
  /// In en, this message translates to:
  /// **'API Price: {price}'**
  String reportApiPrice(String price);

  /// No description provided for @reportCognitiveWork.
  ///
  /// In en, this message translates to:
  /// **'Cognitive Work (Tokens)'**
  String get reportCognitiveWork;

  /// No description provided for @reportTextSynthesis.
  ///
  /// In en, this message translates to:
  /// **'Text / Synthesis'**
  String get reportTextSynthesis;

  /// No description provided for @reportQuoteTitle.
  ///
  /// In en, this message translates to:
  /// **'💬 Excerpt from original text:\n{quote}'**
  String reportQuoteTitle(String quote);

  /// No description provided for @reportSemanticExplanationTitle.
  ///
  /// In en, this message translates to:
  /// **'💡 AI Semantic Explanation (Contextual Override):\n{reasoning}'**
  String reportSemanticExplanationTitle(String reasoning);

  /// No description provided for @reportFrameworkReference.
  ///
  /// In en, this message translates to:
  /// **'⚖️ Reference framework: {source}'**
  String reportFrameworkReference(String source);

  /// No description provided for @reportGoogleVerified.
  ///
  /// In en, this message translates to:
  /// **'Verified from Google sources:\n{citation}'**
  String reportGoogleVerified(String citation);

  /// No description provided for @reportInteractionMatrix2D.
  ///
  /// In en, this message translates to:
  /// **'Interaction Matrix (2D)'**
  String get reportInteractionMatrix2D;

  /// No description provided for @reportRadarAnalysis2D.
  ///
  /// In en, this message translates to:
  /// **'Radar Analysis (2D)'**
  String get reportRadarAnalysis2D;

  /// No description provided for @reportComparisonView.
  ///
  /// In en, this message translates to:
  /// **'Comparison View'**
  String get reportComparisonView;

  /// No description provided for @reportAnalyticalFramework3D.
  ///
  /// In en, this message translates to:
  /// **'Analytical Framework (3D)'**
  String get reportAnalyticalFramework3D;

  /// No description provided for @reportAnalyticalFramework2D.
  ///
  /// In en, this message translates to:
  /// **'Analytical Framework (2D)'**
  String get reportAnalyticalFramework2D;

  /// No description provided for @reportCoachingTitle.
  ///
  /// In en, this message translates to:
  /// **'💡 Coaching Tip'**
  String get reportCoachingTitle;

  /// No description provided for @reportFalsificationTitle.
  ///
  /// In en, this message translates to:
  /// **'⚖️ Devil\'s Advocate'**
  String get reportFalsificationTitle;

  /// No description provided for @reportMissingContextTitle.
  ///
  /// In en, this message translates to:
  /// **'🔍 Missing Context'**
  String get reportMissingContextTitle;

  /// No description provided for @reportRiskFlagTitle.
  ///
  /// In en, this message translates to:
  /// **'⚠️ High Risk Identified'**
  String get reportRiskFlagTitle;

  /// No description provided for @reportRemediationStepsTitle.
  ///
  /// In en, this message translates to:
  /// **'🛠️ Remediation Steps'**
  String get reportRemediationStepsTitle;

  /// No description provided for @reportEmotionalSentimentTitle.
  ///
  /// In en, this message translates to:
  /// **'🎭 Sentiment Analysis'**
  String get reportEmotionalSentimentTitle;

  /// No description provided for @reportTheoryLinkTitle.
  ///
  /// In en, this message translates to:
  /// **'📚 Theoretical Connection'**
  String get reportTheoryLinkTitle;

  /// No description provided for @reportConfidenceTitle.
  ///
  /// In en, this message translates to:
  /// **'AI Confidence: {value}%'**
  String reportConfidenceTitle(String value);

  /// Actionable hint label for resuming a failed execution
  ///
  /// In en, this message translates to:
  /// **'Resume Execution (Try Again)'**
  String get resumeActionableHint;

  /// Error message when execution resume fails.
  ///
  /// In en, this message translates to:
  /// **'Failed to resume execution.'**
  String get failedToResume;

  /// Error message when an external tool or MCP call fails
  ///
  /// In en, this message translates to:
  /// **'Tool execution failed'**
  String get toolExecutionFailed;

  /// Actionable hint given when a tool fails
  ///
  /// In en, this message translates to:
  /// **'Check the tool connection, verify the prompt context, or try again later.'**
  String get actionHintToolFailed;

  /// Title for the XAI Evidence Box showing MCP tool search results
  ///
  /// In en, this message translates to:
  /// **'AI Expert Sources (Fact-Check)'**
  String get xaiEvidenceTitle;

  /// Label for the original verbatim claim that triggered the search
  ///
  /// In en, this message translates to:
  /// **'Original Claim'**
  String get xaiEvidenceClaim;

  /// Label for the search query in XAI evidence entries
  ///
  /// In en, this message translates to:
  /// **'Search query'**
  String get xaiEvidenceQuery;

  /// Label for source URLs in XAI evidence entries
  ///
  /// In en, this message translates to:
  /// **'Sources'**
  String get xaiEvidenceSources;

  /// Label for search duration in XAI evidence entries
  ///
  /// In en, this message translates to:
  /// **'Duration'**
  String get xaiEvidenceDuration;

  /// Label for AI reasoning in XAI evidence entries
  ///
  /// In en, this message translates to:
  /// **'Reasoning'**
  String get xaiEvidenceReasoning;

  /// Title for MCP tools section in step builder
  ///
  /// In en, this message translates to:
  /// **'Allowed MCP Tools'**
  String get stepBuilderMCPToolsTitle;

  /// Button label to add a new MCP tool to a step
  ///
  /// In en, this message translates to:
  /// **'Add Tool'**
  String get stepBuilderAddTool;

  /// Hint text for MCP tool input field
  ///
  /// In en, this message translates to:
  /// **'Tool slug (e.g. mcp_tavily_search)'**
  String get stepBuilderToolHint;

  /// No description provided for @studioDashboardGatewaysTitle.
  ///
  /// In en, this message translates to:
  /// **'MCP Gateways'**
  String get studioDashboardGatewaysTitle;

  /// No description provided for @studioDashboardGatewaysDesc.
  ///
  /// In en, this message translates to:
  /// **'Manage external tools and AI fact-checking integrations.'**
  String get studioDashboardGatewaysDesc;

  /// No description provided for @mcpGatewaysTitle.
  ///
  /// In en, this message translates to:
  /// **'XAI Reporting / Toolkit Injection (MCP Gateways)'**
  String get mcpGatewaysTitle;

  /// No description provided for @mcpGatewaysDesc.
  ///
  /// In en, this message translates to:
  /// **'Configure system-level MCP tool gateways for AI execution.'**
  String get mcpGatewaysDesc;

  /// No description provided for @mcpToolSettings.
  ///
  /// In en, this message translates to:
  /// **'MCP Tool Settings'**
  String get mcpToolSettings;

  /// No description provided for @mcpToolIdLabel.
  ///
  /// In en, this message translates to:
  /// **'Tool ID'**
  String get mcpToolIdLabel;

  /// No description provided for @mcpToolNameLabel.
  ///
  /// In en, this message translates to:
  /// **'Tool Name'**
  String get mcpToolNameLabel;

  /// No description provided for @mcpToolDescLabel.
  ///
  /// In en, this message translates to:
  /// **'Description'**
  String get mcpToolDescLabel;

  /// No description provided for @mcpToolInputSchemaLabel.
  ///
  /// In en, this message translates to:
  /// **'Input Schema (JSON)'**
  String get mcpToolInputSchemaLabel;

  /// No description provided for @mcpAddToolBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Tool'**
  String get mcpAddToolBtn;

  /// No description provided for @mcpEditToolBtn.
  ///
  /// In en, this message translates to:
  /// **'Edit Tool'**
  String get mcpEditToolBtn;

  /// No description provided for @noMcpGatewaysDefined.
  ///
  /// In en, this message translates to:
  /// **'No MCP gateways defined.'**
  String get noMcpGatewaysDefined;

  /// No description provided for @tooltipDuplicate.
  ///
  /// In en, this message translates to:
  /// **'Duplicate (Shallow-Deep Copy)'**
  String get tooltipDuplicate;

  /// No description provided for @msgEntityClonedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Entity cloned securely.'**
  String get msgEntityClonedSuccess;

  /// No description provided for @msgEntityCloneFailed.
  ///
  /// In en, this message translates to:
  /// **'Failed to clone: {error}'**
  String msgEntityCloneFailed(String error);

  /// No description provided for @categoryMatrix.
  ///
  /// In en, this message translates to:
  /// **'Evaluation Matrix'**
  String get categoryMatrix;

  /// No description provided for @categoryAgentRole.
  ///
  /// In en, this message translates to:
  /// **'Agent Role Persona'**
  String get categoryAgentRole;

  /// No description provided for @categoryTaskDefinition.
  ///
  /// In en, this message translates to:
  /// **'Task Definition'**
  String get categoryTaskDefinition;

  /// No description provided for @categorySystemRule.
  ///
  /// In en, this message translates to:
  /// **'System Rule / Heuristic'**
  String get categorySystemRule;

  /// No description provided for @categoryProtocol.
  ///
  /// In en, this message translates to:
  /// **'Execution Protocol'**
  String get categoryProtocol;

  /// No description provided for @categoryRuntimeVariables.
  ///
  /// In en, this message translates to:
  /// **'Runtime Variables'**
  String get categoryRuntimeVariables;

  /// No description provided for @categoryExecutionPersona.
  ///
  /// In en, this message translates to:
  /// **'Execution Persona'**
  String get categoryExecutionPersona;

  /// No description provided for @technicalDetails.
  ///
  /// In en, this message translates to:
  /// **'Technical Details'**
  String get technicalDetails;

  /// No description provided for @systemError.
  ///
  /// In en, this message translates to:
  /// **'System Error'**
  String get systemError;

  /// No description provided for @signInSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Sign in to continue'**
  String get signInSubtitle;

  /// No description provided for @errorEmptyEmail.
  ///
  /// In en, this message translates to:
  /// **'Please enter your email'**
  String get errorEmptyEmail;

  /// No description provided for @errorInvalidEmail.
  ///
  /// In en, this message translates to:
  /// **'Invalid email address'**
  String get errorInvalidEmail;

  /// No description provided for @errorEmptyPassword.
  ///
  /// In en, this message translates to:
  /// **'Please enter your password'**
  String get errorEmptyPassword;

  /// No description provided for @signInButton.
  ///
  /// In en, this message translates to:
  /// **'Sign In'**
  String get signInButton;

  /// No description provided for @executionTargetLabel.
  ///
  /// In en, this message translates to:
  /// **'Target: {id}'**
  String executionTargetLabel(String id);

  /// No description provided for @executionMetricsTitle.
  ///
  /// In en, this message translates to:
  /// **'Performance Metrics'**
  String get executionMetricsTitle;

  /// No description provided for @executionTokensBreakdown.
  ///
  /// In en, this message translates to:
  /// **'Total Tokens: {total} (Prompt: {prompt}, Completion: {comp})'**
  String executionTokensBreakdown(int total, int prompt, int comp);

  /// No description provided for @executionTokensCached.
  ///
  /// In en, this message translates to:
  /// **'Cached Tokens saved: {cached}'**
  String executionTokensCached(int cached);

  /// No description provided for @executionTokensReasoning.
  ///
  /// In en, this message translates to:
  /// **'Reasoning Tokens spent: {reasoning}'**
  String executionTokensReasoning(int reasoning);

  /// No description provided for @executionCostEstimate.
  ///
  /// In en, this message translates to:
  /// **'Estimated Cost: \${cost}'**
  String executionCostEstimate(String cost);

  /// No description provided for @workflowPrefixLabel.
  ///
  /// In en, this message translates to:
  /// **'Workflow: {name}'**
  String workflowPrefixLabel(String name);

  /// No description provided for @deleteExecutionTooltip.
  ///
  /// In en, this message translates to:
  /// **'Delete Execution'**
  String get deleteExecutionTooltip;

  /// No description provided for @errSaveTimeout.
  ///
  /// In en, this message translates to:
  /// **'File save dialog did not respond (Timeout).'**
  String get errSaveTimeout;

  /// No description provided for @startWorkflowTitle.
  ///
  /// In en, this message translates to:
  /// **'Start Workflow: {id}'**
  String startWorkflowTitle(String id);

  /// No description provided for @failedToLoadSchema.
  ///
  /// In en, this message translates to:
  /// **'Failed to load schema: {error}'**
  String failedToLoadSchema(String error);

  /// No description provided for @navSystemInspector.
  ///
  /// In en, this message translates to:
  /// **'System Inspector'**
  String get navSystemInspector;

  /// No description provided for @gatewayMetadataTitle.
  ///
  /// In en, this message translates to:
  /// **'Gateway Metadata'**
  String get gatewayMetadataTitle;

  /// No description provided for @slugLabel.
  ///
  /// In en, this message translates to:
  /// **'Slug (e.g., task_guard)'**
  String get slugLabel;

  /// No description provided for @allowedMcpToolsTitle.
  ///
  /// In en, this message translates to:
  /// **'Allowed MCP Tools'**
  String get allowedMcpToolsTitle;

  /// No description provided for @addToolButton.
  ///
  /// In en, this message translates to:
  /// **'Add Tool'**
  String get addToolButton;

  /// No description provided for @noToolsDefinedGateway.
  ///
  /// In en, this message translates to:
  /// **'No tools defined for this gateway.'**
  String get noToolsDefinedGateway;

  /// No description provided for @deleteGatewayTitle.
  ///
  /// In en, this message translates to:
  /// **'Delete MCP Gateway?'**
  String get deleteGatewayTitle;

  /// No description provided for @deleteGatewayConfirmation.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete gateway {id}?'**
  String deleteGatewayConfirmation(String id);

  /// No description provided for @cancelButton.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancelButton;

  /// No description provided for @deleteButton.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get deleteButton;

  /// No description provided for @gatewaySavedSuccess.
  ///
  /// In en, this message translates to:
  /// **'MCP Gateway saved successfully.'**
  String get gatewaySavedSuccess;

  /// No description provided for @saveFailedError.
  ///
  /// In en, this message translates to:
  /// **'Save failed: {error}'**
  String saveFailedError(String error);

  /// No description provided for @deleteFailedError.
  ///
  /// In en, this message translates to:
  /// **'Delete failed: {error}'**
  String deleteFailedError(String error);

  /// No description provided for @toolTitlePrefix.
  ///
  /// In en, this message translates to:
  /// **'Tool: {name}'**
  String toolTitlePrefix(String name);

  /// No description provided for @toolIdLabel.
  ///
  /// In en, this message translates to:
  /// **'Tool ID (Slug)'**
  String get toolIdLabel;

  /// No description provided for @uiDisplayNameTitle.
  ///
  /// In en, this message translates to:
  /// **'UI Display Name (I18nText)'**
  String get uiDisplayNameTitle;

  /// No description provided for @englishNameLabel.
  ///
  /// In en, this message translates to:
  /// **'English Name'**
  String get englishNameLabel;

  /// No description provided for @finnishNameLabel.
  ///
  /// In en, this message translates to:
  /// **'Finnish Name'**
  String get finnishNameLabel;

  /// No description provided for @toolDescriptionLabel.
  ///
  /// In en, this message translates to:
  /// **'Tool Description (English only for LLM)'**
  String get toolDescriptionLabel;

  /// No description provided for @jsonInputSchemaLabel.
  ///
  /// In en, this message translates to:
  /// **'JSON Input Schema'**
  String get jsonInputSchemaLabel;

  /// No description provided for @invalidJsonError.
  ///
  /// In en, this message translates to:
  /// **'Invalid JSON'**
  String get invalidJsonError;

  /// No description provided for @deleteConfigTitle.
  ///
  /// In en, this message translates to:
  /// **'Delete Configuration?'**
  String get deleteConfigTitle;

  /// No description provided for @deleteConfigConfirmation.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete config {id}?'**
  String deleteConfigConfirmation(String id);

  /// No description provided for @configSavedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Model Registry saved successfully.'**
  String get configSavedSuccess;

  /// No description provided for @profileSavedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Profile saved successfully.'**
  String get profileSavedSuccess;

  /// No description provided for @deleteProfileTitle.
  ///
  /// In en, this message translates to:
  /// **'Delete Profile?'**
  String get deleteProfileTitle;

  /// No description provided for @deleteProfileConfirmation.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete {id}?'**
  String deleteProfileConfirmation(String id);

  /// No description provided for @newOutputProfileTitle.
  ///
  /// In en, this message translates to:
  /// **'New Output Profile'**
  String get newOutputProfileTitle;

  /// No description provided for @editOutputProfileTitle.
  ///
  /// In en, this message translates to:
  /// **'Edit Output Profile'**
  String get editOutputProfileTitle;

  /// No description provided for @profileIdLabel.
  ///
  /// In en, this message translates to:
  /// **'Profile ID (e.g. general_executive)'**
  String get profileIdLabel;

  /// No description provided for @urlSlugLabel.
  ///
  /// In en, this message translates to:
  /// **'URL Slug (e.g. default)'**
  String get urlSlugLabel;

  /// No description provided for @workflowIdBindingLabel.
  ///
  /// In en, this message translates to:
  /// **'Workflow ID Binding'**
  String get workflowIdBindingLabel;

  /// No description provided for @selectWorkflowHint.
  ///
  /// In en, this message translates to:
  /// **'Select a Workflow...'**
  String get selectWorkflowHint;

  /// No description provided for @noneDefaultLabel.
  ///
  /// In en, this message translates to:
  /// **'None (Default)'**
  String get noneDefaultLabel;

  /// No description provided for @profileDisplayNameLabel.
  ///
  /// In en, this message translates to:
  /// **'Profile Display Name'**
  String get profileDisplayNameLabel;

  /// No description provided for @profileDescriptionLabel.
  ///
  /// In en, this message translates to:
  /// **'Profile Description (Optional)'**
  String get profileDescriptionLabel;

  /// No description provided for @workflowSelectWarning.
  ///
  /// In en, this message translates to:
  /// **'⚠️ Please select a Workflow ID Binding above to configure report layouts.'**
  String get workflowSelectWarning;

  /// No description provided for @layoutBlocksTitle.
  ///
  /// In en, this message translates to:
  /// **'Layout Blocks'**
  String get layoutBlocksTitle;

  /// No description provided for @addLayoutBlockBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Layout Block'**
  String get addLayoutBlockBtn;

  /// No description provided for @noLayoutBlocksDefined.
  ///
  /// In en, this message translates to:
  /// **'No layout blocks defined. Report will be empty.'**
  String get noLayoutBlocksDefined;

  /// No description provided for @presetViewLabel.
  ///
  /// In en, this message translates to:
  /// **'Preset View'**
  String get presetViewLabel;

  /// No description provided for @preset1dTable.
  ///
  /// In en, this message translates to:
  /// **'1D Table'**
  String get preset1dTable;

  /// No description provided for @preset2dGrid.
  ///
  /// In en, this message translates to:
  /// **'2D Grid'**
  String get preset2dGrid;

  /// No description provided for @preset3dRadar.
  ///
  /// In en, this message translates to:
  /// **'3D Radar/Composite'**
  String get preset3dRadar;

  /// No description provided for @presetTextOnly.
  ///
  /// In en, this message translates to:
  /// **'Text/Synthesis Only'**
  String get presetTextOnly;

  /// No description provided for @presetAutomatic.
  ///
  /// In en, this message translates to:
  /// **'Automatic Validation'**
  String get presetAutomatic;

  /// No description provided for @presetMatrixSummary.
  ///
  /// In en, this message translates to:
  /// **'Matrix Summary'**
  String get presetMatrixSummary;

  /// No description provided for @textDeliveryModeLabel.
  ///
  /// In en, this message translates to:
  /// **'Text Detail Level'**
  String get textDeliveryModeLabel;

  /// No description provided for @textModeFull.
  ///
  /// In en, this message translates to:
  /// **'Full (Graph, titles and body text)'**
  String get textModeFull;

  /// No description provided for @textModeTitlesOnly.
  ///
  /// In en, this message translates to:
  /// **'Titles Only (Graph and titles/scores)'**
  String get textModeTitlesOnly;

  /// No description provided for @textModeNone.
  ///
  /// In en, this message translates to:
  /// **'Reduced (Graph and summary only)'**
  String get textModeNone;

  /// No description provided for @layoutBlockTitleLabel.
  ///
  /// In en, this message translates to:
  /// **'Layout Block Title'**
  String get layoutBlockTitleLabel;

  /// No description provided for @targetComponentsTitle.
  ///
  /// In en, this message translates to:
  /// **'Target Components'**
  String get targetComponentsTitle;

  /// No description provided for @componentXAxisLabel.
  ///
  /// In en, this message translates to:
  /// **'Component 1 (X-Axis/Primary)'**
  String get componentXAxisLabel;

  /// No description provided for @componentYAxisLabel.
  ///
  /// In en, this message translates to:
  /// **'Component 2 (Y-Axis)'**
  String get componentYAxisLabel;

  /// No description provided for @componentZAxisLabel.
  ///
  /// In en, this message translates to:
  /// **'Component 3 (Z-Axis)'**
  String get componentZAxisLabel;

  /// No description provided for @componentGenericLabel.
  ///
  /// In en, this message translates to:
  /// **'Component {num}'**
  String componentGenericLabel(String num);

  /// No description provided for @selectAllComponentsLabel.
  ///
  /// In en, this message translates to:
  /// **'All Components (*)'**
  String get selectAllComponentsLabel;

  /// No description provided for @selectComponentHint.
  ///
  /// In en, this message translates to:
  /// **'Select component...'**
  String get selectComponentHint;

  /// No description provided for @duplicateComponentError.
  ///
  /// In en, this message translates to:
  /// **'The same target component is already selected.'**
  String get duplicateComponentError;

  /// No description provided for @editProfilesTitle.
  ///
  /// In en, this message translates to:
  /// **'Edit Profiles: {slug}'**
  String editProfilesTitle(String slug);

  /// No description provided for @outputProfilesDictionary.
  ///
  /// In en, this message translates to:
  /// **'Output Profiles Dictionary'**
  String get outputProfilesDictionary;

  /// No description provided for @addVariantBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Variant'**
  String get addVariantBtn;

  /// No description provided for @newProfileIdTitle.
  ///
  /// In en, this message translates to:
  /// **'New Profile ID'**
  String get newProfileIdTitle;

  /// No description provided for @profileIdHint.
  ///
  /// In en, this message translates to:
  /// **'Profile ID (e.g. executive)'**
  String get profileIdHint;

  /// No description provided for @variantIdLabel.
  ///
  /// In en, this message translates to:
  /// **'Variant ID: {id}'**
  String variantIdLabel(String id);

  /// No description provided for @reportLayoutSequenceLabel.
  ///
  /// In en, this message translates to:
  /// **'Report Layout Sequence'**
  String get reportLayoutSequenceLabel;

  /// No description provided for @preset2dCompare.
  ///
  /// In en, this message translates to:
  /// **'2D Compare'**
  String get preset2dCompare;

  /// No description provided for @preset3dComplex.
  ///
  /// In en, this message translates to:
  /// **'3D Complex'**
  String get preset3dComplex;

  /// No description provided for @presetDefaultView.
  ///
  /// In en, this message translates to:
  /// **'Default View'**
  String get presetDefaultView;

  /// No description provided for @sectionTitleLabel.
  ///
  /// In en, this message translates to:
  /// **'Section Title (Optional)'**
  String get sectionTitleLabel;

  /// No description provided for @sectionDescLabel.
  ///
  /// In en, this message translates to:
  /// **'Section Description (Optional)'**
  String get sectionDescLabel;

  /// No description provided for @promptBlockSavedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Prompt Block saved (Optimistic).'**
  String get promptBlockSavedSuccess;

  /// No description provided for @simulatorCorruptionError.
  ///
  /// In en, this message translates to:
  /// **'Simulator did not return rendered_prompt. Data corruption detected.'**
  String get simulatorCorruptionError;

  /// No description provided for @simulatorOutputTitle.
  ///
  /// In en, this message translates to:
  /// **'Simulator Output'**
  String get simulatorOutputTitle;

  /// No description provided for @simulatorFailedError.
  ///
  /// In en, this message translates to:
  /// **'Simulation Error: {error}'**
  String simulatorFailedError(String error);

  /// No description provided for @promptBlockEditTitle.
  ///
  /// In en, this message translates to:
  /// **'Edit Prompt Block'**
  String get promptBlockEditTitle;

  /// No description provided for @promptBlockBuilderTitleId.
  ///
  /// In en, this message translates to:
  /// **'Builder: {id}'**
  String promptBlockBuilderTitleId(String id);

  /// No description provided for @promptBlockMandatoryEnglishError.
  ///
  /// In en, this message translates to:
  /// **'English Label is required (English-Only Mandate).'**
  String get promptBlockMandatoryEnglishError;

  /// No description provided for @promptBlockConfigTitle.
  ///
  /// In en, this message translates to:
  /// **'Prompt Block Configuration'**
  String get promptBlockConfigTitle;

  /// No description provided for @opaqueIdLabel.
  ///
  /// In en, this message translates to:
  /// **'Opaque ID: {id}'**
  String opaqueIdLabel(String id);

  /// No description provided for @promptBlockPropertiesTitle.
  ///
  /// In en, this message translates to:
  /// **'Prompt Block Properties'**
  String get promptBlockPropertiesTitle;

  /// No description provided for @categoryLabel.
  ///
  /// In en, this message translates to:
  /// **'Category'**
  String get categoryLabel;

  /// No description provided for @blockLabelName.
  ///
  /// In en, this message translates to:
  /// **'Block Label (Name)'**
  String get blockLabelName;

  /// No description provided for @shortDescriptionHint.
  ///
  /// In en, this message translates to:
  /// **'Short Description (UI Hint)'**
  String get shortDescriptionHint;

  /// No description provided for @systemPromptMandatory.
  ///
  /// In en, this message translates to:
  /// **'System Prompt / Cognitive Blueprint (MANDATORY ENGLISH)'**
  String get systemPromptMandatory;

  /// No description provided for @dataTypeExecutionConstraints.
  ///
  /// In en, this message translates to:
  /// **'Data Type & Execution Constraints'**
  String get dataTypeExecutionConstraints;

  /// No description provided for @typeInstruction.
  ///
  /// In en, this message translates to:
  /// **'Text Instruction (No JSON Output)'**
  String get typeInstruction;

  /// No description provided for @typeNumber.
  ///
  /// In en, this message translates to:
  /// **'Number (Numeric)'**
  String get typeNumber;

  /// No description provided for @typeInteger.
  ///
  /// In en, this message translates to:
  /// **'Integer'**
  String get typeInteger;

  /// No description provided for @allowDecimals.
  ///
  /// In en, this message translates to:
  /// **'Allow Decimals'**
  String get allowDecimals;

  /// No description provided for @isEvaluativeMatrix.
  ///
  /// In en, this message translates to:
  /// **'Evaluative (Calculated)'**
  String get isEvaluativeMatrix;

  /// No description provided for @promptBlockEnsembleToggle.
  ///
  /// In en, this message translates to:
  /// **'Use Fast-Model Ensemble (Best of 3)'**
  String get promptBlockEnsembleToggle;

  /// No description provided for @promptBlockEnsembleToggleDesc.
  ///
  /// In en, this message translates to:
  /// **'Runs the entire matrix 3 times in parallel and applies majority voting.'**
  String get promptBlockEnsembleToggleDesc;

  /// No description provided for @xaiOutputExtensionsTitle.
  ///
  /// In en, this message translates to:
  /// **'XAI Output Extensions (Proaktiivinen Valmentaja & Report Fields)'**
  String get xaiOutputExtensionsTitle;

  /// No description provided for @xaiJustification.
  ///
  /// In en, this message translates to:
  /// **'Justification'**
  String get xaiJustification;

  /// No description provided for @xaiGlobalExtensionsHeader.
  ///
  /// In en, this message translates to:
  /// **'AI Observations'**
  String get xaiGlobalExtensionsHeader;

  /// No description provided for @xaiCoachingTip.
  ///
  /// In en, this message translates to:
  /// **'Coaching Tip'**
  String get xaiCoachingTip;

  /// No description provided for @xaiDevilsAdvocate.
  ///
  /// In en, this message translates to:
  /// **'Devil\'s Advocate'**
  String get xaiDevilsAdvocate;

  /// No description provided for @xaiMissingContext.
  ///
  /// In en, this message translates to:
  /// **'Missing Context'**
  String get xaiMissingContext;

  /// No description provided for @xaiRiskFlag.
  ///
  /// In en, this message translates to:
  /// **'Risk Flag'**
  String get xaiRiskFlag;

  /// No description provided for @xaiRemediation.
  ///
  /// In en, this message translates to:
  /// **'Remediation'**
  String get xaiRemediation;

  /// No description provided for @xaiSentiment.
  ///
  /// In en, this message translates to:
  /// **'Sentiment'**
  String get xaiSentiment;

  /// No description provided for @xaiTheoryLink.
  ///
  /// In en, this message translates to:
  /// **'Theory Link'**
  String get xaiTheoryLink;

  /// No description provided for @xaiConfidence.
  ///
  /// In en, this message translates to:
  /// **'AI Confidence'**
  String get xaiConfidence;

  /// No description provided for @xaiSourceCitation.
  ///
  /// In en, this message translates to:
  /// **'Source Citation'**
  String get xaiSourceCitation;

  /// No description provided for @xaiContextualOverride.
  ///
  /// In en, this message translates to:
  /// **'Contextual Override'**
  String get xaiContextualOverride;

  /// No description provided for @xaiSourceId.
  ///
  /// In en, this message translates to:
  /// **'Source ID'**
  String get xaiSourceId;

  /// No description provided for @theoryGroundingTitle.
  ///
  /// In en, this message translates to:
  /// **'Theory Grounding (RAG)'**
  String get theoryGroundingTitle;

  /// No description provided for @sourceUrlLabel.
  ///
  /// In en, this message translates to:
  /// **'Source URL (e.g. jstor.org/...)'**
  String get sourceUrlLabel;

  /// No description provided for @citationReferenceLabel.
  ///
  /// In en, this message translates to:
  /// **'Citation Reference (e.g. Kahnamen, 2011)'**
  String get citationReferenceLabel;

  /// No description provided for @gridRowsOptional.
  ///
  /// In en, this message translates to:
  /// **'Grid Rows (Optional)'**
  String get gridRowsOptional;

  /// No description provided for @gridColumnsOptional.
  ///
  /// In en, this message translates to:
  /// **'Grid Columns (Optional)'**
  String get gridColumnsOptional;

  /// No description provided for @addGridItemBtn.
  ///
  /// In en, this message translates to:
  /// **'Add item'**
  String get addGridItemBtn;

  /// No description provided for @barsScalesTitle.
  ///
  /// In en, this message translates to:
  /// **'BARS Scales / Score Grades'**
  String get barsScalesTitle;

  /// No description provided for @addGradeBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Grade'**
  String get addGradeBtn;

  /// No description provided for @scaleMinLabel.
  ///
  /// In en, this message translates to:
  /// **'Scale Min (e.g. 4)'**
  String get scaleMinLabel;

  /// No description provided for @scaleMaxLabel.
  ///
  /// In en, this message translates to:
  /// **'Scale Max (e.g. 10)'**
  String get scaleMaxLabel;

  /// No description provided for @claimsCountLabel.
  ///
  /// In en, this message translates to:
  /// **'{count} Claims'**
  String claimsCountLabel(String count);

  /// No description provided for @gradeScoreLabel.
  ///
  /// In en, this message translates to:
  /// **'Grade/Score: {score} {name}'**
  String gradeScoreLabel(String score, String name);

  /// No description provided for @closeModalBtn.
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get closeModalBtn;

  /// No description provided for @studioSaveSuccess.
  ///
  /// In en, this message translates to:
  /// **'Saved successfully'**
  String get studioSaveSuccess;

  /// No description provided for @stepSavedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Step saved (Optimistic).'**
  String get stepSavedSuccess;

  /// No description provided for @stepEditTitle.
  ///
  /// In en, this message translates to:
  /// **'Edit Step'**
  String get stepEditTitle;

  /// No description provided for @simulateStepTooltip.
  ///
  /// In en, this message translates to:
  /// **'Simulate Step'**
  String get simulateStepTooltip;

  /// No description provided for @idRequiredError.
  ///
  /// In en, this message translates to:
  /// **'ID is required.'**
  String get idRequiredError;

  /// No description provided for @configurationTitle.
  ///
  /// In en, this message translates to:
  /// **'Configuration'**
  String get configurationTitle;

  /// No description provided for @nameLabel.
  ///
  /// In en, this message translates to:
  /// **'Name'**
  String get nameLabel;

  /// No description provided for @descriptionLabel.
  ///
  /// In en, this message translates to:
  /// **'Description'**
  String get descriptionLabel;

  /// No description provided for @preHooksTitle.
  ///
  /// In en, this message translates to:
  /// **'Pre Hooks'**
  String get preHooksTitle;

  /// No description provided for @postHooksTitle.
  ///
  /// In en, this message translates to:
  /// **'Post Hooks'**
  String get postHooksTitle;

  /// No description provided for @addHookBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Hook'**
  String get addHookBtn;

  /// No description provided for @preHookEngineLabel.
  ///
  /// In en, this message translates to:
  /// **'Pre-Execution Hook Engine'**
  String get preHookEngineLabel;

  /// No description provided for @postHookEngineLabel.
  ///
  /// In en, this message translates to:
  /// **'Post-Execution Hook Engine'**
  String get postHookEngineLabel;

  /// No description provided for @hookWaterfall.
  ///
  /// In en, this message translates to:
  /// **'Waterfall Scoring (waterfall_scoring_hook)'**
  String get hookWaterfall;

  /// No description provided for @hookNormalize.
  ///
  /// In en, this message translates to:
  /// **'Normalize Matrix Scores (normalize_matrix_scores)'**
  String get hookNormalize;

  /// No description provided for @hookVerifyCitation.
  ///
  /// In en, this message translates to:
  /// **'Verify Citation Integrity (verify_citation_integrity)'**
  String get hookVerifyCitation;

  /// No description provided for @hookHypothesis.
  ///
  /// In en, this message translates to:
  /// **'Enforce Hypothesis Linking (enforce_hypothesis_linking)'**
  String get hookHypothesis;

  /// No description provided for @hookTavily.
  ///
  /// In en, this message translates to:
  /// **'Tavily Web Search (search_hook)'**
  String get hookTavily;

  /// No description provided for @hookMemory.
  ///
  /// In en, this message translates to:
  /// **'Contextual Memory (memory_hook)'**
  String get hookMemory;

  /// No description provided for @hookValidation.
  ///
  /// In en, this message translates to:
  /// **'Strict Validation (validation_hook)'**
  String get hookValidation;

  /// No description provided for @hookScore.
  ///
  /// In en, this message translates to:
  /// **'Grading Matrix (score_hook)'**
  String get hookScore;

  /// No description provided for @hookLegacy.
  ///
  /// In en, this message translates to:
  /// **'Legacy: {name}'**
  String hookLegacy(String name);

  /// No description provided for @promptBlocksTitle.
  ///
  /// In en, this message translates to:
  /// **'Prompt Blocks'**
  String get promptBlocksTitle;

  /// No description provided for @addPromptBlockBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Prompt Block'**
  String get addPromptBlockBtn;

  /// No description provided for @promptBlockLabel.
  ///
  /// In en, this message translates to:
  /// **'Prompt Block'**
  String get promptBlockLabel;

  /// No description provided for @workflowSavedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Workflow saved successfully.'**
  String get workflowSavedSuccess;

  /// No description provided for @simulatorValidDag.
  ///
  /// In en, this message translates to:
  /// **'DAG is Valid!'**
  String get simulatorValidDag;

  /// No description provided for @simulatorDagErrors.
  ///
  /// In en, this message translates to:
  /// **'DAG Errors: {errors}'**
  String simulatorDagErrors(String errors);

  /// No description provided for @workflowNameMissingError.
  ///
  /// In en, this message translates to:
  /// **'Workflow name is missing for existing workflow.'**
  String get workflowNameMissingError;

  /// No description provided for @validateDagBtn.
  ///
  /// In en, this message translates to:
  /// **'Validate DAG'**
  String get validateDagBtn;

  /// No description provided for @workflowTabGeneral.
  ///
  /// In en, this message translates to:
  /// **'1. General & Outputs'**
  String get workflowTabGeneral;

  /// No description provided for @workflowTabInputs.
  ///
  /// In en, this message translates to:
  /// **'2. Inputs'**
  String get workflowTabInputs;

  /// No description provided for @workflowTabSteps.
  ///
  /// In en, this message translates to:
  /// **'3. Steps & Dependencies'**
  String get workflowTabSteps;

  /// No description provided for @errNavigationFallback.
  ///
  /// In en, this message translates to:
  /// **'Navigation Error: {uri} not found. Returning to workspace...'**
  String errNavigationFallback(String uri);

  /// No description provided for @studioWorkflowIdOpaque.
  ///
  /// In en, this message translates to:
  /// **'Opaque Workflow ID (System Generated)'**
  String get studioWorkflowIdOpaque;

  /// No description provided for @studioWorkflowSlugSemantic.
  ///
  /// In en, this message translates to:
  /// **'Semantic Routing Slug (e.g. audit-master)'**
  String get studioWorkflowSlugSemantic;

  /// No description provided for @studioWorkflowIdentity.
  ///
  /// In en, this message translates to:
  /// **'Workflow Identity'**
  String get studioWorkflowIdentity;

  /// No description provided for @studioWorkflowNameLabel.
  ///
  /// In en, this message translates to:
  /// **'Workflow Name'**
  String get studioWorkflowNameLabel;

  /// No description provided for @studioWorkflowDescEnLabel.
  ///
  /// In en, this message translates to:
  /// **'Description (EN)'**
  String get studioWorkflowDescEnLabel;

  /// No description provided for @studioWorkflowDescFiLabel.
  ///
  /// In en, this message translates to:
  /// **'Kuvaus (FI)'**
  String get studioWorkflowDescFiLabel;

  /// No description provided for @studioWorkflowGlobalSettings.
  ///
  /// In en, this message translates to:
  /// **'Global Execution Settings'**
  String get studioWorkflowGlobalSettings;

  /// No description provided for @studioWorkflowDefaultProfile.
  ///
  /// In en, this message translates to:
  /// **'Default Fallback Profile'**
  String get studioWorkflowDefaultProfile;

  /// No description provided for @studioWorkflowInputsEmpty.
  ///
  /// In en, this message translates to:
  /// **'No expected inputs defined.'**
  String get studioWorkflowInputsEmpty;

  /// No description provided for @studioWorkflowStepCount.
  ///
  /// In en, this message translates to:
  /// **'Step {count}'**
  String studioWorkflowStepCount(int count);

  /// No description provided for @studioWorkflowNodeIdOpaque.
  ///
  /// In en, this message translates to:
  /// **'Node ID (Opaque Stripe Pattern)'**
  String get studioWorkflowNodeIdOpaque;

  /// No description provided for @studioWorkflowTaskBlueprint.
  ///
  /// In en, this message translates to:
  /// **'Task Blueprint (Cognitive Engine)'**
  String get studioWorkflowTaskBlueprint;

  /// No description provided for @studioWorkflowXaiReporting.
  ///
  /// In en, this message translates to:
  /// **'XAI Reporting / Toolkit Injection (MCP Gateways):'**
  String get studioWorkflowXaiReporting;

  /// No description provided for @studioWorkflowDependsOn.
  ///
  /// In en, this message translates to:
  /// **'Depends On (Executes AFTER these steps finish):'**
  String get studioWorkflowDependsOn;

  /// No description provided for @studioWorkflowNoDependencies.
  ///
  /// In en, this message translates to:
  /// **'No previous steps available to depend on.'**
  String get studioWorkflowNoDependencies;

  /// No description provided for @studioWorkflowInputMappings.
  ///
  /// In en, this message translates to:
  /// **'Input Mappings (State Data Injection):'**
  String get studioWorkflowInputMappings;

  /// No description provided for @studioWorkflowTargetArgName.
  ///
  /// In en, this message translates to:
  /// **'Target Arg Name'**
  String get studioWorkflowTargetArgName;

  /// No description provided for @studioWorkflowSourceToken.
  ///
  /// In en, this message translates to:
  /// **'Source Token (e.g. \\\$inputs, step_1)'**
  String get studioWorkflowSourceToken;

  /// No description provided for @studioWorkflowStepsNoInputsMappingWarning.
  ///
  /// In en, this message translates to:
  /// **'Error: Unmapped inputs found.'**
  String get studioWorkflowStepsNoInputsMappingWarning;

  /// No description provided for @studioWorkflowStepsInputMappingTitle.
  ///
  /// In en, this message translates to:
  /// **'Input Mappings (External -> Internal)'**
  String get studioWorkflowStepsInputMappingTitle;

  /// No description provided for @studioWorkflowStepsAddMappingBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Mapping'**
  String get studioWorkflowStepsAddMappingBtn;

  /// No description provided for @studioWorkflowStepsDataMissingText.
  ///
  /// In en, this message translates to:
  /// **'Wait, missing data object?'**
  String get studioWorkflowStepsDataMissingText;

  /// No description provided for @studioWorkflowStepsNoTargetComponents.
  ///
  /// In en, this message translates to:
  /// **'None selected'**
  String get studioWorkflowStepsNoTargetComponents;

  /// No description provided for @studioViewsBlueprintRulesTitle.
  ///
  /// In en, this message translates to:
  /// **'Output Mapping (Presentation Rules)'**
  String get studioViewsBlueprintRulesTitle;

  /// No description provided for @studioViewsPresetViewTheme.
  ///
  /// In en, this message translates to:
  /// **'Preset View Theme'**
  String get studioViewsPresetViewTheme;

  /// No description provided for @studioViews1dMetricsList.
  ///
  /// In en, this message translates to:
  /// **'1D Metrics List'**
  String get studioViews1dMetricsList;

  /// No description provided for @studioViews2dCompare.
  ///
  /// In en, this message translates to:
  /// **'2D Compare View'**
  String get studioViews2dCompare;

  /// No description provided for @studioViews3dComplex.
  ///
  /// In en, this message translates to:
  /// **'3D Complex Matrix'**
  String get studioViews3dComplex;

  /// No description provided for @studioViewsFailedToClone.
  ///
  /// In en, this message translates to:
  /// **'Failed to clone: {error}'**
  String studioViewsFailedToClone(String error);

  /// No description provided for @studioViewsNewMatrix.
  ///
  /// In en, this message translates to:
  /// **'New Matrix'**
  String get studioViewsNewMatrix;

  /// No description provided for @studioViewsErrorLoadingWorkflows.
  ///
  /// In en, this message translates to:
  /// **'Error loading workflows: {error}'**
  String studioViewsErrorLoadingWorkflows(String error);

  /// No description provided for @targetBlockOrderTitle.
  ///
  /// In en, this message translates to:
  /// **'Target Block Order'**
  String get targetBlockOrderTitle;

  /// No description provided for @targetBlockOrderSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Drag and drop to reorder the blocks dispatched during execution.'**
  String get targetBlockOrderSubtitle;

  /// No description provided for @studioViewsProfileIdRequired.
  ///
  /// In en, this message translates to:
  /// **'Profile ID is required'**
  String get studioViewsProfileIdRequired;

  /// No description provided for @studioViewsErrorLoadingBlocks.
  ///
  /// In en, this message translates to:
  /// **'Error loading blocks: {error}'**
  String studioViewsErrorLoadingBlocks(String error);

  /// No description provided for @studioViewsOutputProfilesMasterTitle.
  ///
  /// In en, this message translates to:
  /// **'Output Profiles'**
  String get studioViewsOutputProfilesMasterTitle;

  /// No description provided for @studioViewsNewProfileBtn.
  ///
  /// In en, this message translates to:
  /// **'New Profile'**
  String get studioViewsNewProfileBtn;

  /// No description provided for @studioViewsNoOutputProfiles.
  ///
  /// In en, this message translates to:
  /// **'No Output Profiles defined.'**
  String get studioViewsNoOutputProfiles;

  /// No description provided for @studioViewsUnnamedProfile.
  ///
  /// In en, this message translates to:
  /// **'Unnamed Profile'**
  String get studioViewsUnnamedProfile;

  /// No description provided for @studioViewsProfileListSubtitle.
  ///
  /// In en, this message translates to:
  /// **'ID: {id} | Workflow: {workflow} | {layouts} Layout Blocks'**
  String studioViewsProfileListSubtitle(
    String id,
    String workflow,
    int layouts,
  );

  /// No description provided for @studioViewsNone.
  ///
  /// In en, this message translates to:
  /// **'None'**
  String get studioViewsNone;

  /// No description provided for @studioViewsAddBtn.
  ///
  /// In en, this message translates to:
  /// **'Add'**
  String get studioViewsAddBtn;

  /// No description provided for @studioViewsWarningNoModels.
  ///
  /// In en, this message translates to:
  /// **'Warning: No models found.'**
  String get studioViewsWarningNoModels;

  /// No description provided for @studioViewsModelStrategyLabel.
  ///
  /// In en, this message translates to:
  /// **'Model Strategy (Cost/Cognition Override)'**
  String get studioViewsModelStrategyLabel;

  /// No description provided for @studioViewsAdminStudioV2.
  ///
  /// In en, this message translates to:
  /// **'Admin Studio V2'**
  String get studioViewsAdminStudioV2;

  /// No description provided for @studioViewsPromptBlocksTab.
  ///
  /// In en, this message translates to:
  /// **'Prompt Blocks'**
  String get studioViewsPromptBlocksTab;

  /// No description provided for @studioViewsStepsTab.
  ///
  /// In en, this message translates to:
  /// **'Steps'**
  String get studioViewsStepsTab;

  /// No description provided for @studioViewsProfilesTab.
  ///
  /// In en, this message translates to:
  /// **'Profiles'**
  String get studioViewsProfilesTab;

  /// No description provided for @studioViewsPromptBlocksStandard.
  ///
  /// In en, this message translates to:
  /// **'Prompt Blocks (Standard)'**
  String get studioViewsPromptBlocksStandard;

  /// No description provided for @studioViewsNoStandardPromptBlocks.
  ///
  /// In en, this message translates to:
  /// **'No standard prompt blocks defined.'**
  String get studioViewsNoStandardPromptBlocks;

  /// No description provided for @studioViewsSlugSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Slug: {slug}'**
  String studioViewsSlugSubtitle(String slug);

  /// No description provided for @studioViewsNoMatricesDefined.
  ///
  /// In en, this message translates to:
  /// **'No matrices defined.'**
  String get studioViewsNoMatricesDefined;

  /// No description provided for @studioViewsNoStepsDefined.
  ///
  /// In en, this message translates to:
  /// **'No Steps defined.'**
  String get studioViewsNoStepsDefined;

  /// No description provided for @studioViewsStepsSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Blocks: {blocks} | Hooks: {hooks}'**
  String studioViewsStepsSubtitle(int blocks, int hooks);

  /// No description provided for @studioViewsNoSystemConfigs.
  ///
  /// In en, this message translates to:
  /// **'No System Configs defined.'**
  String get studioViewsNoSystemConfigs;

  /// No description provided for @studioViewsConfiguredModels.
  ///
  /// In en, this message translates to:
  /// **'Configured Models: {count}'**
  String studioViewsConfiguredModels(int count);

  /// No description provided for @studioViewsNewBtn.
  ///
  /// In en, this message translates to:
  /// **'New'**
  String get studioViewsNewBtn;

  /// No description provided for @studioViewsWorkflowBuilderTitle.
  ///
  /// In en, this message translates to:
  /// **'Workflow Builder'**
  String get studioViewsWorkflowBuilderTitle;

  /// No description provided for @studioViewsNewWorkflowBtn.
  ///
  /// In en, this message translates to:
  /// **'New Workflow'**
  String get studioViewsNewWorkflowBtn;

  /// No description provided for @studioViewsWorkflowBuilderDesc.
  ///
  /// In en, this message translates to:
  /// **'Manage master execution blueprints (DAGs) defining agentic workflows, inputs, and strategies.'**
  String get studioViewsWorkflowBuilderDesc;

  /// No description provided for @studioViewsNoWorkflowsConfigured.
  ///
  /// In en, this message translates to:
  /// **'No workflows configured.'**
  String get studioViewsNoWorkflowsConfigured;

  /// No description provided for @studioViewsWorkflowSubtitle.
  ///
  /// In en, this message translates to:
  /// **'ID: {id} | Nodes: {nodes} | Status: {status}'**
  String studioViewsWorkflowSubtitle(String id, int nodes, String status);

  /// No description provided for @studioWorkflowAddMappingBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Mapping'**
  String get studioWorkflowAddMappingBtn;

  /// No description provided for @studioWorkflowStepsDependencies.
  ///
  /// In en, this message translates to:
  /// **'Steps & Dependencies'**
  String get studioWorkflowStepsDependencies;

  /// No description provided for @studioWorkflowAddStepNodeBtn.
  ///
  /// In en, this message translates to:
  /// **'Add Step Node'**
  String get studioWorkflowAddStepNodeBtn;

  /// No description provided for @studioWorkflowStepsEmpty.
  ///
  /// In en, this message translates to:
  /// **'No steps defined. Add a node to start creating the orchestration graph.'**
  String get studioWorkflowStepsEmpty;

  /// No description provided for @studioViewsMatricesDescription.
  ///
  /// In en, this message translates to:
  /// **'Manage system evaluation matrices.'**
  String get studioViewsMatricesDescription;

  /// No description provided for @studioViewsNoMatricesAvailable.
  ///
  /// In en, this message translates to:
  /// **'No Matrices Available.'**
  String get studioViewsNoMatricesAvailable;

  /// No description provided for @studioViewsMatrixCloned.
  ///
  /// In en, this message translates to:
  /// **'Matrix cloned successfully.'**
  String get studioViewsMatrixCloned;

  /// No description provided for @sharedNoTimelineData.
  ///
  /// In en, this message translates to:
  /// **'No timeline data available.'**
  String get sharedNoTimelineData;

  /// No description provided for @sharedNoReportData.
  ///
  /// In en, this message translates to:
  /// **'No report data available.'**
  String get sharedNoReportData;

  /// No description provided for @sharedFlatReportNoData.
  ///
  /// In en, this message translates to:
  /// **'No Flat Report data found for this execution.'**
  String get sharedFlatReportNoData;

  /// No description provided for @sharedAnalysisPerformed.
  ///
  /// In en, this message translates to:
  /// **'Analysis Performed: '**
  String get sharedAnalysisPerformed;

  /// No description provided for @sharedNoComparisonData.
  ///
  /// In en, this message translates to:
  /// **'No comparison data available.'**
  String get sharedNoComparisonData;

  /// No description provided for @sharedMoreInfoTooltip.
  ///
  /// In en, this message translates to:
  /// **'More information'**
  String get sharedMoreInfoTooltip;

  /// No description provided for @sharedOk.
  ///
  /// In en, this message translates to:
  /// **'OK'**
  String get sharedOk;

  /// No description provided for @sharedUploading.
  ///
  /// In en, this message translates to:
  /// **'Uploading...'**
  String get sharedUploading;

  /// No description provided for @sharedSelectFile.
  ///
  /// In en, this message translates to:
  /// **'Select file...'**
  String get sharedSelectFile;

  /// No description provided for @sharedSystemError.
  ///
  /// In en, this message translates to:
  /// **'System Error'**
  String get sharedSystemError;

  /// No description provided for @sharedUnknownAgent.
  ///
  /// In en, this message translates to:
  /// **'Unknown Agent'**
  String get sharedUnknownAgent;

  /// No description provided for @sharedUnknown.
  ///
  /// In en, this message translates to:
  /// **'Unknown'**
  String get sharedUnknown;

  /// No description provided for @studioWorkflowAllInputsCombined.
  ///
  /// In en, this message translates to:
  /// **'All original inputs combined (\$inputs)'**
  String get studioWorkflowAllInputsCombined;

  /// No description provided for @studioWorkflowAllStepsCombined.
  ///
  /// In en, this message translates to:
  /// **'All previous steps combined (\$steps)'**
  String get studioWorkflowAllStepsCombined;

  /// No description provided for @profileDisplayScaleLabel.
  ///
  /// In en, this message translates to:
  /// **'Display Scale Source'**
  String get profileDisplayScaleLabel;

  /// No description provided for @scaleOriginal.
  ///
  /// In en, this message translates to:
  /// **'Raw Matrix Value (Original)'**
  String get scaleOriginal;

  /// No description provided for @scaleCustom.
  ///
  /// In en, this message translates to:
  /// **'Custom Computed Hook Value'**
  String get scaleCustom;

  /// No description provided for @scaleNormalized100.
  ///
  /// In en, this message translates to:
  /// **'Global Percentage (0 - 100)'**
  String get scaleNormalized100;

  /// No description provided for @synConfigTitle.
  ///
  /// In en, this message translates to:
  /// **'Synthesis & Export Configuration'**
  String get synConfigTitle;

  /// No description provided for @synPreambleLabel.
  ///
  /// In en, this message translates to:
  /// **'Preamble Text'**
  String get synPreambleLabel;

  /// No description provided for @synMaxLengthLabel.
  ///
  /// In en, this message translates to:
  /// **'Max Length Constraint'**
  String get synMaxLengthLabel;

  /// No description provided for @synMaxLengthHelper.
  ///
  /// In en, this message translates to:
  /// **'Leave empty for no limit'**
  String get synMaxLengthHelper;

  /// No description provided for @synEnablePii.
  ///
  /// In en, this message translates to:
  /// **'Enable PII Masking'**
  String get synEnablePii;

  /// No description provided for @synEnablePiiHelper.
  ///
  /// In en, this message translates to:
  /// **'Ensure PII is masked before LLM call'**
  String get synEnablePiiHelper;

  /// No description provided for @synIncludeHistory.
  ///
  /// In en, this message translates to:
  /// **'Include Historical Summary'**
  String get synIncludeHistory;

  /// No description provided for @synOmitEmpty.
  ///
  /// In en, this message translates to:
  /// **'Omit Empty Sections'**
  String get synOmitEmpty;

  /// No description provided for @synAllowedExports.
  ///
  /// In en, this message translates to:
  /// **'Allowed Exports'**
  String get synAllowedExports;

  /// No description provided for @profileEditorVisibleExtensions.
  ///
  /// In en, this message translates to:
  /// **'Visible XAI Extensions'**
  String get profileEditorVisibleExtensions;

  /// No description provided for @profileEditorMaxExtensionItems.
  ///
  /// In en, this message translates to:
  /// **'Max Items per XAI Extension (Top X)'**
  String get profileEditorMaxExtensionItems;

  /// No description provided for @profileEditorMaxExtensionItemsDesc.
  ///
  /// In en, this message translates to:
  /// **'Limits how many most critical items are shown per section (Severity sorted).'**
  String get profileEditorMaxExtensionItemsDesc;

  /// No description provided for @reportExecutiveSummary.
  ///
  /// In en, this message translates to:
  /// **'Executive Summary'**
  String get reportExecutiveSummary;

  /// No description provided for @reportPromptTokens.
  ///
  /// In en, this message translates to:
  /// **'Prompt: {count}'**
  String reportPromptTokens(String count);

  /// No description provided for @reportCompletionTokens.
  ///
  /// In en, this message translates to:
  /// **'Completion: {count}'**
  String reportCompletionTokens(String count);

  /// No description provided for @reportReasoningTokens.
  ///
  /// In en, this message translates to:
  /// **'Reasoning: {count}'**
  String reportReasoningTokens(String count);

  /// No description provided for @strategyKoearvostelu.
  ///
  /// In en, this message translates to:
  /// **'Koearvostelu (Test Evaluation)'**
  String get strategyKoearvostelu;

  /// No description provided for @strategySyvaarvostelu.
  ///
  /// In en, this message translates to:
  /// **'Syväarvostelu (Deep Evaluation)'**
  String get strategySyvaarvostelu;

  /// No description provided for @strategyLineaarinenKeskiarvo.
  ///
  /// In en, this message translates to:
  /// **'Lineaarinen Keskiarvo (Linear Average)'**
  String get strategyLineaarinenKeskiarvo;

  /// No description provided for @strategyPainotettuKeskiarvo.
  ///
  /// In en, this message translates to:
  /// **'Painotettu Keskiarvo (Weighted Average)'**
  String get strategyPainotettuKeskiarvo;

  /// No description provided for @strategyPuhdasMatematiikka.
  ///
  /// In en, this message translates to:
  /// **'Puhdas Matematiikka (Pure Math)'**
  String get strategyPuhdasMatematiikka;

  /// No description provided for @allowContextualOverrideLabel.
  ///
  /// In en, this message translates to:
  /// **'Allow Contextual Override'**
  String get allowContextualOverrideLabel;

  /// No description provided for @allowContextualOverrideDescription.
  ///
  /// In en, this message translates to:
  /// **'Allows the LLM to justify semantic verification without a literal quotation if exact text evidence is physically absent.'**
  String get allowContextualOverrideDescription;

  /// No description provided for @enableContextualOverridesLabel.
  ///
  /// In en, this message translates to:
  /// **'Enable Contextual Overrides'**
  String get enableContextualOverridesLabel;

  /// No description provided for @enableContextualOverridesDescription.
  ///
  /// In en, this message translates to:
  /// **'Master toggle that globally enables or disables claim-level semantic overrides for this entire workflow run.'**
  String get enableContextualOverridesDescription;

  /// No description provided for @roleBlockLabel.
  ///
  /// In en, this message translates to:
  /// **'AI Persona Role Override'**
  String get roleBlockLabel;

  /// No description provided for @roleBlockDescription.
  ///
  /// In en, this message translates to:
  /// **'Select standard LLM persona (e.g. blk_role_critic).'**
  String get roleBlockDescription;

  /// No description provided for @protocolBlockLabel.
  ///
  /// In en, this message translates to:
  /// **'Evidence Extraction Protocol'**
  String get protocolBlockLabel;

  /// No description provided for @protocolBlockDescription.
  ///
  /// In en, this message translates to:
  /// **'Standard mecanic rules for blind mathematical verification.'**
  String get protocolBlockDescription;

  /// No description provided for @criteriaBlocksTitle.
  ///
  /// In en, this message translates to:
  /// **'Evaluation Criteria Matrices'**
  String get criteriaBlocksTitle;

  /// No description provided for @criteriaBlocksDescription.
  ///
  /// In en, this message translates to:
  /// **'Specific domain semantic claims to evaluate.'**
  String get criteriaBlocksDescription;

  /// No description provided for @xaiVarianceValidationTitle.
  ///
  /// In en, this message translates to:
  /// **'🤖 VARIANCE (COGNITIVE VS. MECHANICAL)'**
  String get xaiVarianceValidationTitle;

  /// No description provided for @xaiVerdictAligned.
  ///
  /// In en, this message translates to:
  /// **'✅ Aligned'**
  String get xaiVerdictAligned;

  /// No description provided for @xaiVerdictSycophancy.
  ///
  /// In en, this message translates to:
  /// **'❌ Sycophancy'**
  String get xaiVerdictSycophancy;

  /// No description provided for @xaiVerdictMisaligned.
  ///
  /// In en, this message translates to:
  /// **'⚠️ Misaligned'**
  String get xaiVerdictMisaligned;

  /// No description provided for @xaiVarianceBarAligned.
  ///
  /// In en, this message translates to:
  /// **'Aligned'**
  String get xaiVarianceBarAligned;

  /// No description provided for @xaiVarianceBarMild.
  ///
  /// In en, this message translates to:
  /// **'Mild Conflict'**
  String get xaiVarianceBarMild;

  /// No description provided for @xaiVarianceBarSevere.
  ///
  /// In en, this message translates to:
  /// **'Severe Conflict'**
  String get xaiVarianceBarSevere;

  /// No description provided for @xaiVarianceInfoText.
  ///
  /// In en, this message translates to:
  /// **'This metric reveals whether the AI\'s self-evaluation contradicts hard mechanical facts. For example, if the AI claims its output is perfectly authentic, but the mechanical scanner detects multiple AI filler words, a variance conflict is flagged.'**
  String get xaiVarianceInfoText;

  /// No description provided for @tdaAnchorTarget.
  ///
  /// In en, this message translates to:
  /// **'Anchor Target'**
  String get tdaAnchorTarget;

  /// No description provided for @tdaBoundingBox.
  ///
  /// In en, this message translates to:
  /// **'Bounding Box Scope'**
  String get tdaBoundingBox;

  /// No description provided for @tdaExtractionRule.
  ///
  /// In en, this message translates to:
  /// **'Extraction Rule'**
  String get tdaExtractionRule;

  /// No description provided for @systemAuditTrailLabel.
  ///
  /// In en, this message translates to:
  /// **'System Audit Trail'**
  String get systemAuditTrailLabel;

  /// No description provided for @systemAuditTrailDescription.
  ///
  /// In en, this message translates to:
  /// **'Enables MCPAuditTrace fact-checking report injection at the end of the document.'**
  String get systemAuditTrailDescription;

  /// No description provided for @workflowInputScanPerformative.
  ///
  /// In en, this message translates to:
  /// **'Scan for AI Jargon (Authenticity)'**
  String get workflowInputScanPerformative;

  /// No description provided for @xaiAuthenticityEvaluationTitle.
  ///
  /// In en, this message translates to:
  /// **'AI Jargon (Authenticity)'**
  String get xaiAuthenticityEvaluationTitle;

  /// No description provided for @penaltySecurity.
  ///
  /// In en, this message translates to:
  /// **'Security Threat Detected (-{percentage}%)'**
  String penaltySecurity(String percentage);

  /// No description provided for @penaltyPostHoc.
  ///
  /// In en, this message translates to:
  /// **'Post-Hoc Rationalization Detected (-{percentage}%)'**
  String penaltyPostHoc(String percentage);

  /// No description provided for @penaltySlop.
  ///
  /// In en, this message translates to:
  /// **'-5% Slop Penalty (AI Jargon): detected {phrases}'**
  String penaltySlop(String phrases);

  /// No description provided for @reject_quote_title.
  ///
  /// In en, this message translates to:
  /// **'Reject Evidence'**
  String get reject_quote_title;

  /// No description provided for @reject_quote_confirm.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to reject this piece of evidence?'**
  String get reject_quote_confirm;

  /// No description provided for @quote_rejected_warning.
  ///
  /// In en, this message translates to:
  /// **'Warning: All evidence for this observation has been rejected.'**
  String get quote_rejected_warning;

  /// No description provided for @reject_quote_reason_hint.
  ///
  /// In en, this message translates to:
  /// **'Optional: Reason for rejection'**
  String get reject_quote_reason_hint;

  /// No description provided for @lblNaCascadeReason.
  ///
  /// In en, this message translates to:
  /// **'N/A Cascade Reason: {reasons}'**
  String lblNaCascadeReason(String reasons);

  /// Label for 3D Matrix preset
  ///
  /// In en, this message translates to:
  /// **'3D: Matrix (Bubble)'**
  String get studioViewsMatrix3d;

  /// No description provided for @lexiconTitle.
  ///
  /// In en, this message translates to:
  /// **'Performative Lexicons (Slop Words)'**
  String get lexiconTitle;

  /// No description provided for @lexiconLangEn.
  ///
  /// In en, this message translates to:
  /// **'English (en)'**
  String get lexiconLangEn;

  /// No description provided for @lexiconLangFi.
  ///
  /// In en, this message translates to:
  /// **'Finnish (fi)'**
  String get lexiconLangFi;

  /// No description provided for @lexiconDiscoverNew.
  ///
  /// In en, this message translates to:
  /// **'Discover New'**
  String get lexiconDiscoverNew;

  /// No description provided for @lexiconTranslateMissing.
  ///
  /// In en, this message translates to:
  /// **'Translate Missing'**
  String get lexiconTranslateMissing;

  /// No description provided for @lexiconAddPlaceholder.
  ///
  /// In en, this message translates to:
  /// **'Add a new slop word / phrase'**
  String get lexiconAddPlaceholder;

  /// No description provided for @lexiconAddButton.
  ///
  /// In en, this message translates to:
  /// **'Add'**
  String get lexiconAddButton;

  /// No description provided for @lexiconDiscoveredSuccess.
  ///
  /// In en, this message translates to:
  /// **'Discovered and added {count} new phrases (out of {total}).'**
  String lexiconDiscoveredSuccess(int count, int total);

  /// No description provided for @lexiconDiscoveredEmpty.
  ///
  /// In en, this message translates to:
  /// **'No new phrases discovered.'**
  String get lexiconDiscoveredEmpty;

  /// No description provided for @lexiconTranslatedSuccess.
  ///
  /// In en, this message translates to:
  /// **'Translated and added {count} missing phrases.'**
  String lexiconTranslatedSuccess(int count);

  /// No description provided for @lexiconTranslatedEmpty.
  ///
  /// In en, this message translates to:
  /// **'No missing phrases to translate (did you forget to save the English words first?).'**
  String get lexiconTranslatedEmpty;

  /// No description provided for @studioViewsFailedToCreate.
  ///
  /// In en, this message translates to:
  /// **'Failed to create: {error}'**
  String studioViewsFailedToCreate(String error);

  /// No description provided for @studioViewsMatrixSubtitle.
  ///
  /// In en, this message translates to:
  /// **'ID: {id} | Scales (Grades): {scales}'**
  String studioViewsMatrixSubtitle(String id, int scales);

  /// No description provided for @unnamedGateway.
  ///
  /// In en, this message translates to:
  /// **'Unnamed Gateway'**
  String get unnamedGateway;

  /// No description provided for @gatewaySubtitle.
  ///
  /// In en, this message translates to:
  /// **'Allowed Tools: {tools} | Status: {status}'**
  String gatewaySubtitle(int tools, String status);

  /// No description provided for @activeStatus.
  ///
  /// In en, this message translates to:
  /// **'Active'**
  String get activeStatus;

  /// No description provided for @inactiveStatus.
  ///
  /// In en, this message translates to:
  /// **'Inactive'**
  String get inactiveStatus;

  /// No description provided for @addStrategyButton.
  ///
  /// In en, this message translates to:
  /// **'Add Strategy'**
  String get addStrategyButton;

  /// No description provided for @providerPlaceholder.
  ///
  /// In en, this message translates to:
  /// **'Provider (e.g. google, openai)'**
  String get providerPlaceholder;

  /// No description provided for @jsonMustBeObjectError.
  ///
  /// In en, this message translates to:
  /// **'Must be a valid JSON object'**
  String get jsonMustBeObjectError;

  /// No description provided for @mustBeNumberError.
  ///
  /// In en, this message translates to:
  /// **'Must be a number'**
  String get mustBeNumberError;

  /// No description provided for @mustBeIntegerError.
  ///
  /// In en, this message translates to:
  /// **'Must be an integer'**
  String get mustBeIntegerError;

  /// No description provided for @customPrefaceLabel.
  ///
  /// In en, this message translates to:
  /// **'Custom Preface (Rich Text)'**
  String get customPrefaceLabel;

  /// No description provided for @scoringEngineTitle.
  ///
  /// In en, this message translates to:
  /// **'Scoring Engine and Strictness'**
  String get scoringEngineTitle;

  /// No description provided for @identityMetadataTitle.
  ///
  /// In en, this message translates to:
  /// **'Identity Metadata'**
  String get identityMetadataTitle;

  /// No description provided for @metaDate.
  ///
  /// In en, this message translates to:
  /// **'Date (date)'**
  String get metaDate;

  /// No description provided for @metaOrganization.
  ///
  /// In en, this message translates to:
  /// **'Organization (organization)'**
  String get metaOrganization;

  /// No description provided for @metaUser.
  ///
  /// In en, this message translates to:
  /// **'User (user)'**
  String get metaUser;

  /// No description provided for @metaScoringEngine.
  ///
  /// In en, this message translates to:
  /// **'Scoring Engine (scoring_engine)'**
  String get metaScoringEngine;

  /// No description provided for @metaStrictness.
  ///
  /// In en, this message translates to:
  /// **'Strictness Level (strictness)'**
  String get metaStrictness;

  /// No description provided for @metaCost.
  ///
  /// In en, this message translates to:
  /// **'Cost Estimate (cost)'**
  String get metaCost;

  /// No description provided for @metaTokens.
  ///
  /// In en, this message translates to:
  /// **'Cognitive Load (tokens)'**
  String get metaTokens;

  /// No description provided for @maxExtensionItemsLabel.
  ///
  /// In en, this message translates to:
  /// **'Max Extension Items'**
  String get maxExtensionItemsLabel;

  /// No description provided for @maxExtensionItemsHelper.
  ///
  /// In en, this message translates to:
  /// **'Maximum number of items to show per XAI extension. 999 for unlimited.'**
  String get maxExtensionItemsHelper;

  /// No description provided for @extensionItemsMustBeIntError.
  ///
  /// In en, this message translates to:
  /// **'Given value must be an integer >= 1'**
  String get extensionItemsMustBeIntError;

  /// No description provided for @blockLevelExtensionsLabel.
  ///
  /// In en, this message translates to:
  /// **'Block-level Extensions'**
  String get blockLevelExtensionsLabel;

  /// No description provided for @workflowLevelExtensionsLabel.
  ///
  /// In en, this message translates to:
  /// **'Workflow-level Extensions'**
  String get workflowLevelExtensionsLabel;

  /// No description provided for @toggleLayoutTooltip.
  ///
  /// In en, this message translates to:
  /// **'Toggle Layout'**
  String get toggleLayoutTooltip;

  /// No description provided for @studioViewsErrorLoadingExtensions.
  ///
  /// In en, this message translates to:
  /// **'Error loading extensions: {error}'**
  String studioViewsErrorLoadingExtensions(String error);

  /// No description provided for @excelHeaderMatrix.
  ///
  /// In en, this message translates to:
  /// **'Matrix'**
  String get excelHeaderMatrix;

  /// No description provided for @excelHeaderGrade.
  ///
  /// In en, this message translates to:
  /// **'Grade'**
  String get excelHeaderGrade;

  /// No description provided for @excelHeaderMaxScore.
  ///
  /// In en, this message translates to:
  /// **'Max Score'**
  String get excelHeaderMaxScore;

  /// No description provided for @excelHeaderNote.
  ///
  /// In en, this message translates to:
  /// **'Note'**
  String get excelHeaderNote;

  /// No description provided for @excelHeaderCriterion.
  ///
  /// In en, this message translates to:
  /// **'Criterion Name (UI)'**
  String get excelHeaderCriterion;

  /// No description provided for @excelHeaderAiRule.
  ///
  /// In en, this message translates to:
  /// **'AI Rule'**
  String get excelHeaderAiRule;

  /// No description provided for @excelHeaderInternalizedRule.
  ///
  /// In en, this message translates to:
  /// **'Internalized Rule'**
  String get excelHeaderInternalizedRule;

  /// No description provided for @excelHeaderResultStatus.
  ///
  /// In en, this message translates to:
  /// **'Result (Status)'**
  String get excelHeaderResultStatus;

  /// No description provided for @excelHeaderConfidence.
  ///
  /// In en, this message translates to:
  /// **'Confidence Estimate'**
  String get excelHeaderConfidence;

  /// No description provided for @excelHeaderReasoningLength.
  ///
  /// In en, this message translates to:
  /// **'Reasoning Length'**
  String get excelHeaderReasoningLength;

  /// No description provided for @excelHeaderFoundQuotes.
  ///
  /// In en, this message translates to:
  /// **'Found Quotes'**
  String get excelHeaderFoundQuotes;

  /// No description provided for @excelHeaderUsedSources.
  ///
  /// In en, this message translates to:
  /// **'Used Sources'**
  String get excelHeaderUsedSources;

  /// No description provided for @excelHeaderAiReasoning.
  ///
  /// In en, this message translates to:
  /// **'AI Reasoning'**
  String get excelHeaderAiReasoning;

  /// No description provided for @excelHeaderFalsification.
  ///
  /// In en, this message translates to:
  /// **'Falsification'**
  String get excelHeaderFalsification;

  /// No description provided for @excelNoteNoScores.
  ///
  /// In en, this message translates to:
  /// **'No scoring results in this execution'**
  String get excelNoteNoScores;

  /// No description provided for @excelNoteNoAtoms.
  ///
  /// In en, this message translates to:
  /// **'No atoms found'**
  String get excelNoteNoAtoms;

  /// No description provided for @excelSheetSummary.
  ///
  /// In en, this message translates to:
  /// **'Summary'**
  String get excelSheetSummary;

  /// No description provided for @excelSheetRawData.
  ///
  /// In en, this message translates to:
  /// **'Raw Data'**
  String get excelSheetRawData;

  /// No description provided for @profileTabGeneral.
  ///
  /// In en, this message translates to:
  /// **'General'**
  String get profileTabGeneral;

  /// No description provided for @profileTabXai.
  ///
  /// In en, this message translates to:
  /// **'Extensions (XAI)'**
  String get profileTabXai;

  /// No description provided for @profileTabLayouts.
  ///
  /// In en, this message translates to:
  /// **'Layouts'**
  String get profileTabLayouts;

  /// No description provided for @layoutBlockDescriptionLabel.
  ///
  /// In en, this message translates to:
  /// **'Section Description (Optional)'**
  String get layoutBlockDescriptionLabel;

  /// No description provided for @sectionSynthesisToggleLabel.
  ///
  /// In en, this message translates to:
  /// **'Include in AI Synthesis'**
  String get sectionSynthesisToggleLabel;

  /// No description provided for @sectionSynthesisToggleDesc.
  ///
  /// In en, this message translates to:
  /// **'Toggle to completely exclude this section from AI report synthesis.'**
  String get sectionSynthesisToggleDesc;

  /// No description provided for @sectionCustomSynthesisLabel.
  ///
  /// In en, this message translates to:
  /// **'Use Section-Specific Custom Synthesis'**
  String get sectionCustomSynthesisLabel;

  /// No description provided for @sectionCustomSynthesisDesc.
  ///
  /// In en, this message translates to:
  /// **'Overrides the global synthesis settings for this specific section.'**
  String get sectionCustomSynthesisDesc;

  /// No description provided for @pdfAuditDuration.
  ///
  /// In en, this message translates to:
  /// **'Duration:'**
  String get pdfAuditDuration;

  /// No description provided for @pdfAuditQuery.
  ///
  /// In en, this message translates to:
  /// **'Search Query:'**
  String get pdfAuditQuery;

  /// No description provided for @pdfAuditImpactedAxes.
  ///
  /// In en, this message translates to:
  /// **'This information was used in evaluating the following axes:'**
  String get pdfAuditImpactedAxes;

  /// No description provided for @pdfAuditSources.
  ///
  /// In en, this message translates to:
  /// **'Sources'**
  String get pdfAuditSources;

  /// No description provided for @meta_timestamp.
  ///
  /// In en, this message translates to:
  /// **'Timestamp'**
  String get meta_timestamp;

  /// No description provided for @meta_user.
  ///
  /// In en, this message translates to:
  /// **'Meta User'**
  String get meta_user;

  /// No description provided for @meta_organization.
  ///
  /// In en, this message translates to:
  /// **'Meta Organization'**
  String get meta_organization;

  /// No description provided for @meta_unknown.
  ///
  /// In en, this message translates to:
  /// **'Meta Unknown'**
  String get meta_unknown;

  /// No description provided for @global_score_title.
  ///
  /// In en, this message translates to:
  /// **'Global Score Title'**
  String get global_score_title;

  /// No description provided for @evidence_rejected.
  ///
  /// In en, this message translates to:
  /// **'Evidence Rejected'**
  String get evidence_rejected;

  /// No description provided for @meta_costs.
  ///
  /// In en, this message translates to:
  /// **'Meta Costs'**
  String get meta_costs;

  /// No description provided for @meta_tokens.
  ///
  /// In en, this message translates to:
  /// **'Meta Tokens'**
  String get meta_tokens;
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
