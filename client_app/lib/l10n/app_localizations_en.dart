// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Cognitive Quorum Client';

  @override
  String get loginBtn => 'Login';

  @override
  String get adminPanel => 'Admin Panel';

  @override
  String get settings => 'Settings';

  @override
  String get language => 'Language';

  @override
  String get themeMode => 'Theme Mode';

  @override
  String get system => 'System';

  @override
  String get light => 'Light';

  @override
  String get dark => 'Dark';

  @override
  String configureInputs(String workflowId) {
    return 'Configure Inputs: $workflowId';
  }

  @override
  String get generalInput => 'General Input';

  @override
  String fileInputLabel(String fileName, int size) {
    return 'File: $fileName ($size bytes)';
  }

  @override
  String get selectFile => 'Select a file...';

  @override
  String get fieldRequired => 'This field is required.';

  @override
  String get fileRequired => 'This file is required.';

  @override
  String get dashboardTitle => 'Recent Logic Executions';

  @override
  String get totalRuns => 'Total Runs';

  @override
  String get inProgress => 'In Progress';

  @override
  String get criticalFailures => 'Critical Failures';

  @override
  String get noExecutions => 'No executions found.';

  @override
  String failedToLoad(Object error) {
    return 'Failed to load executions: $error';
  }

  @override
  String get retry => 'Retry';

  @override
  String get newAnalysis => 'New Analysis';

  @override
  String get executionDetails => 'Execution Details';

  @override
  String get overview => 'Overview';

  @override
  String get report => 'Report';

  @override
  String get rawData => 'Raw Data';

  @override
  String get status => 'STATUS';

  @override
  String get timeline => 'Timeline';

  @override
  String get created => 'Created';

  @override
  String get workflowProgress => 'Workflow Progress';

  @override
  String get analysisInProgress => 'Analysis in progress...';

  @override
  String currentStep(Object step) {
    return 'Current Step: $step';
  }

  @override
  String get waitingToStart => 'Waiting to start...';

  @override
  String get executionStarted => 'Execution Started...';

  @override
  String executionFailed(Object error) {
    return 'Execution Failed: $error';
  }

  @override
  String get unknownState => 'Unknown State';

  @override
  String get downloadNotImplemented => 'Download not implemented yet';

  @override
  String get detailsComingSoon => 'Details view coming soon...';

  @override
  String get viewChecklist => 'View Checklist';

  @override
  String get viewRawData => 'View Raw Data';

  @override
  String get analysisResults => 'Analysis Results';

  @override
  String get goToMonitor => 'Go to Monitor';

  @override
  String get analysisNotComplete => 'Analysis is not complete yet.';

  @override
  String get verdict => 'Verdict';

  @override
  String get score => 'Score';

  @override
  String get summary => 'Summary';

  @override
  String get type => 'Type';

  @override
  String get inputs => 'Inputs';

  @override
  String get startAnalysis => 'Start Analysis';

  @override
  String get next => 'Next';

  @override
  String get back => 'Back';

  @override
  String get cancel => 'Cancel';

  @override
  String get analysisStarted => 'Analysis Started!';

  @override
  String submissionFailed(Object error) {
    return 'Submission Failed: $error';
  }

  @override
  String get fillRequiredInputs => 'Please fill in required inputs.';

  @override
  String errorReadingFile(Object error) {
    return 'Error reading file: $error';
  }

  @override
  String get noWorkflowsAvailable => 'No workflows available for your account.';

  @override
  String get enterCustomWorkflowId => 'Or enter Custom Workflow ID';

  @override
  String get statusCompleted => 'COMPLETED';

  @override
  String get statusRunning => 'RUNNING';

  @override
  String get statusFailed => 'FAILED';

  @override
  String get statusRejected => 'REJECTED';

  @override
  String get statusPending => 'PENDING';

  @override
  String get statusStarted => 'STARTED';

  @override
  String get inputChatHistory => '1. Chat History / Evidence (Chat Logs)';

  @override
  String get inputProductTarget =>
      '2. Product / Evaluation Target (Final Product)';

  @override
  String get inputReflection => '3. Reflection / Self-Evaluation';

  @override
  String get unknownWorkflow => 'Unknown Workflow';

  @override
  String get navDashboard => 'Dashboard';

  @override
  String get navSettings => 'Settings';

  @override
  String get navAdmin => 'Admin';

  @override
  String stepLabel(Object stepName) {
    return 'Step: $stepName';
  }

  @override
  String get defaultWorkflowTitle => 'Workflow Execution';

  @override
  String executionIdLabel(Object id) {
    return 'Execution $id';
  }

  @override
  String get resultsTitle => 'Analysis Results';

  @override
  String get viewLogTooltip => 'View Execution Log';

  @override
  String get downloadReportTooltip => 'Download Report';

  @override
  String get downloadNotImplementedPdf => 'Download PDF not implemented yet';

  @override
  String get chooseAnalysisType => 'Choose Analysis Type';

  @override
  String get usageCurrentMonth => 'Current Month Usage';

  @override
  String get usageQuota => 'Usage vs Quota';

  @override
  String tokensUsed(int count) {
    final intl.NumberFormat countNumberFormat = intl
        .NumberFormat.decimalPattern(localeName);
    final String countString = countNumberFormat.format(count);

    return '$countString Tokens Used';
  }

  @override
  String quotaLimit(int limit) {
    final intl.NumberFormat limitNumberFormat = intl
        .NumberFormat.decimalPattern(localeName);
    final String limitString = limitNumberFormat.format(limit);

    return '$limitString Limit';
  }

  @override
  String get selectWorkflowRequired => 'Please select a workflow.';

  @override
  String get adminDashboardTitle => 'Admin Dashboard';

  @override
  String get welcomeAdmin => 'Welcome to Admin Dashboard';

  @override
  String get manageUsersButton => 'Manage Users';

  @override
  String get manageOrganizationsButton => 'Manage Organizations';

  @override
  String get userManagementTitle => 'User Management';

  @override
  String get organizationManagementTitle => 'Organization Management';

  @override
  String get userListPlaceholder => 'User Management List Placeholder';

  @override
  String get organizationListPlaceholder => 'Organization List Placeholder';

  @override
  String monitorTitle(String id) {
    return 'Monitor: $id';
  }

  @override
  String get viewResults => 'View Results';

  @override
  String get analysisCompletedSuccess => 'Analysis Completed Successfully!';

  @override
  String get viewFullReport => 'View Full Report';

  @override
  String get viewRawDataComingSoon => 'View Raw Data (Coming Soon)';

  @override
  String get stepGuard => 'Guard Agent (Safety)';

  @override
  String get stepAnalyst => 'Analyst Agent (Research)';

  @override
  String get stepInteraction => 'Interaction Analyst';

  @override
  String get stepProfiler => 'Profiler Agent';

  @override
  String get stepPanel => 'Panel Audit (Parallel)';

  @override
  String get stepArchivist => 'Archivist (History)';

  @override
  String get stepJudge => 'Judge (Verdict)';

  @override
  String get stepCoach => 'Coach (Feedback)';

  @override
  String get stepReporter => 'Reporter (Final Report)';

  @override
  String get stepInitializing => 'Initializing...';

  @override
  String validationMissingEvidence(String fields) {
    return 'Missing required evidence: $fields';
  }

  @override
  String get validationInputEmpty => 'Inputs cannot be empty.';

  @override
  String get errorUnknown => 'Unknown error occurred.';

  @override
  String get errorNetwork => 'Network error. Please check your connection.';

  @override
  String get errorServer => 'Server error. Please try again later.';

  @override
  String get errorUnauthorized => 'Unauthorized. Please log in again.';

  @override
  String get errorNotFound => 'Resource not found.';

  @override
  String get errorValidation => 'Validation failed.';

  @override
  String get errorValidationEmpty => 'Inputs cannot be empty.';

  @override
  String errorValidationMissing(String fields) {
    return 'Missing required fields: $fields';
  }
}
