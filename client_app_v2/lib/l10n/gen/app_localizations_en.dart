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
  String get delete => 'Delete';

  @override
  String get errorUnknown => 'Unknown error';

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

  @override
  String errorDataMapping(String field, String detail) {
    return 'Mapping Error in field \'$field\': $detail';
  }

  @override
  String errorDataType(String field, String detail) {
    return 'Type Error in field \'$field\': $detail';
  }

  @override
  String get errorLoadingData => 'Error loading data. Please try again.';

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
  String get selectFile => 'Select a file to upload';

  @override
  String get fieldRequired => 'This field is required.';

  @override
  String get authOrganic => 'Organic (Authentic)';

  @override
  String get authPerformative => 'Performative (Staged)';

  @override
  String get authUnknown => 'Unknown';

  @override
  String get verVerified => 'Verified';

  @override
  String get verDebunked => 'Debunked';

  @override
  String get verUncertain => 'Uncertain';

  @override
  String get fileRequired => 'This file is required.';

  @override
  String workflowSubtitle(int steps, int inputs) {
    return 'Steps: $steps | Inputs: $inputs';
  }

  @override
  String matrixSubtitle(int rules) {
    return 'Rules: $rules';
  }

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
  String executionRejected(Object error) {
    return 'Execution Rejected: $error';
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
    return 'Submission failed: $error';
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
  String get statusRejected => 'Rejected';

  @override
  String get statusDraft => 'DRAFT';

  @override
  String get typeString => 'String';

  @override
  String get typeFloat => 'Float';

  @override
  String get typeInt => 'Integer (Whole Number)';

  @override
  String get typeJson => 'JSON';

  @override
  String get typeBoolean => 'Boolean';

  @override
  String get cancelling => 'Cancelling';

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
  String get pasteText => 'Paste Text';

  @override
  String get uploadFile => 'Upload File';

  @override
  String get pasteTextLabel => 'Paste text here...';

  @override
  String get unknownWorkflow => 'Unknown Workflow';

  @override
  String get navDashboard => 'Dashboard';

  @override
  String get navSettings => 'Settings';

  @override
  String get navAdmin => 'Admin';

  @override
  String get navStudio => 'Studio';

  @override
  String get navRegistry => 'Registry';

  @override
  String get navAnalytics => 'Analytics';

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
  String get printVariantSelectorTitle => 'Select Print Variant';

  @override
  String get printVariantSelectorDescription =>
      'Choose a variant for this execution report.';

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
    final intl.NumberFormat countNumberFormat =
        intl.NumberFormat.decimalPattern(localeName);
    final String countString = countNumberFormat.format(count);

    return '$countString Tokens Used';
  }

  @override
  String quotaLimit(int limit) {
    final intl.NumberFormat limitNumberFormat =
        intl.NumberFormat.decimalPattern(localeName);
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
  String get systemSettingsTitle => 'System Settings';

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
  String get stepXai => 'XAI Reporter (Final Report)';

  @override
  String get stepInitializing => 'Initializing...';

  @override
  String get stepLogician => 'Logic Audit (Logician)';

  @override
  String get stepFalsifier => 'Critical Audit (Falsifier)';

  @override
  String get stepCausal => 'Causal Audit (Causal)';

  @override
  String get stepDetector => 'Illusion Audit (Detector)';

  @override
  String get stepOverseer => 'Overseer (Fact)';

  @override
  String get stepJudgeCognitive => 'Judge (Cognitive)';

  @override
  String get stepContext => 'Context Retrieval';

  @override
  String get stepInputProcessor => 'Input Processing';

  @override
  String validationMissingEvidence(String fields) {
    return 'Missing required evidence: $fields';
  }

  @override
  String get validationInputEmpty => 'Inputs cannot be empty.';

  @override
  String get createOrganization => 'Create Organization';

  @override
  String get editOrganization => 'Edit Organization';

  @override
  String get deleteOrganization => 'Delete Organization';

  @override
  String get errorDeleteBlockedByExecutions =>
      'Cannot delete: Item has active executions.';

  @override
  String get errorDeleteBlockedByMatrix =>
      'Cannot delete: Observation is bound to a PromptBlock.';

  @override
  String get errorResourceInUse => 'Cannot delete: Record is still in use.';

  @override
  String get save => 'Save';

  @override
  String get orgNameLabel => 'Organization Name';

  @override
  String get orgTierLabel => 'Tier';

  @override
  String get basicTier => 'Basic';

  @override
  String get premiumTier => 'Premium';

  @override
  String get enterpriseTier => 'Enterprise';

  @override
  String deleteOrgConfirmation(String name) {
    return 'Are you sure you want to delete $name?';
  }

  @override
  String get deleteOrgHasUsersTitle => 'Organization has users';

  @override
  String get deleteOrgHasUsersMessage =>
      'This organization contains users. Deleting it will also permanently delete all its users. This action cannot be undone.';

  @override
  String get deleteForceConfirm => 'Delete everything';

  @override
  String get contactEmailLabel => 'Contact Email';

  @override
  String get userManagement => 'User Management';

  @override
  String get roleManager => 'Role Manager';

  @override
  String get lastActive => 'Last Active';

  @override
  String get executionCount => 'Executions';

  @override
  String get roleUpdateSuccess => 'Role updated successfully.';

  @override
  String get demoteLastAdminError =>
      'Cannot demote the last Admin. Promote another user first.';

  @override
  String get queueStatus => 'System Queue';

  @override
  String get queuedJobs => 'Queued';

  @override
  String get activeJobs => 'Active';

  @override
  String get roleLabel => 'Role';

  @override
  String get lastLogin => 'Last seen';

  @override
  String get lblWeak => 'Weak';

  @override
  String get lblModerate => 'Moderate';

  @override
  String get lblStrong => 'Strong';

  @override
  String get lblSource => 'Source';

  @override
  String get lblAbstractQuadrant => 'Abstract (High Bloom + Low Toulmin)';

  @override
  String get lblSuperficialQuadrant => 'Superficial (Low Bloom + Low Toulmin)';

  @override
  String get actions => 'Actions';

  @override
  String get editRole => 'Edit Role';

  @override
  String get confirmDemotion =>
      'Warning: Demoting an Admin limits their access immediately.';

  @override
  String get organizationMembers => 'Organization Members';

  @override
  String get refresh => 'Refresh';

  @override
  String get noUsersFound => 'No users found.';

  @override
  String get loginRequired => 'Login Required';

  @override
  String get createUser => 'Create User';

  @override
  String get editUser => 'Edit User';

  @override
  String get deleteUser => 'Delete User';

  @override
  String get displayNameLabel => 'Display Name';

  @override
  String get emailLabel => 'Email';

  @override
  String get passwordLabel => 'Password';

  @override
  String deleteUserConfirmation(String name) {
    return 'Are you sure you want to delete $name?';
  }

  @override
  String get userCreatedSuccess => 'User created successfully.';

  @override
  String get userUpdatedSuccess => 'User updated successfully.';

  @override
  String get userDeletedSuccess => 'User deleted successfully.';

  @override
  String get organizationId => 'Organization ID';

  @override
  String get helpBloom =>
      'Based on the Revised Bloom\'s Taxonomy (Anderson & Krathwohl, 2001), this metric evaluates the cognitive complexity of the output. It distinguishes between lower-order thinking (Remembering, Understanding) and higher-order skills (Applying, Analyzing, Evaluating, Creating). High scores indicate the agent is not just retrieving facts but synthesizing new information.';

  @override
  String get helpToulmin =>
      'Derived from Stephen Toulmin\'s \'The Uses of Argument\' (1958), this model moves beyond formal logic to practical argumentation. It assesses whether the Claim is supported by Data and connected via a Warrant. This structure ensures that arguments are not just assertions but reasoned positions.';

  @override
  String get helpWalton =>
      'Based on Douglas Walton\'s Argumentation Schemes, Fidelity measures dialectical consistency. It checks if the reasoning strictly adheres to the provided premises (Source Data) or if the agent engages in \'Post-Hoc Rationalization\'—inventing justifications after the fact to support a hallucinated or biased conclusion.';

  @override
  String get helpControlRatio =>
      'Based on Discourse Analysis and Interaction Dynamics, this ratio measures the balance of initiative. A \'Passenger\' merely responds (reactive), while a \'Driver\' or \'Architect\' sets the frame and direction of the conversation (proactive). High control indicates the AI is leading the cognitive work.';

  @override
  String get helpMethodology =>
      'The Methodological Log tells what analysis methods the AI has applied in this phase (e.g. \'Logic Audit\', \'Causality Testing\').';

  @override
  String get rolePassenger => 'Passenger';

  @override
  String get roleNavigator => 'Navigator';

  @override
  String get roleDriver => 'Driver';

  @override
  String get roleArchitect => 'Architect';

  @override
  String get lblCognitiveLevel => 'Cognitive Level';

  @override
  String get lblStrategicDepth => 'Strategic Depth';

  @override
  String get lblArguments => 'Arguments';

  @override
  String get lblWaltonScheme => 'Walton Scheme';

  @override
  String get lblCriticalQuestions => 'Critical Questions';

  @override
  String get lblRoleAndPosition => 'User Role & Position';

  @override
  String get lblControlRatio => 'Control Ratio';

  @override
  String get biasDetected => 'BIAS DETECTED';

  @override
  String get biasNone => 'No Bias';

  @override
  String get gapDetected => 'GAP DETECTED';

  @override
  String get gapNone => 'Consistent';

  @override
  String get lblBloomScore => 'Bloom Score';

  @override
  String get lblToulminScore => 'Toulmin Score';

  @override
  String get lblMethodologicalLog => 'Methodological Log';

  @override
  String get lblLogicMatrix => 'Logic Matrix';

  @override
  String get lblMatrixSubtitle => 'Visual analysis of reasoning quality.';

  @override
  String get lblFidelity => 'Reasoning Fidelity';

  @override
  String get lblPostHocWarning => '⚠️ Post-Hoc Rationalization detected!';

  @override
  String get lblNoRationalization => '✅ No rationalization.';

  @override
  String get lblAbductiveReasoning => 'Abductive Reasoning';

  @override
  String get lblScenarioActual => 'Scenario A (Actual)';

  @override
  String get lblScenarioSimulation => 'Scenario B (Simulation)';

  @override
  String get lblCredibility => 'Credibility';

  @override
  String get lblTextMetrics => 'Text Metrics';

  @override
  String get lblBias => 'Identified Biases';

  @override
  String get lblAuthors => 'Authors';

  @override
  String get lblIntent => 'Author Intent';

  @override
  String get lblPsychProfile => 'Psychological Profile';

  @override
  String get lblFactCheck => 'Fact Check';

  @override
  String get lblEthicalObservation => 'Ethical Observation';

  @override
  String get lblAuthenticity => 'Authenticity Assessment';

  @override
  String get lblHeuristics => 'Heuristics';

  @override
  String get lblComplianceAnalysis => 'Compliance Analysis';

  @override
  String get helpComplianceAnalysis => 'Compliance Analysis';

  @override
  String get helpFidelity =>
      'Fidelity measures the logical consistency of the argument. It checks if the conclusion follows strictly from the premises, without inventing new information (Hallucination) or justifying a pre-decided conclusion (Post-Hoc Rationalization).';

  @override
  String get helpAbductive =>
      'Abductive Reasoning (Inference to Best Explanation) evaluates if the AI\'s conclusion is the most plausible explanation for the observations, rejecting less likely alternatives.';

  @override
  String get helpStressTest =>
      'Walton\'s stress test audits the fidelity of reasoning. It reveals \'Post-Hoc rationalization\' if the AI has merely invented justifications afterwards and did not actually derive the result from them.';

  @override
  String get helpCausal =>
      'Rooted in C.S. Peirce\'s logic of \'Inference to the Best Explanation\', Abductive reasoning infers the most likely cause. Plausibility, grounded in Counterfactual theories (e.g. Judea Pearl), tests causal understanding by simulating \'What If?\' scenarios to check logical consistency.';

  @override
  String get helpProfiler =>
      'Profiling analyzes text tone, vocabulary, and latent biases. It helps identify if the AI is attempting to manipulate or is biased.';

  @override
  String get helpFactCheck =>
      'Fact Check compares claims against a known knowledge base and scans for ethical risks.';

  @override
  String get helpPerformativity =>
      'Performativity analysis evaluates whether the response is authentic and organic or artificial and staged. It detects \'purple prose\', excessive humility, and other inauthentic traits.';

  @override
  String get helpArchivist =>
      'In the context of AI Alignment and Constitutional AI, Compliance measures the agent\'s adherence to defined behavioral constraints (The Constitution) and organizational norms, ensuring safety and goal alignment regardless of the user\'s prompt.';

  @override
  String get studioStepsTitle => 'Steps';

  @override
  String get studioConfigurationTitle => 'Configuration';

  @override
  String get studioAddStepButton => 'Add Step';

  @override
  String get studioSaveButton => 'Save Changes';

  @override
  String get studioUnsavedChanges => 'Unsaved changes';

  @override
  String get studioSelectStepPrompt => 'Select a step to configure';

  @override
  String get studioStepsHeader => 'Steps';

  @override
  String get studioAddStep => 'Add Step';

  @override
  String get studioNoSteps => 'No steps defined';

  @override
  String get studioRunTest => 'Run Test';

  @override
  String get studioSaving => 'Saving...';

  @override
  String get studioChangesSaved => 'Changes saved';

  @override
  String get studioCreateNew => 'Create New';

  @override
  String get studioCopyWorkflow => 'Copy Workflow';

  @override
  String get studioNewNameLabel => 'New Name';

  @override
  String get studioTabWorkflows => 'Workflows';

  @override
  String get studioTabMatrices => 'PromptBlocks';

  @override
  String get studioCreateMatrix => 'Create PromptBlock';

  @override
  String get studioMatrixName => 'Block Name';

  @override
  String get studioMatrixDesc => 'Description';

  @override
  String get matrixRole => 'Role Persona (For Instructions)';

  @override
  String get matrixScale => 'Scale (Min - Max)';

  @override
  String get matrixCriteria => 'Criteria (Schema)';

  @override
  String get matrixAddCriterion => 'Add Observation';

  @override
  String matrixLevel(Object level) {
    return 'Level $level';
  }

  @override
  String get studioSelectMatrix => 'Select PromptBlock';

  @override
  String get update => 'Update';

  @override
  String get editDimension => 'Edit Observation';

  @override
  String get systemInspectorTitle => 'System Inspector';

  @override
  String get workflowConfig => 'Config';

  @override
  String get stepPreview => 'Preview';

  @override
  String get generateChain => 'Generate Chain';

  @override
  String get systemInstruction => 'System Instruction';

  @override
  String get userPrompt => 'User Prompt';

  @override
  String get exportTab => 'Export';

  @override
  String get selectStepPlaceholder => 'Select a step...';

  @override
  String get copyToClipboard => 'Copy to Clipboard';

  @override
  String get copiedToClipboard => 'Copied to Clipboard!';

  @override
  String get modelRegistryTitle => 'Model Registry';

  @override
  String get providerSettings => 'Provider Settings';

  @override
  String get testLab => 'Test Laboratory';

  @override
  String get runTest => 'Run Test';

  @override
  String get latency => 'Latency';

  @override
  String get providerLabel => 'Provider';

  @override
  String get apiKeyLabel => 'API Key';

  @override
  String get baseUrlLabel => 'Base URL';

  @override
  String get temperatureLabel => 'Temperature';

  @override
  String get modelNameLabel => 'Model Name';

  @override
  String get testConnection => 'Test Connection';

  @override
  String get adhocTest => 'Ad-Hoc Test';

  @override
  String get responseOutput => 'Response Output';

  @override
  String get studioDashboardWorkflowsTitle => 'Workflows';

  @override
  String get studioDashboardWorkflowsDesc =>
      'Design and manage audit workflows.';

  @override
  String get studioDashboardStepsTitle => 'Steps';

  @override
  String get studioDashboardStepsDesc => 'Configure execution steps.';

  @override
  String get studioDashboardMatricesTitle => 'PromptBlocks';

  @override
  String get studioDashboardMatricesDesc =>
      'Manage dynamic LLM evaluation schema and instructions.';

  @override
  String get studioDashboardComponentsTitle => 'V1 Components';

  @override
  String get studioDashboardComponentsDesc =>
      'Manage legacy V1 rules (deprecation pending).';

  @override
  String get helperSelectProvider => 'Select from available providers';

  @override
  String get helperSelectModel => 'Select valid model for provider';

  @override
  String get helperApiKeyMasked => 'Leave as ******** to keep existing key';

  @override
  String get helperOptionalOverride => 'Optional override';

  @override
  String get errorMustBeNumber => 'Must be a number';

  @override
  String get errorRangeTemperature => 'Must be between 0.0 and 2.0';

  @override
  String get errorMustBeInteger => 'Must be an integer';

  @override
  String get selectProviderPlaceholder => 'Select a provider to configure.';

  @override
  String get searchSteps => 'Search Steps';

  @override
  String get stepSelectToEdit => 'Select a step to edit';

  @override
  String deleteWorkflowConfirmation(String name) {
    return 'Are you sure you want to delete $name?';
  }

  @override
  String get workflowDeleteConfirmTitle => 'Delete Workflow';

  @override
  String workflowDeleteConfirmDesc(String id) {
    return 'Are you sure you want to delete workflow \"$id\"?';
  }

  @override
  String get noMatricesFound => 'No PromptBlocks found. Create one!';

  @override
  String get stepCreateNew => 'Create New Step';

  @override
  String get stepEdit => 'Edit Step';

  @override
  String get stepIdLabel => 'Step ID (UUID or Unique String)';

  @override
  String get stepIdHelper => 'Unique identifier (e.g. \'step_analyst\')';

  @override
  String get stepNameLabel => 'Name';

  @override
  String get stepDescriptionLabel => 'Description';

  @override
  String get stepAgentLogicClass => 'Agent Logic Class';

  @override
  String get stepJudgeConfig => 'Judge Configuration';

  @override
  String get stepEvaluationMatrix => 'PromptBlock (Evaluation)';

  @override
  String get stepEvaluationMatrixHelper =>
      'The criteria used for schema generation.';

  @override
  String get stepPromptAssembly => 'PromptBlock (Instructions)';

  @override
  String get stepAddPrompt => 'Attach PromptBlock';

  @override
  String get stepPromptAssemblyHelper =>
      'Blocks that shape the step\'s system instruction.';

  @override
  String get stepSaveSuccess => 'Step saved!';

  @override
  String get stepDeleteConfirmTitle => 'Delete Step';

  @override
  String stepDeleteConfirmMessage(String id) {
    return 'Are you sure you want to delete step \"$id\"?';
  }

  @override
  String get stepAddPromptTitle => 'Attach PromptBlock to Step';

  @override
  String get stepSearchPrompts => 'Search PromptBlocks';

  @override
  String get close => 'Close';

  @override
  String get stepIdNameRequired => 'ID and Name are required.';

  @override
  String get executionNotFound => 'Execution Not Found';

  @override
  String get ontologyNameLabel => 'Name (e.g. \"Reasoning\")';

  @override
  String get ontologyDescriptionLabel => 'Description';

  @override
  String get registerDimension => 'Register Observation';

  @override
  String get newDimension => 'New Observation';

  @override
  String get lblQuestion => 'Question';

  @override
  String get lblEvidenceHeld => 'Evidence Held?';

  @override
  String get lblObservation => 'Observation';

  @override
  String get lblCausalAudit => 'Causal Audit';

  @override
  String get lblCounterfactualTest => 'Counterfactual Test';

  @override
  String get btnHideRawData => 'Hide Raw Data';

  @override
  String get btnShowJson => 'JSON';

  @override
  String get msgJsonCopied => 'JSON copied to clipboard';

  @override
  String get errDataIntegrity => 'Data Integrity Error (Fail Fast)';

  @override
  String get subLogicAnalysis => 'Toulmin & Cognitive Level';

  @override
  String get subStressTest => 'Walton Falsification';

  @override
  String get subCausalAnalysis => 'Causal & Counterfactual';

  @override
  String get subPerformativityCheck => 'Authenticity & Pre-Mortem';

  @override
  String get subFactCheck => 'Hallucinations & Ethics';

  @override
  String get subProfilerAnalysis => 'Biases & Psycho-profile';

  @override
  String get subArchivistCheck => 'Compliance & Precedents';

  @override
  String get lblWordCount => 'Word Count';

  @override
  String get lblSentenceCount => 'Sentence Count';

  @override
  String get lblAvgSentence => 'Avg Sentence';

  @override
  String get lblLexicalDiversity => 'Lexical Diversity';

  @override
  String get lblCapitalsRatio => 'Capitals Ratio';

  @override
  String get lblAutomationBias => 'Automation Bias';

  @override
  String get lblSayDoGap => 'Say-Do Gap';

  @override
  String get lblBehavioralIndicators => 'Behavioral Indicators:';

  @override
  String lblAutomationBiasValue(String value) {
    return 'Automation Bias: $value';
  }

  @override
  String lblSayDoGapValue(String value) {
    return 'Say-Do Gap: $value';
  }

  @override
  String get plausibility_desc =>
      'Plausibility measures scenario realism and consistency.';

  @override
  String get bloomRemembering => 'Remembering';

  @override
  String get bloomUnderstanding => 'Understanding';

  @override
  String get bloomApplying => 'Applying';

  @override
  String get bloomAnalyzing => 'Analyzing';

  @override
  String get bloomEvaluating => 'Evaluating';

  @override
  String get bloomCreating => 'Creating';

  @override
  String get stratLow => 'Tactical';

  @override
  String get stratMedium => 'Operational';

  @override
  String get stratHigh => 'Strategic';

  @override
  String get stratVisionary => 'Visionary';

  @override
  String get logicMatrixTitle => 'Logic Matrix (Decision Profiling)';

  @override
  String get logicMatrixQ1Title => 'Grounded Synthesis';

  @override
  String get logicMatrixQ1Desc =>
      'Strong argumentation and deep synthesis. Reliable and innovative.';

  @override
  String get logicMatrixQ2Title => 'Unwarranted Ideation';

  @override
  String get logicMatrixQ2Desc =>
      'High-level thinking without sufficient warrants. Potential hallucination.';

  @override
  String get logicMatrixQ3Title => 'Pedantic Fact-telling';

  @override
  String get logicMatrixQ3Desc =>
      'Strictly warranted, but limited to repeating existing knowledge.';

  @override
  String get logicMatrixQ4Title => 'Weak Assertions';

  @override
  String get logicMatrixQ4Desc =>
      'Low cognitive level and weak warrants. Not actionable.';

  @override
  String get helpLogicMatrix =>
      'The Logic Matrix visualizes the relationship between argumentation quality and cognitive depth. NEW: Bubble size represents Strategic Depth (Agency). Large bubble implies visionary approach.';

  @override
  String get helpStrategicDepth =>
      'Drawing on Systems Thinking and Foresight methodologies, Strategic Depth measures the temporal and systemic scope of the response. It contrasts \'Tactical\' (immediate, reactive) thinking with \'Visionary\' (long-term, systemic) thinking, evaluating the agent\'s ability to model second- and third-order consequences.';

  @override
  String get helpAuthenticity =>
      'Authenticity measures the naturalness of the response on a scale of 1-3. 3 = Organic, 2 = Mixed, 1 = Performative.';

  @override
  String get helpWordCount => 'Total word count of the response.';

  @override
  String get secThreatDetected => 'THREAT DETECTED';

  @override
  String get secThreatNone => 'No Threats';

  @override
  String get secAnonymized => 'ANONYMIZED';

  @override
  String get secNotAnonymized => 'NOT ANONYMIZED';

  @override
  String get riskHigh => 'HIGH RISK';

  @override
  String get riskMedium => 'Medium Risk';

  @override
  String get riskLow => 'Low Risk';

  @override
  String get riskUnknown => 'Unknown Risk';

  @override
  String get lblDriver => 'Driver';

  @override
  String get lblPassenger => 'Passenger';

  @override
  String get lblRiskLevel => 'Risk Level';

  @override
  String get lblEmotionalTone => 'Emotional Tone';

  @override
  String get lblNoFindings => 'No significant findings.';

  @override
  String get knowledgeBaseIngestionTitle => 'Knowledge Base Ingestion';

  @override
  String get uploadDocxMd => 'Upload DOCX / MD';

  @override
  String get ingestionComplete => 'Ingestion Complete!';

  @override
  String referencesCount(int count) {
    return 'References: $count';
  }

  @override
  String claimsCount(int count) {
    return 'Claims: $count';
  }

  @override
  String get studioDashboardKnowledgeTitle => 'Ingestion';

  @override
  String get studioDashboardKnowledgeDesc =>
      'Upload documents to Knowledge Base.';

  @override
  String get addStrategyTooltip => 'Add Strategy';

  @override
  String get resetKnowledgeBaseTitle => 'Reset Knowledge Base?';

  @override
  String get resetKnowledgeBaseConfirmation =>
      'This will adhere to the \"Clean Slate\" protocol and permanently delete all ingested documents. Continue?';

  @override
  String get resetButton => 'Reset';

  @override
  String get analysisLevelLabel => 'Analysis Level (Model Strategy)';

  @override
  String get analysisLevelHelper =>
      'Select \"Deep\" for complex reasoning or \"Fast\" for speed.';

  @override
  String get analysisLevelNone => 'None (Parsing Only)';

  @override
  String strategiesLoadError(Object error) {
    return 'Failed to load strategies: $error';
  }

  @override
  String get processingStatus => 'Processing...';

  @override
  String get errorKnowledgeIngestionFailed =>
      'Knowledge ingestion failed. Check file and try again.';

  @override
  String get errorKnowledgeResetFailed =>
      'Knowledge base reset failed. Contact support.';

  @override
  String get errorKnowledgeRetrievalFailed =>
      'Knowledge retrieval failed. Server unresponsive.';

  @override
  String get errValidationFailed => 'Validation Failed';

  @override
  String get errInternalServerError => 'Internal Server Error';

  @override
  String get errResourceNotFound => 'Resource Not Found';

  @override
  String get errDataCorruptionDesc =>
      'Data integrity error: The heavy data file associated with this record could not be found on the physical disk. A report cannot be generated.';

  @override
  String get actionHintRunAgain =>
      'Hint: You must execute this analysis again to generate new data.';

  @override
  String get errAuthenticationFailed => 'Authentication Failed';

  @override
  String get errPermissionDenied => 'Permission Denied';

  @override
  String get errServiceUnavailable => 'Service Unavailable';

  @override
  String get errAgentExecutionCritical => 'Agent Execution Critical';

  @override
  String get errWorkflowExecutionFailed => 'Workflow Execution Failed';

  @override
  String get errKnowledgeNotIngestedTitle => 'Knowledge Base Empty';

  @override
  String get errKnowledgeNotIngested =>
      'Knowledge Base is empty. Please upload documents in the Ingestion view before running analysis.';

  @override
  String get actionGoToIngestion => 'Go to Ingestion';

  @override
  String get knowledgeActive => 'Knowledge Base Active';

  @override
  String knowledgeStats(int docCount, int precCount) {
    return 'Documents: $docCount | Precedents: $precCount';
  }

  @override
  String get addReflectionIntent => 'Add reflection (Intent)';

  @override
  String get reflectionDescription =>
      'Describe your own reasoning and how you guided the AI during the process. This is the most critical phase for evaluation.';

  @override
  String get guidedReflectionRecommended => 'Guided reflection (Recommended)';

  @override
  String get q1GoalTitle => 'Goal and strategic planning (Architect)';

  @override
  String get q1GoalHint =>
      'What was your original goal and how did you break down the task?';

  @override
  String get q2FalsificationTitle =>
      'AI steering and critical iteration (Falsifier)';

  @override
  String get q2FalsificationHint =>
      'What shortcomings or errors did you notice in the AI\'s response and how did you correct them?';

  @override
  String get q3SynthesisTitle => 'Own contribution and creativity (Architect)';

  @override
  String get q3SynthesisHint =>
      'What is genuinely your own human contribution in the final product?';

  @override
  String get q4ArgumentationTitle =>
      'Quality assurance and metacognition (Judge)';

  @override
  String get q4ArgumentationHint =>
      'On what grounds do you trust the outcome? What would you do differently?';

  @override
  String get minCharsRequired => 'Text must be at least 100 characters long.';

  @override
  String charsRemainingLength(int len) {
    return 'Answer must be at least 100 characters ($len/100).';
  }

  @override
  String expandArgumentationHint(int len) {
    return 'It is recommended to expand your reasoning ($len/100 chars)';
  }

  @override
  String get dataUnavailable => 'Data unavailable';

  @override
  String get noDetailedData => 'No detailed observation data available.';

  @override
  String get detailedBreakdown => 'Detailed Breakdown';

  @override
  String scaleInfo(int min, int max) {
    return '(Scale: $min-$max)';
  }

  @override
  String get lblClaim => 'Claim';

  @override
  String get lblData => 'Data';

  @override
  String get lblWarrant => 'Warrant';

  @override
  String get lblBacking => 'Backing';

  @override
  String get lblRebuttal => 'Rebuttal';

  @override
  String get lblQualifier => 'Qualifier';

  @override
  String get lblFindings => 'Findings';

  @override
  String get lblNoSignificantFindings => 'No significant findings.';

  @override
  String get lblImperativeCommands => 'Imperative Commands';

  @override
  String get helpImperativeCommands =>
      'A metric that measures how many direct commands or demands (imperatives) the user made in their text. This indicates initiative and the need for control in the interaction.';

  @override
  String get lblPostHocRationalization => 'Post-Hoc Rationalization';

  @override
  String get lblReasoning => 'Reasoning';

  @override
  String get lblAvgSentenceLength => 'Average Sentence Length';

  @override
  String get lblPsychologicalProfile => 'Psychological Profile';

  @override
  String get lblAuthorIntent => 'Author Intent';

  @override
  String get lblNoAnalysis => 'No analysis.';

  @override
  String errNetworkOrTimeout(String reason) {
    return 'Network error or timeout. Please try again. Reason: $reason';
  }

  @override
  String errSystemError(String error) {
    return 'System error: $error';
  }

  @override
  String get errInvalidWorkflow =>
      'Error: Invalid Workflow Selection. Please refresh.';

  @override
  String get systemConfigsTitle => 'System Configs';

  @override
  String get modelRegistryDesc =>
      'Configure globally available models, LLM parameters and API overrides.';

  @override
  String get systemMetaTitle => 'System Meta';

  @override
  String get configIdLabel => 'Config ID';

  @override
  String get configTypeLabel => 'Config Type';

  @override
  String get maxTokensLabel => 'Max Tokens';

  @override
  String get topPLabel => 'Top-P (Nucleus Sampling)';

  @override
  String get tpmLimitLabel => 'TPM Limit (Tokens/Min)';

  @override
  String get rpmLimitLabel => 'RPM Limit (Requests/Min)';

  @override
  String get parsingModeLabel => 'Parsing Mode';

  @override
  String get isActiveLabel => 'Is Active';

  @override
  String get supportsGroundingLabel => 'Supports Grounding';

  @override
  String get strategyLabel => 'Strategy';

  @override
  String get noModelsDefined => 'No models defined in registry.';

  @override
  String get workflowEditTitle => 'Edit DAG Workflow';

  @override
  String get workflowConfigTitle => 'Workflow Configuration';

  @override
  String get workflowIdLabel => 'Workflow ID (e.g. analysis_pipeline)';

  @override
  String get workflowSlugLabel =>
      'Workflow Identifier (URL slug, lowercase and underscores only, e.g., holistic_audit)';

  @override
  String get workflowNameLabel => 'Workflow Name';

  @override
  String get workflowInputsTitle => 'Expected Inputs (Global Roles)';

  @override
  String get workflowAddInputBtn => 'Add Input';

  @override
  String get workflowStepsTitle => 'Execution Steps (DAG Graph)';

  @override
  String get workflowAddStepBtn => 'Add Step';

  @override
  String get workflowRoleKeyLabel =>
      'Role Key (e.g. source_text, represents a global role)';

  @override
  String get workflowDescLabel => 'Description';

  @override
  String get workflowTypeString => 'String (Text)';

  @override
  String get workflowTypeFile => 'File (PDF/Word)';

  @override
  String get workflowTypeJson => 'JSON Struct';

  @override
  String get workflowStepIdLabel => 'Step ID (e.g. initial_eval)';

  @override
  String get workflowAgentTypeLabel => 'Role (Cognitive Strategy)';

  @override
  String get workflowDependsOnLabel => 'Depends On (DAG Edges):';

  @override
  String get workflowNoPrevSteps => 'No previous steps available.';

  @override
  String get workflowInputMappingsLabel => 'Input Mappings (Semantic Routing):';

  @override
  String get workflowAgentInputKey => 'Agent Input Key (e.g. inputs)';

  @override
  String get workflowSourceVarLabel => 'Data Source (e.g. \$inputs)';

  @override
  String get workflowMappingHelperTitle => 'How does Semantic Routing work?';

  @override
  String get workflowMappingHelperDesc =>
      '1. Left side (Agent Input Key) is the XML tag name the AI will use to read the data. In V2 Architecture, it is almost always just the word \'inputs\' (lower_snake_case).\n2. Right side is the data source. \'\$inputs\' captures all values provided by the user in the form. \'\$steps.step_x.outputs\' directly connects the previous agent\'s output as an input here.\nTo pass a hardcoded rule (e.g. the word \'doctor\'), simply type it on the right side without a dollar sign.';

  @override
  String get workflowAddMappingBtn => 'Add Mapping';

  @override
  String get workflowInputKeyLabel =>
      'Input Key/Role (e.g. product_text, the role this input binds to in the workflow)';

  @override
  String get workflowDeleteInputTooltip => 'Delete Input';

  @override
  String get workflowInputRequired => 'Required';

  @override
  String get workflowInputIsChatHistory => 'Is Chat History (LLM Parse)';

  @override
  String get workflowInputModesLabel => 'Input Modes:';

  @override
  String get inputModeFile => 'file';

  @override
  String get inputModePaste => 'paste';

  @override
  String get inputModeQuestionnaire => 'questionnaire';

  @override
  String get workflowInputLabelTitle =>
      'Label (UI Form Title, e.g. \'Final Product\')';

  @override
  String get workflowInputDescriptionTitle =>
      'Description (UI Hint, e.g. \'Paste the final product in PDF format\')';

  @override
  String get workflowInputAiDescriptionTitle =>
      'AI Semantic Description (For LLM Grounding)';

  @override
  String get workflowInputQuestionnaireDefTitle => 'Questionnaire Definition:';

  @override
  String get workflowInputNoQuestionsDefined =>
      'No questions defined yet. Add one below.';

  @override
  String get workflowInputQuestionIdLabel => 'Question ID (e.g. q1)';

  @override
  String get workflowInputQuestionTextLabel => 'Question Text';

  @override
  String get workflowInputAddQuestionBtn => 'Add Question';

  @override
  String get mockLoginSuccess => 'Mock Login Successful! Redirecting...';

  @override
  String mockLoginFailed(String error) {
    return 'Mock login failed. Verify user data: $error';
  }

  @override
  String get actionHintCheckInput =>
      'Hint: Please check your input and try again.';

  @override
  String get actionHintLoginAgain =>
      'Hint: Session expired. Please log in again.';

  @override
  String get actionHintTryAgainLater =>
      'Hint: Server error. Please wait a moment and try again.';

  @override
  String get actionHintContactSupport =>
      'Hint: If the issue persists, contact support.';

  @override
  String get actionHintRunIngestion =>
      'Hint: Please upload documents to the Knowledge Base first.';

  @override
  String get actionHintCheckUrl =>
      'Hint: Please verify the spelling of the URL.';

  @override
  String get actionHintCheckConnection =>
      'Hint: Please check your network connection.';

  @override
  String get confirmDeletionTitle => 'Confirm Deletion';

  @override
  String get confirmDeletionMessage =>
      'Are you sure you want to delete this execution? This action cannot be undone.';

  @override
  String get executionsDashboardTitle => 'Executions Dashboard';

  @override
  String get newAnalysisPipelineTitle => 'New Analysis Pipeline (SDUI)';

  @override
  String get liveExecutionTitle => 'Live Execution';

  @override
  String get establishingConnection => 'Establishing connection...';

  @override
  String statusLabel(String status) {
    return 'Status: $status';
  }

  @override
  String auditDriftWarning(String versionId) {
    return 'Audit Drift Warning: This execution was completed with system parameters ($versionId) that differ from the current active ruleset (v2.0.0). Results should be interpreted with caution.';
  }

  @override
  String get noUiHintsAvailable =>
      'No UI hints available yet. Waiting for stream...';

  @override
  String get executionStartedSuccessfully => 'Execution started successfully!';

  @override
  String failedToStartExecution(String error) {
    return 'Failed to start execution: $error';
  }

  @override
  String get executionDeletedSuccessfully => 'Execution deleted successfully.';

  @override
  String failedToDeleteExecution(String error) {
    return 'Failed to delete execution: $error';
  }

  @override
  String get reportTitleMain => 'Execution Report';

  @override
  String get reportMetrics => 'Performance Metrics';

  @override
  String get reportScore => 'Total Score';

  @override
  String get xAxisLabel => 'X-Axis (Matrix ID)';

  @override
  String get yAxisLabel => 'Y-Axis (Matrix ID)';

  @override
  String get zAxisLabel => 'Z-Axis (Matrix ID)';

  @override
  String get selectWorkflowPrompt =>
      'Select a workflow from the list to begin.';

  @override
  String noInputsRequired(String id) {
    return 'No inputs strictly required for \n$id';
  }

  @override
  String configureInputsFor(String id) {
    return 'Configure Inputs for $id';
  }

  @override
  String inputLabel(String key) {
    return 'Input: $key';
  }

  @override
  String selectedFile(String fileName) {
    return 'Selected: $fileName';
  }

  @override
  String get noFileSelected => 'No file selected';

  @override
  String get browseFile => 'Browse';

  @override
  String inputTypeHint(String typeHint) {
    return 'Type: $typeHint';
  }

  @override
  String questionnaireTitle(String title) {
    return 'Questionnaire: $title';
  }

  @override
  String get startAiExecution => 'Start AI Execution';

  @override
  String get strictnessLevelTitle => 'Strictness Level';

  @override
  String get strictnessGricean => 'Level 1: Cooperative (Gricean)';

  @override
  String get strictnessLiteral => 'Level 2: Literal (Lexical)';

  @override
  String get strictnessCausal => 'Level 3: Causal (Default)';

  @override
  String get strictnessFalsification => 'Level 4: Adversarial (Falsification)';

  @override
  String get strictnessZeroTrust => 'Level 5: Zero-Trust';

  @override
  String get strictnessWarningLvl4 =>
      'Warning: Level 4 is adversarial and searches for flaws. Expect significantly lower scores.';

  @override
  String get strictnessWarningLvl5 =>
      'Warning: Zero-Trust. Zero points unless external frameworks and hard evidence are used flawlessly.';

  @override
  String get barsCompliance1 =>
      'Critically Misaligned - Completely random process';

  @override
  String get barsCompliance2 => 'Misaligned - Scattered process adherence';

  @override
  String get barsCompliance3 => 'Neutral - Some process visible';

  @override
  String get barsCompliance4 => 'Aligned - Adheres to industry standards';

  @override
  String get barsCompliance5 =>
      'Strongly Aligned - Perfect State-of-the-Art practice';

  @override
  String get barsRole1 => 'Passenger - Passive requester';

  @override
  String get barsRole2 => 'Navigator - Navigates existing data';

  @override
  String get barsRole3 => 'Driver - Active director';

  @override
  String get barsRole4 => 'Architect - Strategic planner';

  @override
  String get barsStrategy1 => 'Zero-shot';

  @override
  String get barsStrategy2 => 'Few-shot';

  @override
  String get barsStrategy3 => 'Chain-of-Thought';

  @override
  String get barsSim1 => 'Impossible (True dependence)';

  @override
  String get barsSim2 => 'Possible (Dependent)';

  @override
  String get barsSim3 => 'Probable (Independent)';

  @override
  String get barsConf0 => 'Completely uncertain (0%)';

  @override
  String get barsConf25 => 'Uncertain (25%)';

  @override
  String get barsConf50 => 'Neutral (50%)';

  @override
  String get barsConf75 => 'Fairly certain (75%)';

  @override
  String get barsConf100 => 'Absolutely certain (100%)';

  @override
  String get barsRisk1 => 'Low risk (Safe)';

  @override
  String get barsRisk2 => 'Medium risk (Warning)';

  @override
  String get barsRisk3 => 'High risk (Lazy prompt)';

  @override
  String get rawOutputFallbackTitle => 'Raw Output (UI Missing)';

  @override
  String get adminAiDescriptionHint =>
      'MANDATORY: Must be written in English. Cognitive prompt, not user data.';

  @override
  String get adminBilingualPromptHint =>
      'MANDATORY: English translation required. Use EXTREME PRECISION. This text directly dictates the AI\'s cognitive reasoning and structural rules.';

  @override
  String get adminPromptBestPracticesHint =>
      'BEST PRACTICE: Use command keywords like ROLE:, TASK:, RULE: and CONTEXT:. NEVER translate these keywords into Finnish inside the text.';

  @override
  String get blueprintEditorTitle => 'Blueprint Editor';

  @override
  String get blueprintComponentsTitle => 'Components';

  @override
  String get blueprintAddComponentBtn => 'Add Component';

  @override
  String get blueprintEmptyStateMsg =>
      'No components added yet. Add a component to start building the report.';

  @override
  String get blueprintComponentHeader => 'Header';

  @override
  String get blueprintComponentMetadataHeader => 'Metadata Header';

  @override
  String get blueprintComponentBibliography => 'Bibliography';

  @override
  String get blueprintComponent1dGauge => '1D Gauge';

  @override
  String get blueprintComponent2dMatrix => '2D Matrix';

  @override
  String get blueprintComponent3dScatter => '3D Scatter';

  @override
  String get blueprintComponentEvaluationNotes => 'Evaluation Notes';

  @override
  String get blueprintSettingsTitle => 'Component Settings';

  @override
  String get blueprintSettingsSave => 'Save Component';

  @override
  String get blueprintSaveBlueprint => 'Save Blueprint';

  @override
  String get blueprintSaveSuccess => 'Blueprint saved successfully';

  @override
  String blueprintSaveFailed(String error) {
    return 'Failed to save blueprint: $error';
  }

  @override
  String get blueprintPropertyDataPath => 'Data Path (\$results.X)';

  @override
  String get blueprintPropertyXAxis => 'X Axis Path';

  @override
  String get blueprintPropertyYAxis => 'Y Axis Path';

  @override
  String get blueprintPropertyZAxis => 'Z Axis Path';

  @override
  String get blueprintPropertyXAxisNote => 'X Axis Note Path';

  @override
  String get blueprintPropertyYAxisNote => 'Y Axis Note Path';

  @override
  String get blueprintPropertyTitle => 'Title (i18n Key or Text)';

  @override
  String get blueprintPropertyDataPathsInfo => 'Comma-separated paths';

  @override
  String get downloadSuccess => 'PDF Downloaded Successfully';

  @override
  String get i18nAddLanguageVersion => 'Add Language Version';

  @override
  String get i18nLanguageCodePlaceholder => 'Language Code (e.g., en, sv)';

  @override
  String get i18nLanguageCodeHelp =>
      'An inline editor box will be added for this language.';

  @override
  String get i18nCancel => 'Cancel';

  @override
  String get i18nCreate => 'Create';

  @override
  String get i18nAddTranslation => 'Add Translation';

  @override
  String i18nDefaultFormLabel(String locale) {
    return 'Default Form ($locale usually expected)';
  }

  @override
  String get i18nOtherTranslations => 'Other Translations:';

  @override
  String get i18nDeleteTranslation => 'Delete translation';

  @override
  String i18nTranslateToPlaceholder(String locale) {
    return 'Translate to $locale...';
  }

  @override
  String get workflowCloneBtn => 'Clone Workflow';

  @override
  String get workflowCloneSuccess => 'Workflow Cloned successfully';

  @override
  String get workflowCloneErrorMissingDep =>
      'Clone failed: Step dependency points to a non-existent step.';

  @override
  String get workflowSharedBlueprintWarning =>
      'Cloning a workflow will create a deep copy of the workflow configuration, but it will STILL reference the same Steps (DAG Nodes) by ID. If you edit a Step, it will be edited for both workflows. Are you sure you want to clone?';

  @override
  String get overall_system_profile => 'Overall System Profile';

  @override
  String get blueprintSelectWorkflow => 'Select Workflow';

  @override
  String get blueprintVariantName => 'Variant Name';

  @override
  String get blueprintDefaultVariant => 'default';

  @override
  String get blueprintCopyVariant => 'Copy Blueprint';

  @override
  String get blueprintGridRowLabel => 'Grid Row';

  @override
  String get blueprintGridRowDesc => 'Number of columns';

  @override
  String blueprintChildComponents(int count) {
    return 'Parallel child components ($count):';
  }

  @override
  String get blueprintAddChildBtn => 'Add child component';

  @override
  String get blueprintClearFormCache => 'Clear Form Cache';

  @override
  String get blueprintTabTitle => 'Blueprints';

  @override
  String get blueprintTabDesc => 'Manage SDUI report layouts and printouts.';

  @override
  String get blueprintCreateNew => 'Create New Blueprint';

  @override
  String blueprintVariantSelector(String variant) {
    return 'Variant: $variant';
  }

  @override
  String get reportEmptyProfile => 'Empty profile (No layout blocks defined)';

  @override
  String get reportUnknownOrg => 'Unknown organization';

  @override
  String reportTopicProfile(String name) {
    return 'Topic & Profile: $name';
  }

  @override
  String reportContext(String orgName) {
    return 'Context: $orgName';
  }

  @override
  String reportTimestamp(String timestamp) {
    return 'Timestamp: $timestamp';
  }

  @override
  String get reportCosts => 'Costs';

  @override
  String reportApiPrice(String price) {
    return 'API Price: $price';
  }

  @override
  String get reportCognitiveWork => 'Cognitive Work (Tokens)';

  @override
  String get reportTextSynthesis => 'Text / Synthesis';

  @override
  String reportQuoteTitle(String quote) {
    return '💬 Excerpt from original text:\n$quote';
  }

  @override
  String reportFrameworkReference(String source) {
    return '⚖️ Reference framework: $source';
  }

  @override
  String reportGoogleVerified(String citation) {
    return 'Verified from Google sources:\n$citation';
  }

  @override
  String get reportInteractionMatrix2D => 'Interaction Matrix (2D)';

  @override
  String get reportRadarAnalysis2D => 'Radar Analysis (2D)';

  @override
  String get reportComparisonView => 'Comparison View';

  @override
  String get reportAnalyticalFramework3D => 'Analytical Framework (3D)';

  @override
  String get reportAnalyticalFramework2D => 'Analytical Framework (2D)';

  @override
  String get reportCoachingTitle => '💡 Coaching Tip';

  @override
  String get reportFalsificationTitle => '⚖️ Devil\'s Advocate';

  @override
  String get reportMissingContextTitle => '🔍 Missing Context';

  @override
  String get reportRiskFlagTitle => '⚠️ High Risk Identified';

  @override
  String get reportRemediationStepsTitle => '🛠️ Remediation Steps';

  @override
  String get reportEmotionalSentimentTitle => '🎭 Sentiment Analysis';

  @override
  String get reportTheoryLinkTitle => '📚 Theoretical Connection';

  @override
  String reportConfidenceTitle(String value) {
    return 'AI Confidence: $value%';
  }

  @override
  String get resumeActionableHint => 'Resume Execution (Try Again)';

  @override
  String get failedToResume => 'Failed to resume execution.';

  @override
  String get toolExecutionFailed => 'Tool execution failed';

  @override
  String get actionHintToolFailed =>
      'Check the tool connection, verify the prompt context, or try again later.';

  @override
  String get xaiEvidenceTitle => 'AI Expert Sources (Fact-Check)';

  @override
  String get xaiEvidenceQuery => 'Search query';

  @override
  String get xaiEvidenceSources => 'Sources';

  @override
  String get xaiEvidenceDuration => 'Duration';

  @override
  String get stepBuilderMCPToolsTitle => 'Allowed MCP Tools';

  @override
  String get stepBuilderAddTool => 'Add Tool';

  @override
  String get stepBuilderToolHint => 'Tool slug (e.g. mcp_tavily_search)';

  @override
  String get studioDashboardGatewaysTitle => 'MCP Gateways';

  @override
  String get studioDashboardGatewaysDesc =>
      'Manage external tools and AI fact-checking integrations.';

  @override
  String get mcpGatewaysTitle =>
      'XAI Reporting / Toolkit Injection (MCP Gateways)';

  @override
  String get mcpGatewaysDesc =>
      'Configure system-level MCP tool gateways for AI execution.';

  @override
  String get mcpToolSettings => 'MCP Tool Settings';

  @override
  String get mcpToolIdLabel => 'Tool ID';

  @override
  String get mcpToolNameLabel => 'Tool Name';

  @override
  String get mcpToolDescLabel => 'Description';

  @override
  String get mcpToolInputSchemaLabel => 'Input Schema (JSON)';

  @override
  String get mcpAddToolBtn => 'Add Tool';

  @override
  String get mcpEditToolBtn => 'Edit Tool';

  @override
  String get noMcpGatewaysDefined => 'No MCP gateways defined.';

  @override
  String get tooltipDuplicate => 'Duplicate (Shallow-Deep Copy)';

  @override
  String get msgEntityClonedSuccess => 'Entity cloned securely.';

  @override
  String msgEntityCloneFailed(String error) {
    return 'Failed to clone: $error';
  }

  @override
  String get categoryMatrix => 'Evaluation Matrix';

  @override
  String get categoryAgentRole => 'Agent Role Persona';

  @override
  String get categoryTaskDefinition => 'Task Definition';

  @override
  String get categorySystemRule => 'System Rule / Heuristic';

  @override
  String get categoryProtocol => 'Execution Protocol';

  @override
  String get technicalDetails => 'Technical Details';

  @override
  String get systemError => 'System Error';

  @override
  String get signInSubtitle => 'Sign in to continue';

  @override
  String get errorEmptyEmail => 'Please enter your email';

  @override
  String get errorInvalidEmail => 'Invalid email address';

  @override
  String get errorEmptyPassword => 'Please enter your password';

  @override
  String get signInButton => 'Sign In';

  @override
  String executionTargetLabel(String id) {
    return 'Target: $id';
  }

  @override
  String get executionMetricsTitle => 'Performance Metrics';

  @override
  String executionTokensBreakdown(int total, int prompt, int comp) {
    return 'Total Tokens: $total (Prompt: $prompt, Completion: $comp)';
  }

  @override
  String executionTokensCached(int cached) {
    return 'Cached Tokens saved: $cached';
  }

  @override
  String executionTokensReasoning(int reasoning) {
    return 'Reasoning Tokens spent: $reasoning';
  }

  @override
  String executionCostEstimate(String cost) {
    return 'Estimated Cost: \$$cost';
  }

  @override
  String workflowPrefixLabel(String name) {
    return 'Workflow: $name';
  }

  @override
  String get deleteExecutionTooltip => 'Delete Execution';

  @override
  String get errSaveTimeout => 'File save dialog did not respond (Timeout).';

  @override
  String startWorkflowTitle(String id) {
    return 'Start Workflow: $id';
  }

  @override
  String failedToLoadSchema(String error) {
    return 'Failed to load schema: $error';
  }

  @override
  String get navSystemInspector => 'System Inspector';

  @override
  String get gatewayMetadataTitle => 'Gateway Metadata';

  @override
  String get slugLabel => 'Slug (e.g., task_guard)';

  @override
  String get allowedMcpToolsTitle => 'Allowed MCP Tools';

  @override
  String get addToolButton => 'Add Tool';

  @override
  String get noToolsDefinedGateway => 'No tools defined for this gateway.';

  @override
  String get deleteGatewayTitle => 'Delete MCP Gateway?';

  @override
  String deleteGatewayConfirmation(String id) {
    return 'Are you sure you want to delete gateway $id?';
  }

  @override
  String get cancelButton => 'Cancel';

  @override
  String get deleteButton => 'Delete';

  @override
  String get gatewaySavedSuccess => 'MCP Gateway saved successfully.';

  @override
  String saveFailedError(String error) {
    return 'Save failed: $error';
  }

  @override
  String deleteFailedError(String error) {
    return 'Delete failed: $error';
  }

  @override
  String toolTitlePrefix(String name) {
    return 'Tool: $name';
  }

  @override
  String get toolIdLabel => 'Tool ID (Slug)';

  @override
  String get uiDisplayNameTitle => 'UI Display Name (I18nText)';

  @override
  String get englishNameLabel => 'English Name';

  @override
  String get finnishNameLabel => 'Finnish Name';

  @override
  String get toolDescriptionLabel => 'Tool Description (English only for LLM)';

  @override
  String get jsonInputSchemaLabel => 'JSON Input Schema';

  @override
  String get invalidJsonError => 'Invalid JSON';

  @override
  String get deleteConfigTitle => 'Delete Configuration?';

  @override
  String deleteConfigConfirmation(String id) {
    return 'Are you sure you want to delete config $id?';
  }

  @override
  String get configSavedSuccess => 'Model Registry saved successfully.';

  @override
  String get profileSavedSuccess => 'Profile saved successfully.';

  @override
  String get deleteProfileTitle => 'Delete Profile?';

  @override
  String deleteProfileConfirmation(String id) {
    return 'Are you sure you want to delete $id?';
  }

  @override
  String get newOutputProfileTitle => 'New Output Profile';

  @override
  String get editOutputProfileTitle => 'Edit Output Profile';

  @override
  String get profileIdLabel => 'Profile ID (e.g. general_executive)';

  @override
  String get urlSlugLabel => 'URL Slug (e.g. default)';

  @override
  String get workflowIdBindingLabel => 'Workflow ID Binding';

  @override
  String get selectWorkflowHint => 'Select a Workflow...';

  @override
  String get noneDefaultLabel => 'None (Default)';

  @override
  String get profileDisplayNameLabel => 'Profile Display Name';

  @override
  String get profileDescriptionLabel => 'Profile Description (Optional)';

  @override
  String get workflowSelectWarning =>
      '⚠️ Please select a Workflow ID Binding above to configure report layouts.';

  @override
  String get layoutBlocksTitle => 'Layout Blocks';

  @override
  String get addLayoutBlockBtn => 'Add Layout Block';

  @override
  String get noLayoutBlocksDefined =>
      'No layout blocks defined. Report will be empty.';

  @override
  String get presetViewLabel => 'Preset View';

  @override
  String get preset1dTable => '1D Table';

  @override
  String get preset2dGrid => '2D Grid';

  @override
  String get preset3dRadar => '3D Radar/Composite';

  @override
  String get presetTextOnly => 'Text/Synthesis Only';

  @override
  String get presetAutomatic => 'Automatic Validation';

  @override
  String get showTextLabel => 'Show Text';

  @override
  String get layoutBlockTitleLabel => 'Layout Block Title';

  @override
  String get targetComponentsTitle => 'Target Components';

  @override
  String get componentXAxisLabel => 'Component 1 (X-Axis/Primary)';

  @override
  String get componentYAxisLabel => 'Component 2 (Y-Axis)';

  @override
  String get componentZAxisLabel => 'Component 3 (Z-Axis)';

  @override
  String componentGenericLabel(String num) {
    return 'Component $num';
  }

  @override
  String get selectAllComponentsLabel => 'All Components (*)';

  @override
  String get selectComponentHint => 'Select component...';

  @override
  String editProfilesTitle(String slug) {
    return 'Edit Profiles: $slug';
  }

  @override
  String get outputProfilesDictionary => 'Output Profiles Dictionary';

  @override
  String get addVariantBtn => 'Add Variant';

  @override
  String get newProfileIdTitle => 'New Profile ID';

  @override
  String get profileIdHint => 'Profile ID (e.g. executive)';

  @override
  String variantIdLabel(String id) {
    return 'Variant ID: $id';
  }

  @override
  String get reportLayoutSequenceLabel => 'Report Layout Sequence';

  @override
  String get preset2dCompare => '2D Compare';

  @override
  String get preset3dComplex => '3D Complex';

  @override
  String get presetDefaultView => 'Default View';

  @override
  String get sectionTitleLabel => 'Section Title (Optional)';

  @override
  String get sectionDescLabel => 'Section Description (Optional)';

  @override
  String get promptBlockSavedSuccess => 'Prompt Block saved (Optimistic).';

  @override
  String get simulatorCorruptionError =>
      'Simulator did not return rendered_prompt. Data corruption detected.';

  @override
  String get simulatorOutputTitle => 'Simulator Output';

  @override
  String simulatorFailedError(String error) {
    return 'Simulation Error: $error';
  }

  @override
  String get promptBlockEditTitle => 'Edit Prompt Block';

  @override
  String promptBlockBuilderTitleId(String id) {
    return 'Builder: $id';
  }

  @override
  String get promptBlockMandatoryEnglishError =>
      'English Label is required (English-Only Mandate).';

  @override
  String get promptBlockConfigTitle => 'Prompt Block Configuration';

  @override
  String opaqueIdLabel(String id) {
    return 'Opaque ID: $id';
  }

  @override
  String get promptBlockPropertiesTitle => 'Prompt Block Properties';

  @override
  String get categoryLabel => 'Category';

  @override
  String get blockLabelName => 'Block Label (Name)';

  @override
  String get shortDescriptionHint => 'Short Description (UI Hint)';

  @override
  String get systemPromptMandatory =>
      'System Prompt / Cognitive Blueprint (MANDATORY ENGLISH)';

  @override
  String get dataTypeExecutionConstraints =>
      'Data Type & Execution Constraints';

  @override
  String get typeInstruction => 'Text Instruction (No JSON Output)';

  @override
  String get typeNumber => 'Number (Numeric)';

  @override
  String get typeInteger => 'Integer';

  @override
  String get allowDecimals => 'Allow Decimals';

  @override
  String get isEvaluativeMatrix => 'Evaluative (Calculated)';

  @override
  String get xaiOutputExtensionsTitle =>
      'XAI Output Extensions (Proaktiivinen Valmentaja & Report Fields)';

  @override
  String get xaiJustification => 'Justification';

  @override
  String get xaiCoachingTip => 'Coaching Tip';

  @override
  String get xaiDevilsAdvocate => 'Devil\'s Advocate';

  @override
  String get xaiMissingContext => 'Missing Context';

  @override
  String get xaiRiskFlag => 'Risk Flag';

  @override
  String get xaiRemediation => 'Remediation';

  @override
  String get xaiSentiment => 'Sentiment';

  @override
  String get xaiTheoryLink => 'Theory Link';

  @override
  String get xaiConfidence => 'AI Confidence';

  @override
  String get xaiSourceCitation => 'Source Citation';

  @override
  String get theoryGroundingTitle => 'Theory Grounding (RAG)';

  @override
  String get sourceUrlLabel => 'Source URL (e.g. jstor.org/...)';

  @override
  String get citationReferenceLabel =>
      'Citation Reference (e.g. Kahnamen, 2011)';

  @override
  String get gridRowsOptional => 'Grid Rows (Optional)';

  @override
  String get gridColumnsOptional => 'Grid Columns (Optional)';

  @override
  String get addGridItemBtn => 'Add item';

  @override
  String get barsScalesTitle => 'BARS Scales / Score Grades';

  @override
  String get addGradeBtn => 'Add Grade';

  @override
  String get scaleMinLabel => 'Scale Min (e.g. 4)';

  @override
  String get scaleMaxLabel => 'Scale Max (e.g. 10)';

  @override
  String claimsCountLabel(String count) {
    return '$count Claims';
  }

  @override
  String gradeScoreLabel(String score, String name) {
    return 'Grade/Score: $score $name';
  }

  @override
  String get closeModalBtn => 'Close';

  @override
  String get studioSaveSuccess => 'Saved successfully';

  @override
  String get stepSavedSuccess => 'Step saved (Optimistic).';

  @override
  String get stepEditTitle => 'Edit Step';

  @override
  String get simulateStepTooltip => 'Simulate Step';

  @override
  String get idRequiredError => 'ID is required.';

  @override
  String get configurationTitle => 'Configuration';

  @override
  String get nameLabel => 'Name';

  @override
  String get descriptionLabel => 'Description';

  @override
  String get preHooksTitle => 'Pre Hooks';

  @override
  String get addHookBtn => 'Add Hook';

  @override
  String get preHookEngineLabel => 'Pre-Execution Hook Engine';

  @override
  String get hookTavily => 'Tavily Web Search (search_hook)';

  @override
  String get hookMemory => 'Contextual Memory (memory_hook)';

  @override
  String get hookValidation => 'Strict Validation (validation_hook)';

  @override
  String get hookScore => 'Grading Matrix (score_hook)';

  @override
  String hookLegacy(String name) {
    return 'Legacy: $name';
  }

  @override
  String get promptBlocksTitle => 'Prompt Blocks';

  @override
  String get addPromptBlockBtn => 'Add Prompt Block';

  @override
  String get promptBlockLabel => 'Prompt Block';

  @override
  String get workflowSavedSuccess => 'Workflow saved successfully.';

  @override
  String get simulatorValidDag => 'DAG is Valid!';

  @override
  String simulatorDagErrors(String errors) {
    return 'DAG Errors: $errors';
  }

  @override
  String get workflowNameMissingError =>
      'Workflow name is missing for existing workflow.';

  @override
  String get validateDagBtn => 'Validate DAG';

  @override
  String get workflowTabGeneral => '1. General & Outputs';

  @override
  String get workflowTabInputs => '2. Inputs';

  @override
  String get workflowTabSteps => '3. Steps & Dependencies';

  @override
  String errNavigationFallback(String uri) {
    return 'Navigation Error: $uri not found. Returning to workspace...';
  }

  @override
  String get studioWorkflowIdOpaque => 'Opaque Workflow ID (System Generated)';

  @override
  String get studioWorkflowSlugSemantic =>
      'Semantic Routing Slug (e.g. audit-master)';

  @override
  String get studioWorkflowIdentity => 'Workflow Identity';

  @override
  String get studioWorkflowNameLabel => 'Workflow Name';

  @override
  String get studioWorkflowDescEnLabel => 'Description (EN)';

  @override
  String get studioWorkflowDescFiLabel => 'Kuvaus (FI)';

  @override
  String get studioWorkflowGlobalSettings => 'Global Execution Settings';

  @override
  String get studioWorkflowDefaultProfile => 'Default Fallback Profile';

  @override
  String get studioWorkflowInputsEmpty => 'No expected inputs defined.';

  @override
  String studioWorkflowStepCount(int count) {
    return 'Step $count';
  }

  @override
  String get studioWorkflowNodeIdOpaque => 'Node ID (Opaque Stripe Pattern)';

  @override
  String get studioWorkflowTaskBlueprint => 'Task Blueprint (Cognitive Engine)';

  @override
  String get studioWorkflowXaiReporting =>
      'XAI Reporting / Toolkit Injection (MCP Gateways):';

  @override
  String get studioWorkflowDependsOn =>
      'Depends On (Executes AFTER these steps finish):';

  @override
  String get studioWorkflowNoDependencies =>
      'No previous steps available to depend on.';

  @override
  String get studioWorkflowInputMappings =>
      'Input Mappings (State Data Injection):';

  @override
  String get studioWorkflowTargetArgName => 'Target Arg Name';

  @override
  String get studioWorkflowSourceToken =>
      'Source Token (e.g. \\\$inputs, step_1)';

  @override
  String get studioWorkflowStepsNoInputsMappingWarning =>
      'Error: Unmapped inputs found.';

  @override
  String get studioWorkflowStepsInputMappingTitle =>
      'Input Mappings (External -> Internal)';

  @override
  String get studioWorkflowStepsAddMappingBtn => 'Add Mapping';

  @override
  String get studioWorkflowStepsDataMissingText => 'Wait, missing data object?';

  @override
  String get studioWorkflowStepsNoTargetComponents => 'None selected';

  @override
  String get studioViewsBlueprintRulesTitle =>
      'Output Mapping (Presentation Rules)';

  @override
  String get studioViewsPresetViewTheme => 'Preset View Theme';

  @override
  String get studioViews1dMetricsList => '1D Metrics List';

  @override
  String get studioViews2dCompare => '2D Compare View';

  @override
  String get studioViews3dComplex => '3D Complex Matrix';

  @override
  String studioViewsFailedToClone(String error) {
    return 'Failed to clone: $error';
  }

  @override
  String get studioViewsNewMatrix => 'New Matrix';

  @override
  String studioViewsErrorLoadingWorkflows(String error) {
    return 'Error loading workflows: $error';
  }

  @override
  String get studioViewsProfileIdRequired => 'Profile ID is required';

  @override
  String studioViewsErrorLoadingBlocks(String error) {
    return 'Error loading blocks: $error';
  }

  @override
  String get studioViewsOutputProfilesMasterTitle => 'Output Profiles';

  @override
  String get studioViewsNewProfileBtn => 'New Profile';

  @override
  String get studioViewsNoOutputProfiles => 'No Output Profiles defined.';

  @override
  String get studioViewsUnnamedProfile => 'Unnamed Profile';

  @override
  String studioViewsProfileListSubtitle(
    String id,
    String workflow,
    int layouts,
  ) {
    return 'ID: $id | Workflow: $workflow | $layouts Layout Blocks';
  }

  @override
  String get studioViewsNone => 'None';

  @override
  String get studioViewsAddBtn => 'Add';

  @override
  String get studioViewsWarningNoModels => 'Warning: No models found.';

  @override
  String get studioViewsModelStrategyLabel =>
      'Model Strategy (Cost/Cognition Override)';

  @override
  String get studioViewsAdminStudioV2 => 'Admin Studio V2';

  @override
  String get studioViewsPromptBlocksTab => 'Prompt Blocks';

  @override
  String get studioViewsStepsTab => 'Steps';

  @override
  String get studioViewsProfilesTab => 'Profiles';

  @override
  String get studioViewsPromptBlocksStandard => 'Prompt Blocks (Standard)';

  @override
  String get studioViewsNoStandardPromptBlocks =>
      'No standard prompt blocks defined.';

  @override
  String studioViewsSlugSubtitle(String slug) {
    return 'Slug: $slug';
  }

  @override
  String get studioViewsNoMatricesDefined => 'No matrices defined.';

  @override
  String get studioViewsNoStepsDefined => 'No Steps defined.';

  @override
  String studioViewsStepsSubtitle(int blocks, int hooks) {
    return 'Blocks: $blocks | Hooks: $hooks';
  }

  @override
  String get studioViewsNoSystemConfigs => 'No System Configs defined.';

  @override
  String studioViewsConfiguredModels(int count) {
    return 'Configured Models: $count';
  }

  @override
  String get studioViewsNewBtn => 'New';

  @override
  String get studioViewsWorkflowBuilderTitle => 'Workflow Builder';

  @override
  String get studioViewsNewWorkflowBtn => 'New Workflow';

  @override
  String get studioViewsWorkflowBuilderDesc =>
      'Manage master execution blueprints (DAGs) defining agentic workflows, inputs, and strategies.';

  @override
  String get studioViewsNoWorkflowsConfigured => 'No workflows configured.';

  @override
  String studioViewsWorkflowSubtitle(String id, int nodes, String status) {
    return 'ID: $id | Nodes: $nodes | Status: $status';
  }

  @override
  String get studioWorkflowAddMappingBtn => 'Add Mapping';

  @override
  String get studioWorkflowStepsDependencies => 'Steps & Dependencies';

  @override
  String get studioWorkflowAddStepNodeBtn => 'Add Step Node';

  @override
  String get studioWorkflowStepsEmpty =>
      'No steps defined. Add a node to start creating the orchestration graph.';

  @override
  String get studioViewsMatricesDescription =>
      'Manage system evaluation matrices.';

  @override
  String get studioViewsNoMatricesAvailable => 'No Matrices Available.';

  @override
  String get studioViewsMatrixCloned => 'Matrix cloned successfully.';

  @override
  String get sharedNoTimelineData => 'No timeline data available.';

  @override
  String get sharedNoReportData => 'No report data available.';

  @override
  String get sharedDatagridUnsupported =>
      'DataGrid is currently unsupported in V2';

  @override
  String get sharedFlatReportNoData =>
      'No Flat Report data found for this execution.';

  @override
  String get sharedAnalysisPerformed => 'Analysis Performed: ';

  @override
  String get sharedNoComparisonData => 'No comparison data available.';

  @override
  String get sharedMoreInfoTooltip => 'More information';

  @override
  String get sharedOk => 'OK';

  @override
  String get sharedUploading => 'Uploading...';

  @override
  String get sharedSelectFile => 'Select file...';

  @override
  String get sharedSystemError => 'System Error';

  @override
  String get sharedUnknownAgent => 'Unknown Agent';

  @override
  String get sharedUnknown => 'Unknown';
}
