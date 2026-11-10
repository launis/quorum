import 'dart:async';

import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/features/execution/views/task_assignment_portal_view.dart';
import 'package:client_app/features/settings/domain/models/tenant_secret_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';

class _StubAuthController extends AuthController {
  User? _user;
  int signOutCallCount = 0;

  _StubAuthController(this._user);

  @override
  FutureOr<User?> build() => _user;

  @override
  void setOptimisticUser(User updatedUser) {
    _user = updatedUser;
    state = AsyncData(updatedUser);
  }

  @override
  Future<void> applyTokenExchangeResponse(
    TokenExchangeResponseDto exchangeDto,
  ) async {
    _user = exchangeDto.user;
    state = AsyncData(exchangeDto.user);
  }

  @override
  Future<void> signOut({bool revokeAllSessions = false}) async {
    signOutCallCount++;
    _user = null;
    state = const AsyncData(null);
  }
}

class _FakeAuthRepository extends AuthRepository {
  int authOnboardingCalls = 0;
  int prepareEnrollmentCalls = 0;
  String? lastTotpCode;

  _FakeAuthRepository() : super(null, Dio());

  @override
  Future<Either<AppException, String>> authenticateForTaskOnboarding({
    required String email,
    required String password,
    String? totpCode,
  }) async {
    authOnboardingCalls++;
    lastTotpCode = totpCode;
    if (totpCode != null && totpCode.trim().length == 6) {
      return const Right('firebase_mfa_enrolled_jwt');
    }
    return const Right('firebase_single_factor_jwt');
  }

  @override
  Future<Either<AppException, MfaPendingState>>
  prepareEnrollmentForCurrentUser({
    required String fallbackEmail,
    bool reloadUser = false,
  }) async {
    prepareEnrollmentCalls++;
    const state = MfaPendingState(
      type: MfaRequirementType.enrollment,
      email: 'bob@org.com',
      secretKey: 'PORTAL-TOTP-SECRET-KEY',
    );
    setPendingMfaState(state);
    return const Right(state);
  }
}

class _FakeExecutionClient implements ExecutionClient {
  int previewCallCount = 0;
  int activateCallCount = 0;
  int saveDraftCallCount = 0;
  int submitCallCount = 0;
  int onboardCallCount = 0;
  ExecutionAssignmentSubmitDto? lastSubmittedPayload;
  ExecutionAssignmentDraftDto? lastSavedDraftPayload;

  final String assignedEmailMasked;
  final Object? previewError;
  final DateTime? overrideHardDeadlineAt;
  final TaskAssignmentBriefDto? taskBrief;
  final bool requireMfaOnFirstOnboard;

  _FakeExecutionClient({
    this.assignedEmailMasked = 'bob@org.com',
    this.previewError,
    this.overrideHardDeadlineAt,
    this.taskBrief,
    this.requireMfaOnFirstOnboard = false,
  });

  @override
  Future<ExecutionAssignmentPreviewDto> previewAssignment(String token) async {
    previewCallCount++;
    if (previewError != null) {
      throw previewError!;
    }
    return ExecutionAssignmentPreviewDto(
      id: 'asg_01960000000070008000000000000001',
      organizationId: 'org_01960000000070008000000000000001',
      organizationName: 'Quorum Org',
      assignedEmailMasked: assignedEmailMasked,
      workflowId: 'wf_01960000000070008000000000000001',
      taskBriefId: taskBrief?.id,
      taskBrief: taskBrief,
      targetLocale: 'en',
      status: AssignmentStatus.pending,
      hardDeadlineAt:
          overrideHardDeadlineAt ??
          DateTime.now().toUtc().add(const Duration(hours: 24)),
      relativeDurationSeconds: 1800,
    );
  }

  @override
  Future<TokenExchangeResponseDto> onboardAssignee({
    required String token,
    required ExecutionAssignmentOnboardingRequestDto payload,
  }) async {
    onboardCallCount++;
    if (requireMfaOnFirstOnboard && onboardCallCount == 1) {
      throw const AppException(
        status: 403,
        title: 'MFA Required',
        detail: '2FA TOTP enrollment is required.',
        extensions: {'error_code': 'MFA_REQUIRED'},
      );
    }
    return const TokenExchangeResponseDto(
      accessToken: 'jwt_onboarded_session',
      expiresInSeconds: 900,
      user: User(
        id: 'usr_01960000000070008000000000000002',
        email: 'bob@org.com',
        role: UserRole.member,
        organizationId: 'org_01960000000070008000000000000001',
      ),
    );
  }

