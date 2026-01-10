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
}
