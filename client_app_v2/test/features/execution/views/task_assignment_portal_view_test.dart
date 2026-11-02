import 'dart:async';

import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/features/execution/views/task_assignment_portal_view.dart';
import 'package:client_app/features/settings/domain/models/tenant_secret_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

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
  Future<void> signOut({bool revokeAllSessions = false}) async {
    signOutCallCount++;
    _user = null;
    state = const AsyncData(null);
  }
}

class _FakeExecutionClient implements ExecutionClient {
  int previewCallCount = 0;
  int activateCallCount = 0;
  int saveDraftCallCount = 0;
  int submitCallCount = 0;

  final String assignedEmailMasked;

  _FakeExecutionClient({this.assignedEmailMasked = 'bob@org.com'});

  @override
  Future<ExecutionAssignmentPreviewDto> previewAssignment(String token) async {
    previewCallCount++;
    return ExecutionAssignmentPreviewDto(
      id: 'asg_01960000000070008000000000000001',
      organizationId: 'org_01960000000070008000000000000001',
      organizationName: 'Quorum Org',
      assignedEmailMasked: assignedEmailMasked,
      workflowId: 'wf_01960000000070008000000000000001',
      targetLocale: 'en',
      status: AssignmentStatus.pending,
      hardDeadlineAt: DateTime.now().toUtc().add(const Duration(hours: 24)),
      relativeDurationSeconds: 1800,
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
      targetLocale: 'en',
      lockedInputs: const WorkflowInputs(),
      assigneeInputKeys: const ['candidate_essay'],
      draftInputs: const WorkflowInputs(),
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
  Future<ExecutionAssignmentResponseDto> saveAssignmentDraft({
    required String assignmentId,
    required ExecutionAssignmentDraftDto payload,
  }) async {
    saveDraftCallCount++;
    return ExecutionAssignmentResponseDto(
      id: assignmentId,
      organizationId: 'org_01960000000070008000000000000001',
      assignedEmail: 'bob@org.com',
      invitedRole: UserRole.member,
      workflowId: 'wf_01960000000070008000000000000001',
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
  String token = 'tok_01960000000070008000000000000001',
}) {
  return ProviderScope(
    overrides: [
      authControllerProvider.overrideWith(() => authController),
      executionClientProvider.overrideWithValue(execClient),
    ],
    child: MaterialApp(
      localizationsDelegates: const [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: const [Locale('en'), Locale('fi')],
      home: TaskAssignmentPortalView(token: token),
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
  });
}