  @override
  Future<ExecutionAssignmentResponseDto> activateAssignment(
    String assignmentId,
  ) async {
    activateCallCount++;
    return ExecutionAssignmentResponseDto(
      id: assignmentId,
      organizationId: 'org_01960000000070008000000000000001',
      assignedEmail: 'bob@org.com',
      invitedRole: UserRole.member,
      workflowId: 'wf_01960000000070008000000000000001',
      taskBriefId: taskBrief?.id,
      taskBrief: taskBrief,
      targetLocale: 'en',
      lockedInputs: const WorkflowInputs(),
      assigneeInputKeys: const ['candidate_essay'],
      draftInputs: const WorkflowInputs(),
      status: AssignmentStatus.activated,
      emailDeliveryStatus: EmailDeliveryStatus.sent,
      resultVisibility: AssignmentResultVisibility.confirmationOnly,
      hardDeadlineAt:
          overrideHardDeadlineAt ??
          DateTime.now().toUtc().add(const Duration(hours: 24)),
      relativeDurationSeconds: 1800,
      activatedAt: DateTime.now().toUtc(),
      createdBy: 'usr_01960000000070008000000000000001',
      createdAt: DateTime.now().toUtc(),
    );
  }

  @override
  Future<ExecutionAssignmentResponseDto> saveAssignmentDraft({
    required String assignmentId,
    required ExecutionAssignmentDraftDto payload,
  }) async {
    saveDraftCallCount++;
    lastSavedDraftPayload = payload;
    return ExecutionAssignmentResponseDto(
      id: assignmentId,
      organizationId: 'org_01960000000070008000000000000001',
      assignedEmail: 'bob@org.com',
      invitedRole: UserRole.member,
      workflowId: 'wf_01960000000070008000000000000001',
      taskBriefId: taskBrief?.id,
      taskBrief: taskBrief,
      targetLocale: 'en',
      lockedInputs: const WorkflowInputs(),
      assigneeInputKeys: const ['candidate_essay'],
      draftInputs: payload.draftInputs,
      status: AssignmentStatus.activated,
      emailDeliveryStatus: EmailDeliveryStatus.sent,
      resultVisibility: AssignmentResultVisibility.confirmationOnly,
      hardDeadlineAt: DateTime.now().toUtc().add(const Duration(hours: 24)),
      relativeDurationSeconds: 1800,
      activatedAt: DateTime.now().toUtc(),
      createdBy: 'usr_01960000000070008000000000000001',
      createdAt: DateTime.now().toUtc(),
    );
  }

  @override
  Future<ExecutionRecord> submitAssignment({
    required String assignmentId,
    required ExecutionAssignmentSubmitDto payload,
  }) async {
    submitCallCount++;
    lastSubmittedPayload = payload;
    return const ExecutionRecord(
      id: 'exec_01960000000070008000000000000099',
      workflowId: 'wf_01960000000070008000000000000001',
      targetLocale: 'en',
      status: 'RUNNING',
    );
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

Widget _buildPortalTestApp({
  required _StubAuthController authController,
  required _FakeExecutionClient execClient,
  AuthRepository? authRepo,
  Future<WorkflowInputValue?> Function(String inputKey)? onPickFile,
  String token = 'tok_01960000000070008000000000000001',
}) {
  return ProviderScope(
    overrides: [
      authControllerProvider.overrideWith(() => authController),
      executionClientProvider.overrideWithValue(execClient),
      if (authRepo != null) authRepositoryProvider.overrideWithValue(authRepo),
    ],
    child: MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en'), Locale('fi')],
      home: TaskAssignmentPortalView(token: token, onPickFile: onPickFile),
    ),
  );
}

void main() {
  const aliceUser = User(
    id: 'usr_01960000000070008000000000000001',
    email: 'alice@org.com',
    role: UserRole.member,
    organizationId: 'org_01960000000070008000000000000001',
  );

  const bobUser = User(
    id: 'usr_01960000000070008000000000000002',
    email: 'bob@org.com',
    role: UserRole.member,
    organizationId: 'org_01960000000070008000000000000001',
  );

  group('TaskAssignmentPortalView Widget Tests', () {
    testWidgets('test_task_assignment_portal_view_identity_mismatch_negative', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(1440, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final authController = _StubAuthController(aliceUser);
      final execClient = _FakeExecutionClient(
        assignedEmailMasked: 'bob@org.com',
      );

      await tester.pumpWidget(
        _buildPortalTestApp(
          authController: authController,
          execClient: execClient,
        ),
      );
      await tester.pumpAndSettle();

      // Must display IDENTITY_MISMATCH banner and Sign Out & Switch Account button
      // without activating the task timer.
      expect(
        find.byKey(const Key('task_portal_identity_mismatch_banner')),
        findsOneWidget,
      );
      expect(find.textContaining('IDENTITY_MISMATCH'), findsOneWidget);
      expect(
        find.byKey(const Key('task_portal_switch_account_btn')),
        findsOneWidget,
      );
      expect(execClient.activateCallCount, 0);

      // Clicking Sign Out & Switch Account signs out alice@org.com and shows JIT onboarding card
      await tester.tap(find.byKey(const Key('task_portal_switch_account_btn')));
      await tester.pumpAndSettle();

      expect(authController.signOutCallCount, 1);
      expect(
        find.byKey(const Key('task_portal_jit_onboarding_card')),
        findsOneWidget,
      );
    });

    testWidgets(
      'positive & boundary: renders SafeLinks-immune preview without starting timer, activates on Start Task click, saves draft, and submits task',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final authController = _StubAuthController(bobUser);
        final execClient = _FakeExecutionClient(
          assignedEmailMasked: 'bob@org.com',
        );

        await tester.pumpWidget(
          _buildPortalTestApp(
            authController: authController,
            execClient: execClient,
          ),
        );
        await tester.pumpAndSettle();

        // Preview loaded, timer NOT yet started
        expect(
          find.byKey(const Key('task_portal_preview_card')),
          findsOneWidget,
        );
        expect(
          find.byKey(const Key('task_portal_start_task_btn')),
          findsOneWidget,
        );
        expect(execClient.activateCallCount, 0);

        // Click Start Task to explicitly activate timer
        await tester.tap(find.byKey(const Key('task_portal_start_task_btn')));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 100));

        expect(execClient.activateCallCount, 1);
        expect(
          find.byKey(const Key('task_portal_workspace_card')),
          findsOneWidget,
        );
        expect(
          find.byKey(const Key('task_portal_countdown_badge')),
          findsOneWidget,
        );

        // Enter assignee input, save draft, and submit
        await tester.enterText(
          find.byKey(const Key('task_portal_input_candidate_essay')),
          'Strategic response for evaluation.',
        );
        await tester.tap(find.byKey(const Key('task_portal_save_draft_btn')));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 100));
        expect(execClient.saveDraftCallCount, 1);

        await tester.tap(find.byKey(const Key('task_portal_submit_btn')));
        await tester.pumpAndSettle();
        expect(execClient.submitCallCount, 1);
        expect(
          find.byKey(const Key('task_portal_submitted_card')),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'negative & boundary: renders ErrorView on preview failure and clamps expired deadline countdown to 0s',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 900);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final authController = _StubAuthController(bobUser);
        final failingClient = _FakeExecutionClient(
          previewError: StateError('Invalid or expired invitation token'),
        );

        await tester.pumpWidget(
          _buildPortalTestApp(
            authController: authController,
            execClient: failingClient,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byKey(const Key('task_portal_preview_card')), findsNothing);

        // Boundary check: hard deadline already in the past clamps remaining seconds to 0s
        final expiredClient = _FakeExecutionClient(
          overrideHardDeadlineAt: DateTime.now().toUtc().subtract(
            const Duration(seconds: 5),
          ),
        );
        await tester.pumpWidget(
          _buildPortalTestApp(
            authController: authController,
            execClient: expiredClient,
            token: 'tok_01960000000070008000000000000002',
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byKey(const Key('task_portal_start_task_btn')));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 100));

        expect(
          find.byKey(const Key('task_portal_countdown_badge')),
          findsOneWidget,
        );
        expect(find.textContaining('0s'), findsOneWidget);
      },
    );

    testWidgets(
      'positive: completes MFA_REQUIRED TOTP JIT onboarding, renders task_portal_task_brief_card, and uploads/clears file input',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 1000);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final authController = _StubAuthController(null);
        final fakeAuthRepo = _FakeAuthRepository();
        const brief = TaskAssignmentBriefDto(
          id: 'blk_01960000000070008000000000000001',
          label: I18nText(
            translations: <String, String>{
              'en': 'Executive Strategy Brief',
              'fi': 'Strategian tehtävänanto',
            },
          ),
          instructionText: 'Read the case study and upload your response PDF.',
          sourceUrl: 'https://docs.qrum.ai/cases/strategy-1',
        );
        final execClient = _FakeExecutionClient(
          assignedEmailMasked: 'bob@org.com',
          taskBrief: brief,
          requireMfaOnFirstOnboard: true,
        );

        await tester.pumpWidget(
          _buildPortalTestApp(
            authController: authController,
            execClient: execClient,
            authRepo: fakeAuthRepo,
            onPickFile: (inputKey) async => WorkflowInputValue.file(
              filename: 'candidate_response.pdf',
              contentBase64: 'cGRmX2J5dGVz',
            ),
          ),
        );
        await tester.pumpAndSettle();

        // Task Brief Card is rendered with title, body, and link
        expect(
          find.byKey(const Key('task_portal_task_brief_card')),
          findsOneWidget,
        );
        expect(find.text('Executive Strategy Brief'), findsOneWidget);
        expect(
          find.byKey(const Key('task_portal_task_brief_body')),
          findsOneWidget,
        );
        expect(
          find.byKey(const Key('task_portal_task_brief_link')),
          findsOneWidget,
        );

        // 1st click on JIT onboarding triggers MFA_REQUIRED -> displays TOTP secret key
        await tester.enterText(
          find.byKey(const Key('task_portal_onboard_name_field')),
          'Bob Candidate',
        );
        await tester.enterText(
          find.byKey(const Key('task_portal_onboard_token_field')),
          'StrongPassword123!',
        );
        await tester.tap(find.byKey(const Key('task_portal_onboard_btn')));
        await tester.pumpAndSettle();

        expect(fakeAuthRepo.authOnboardingCalls, 1);
        expect(fakeAuthRepo.prepareEnrollmentCalls, 1);
        expect(
          find.byKey(const Key('task_portal_totp_secret_text')),
          findsOneWidget,
        );
        expect(find.text('PORTAL-TOTP-SECRET-KEY'), findsOneWidget);

        // Enter 6-digit TOTP code and click onboard button again -> completes onboarding
        await tester.enterText(
          find.byKey(const Key('task_portal_onboard_totp_field')),
          '654321',
        );
        await tester.tap(find.byKey(const Key('task_portal_onboard_btn')));
        await tester.pumpAndSettle();

        expect(fakeAuthRepo.authOnboardingCalls, 2);
        expect(execClient.onboardCallCount, 2);
        expect(
          find.byKey(const Key('task_portal_start_task_btn')),
          findsOneWidget,
        );

        // Activate task and test file upload & clear
        await tester.tap(find.byKey(const Key('task_portal_start_task_btn')));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 100));

        await tester.tap(
          find.byKey(const Key('task_portal_upload_file_btn_candidate_essay')),
        );
        await tester.pump();
        expect(
          find.byKey(
            const Key('task_portal_attached_filename_candidate_essay'),
          ),
          findsOneWidget,
        );
        expect(find.text('candidate_response.pdf'), findsOneWidget);

        // Save draft with attached file
        await tester.tap(find.byKey(const Key('task_portal_save_draft_btn')));
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 100));
        expect(execClient.saveDraftCallCount, 1);
        expect(
          execClient
              .lastSavedDraftPayload
              ?.draftInputs
              .dynamicInputs['candidate_essay']
              ?.fileValue
              ?.filename,
          equals('candidate_response.pdf'),
        );

        // Clear attached file, re-upload, and submit
        await tester.tap(
          find.byKey(const Key('task_portal_clear_file_btn_candidate_essay')),
        );
        await tester.pump();
        expect(
          find.byKey(
            const Key('task_portal_attached_filename_candidate_essay'),
          ),
          findsNothing,
        );

        await tester.tap(
          find.byKey(const Key('task_portal_upload_file_btn_candidate_essay')),
        );
        await tester.pump();

        await tester.tap(find.byKey(const Key('task_portal_submit_btn')));
        await tester.pumpAndSettle();
        expect(execClient.submitCallCount, 1);
        expect(
          execClient
              .lastSubmittedPayload
              ?.submittedInputs
              .dynamicInputs['candidate_essay']
              ?.fileValue
              ?.filename,
          equals('candidate_response.pdf'),
        );
      },
    );
  });
}
