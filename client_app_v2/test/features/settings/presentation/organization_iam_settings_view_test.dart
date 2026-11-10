import 'dart:async';

import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/features/settings/domain/models/tenant_secret_dto.dart';
import 'package:client_app/features/settings/presentation/organization_iam_settings_view.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/features/studio/models/prompt_block.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/router/scaffold_with_nav.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:go_router/go_router.dart';

class _StubAuthController extends AuthController {
  final User? _user;

  _StubAuthController(this._user);

  @override
  FutureOr<User?> build() => _user;
}

class _FakeUserRepository implements UserRepository {
  static const String primaryOrgId = 'org_01960000000070008000000000000001';
  static const String secondaryOrgId = 'org_01960000000070008000000000000002';

  List<Organization> organizations = [
    const Organization(
      id: primaryOrgId,
      name: 'Quorum Enterprise Ltd',
      contactEmail: 'ops@quorum.ai',
      quotaLimit: 5000.0,
      tpmLimit: 250000,
      rpmLimit: 120,
    ),
    const Organization(
      id: secondaryOrgId,
      name: 'Partner Org Oy',
      contactEmail: 'admin@partner.fi',
      quotaLimit: 2000.0,
      tpmLimit: 100000,
      rpmLimit: 60,
    ),
  ];

  List<User> users = [
    const User(
      id: 'usr_01960000000070008000000000000001',
      email: 'admin@quorum.ai',
      name: 'Admin User',
      role: UserRole.admin,
      organizationId: primaryOrgId,
      isActive: true,
    ),
    const User(
      id: 'usr_01960000000070008000000000000002',
      email: 'member@quorum.ai',
      name: 'Member User',
      role: UserRole.member,
      organizationId: primaryOrgId,
      isActive: true,
    ),
    const User(
      id: 'usr_01960000000070008000000000000003',
      email: 'partner_member@partner.fi',
      name: 'Partner Member',
      role: UserRole.member,
      organizationId: secondaryOrgId,
      isActive: true,
    ),
  ];

  OrganizationUpdateDto? lastUpdatedOrganization;
  TenantSecretCreateDto? lastSavedSecret;
  UserCreate? lastCreatedUser;
  String? lastUpdatedUserId;
  UserUpdate? lastUpdatedUserPayload;
  String? lastDeletedUserId;
  AppException? createUserError;

  @override
  Future<Either<AppException, List<Organization>>> listOrganizations() async {
    return Right(List<Organization>.unmodifiable(organizations));
  }

  @override
  Future<Either<AppException, Organization>> getOrganization(
    String orgId,
  ) async {
    final match = organizations.where((o) => o.id == orgId).firstOrNull;
    return Right(match ?? organizations.first);
  }

  @override
  Future<Either<AppException, Organization>> updateOrganization(
    String orgId,
    OrganizationUpdateDto payload,
  ) async {
    lastUpdatedOrganization = payload;
    final idx = organizations.indexWhere((o) => o.id == orgId);
    final current = idx >= 0 ? organizations[idx] : organizations.first;
    final updated = current.copyWith(
      name: payload.name ?? current.name,
      contactEmail: payload.contactEmail ?? current.contactEmail,
    );
    if (idx >= 0) {
      organizations[idx] = updated;
    }
    return Right(updated);
  }

  @override
  Future<Either<AppException, User>> createUser(UserCreate payload) async {
    if (createUserError != null) {
      return Left(createUserError!);
    }
    lastCreatedUser = payload;
    final created = User(
      id: 'usr_01960000000070008000000000000004',
      email: payload.email,
      name: payload.name,
      role: payload.role,
      organizationId: payload.organizationId,
      isActive: payload.isActive,
      language: payload.language,
      themeMode: payload.themeMode,
    );
    users = [...users, created];
    return Right(created);
  }

  @override
  Future<Either<AppException, User>> updateUser(
    String userId,
    UserUpdate payload,
  ) async {
    lastUpdatedUserId = userId;
    lastUpdatedUserPayload = payload;
    final idx = users.indexWhere((u) => u.id == userId);
    if (idx < 0) {
      return Left(AppException.notFound('User not found'));
    }
    final current = users[idx];
    final updated = current.copyWith(
      name: payload.name ?? current.name,
      role: payload.role ?? current.role,
      organizationId: payload.organizationId ?? current.organizationId,
      isActive: payload.isActive ?? current.isActive,
    );
    users = [
      for (var i = 0; i < users.length; i++)
        if (i == idx) updated else users[i],
    ];
    return Right(updated);
  }

  @override
  Future<Either<AppException, UserDeleteResponse>> deleteUser(
    String userId,
  ) async {
    lastDeletedUserId = userId;
    users = users.where((u) => u.id != userId).toList();
    return Right(UserDeleteResponse(status: 'deleted', id: userId));
  }

  @override
  Future<Either<AppException, List<InvitationResponseDto>>> listInvitations(
    String orgId,
  ) async {
    return Right([
      InvitationResponseDto(
        id: 'inv_01960000000070008000000000000001',
        organizationId: orgId,
        email: 'invitee@quorum.ai',
        role: UserRole.member,
        status: InvitationStatus.pending,
        emailDeliveryStatus: EmailDeliveryStatus.sent,
        invitedBy: 'usr_01960000000070008000000000000001',
        expiresAt: DateTime.utc(2026, 12, 31),
        createdAt: DateTime.utc(2026, 11, 1),
      ),
    ]);
  }

  @override
  Future<Either<AppException, List<User>>> listUsers() async {
    return Right(List<User>.unmodifiable(users));
  }

  List<TenantSecretResponseDto> secrets = [
    TenantSecretResponseDto(
      id: 'sec_01960000000070008000000000000001',
      organizationId: primaryOrgId,
      scope: SecretScope.llmProvider,
      targetIdentifier: 'openai',
      storageMode: SecretStorageMode.envelopeKms,
      configured: true,
      maskedHint: '****abcd',
      kekVersion: 'v1',
      updatedAt: DateTime.utc(2026, 11, 1),
    ),
  ];

  @override
  Future<Either<AppException, List<TenantSecretResponseDto>>> listSecrets(
    String orgId,
  ) async {
    return Right(
      secrets
          .map((s) => s.copyWith(organizationId: orgId))
          .toList(growable: false),
    );
  }

  @override
  Future<Either<AppException, TenantSecretResponseDto>> upsertSecret(
    String orgId,
    TenantSecretCreateDto payload,
  ) async {
    lastSavedSecret = payload;
    final saved = TenantSecretResponseDto(
      id: 'sec_01960000000070008000000000000002',
      organizationId: orgId,
      scope: payload.scope,
      targetIdentifier: payload.targetIdentifier,
      storageMode: payload.storageMode,
      configured: true,
      maskedHint: '****9999',
      kekVersion: 'v1',
      updatedAt: DateTime.utc(2026, 11, 2),
    );
    secrets = [
      ...secrets.where(
        (s) =>
            !(s.scope == payload.scope &&
                s.targetIdentifier == payload.targetIdentifier),
      ),
      saved,
    ];
    return Right(saved);
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _FakeStudioClient implements StudioClient {
  List<McpGateway> gateways;
  List<PromptBlock> promptBlocks;
  List<Workflow> workflows;
  String defaultDraftOrganizationId;
  int _draftCounter = 0;

  _FakeStudioClient({
    this.gateways = const <McpGateway>[
      McpGateway(
        id: 'sys_0195f3a00000700080008172bda70c86',
        name: 'Tavily MCP Gateway',
        slug: 'default_mcp_gateway',
        type: 'mcp_gateways',
      ),
    ],
    List<PromptBlock>? promptBlocks,
    List<Workflow>? workflows,
    this.defaultDraftOrganizationId = _FakeUserRepository.primaryOrgId,
  }) : promptBlocks = List<PromptBlock>.from(promptBlocks ?? const []),
       workflows = List<Workflow>.from(
         workflows ??
             const <Workflow>[
               Workflow(
                 id: 'wor_01960000000070008000000000000010',
                 slug: 'leadership_workflow',
                 name: I18nText(
                   translations: {
                     'en': 'Leadership Evaluation',
                     'fi': 'Johtajuusarviointi',
                   },
                 ),
                 description: I18nText(
                   translations: {
                     'en': 'Evaluate leadership case',
                     'fi': 'Arvioi johtamistapaus',
                   },
                 ),
                 modelRegistryId: 'sys_01960000000070008000000000000090',
                 expectedInputs: [
                   ExpectedInput(
                     inputKey: 'candidate_response',
                     label: I18nText(
                       translations: {
                         'en': 'Candidate Response',
                         'fi': 'Kandidaatin vastaus',
                       },
                     ),
                     description: I18nText(
                       translations: {
                         'en': 'Submit response',
                         'fi': 'Lähetä vastaus',
                       },
                     ),
                     required: true,
                     inputModes: ['text'],
                   ),
                 ],
               ),
             ],
       );

  @override
  Future<List<McpGateway>> getMcpGateways() async => gateways;

  @override
  Future<List<Workflow>> getWorkflows() async =>
      List<Workflow>.unmodifiable(workflows);

  @override
  Future<List<PromptBlock>> getPromptBlocks() async =>
      List<PromptBlock>.unmodifiable(promptBlocks);

  @override
  Future<PromptBlock> createPromptBlockDraft({String? categoryId}) async {
    _draftCounter += 1;
    final hexTail = _draftCounter.toRadixString(16).padLeft(8, '0');
    final draftId = 'blk_019600000000700080000000$hexTail';
    final PromptBlock draft = switch (categoryId) {
      'task_definition' => TaskDefinitionPromptBlock(
        id: draftId,
        slug: 'draft_task_brief_$_draftCounter',
        organizationId: defaultDraftOrganizationId,
        label: const I18nText(
          translations: {'en': 'Draft Task Brief', 'fi': 'Luonnostehtävä'},
        ),
        description: const I18nText(
          translations: {'en': 'Draft description', 'fi': 'Luonnoskuvaus'},
        ),
        instructionText: 'Initial draft instructions',
      ),
      _ => SystemRulePromptBlock(
        id: draftId,
        slug: 'draft_rule_$_draftCounter',
        organizationId: defaultDraftOrganizationId,
        label: const I18nText(
          translations: {'en': 'Draft Rule', 'fi': 'Luonnossääntö'},
        ),
        description: const I18nText(
          translations: {'en': 'Draft description', 'fi': 'Luonnoskuvaus'},
        ),
        instructionText: 'Initial rule',
      ),
    };
    promptBlocks = <PromptBlock>[draft, ...promptBlocks];
    return draft;
  }

  @override
  Future<PromptBlock> savePromptBlock(String id, PromptBlock data) async {
    final idx = promptBlocks.indexWhere((b) => b.id == id);
    if (idx < 0) {
      throw AppException.notFound('PromptBlock not found: $id');
    }
    promptBlocks = <PromptBlock>[
      for (var i = 0; i < promptBlocks.length; i++)
        if (i == idx) data else promptBlocks[i],
    ];
    return data;
  }

  @override
  Future<PromptBlock> clonePromptBlock(String id) async {
    final original = promptBlocks.where((b) => b.id == id).firstOrNull;
    if (original == null) {
      throw AppException.notFound('PromptBlock not found: $id');
    }
    _draftCounter += 1;
    final hexTail = _draftCounter.toRadixString(16).padLeft(8, '0');
    final clonedId = 'blk_019600000000700080000000$hexTail';
    final enTitle = original.label.translations['en'] ?? 'Brief';
    final fiTitle = original.label.translations['fi'] ?? enTitle;
    final cloned = original.copyWith(
      id: clonedId,
      slug: '${original.slug}_copy_$_draftCounter',
      organizationId: defaultDraftOrganizationId,
      label: I18nText(
        translations: <String, String>{
          'en': '$enTitle (Copy)',
          'fi': '$fiTitle (Copy)',
        },
      ),
    );
    promptBlocks = <PromptBlock>[cloned, ...promptBlocks];
    return cloned;
  }

  @override
  Future<void> deletePromptBlock(String id) async {
    promptBlocks = promptBlocks.where((b) => b.id != id).toList();
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _FakeExecutionClient implements ExecutionClient {
  ExecutionAssignmentCreateDto? lastCreatedAssignment;
  List<ExecutionAssignmentResponseDto> assignments = [
    ExecutionAssignmentResponseDto(
      id: 'asg_01960000000070008000000000000001',
      organizationId: 'org_01960000000070008000000000000001',
      assignedEmail: 'candidate@quorum.ai',
      invitedRole: UserRole.member,
      workflowId: 'wf_01960000000070008000000000000001',
      targetLocale: 'fi',
      lockedInputs: const WorkflowInputs(),
      assigneeInputKeys: const ['candidate_response'],
      draftInputs: const WorkflowInputs(),
      status: AssignmentStatus.pending,
      emailDeliveryStatus: EmailDeliveryStatus.sent,
      resultVisibility: AssignmentResultVisibility.confirmationOnly,
      hardDeadlineAt: DateTime.utc(2026, 12, 1),
      createdBy: 'usr_01960000000070008000000000000001',
      createdAt: DateTime.utc(2026, 11, 1),
    ),
  ];

  @override
  Future<List<ExecutionAssignmentResponseDto>> listAssignments({
    String? batchId,
  }) async {
    return List<ExecutionAssignmentResponseDto>.unmodifiable(assignments);
  }

  @override
  Future<ExecutionAssignmentResponseDto> createAssignment(
    ExecutionAssignmentCreateDto dto,
  ) async {
    lastCreatedAssignment = dto;
    final created = ExecutionAssignmentResponseDto(
      id: 'tsk_01960000000070008000000000000099',
      organizationId: _FakeUserRepository.primaryOrgId,
      assignedEmail: dto.assignedEmail,
      invitedRole: dto.invitedRole,
      workflowId: dto.workflowId,
      outputProfileId: dto.outputProfileId,
      taskBriefId: dto.taskBriefId,
      targetLocale: dto.targetLocale,
      lockedInputs: dto.lockedInputs,
      assigneeInputKeys: dto.assigneeInputKeys,
      draftInputs: const WorkflowInputs(),
      status: AssignmentStatus.pending,
      emailDeliveryStatus: EmailDeliveryStatus.sent,
      resultVisibility: dto.resultVisibility,
      hardDeadlineAt: dto.hardDeadlineAt,
      relativeDurationSeconds: dto.relativeDurationSeconds,
      createdBy: 'usr_01960000000070008000000000000001',
      createdAt: DateTime.utc(2026, 11, 2),
    );
    assignments = <ExecutionAssignmentResponseDto>[created, ...assignments];
    return created;
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

Widget _buildIamViewForRole({
  required User user,
  required _FakeUserRepository userRepo,
  required _FakeExecutionClient execClient,
  _FakeStudioClient? studioClient,
}) {
  return ProviderScope(
    key: UniqueKey(),
    overrides: [
      authControllerProvider.overrideWith(() => _StubAuthController(user)),
      userRepositoryProvider.overrideWithValue(userRepo),
      executionClientProvider.overrideWithValue(execClient),
      studioClientProvider.overrideWithValue(
        studioClient ?? _FakeStudioClient(),
      ),
    ],
    child: const MaterialApp(
      localizationsDelegates: [
        AppLocalizations.delegate,
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      supportedLocales: [Locale('en'), Locale('fi')],
      home: OrganizationIamSettingsView(),
    ),
  );
}

void main() {
  const orgId = 'org_01960000000070008000000000000001';

  User userWithRole(UserRole role) => User(
    id: 'usr_01960000000070008000000000000001',
    email: '${role.name}@quorum.ai',
    role: role,
    organizationId: orgId,
  );

  group('OrganizationIamSettingsView & Role Segregation Boundary Tests', () {
    testWidgets('test_user_profile_and_organization_iam_role_segregation_boundary', (
      WidgetTester tester,
    ) async {
      tester.view.physicalSize = const Size(1440, 1200);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final userRepo = _FakeUserRepository();
      final execClient = _FakeExecutionClient();

      // 1. VIEWER & MEMBER in ScaffoldWithNav: see Profile and Sign Out, but NOT /organization
      for (final restrictedRole in [UserRole.viewer, UserRole.member]) {
        final navRouter = GoRouter(
          initialLocation: '/dashboard',
          routes: [
            StatefulShellRoute.indexedStack(
              builder: (context, state, navigationShell) =>
                  ScaffoldWithNav(navigationShell: navigationShell),
              branches: [
                StatefulShellBranch(
                  routes: [
                    GoRoute(
                      path: '/dashboard',
                      builder: (context, state) => const Text('Dash'),
                    ),
                  ],
                ),
                StatefulShellBranch(
                  routes: [
                    GoRoute(
                      path: '/orchestration/new',
                      builder: (context, state) => const Text('New'),
                    ),
                  ],
                ),
                StatefulShellBranch(
                  routes: [
                    GoRoute(
                      path: '/settings',
                      builder: (context, state) => const Text('Profile'),
                    ),
                  ],
                ),
                StatefulShellBranch(
                  routes: [
                    GoRoute(
                      path: '/organization',
                      builder: (context, state) => const Text('Org'),
                    ),
                  ],
                ),
              ],
            ),
          ],
        );

        await tester.pumpWidget(
          ProviderScope(
            key: UniqueKey(),
            overrides: [
              authControllerProvider.overrideWith(
                () => _StubAuthController(userWithRole(restrictedRole)),
              ),
            ],
            child: MaterialApp.router(
              routerConfig: navRouter,
              localizationsDelegates: const [
                AppLocalizations.delegate,
                GlobalMaterialLocalizations.delegate,
                GlobalWidgetsLocalizations.delegate,
                GlobalCupertinoLocalizations.delegate,
              ],
              supportedLocales: const [Locale('en')],
            ),
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.person_outline), findsOneWidget);
        expect(find.byKey(const Key('nav_rail_sign_out_btn')), findsOneWidget);
        expect(find.byIcon(Icons.business_outlined), findsNothing);

        // Also verify OrganizationIamSettingsView blocks VIEWER and MEMBER
        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(restrictedRole),
            userRepo: userRepo,
            execClient: execClient,
          ),
        );
        await tester.pumpAndSettle();

        expect(
          find.byKey(const Key('org_iam_restricted_card')),
          findsOneWidget,
        );
        expect(find.byKey(const Key('org_metadata_card')), findsNothing);
      }

      // 2. MANAGER: edits org name/contact_email and manages task assignments,
      // while BYOK secrets and user invitations/roles are hidden
      await tester.pumpWidget(
        _buildIamViewForRole(
          user: userWithRole(UserRole.manager),
          userRepo: userRepo,
          execClient: execClient,
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('org_metadata_card')), findsOneWidget);
      expect(find.byKey(const Key('org_assignments_card')), findsOneWidget);
      expect(find.byKey(const Key('org_invitations_card')), findsNothing);
      expect(find.byKey(const Key('org_byok_secrets_card')), findsNothing);

      await tester.enterText(
        find.byKey(const Key('org_name_field')),
        'Quorum Manager Updated Org',
      );
      await tester.tap(find.byKey(const Key('org_save_metadata_btn')));
      await tester.pumpAndSettle();
      expect(
        userRepo.lastUpdatedOrganization?.name,
        'Quorum Manager Updated Org',
      );

      // 3. ADMIN & ROOT: see all 4 sections including invitations/roles and BYOK secrets
      for (final privilegedRole in [UserRole.admin, UserRole.root]) {
        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(privilegedRole),
            userRepo: userRepo,
            execClient: execClient,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byKey(const Key('org_metadata_card')), findsOneWidget);
        expect(find.byKey(const Key('org_assignments_card')), findsOneWidget);
        expect(find.byKey(const Key('org_invitations_card')), findsOneWidget);
        expect(find.byKey(const Key('org_byok_secrets_card')), findsOneWidget);
        expect(find.text('****abcd'), findsOneWidget);
      }
    });

    testWidgets(
      'negative: renders ErrorView when organization profile fetch fails with AppException',
      (WidgetTester tester) async {
        final execClient = _FakeExecutionClient();
        final failingRepo = _FailingUserRepository();

        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(UserRole.admin),
            userRepo: failingRepo,
            execClient: execClient,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byKey(const Key('org_metadata_card')), findsOneWidget);
        expect(find.byIcon(Icons.error_outline), findsWidgets);
      },
    );

    testWidgets(
      'boundary: renders errorNotFound when organizationId is empty or null',
      (WidgetTester tester) async {
        final userRepo = _FakeUserRepository();
        final execClient = _FakeExecutionClient();

        await tester.pumpWidget(
          _buildIamViewForRole(
            user: const User(
              id: 'usr_01960000000070008000000000000009',
              email: 'orphan_admin@quorum.ai',
              role: UserRole.admin,
              organizationId: '',
            ),
            userRepo: userRepo,
            execClient: execClient,
          ),
        );
        await tester.pumpAndSettle();

        final l10n = AppLocalizations.of(
          tester.element(find.byType(Scaffold)),
        )!;
        expect(find.byKey(const Key('org_metadata_card')), findsNothing);
        expect(find.text(l10n.errorNotFound), findsOneWidget);
      },
    );

    testWidgets(
      'positive: ADMIN executes full User CRUD (create, update name/isActive/role, delete) within own organization without cross-org selector',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 1400);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final userRepo = _FakeUserRepository();
        final execClient = _FakeExecutionClient();

        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(UserRole.admin),
            userRepo: userRepo,
            execClient: execClient,
          ),
        );
        await tester.pumpAndSettle();

        // ADMIN does NOT see ROOT cross-organization selector or other org's members
        expect(
          find.byKey(const Key('org_root_selector_dropdown')),
          findsNothing,
        );
        expect(find.text('member@quorum.ai'), findsOneWidget);
        expect(find.text('partner_member@partner.fi'), findsNothing);

        // 1. Create User Directly in own organization
        await tester.tap(find.byKey(const Key('org_create_user_mode_chip')));
        await tester.pumpAndSettle();

        await tester.enterText(
          find.byKey(const Key('org_create_user_email_field')),
          'new_coach@quorum.ai',
        );
        await tester.enterText(
          find.byKey(const Key('org_create_user_name_field')),
          'New Coach',
        );
        await tester.enterText(
          find.byKey(const Key('org_create_user_password_field')),
          'secretPass123',
        );
        await tester.tap(find.byKey(const Key('org_create_user_submit_btn')));
        await tester.pumpAndSettle();

        expect(userRepo.lastCreatedUser?.email, equals('new_coach@quorum.ai'));
        expect(userRepo.lastCreatedUser?.name, equals('New Coach'));
        expect(userRepo.lastCreatedUser?.password, equals('secretPass123'));
        expect(
          userRepo.lastCreatedUser?.organizationId,
          equals(_FakeUserRepository.primaryOrgId),
        );
        expect(find.text('new_coach@quorum.ai'), findsOneWidget);

        // 2. Update Member Name & Active Status via Edit Dialog
        const memberId = 'usr_01960000000070008000000000000002';
        await tester.ensureVisible(
          find.byKey(const Key('org_edit_member_btn_$memberId')),
        );
        await tester.tap(
          find.byKey(const Key('org_edit_member_btn_$memberId')),
        );
        await tester.pumpAndSettle();

        expect(find.byKey(const Key('org_edit_member_dialog')), findsOneWidget);
        // ADMIN does not see organization transfer dropdown in edit dialog
        expect(
          find.byKey(const Key('org_edit_member_org_dropdown')),
          findsNothing,
        );

        await tester.enterText(
          find.byKey(const Key('org_edit_member_name_field')),
          'Updated Member Name',
        );
        await tester.tap(
          find.byKey(const Key('org_edit_member_active_switch')),
        );
        await tester.pumpAndSettle();
        await tester.tap(find.byKey(const Key('org_edit_member_save_btn')));
        await tester.pumpAndSettle();

        expect(userRepo.lastUpdatedUserId, equals(memberId));
        expect(
          userRepo.lastUpdatedUserPayload?.name,
          equals('Updated Member Name'),
        );
        expect(userRepo.lastUpdatedUserPayload?.isActive, isFalse);

        // 3. Update Member Role inline
        await tester.tap(
          find.byKey(const Key('org_member_role_dropdown_$memberId')),
        );
        await tester.pumpAndSettle();
        await tester.tap(find.text('MANAGER').last);
        await tester.pumpAndSettle();

        expect(userRepo.lastUpdatedUserId, equals(memberId));
        expect(userRepo.lastUpdatedUserPayload?.role, equals(UserRole.manager));

        // 4. Delete Member (GDPR Soft-Delete)
        await tester.tap(
          find.byKey(const Key('org_delete_member_btn_$memberId')),
        );
        await tester.pumpAndSettle();

        expect(userRepo.lastDeletedUserId, equals(memberId));
        expect(find.text('member@quorum.ai'), findsNothing);
      },
    );

    testWidgets(
      'positive: ROOT switches organizations via org_root_selector_dropdown and executes cross-organization User CRUD and org transfer',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 1400);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final userRepo = _FakeUserRepository();
        final execClient = _FakeExecutionClient();

        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(UserRole.root),
            userRepo: userRepo,
            execClient: execClient,
          ),
        );
        await tester.pumpAndSettle();

        // ROOT sees cross-organization selector card & dropdown
        expect(find.byKey(const Key('org_root_selector_card')), findsOneWidget);
        expect(
          find.byKey(const Key('org_root_selector_dropdown')),
          findsOneWidget,
        );

        // Switch to Secondary Organization ('Partner Org Oy')
        await tester.tap(find.byKey(const Key('org_root_selector_dropdown')));
        await tester.pumpAndSettle();
        await tester.tap(find.text('Partner Org Oy').last);
        await tester.pumpAndSettle();

        // Verify members list switched to secondaryOrgId
        expect(find.text('partner_member@partner.fi'), findsOneWidget);
        expect(find.text('member@quorum.ai'), findsNothing);

        // Create a user directly in secondaryOrgId
        await tester.tap(find.byKey(const Key('org_create_user_mode_chip')));
        await tester.pumpAndSettle();

        await tester.enterText(
          find.byKey(const Key('org_create_user_email_field')),
          'partner_admin@partner.fi',
        );
        await tester.enterText(
          find.byKey(const Key('org_create_user_password_field')),
          'partnerPass123',
        );
        await tester.tap(find.byKey(const Key('org_create_user_submit_btn')));
        await tester.pumpAndSettle();

        expect(
          userRepo.lastCreatedUser?.organizationId,
          equals(_FakeUserRepository.secondaryOrgId),
        );
        expect(find.text('partner_admin@partner.fi'), findsOneWidget);

        // Edit member in secondaryOrgId and transfer them to primaryOrgId via org_edit_member_org_dropdown
        const partnerMemberId = 'usr_01960000000070008000000000000003';
        await tester.ensureVisible(
          find.byKey(const Key('org_edit_member_btn_$partnerMemberId')),
        );
        await tester.tap(
          find.byKey(const Key('org_edit_member_btn_$partnerMemberId')),
        );
        await tester.pumpAndSettle();

        expect(
          find.byKey(const Key('org_edit_member_org_dropdown')),
          findsOneWidget,
        );
        await tester.tap(find.byKey(const Key('org_edit_member_org_dropdown')));
        await tester.pumpAndSettle();
        await tester.tap(find.text('Quorum Enterprise Ltd').last);
        await tester.pumpAndSettle();

        await tester.tap(find.byKey(const Key('org_edit_member_save_btn')));
        await tester.pumpAndSettle();

        expect(userRepo.lastUpdatedUserId, equals(partnerMemberId));
        expect(
          userRepo.lastUpdatedUserPayload?.organizationId,
          equals(_FakeUserRepository.primaryOrgId),
        );
      },
    );

    testWidgets(
      'negative 1 (ISTQB BVA password.length == 5): direct user creation rejects < 6 character password with ErrorView without calling createUser',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 1400);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final userRepo = _FakeUserRepository();
        final execClient = _FakeExecutionClient();

        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(UserRole.admin),
            userRepo: userRepo,
            execClient: execClient,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byKey(const Key('org_create_user_mode_chip')));
        await tester.pumpAndSettle();

        await tester.enterText(
          find.byKey(const Key('org_create_user_email_field')),
          'shortpw@quorum.ai',
        );
        await tester.enterText(
          find.byKey(const Key('org_create_user_password_field')),
          '12345',
        );
        await tester.tap(find.byKey(const Key('org_create_user_submit_btn')));
        await tester.pumpAndSettle();

        expect(userRepo.lastCreatedUser, isNull);
        expect(find.byIcon(Icons.error_outline), findsWidgets);
      },
    );

    testWidgets(
      'negative 2: renders ErrorView when UserRepository.createUser returns Left(AppException.server)',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 1400);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final userRepo = _FakeUserRepository()
          ..createUserError = AppException.server(
            'Firebase provisioning failed',
          );
        final execClient = _FakeExecutionClient();

        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(UserRole.admin),
            userRepo: userRepo,
            execClient: execClient,
          ),
        );
        await tester.pumpAndSettle();

        await tester.tap(find.byKey(const Key('org_create_user_mode_chip')));
        await tester.pumpAndSettle();

        await tester.enterText(
          find.byKey(const Key('org_create_user_email_field')),
          'fail@quorum.ai',
        );
        await tester.enterText(
          find.byKey(const Key('org_create_user_password_field')),
          'validPass123',
        );
        await tester.tap(find.byKey(const Key('org_create_user_submit_btn')));
        await tester.pumpAndSettle();

        expect(find.byIcon(Icons.error_outline), findsWidgets);
      },
    );

    testWidgets(
      'Positive: BYOK secrets card selects MCP gateway by canonical gw.id displaying gw.name and submits storageMode',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 2000);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final userRepo = _FakeUserRepository();
        final execClient = _FakeExecutionClient();
        final studioClient = _FakeStudioClient();

        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(UserRole.admin),
            userRepo: userRepo,
            execClient: execClient,
            studioClient: studioClient,
          ),
        );
        await tester.pumpAndSettle();

        // Legacy free-text target field is eradicated
        expect(find.byKey(const Key('org_secret_target_field')), findsNothing);
        expect(
          find.byKey(const ValueKey<String>('org_secret_target_dropdown')),
          findsOneWidget,
        );

        // Switch scope from LLM Provider to MCP Gateway
        final scopeDropdown = find.byKey(
          const Key('org_secret_scope_dropdown'),
        );
        await tester.ensureVisible(scopeDropdown);
        await tester.tap(scopeDropdown);
        await tester.pumpAndSettle();
        await tester.tap(find.text(SecretScope.mcpGateway.name).last);
        await tester.pumpAndSettle();

        // Verify MCP gateway dropdown displays '${gw.name} (${gw.id})' and never gw.slug
        expect(
          find.text(
            'Tavily MCP Gateway (sys_0195f3a00000700080008172bda70c86)',
          ),
          findsWidgets,
        );

        // Switch storage mode to Cloud Secret Manager
        final storageDropdown = find.byKey(
          const Key('org_secret_storage_mode_dropdown'),
        );
        await tester.ensureVisible(storageDropdown);
        await tester.tap(storageDropdown);
        await tester.pumpAndSettle();
        await tester.tap(
          find.text(SecretStorageMode.cloudSecretManager.name).last,
        );
        await tester.pumpAndSettle();

        // Enter secret URI and submit
        await tester.enterText(
          find.byKey(const Key('org_secret_value_field')),
          'projects/p/secrets/s/versions/1',
        );
        final saveBtn = find.byKey(const Key('org_save_secret_btn'));
        await tester.ensureVisible(saveBtn);
        await tester.tap(saveBtn);
        await tester.pumpAndSettle();

        expect(userRepo.lastSavedSecret, isNotNull);
        expect(userRepo.lastSavedSecret!.scope, equals(SecretScope.mcpGateway));
        expect(
          userRepo.lastSavedSecret!.targetIdentifier,
          equals('sys_0195f3a00000700080008172bda70c86'),
        );
        expect(
          userRepo.lastSavedSecret!.storageMode,
          equals(SecretStorageMode.cloudSecretManager),
        );
        expect(
          userRepo.lastSavedSecret!.plaintextSecret,
          equals('projects/p/secrets/s/versions/1'),
        );
      },
    );

    testWidgets(
      'Negative & Boundary: BYOK secrets card fails fast when secret value is empty or no MCP gateway is configured',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 2000);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final userRepo = _FakeUserRepository();
        final execClient = _FakeExecutionClient();
        final emptyStudioClient = _FakeStudioClient(gateways: const []);

        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(UserRole.admin),
            userRepo: userRepo,
            execClient: execClient,
            studioClient: emptyStudioClient,
          ),
        );
        await tester.pumpAndSettle();

        // Negative 1: Submitting with empty secret value throws AppException.validation and renders ErrorView
        final saveBtn = find.byKey(const Key('org_save_secret_btn'));
        await tester.ensureVisible(saveBtn);
        await tester.tap(saveBtn);
        await tester.pumpAndSettle();

        expect(userRepo.lastSavedSecret, isNull);
        expect(find.byIcon(Icons.error_outline), findsWidgets);

        // Boundary 2: Switching to MCP Gateway scope when 0 gateways exist disables dropdown without crashing
        final scopeDropdown = find.byKey(
          const Key('org_secret_scope_dropdown'),
        );
        await tester.ensureVisible(scopeDropdown);
        await tester.tap(scopeDropdown);
        await tester.pumpAndSettle();
        await tester.tap(find.text(SecretScope.mcpGateway.name).last);
        await tester.pumpAndSettle();

        expect(
          find.byKey(const ValueKey<String>('org_secret_target_dropdown')),
          findsOneWidget,
        );
      },
    );

    testWidgets(
      'Positive: BYOK secrets card toggles visibility for multiline Vertex AI Service Account JSON and renders MCP gateway display name and badges in saved secrets list',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 2200);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        final userRepo = _FakeUserRepository();
        userRepo.secrets = [
          ...userRepo.secrets,
          TenantSecretResponseDto(
            id: 'sec_01960000000070008000000000000003',
            organizationId: _FakeUserRepository.primaryOrgId,
            scope: SecretScope.mcpGateway,
            targetIdentifier: 'sys_0195f3a00000700080008172bda70c86',
            storageMode: SecretStorageMode.cloudSecretManager,
            configured: true,
            maskedHint: '****v1',
            kekVersion: 'v1',
            updatedAt: DateTime.utc(2026, 11, 1),
          ),
        ];
        final execClient = _FakeExecutionClient();
        final studioClient = _FakeStudioClient();

        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(UserRole.admin),
            userRepo: userRepo,
            execClient: execClient,
            studioClient: studioClient,
          ),
        );
        await tester.pumpAndSettle();

        // Saved MCP gateway secret displays human-readable gateway name + ID and scope/storageMode badges
        expect(
          find.text(
            'Tavily MCP Gateway (sys_0195f3a00000700080008172bda70c86)',
          ),
          findsOneWidget,
        );
        expect(find.text(SecretScope.mcpGateway.name), findsWidgets);
        expect(
          find.text(SecretStorageMode.cloudSecretManager.name),
          findsWidgets,
        );

        // Verify visibility toggle expands secret field from masked single-line to unmasked 6-line for Vertex AI JSON
        final toggleBtn = find.byKey(
          const Key('org_secret_visibility_toggle_btn'),
        );
        expect(toggleBtn, findsOneWidget);
        await tester.ensureVisible(toggleBtn);
        await tester.tap(toggleBtn);
        await tester.pumpAndSettle();

        // Select vertex_ai in target dropdown
        final targetDropdown = find.byKey(
          const ValueKey<String>('org_secret_target_dropdown'),
        );
        await tester.ensureVisible(targetDropdown);
        await tester.tap(targetDropdown);
        await tester.pumpAndSettle();
        await tester.tap(find.text('vertex_ai').last);
        await tester.pumpAndSettle();

        const serviceAccountJson =
            '{\n  "type": "service_account",\n  "project_id": "vertex-byok-proj"\n}';
        await tester.enterText(
          find.byKey(const Key('org_secret_value_field')),
          serviceAccountJson,
        );

        final saveBtn = find.byKey(const Key('org_save_secret_btn'));
        await tester.ensureVisible(saveBtn);
        await tester.tap(saveBtn);
        await tester.pumpAndSettle();

        expect(userRepo.lastSavedSecret, isNotNull);
        expect(
          userRepo.lastSavedSecret!.scope,
          equals(SecretScope.llmProvider),
        );
        expect(userRepo.lastSavedSecret!.targetIdentifier, equals('vertex_ai'));
        expect(
          userRepo.lastSavedSecret!.plaintextSecret,
          equals(serviceAccountJson),
        );
      },
    );

    testWidgets(
      'Positive & Negative: SecretScope.telemetry is selectable only by UserRole.root on Root System Organization',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 2200);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        const rootSystemOrgId = 'org_0195f3a0000070008000000000000001';
        final userRepo = _FakeUserRepository();
        userRepo.organizations = [
          const Organization(
            id: rootSystemOrgId,
            name: 'Quorum Root System',
            contactEmail: 'root@quorum.ai',
            quotaLimit: 10000.0,
            tpmLimit: 500000,
            rpmLimit: 240,
          ),
          ...userRepo.organizations,
        ];
        final execClient = _FakeExecutionClient();
        final studioClient = _FakeStudioClient();

        // 1. Negative: ADMIN user does NOT see SecretScope.telemetry even on Root System Organization
        await tester.pumpWidget(
          _buildIamViewForRole(
            user: const User(
              id: 'usr_01960000000070008000000000000001',
              email: 'admin@quorum.ai',
              role: UserRole.admin,
              organizationId: rootSystemOrgId,
            ),
            userRepo: userRepo,
            execClient: execClient,
            studioClient: studioClient,
          ),
        );
        await tester.pumpAndSettle();

        final scopeDropdown = find.byKey(
          const Key('org_secret_scope_dropdown'),
        );
        await tester.ensureVisible(scopeDropdown);
        await tester.tap(scopeDropdown);
        await tester.pumpAndSettle();
        expect(find.text(SecretScope.telemetry.name), findsNothing);
        await tester.tap(find.text(SecretScope.llmProvider.name).last);
        await tester.pumpAndSettle();

        // 2. Negative: ROOT user on non-Root organization does NOT see SecretScope.telemetry
        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(UserRole.root),
            userRepo: userRepo,
            execClient: execClient,
            studioClient: studioClient,
          ),
        );
        await tester.pumpAndSettle();

        await tester.ensureVisible(scopeDropdown);
        await tester.tap(scopeDropdown);
        await tester.pumpAndSettle();
        expect(find.text(SecretScope.telemetry.name), findsNothing);
        await tester.tap(find.text(SecretScope.llmProvider.name).last);
        await tester.pumpAndSettle();

        // 3. Positive: ROOT user on Root System Organization sees SecretScope.telemetry and saves logfire_read
        await tester.pumpWidget(
          _buildIamViewForRole(
            user: const User(
              id: 'usr_0195f3a00000700a83fd6b3d77c748f4',
              email: 'root@quorum.ai',
              role: UserRole.root,
              organizationId: rootSystemOrgId,
            ),
            userRepo: userRepo,
            execClient: execClient,
            studioClient: studioClient,
          ),
        );
        await tester.pumpAndSettle();

        await tester.ensureVisible(scopeDropdown);
        await tester.tap(scopeDropdown);
        await tester.pumpAndSettle();
        expect(find.text(SecretScope.telemetry.name), findsWidgets);
        await tester.tap(find.text(SecretScope.telemetry.name).last);
        await tester.pumpAndSettle();

        final targetDropdown = find.byKey(
          const ValueKey<String>('org_secret_target_dropdown'),
        );
        await tester.ensureVisible(targetDropdown);
        await tester.tap(targetDropdown);
        await tester.pumpAndSettle();
        expect(find.text('logfire'), findsWidgets);
        expect(find.text('logfire_read'), findsWidgets);
        await tester.tap(find.text('logfire_read').last);
        await tester.pumpAndSettle();

        await tester.enterText(
          find.byKey(const Key('org_secret_value_field')),
          'pylf_v1_eu_read_token',
        );
        final saveBtn = find.byKey(const Key('org_save_secret_btn'));
        await tester.ensureVisible(saveBtn);
        await tester.tap(saveBtn);
        await tester.pumpAndSettle();

        expect(userRepo.lastSavedSecret, isNotNull);
        expect(userRepo.lastSavedSecret!.scope, equals(SecretScope.telemetry));
        expect(
          userRepo.lastSavedSecret!.targetIdentifier,
          equals('logfire_read'),
        );
        expect(
          userRepo.lastSavedSecret!.plaintextSecret,
          equals('pylf_v1_eu_read_token'),
        );
      },
    );

    testWidgets(
      'Positive & Boundary: Task Briefs CRUD+Clone lifecycle, blank URL/body null normalization, ROOT_SYSTEM edit/delete guard for ADMIN, MANAGER hidden card, and direct TaskAssignmentConfigDialog launch',
      (WidgetTester tester) async {
        tester.view.physicalSize = const Size(1440, 2400);
        tester.view.devicePixelRatio = 1.0;
        addTearDown(tester.view.resetPhysicalSize);

        const rootBriefId = 'blk_0195f3a0000070008000000000000701';
        const rootBrief = TaskDefinitionPromptBlock(
          id: rootBriefId,
          slug: 'root_standard_brief',
          organizationId: 'org_0195f3a0000070008000000000000001',
          label: I18nText(
            translations: {
              'en': 'Global Case Template',
              'fi': 'Yleinen tehtäväpohja',
            },
          ),
          description: I18nText(
            translations: {'en': 'System template', 'fi': 'Järjestelmäpohja'},
          ),
          instructionText: 'System level instructions.',
          theoryGrounding: TheoryGrounding(
            sourceUrl: 'https://qrum.ai/docs/template.pdf',
          ),
        );

        final userRepo = _FakeUserRepository();
        final execClient = _FakeExecutionClient();
        final studioClient = _FakeStudioClient(
          promptBlocks: const <PromptBlock>[rootBrief],
        );

        // 1. Boundary: MANAGER does not see org_task_briefs_card
        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(UserRole.manager),
            userRepo: userRepo,
            execClient: execClient,
            studioClient: studioClient,
          ),
        );
        await tester.pumpAndSettle();
        expect(find.byKey(const Key('org_task_briefs_card')), findsNothing);

        // 2. Boundary: Tenant ADMIN sees org_task_briefs_card; ROOT_SYSTEM block allows Clone but disables Edit & Delete
        await tester.pumpWidget(
          _buildIamViewForRole(
            user: userWithRole(UserRole.admin),
            userRepo: userRepo,
            execClient: execClient,
            studioClient: studioClient,
          ),
        );
        await tester.pumpAndSettle();

        expect(find.byKey(const Key('org_task_briefs_card')), findsOneWidget);
        final rootCloneBtn = tester.widget<IconButton>(
          find.byKey(const Key('org_clone_task_brief_btn_$rootBriefId')),
        );
        final rootEditBtn = tester.widget<IconButton>(
          find.byKey(const Key('org_edit_task_brief_btn_$rootBriefId')),
        );
        final rootDeleteBtn = tester.widget<IconButton>(
          find.byKey(const Key('org_delete_task_brief_btn_$rootBriefId')),
        );
        expect(rootCloneBtn.onPressed, isNotNull);
        expect(rootEditBtn.onPressed, isNull);
        expect(rootDeleteBtn.onPressed, isNull);

        // 3. Positive: ADMIN clones ROOT_SYSTEM Task Brief into tenant org and edits it (normalizing blank URL and body to null)
        await tester.tap(
          find.byKey(const Key('org_clone_task_brief_btn_$rootBriefId')),
        );
        await tester.pumpAndSettle();

        expect(find.text('Global Case Template (Copy)'), findsOneWidget);
        final clonedBrief = studioClient.promptBlocks
            .whereType<TaskDefinitionPromptBlock>()
            .firstWhere((b) => b.id != rootBriefId);

        await tester.tap(
          find.byKey(Key('org_edit_task_brief_btn_${clonedBrief.id}')),
        );
        await tester.pumpAndSettle();

        expect(
          find.byKey(const Key('org_edit_task_brief_dialog')),
          findsOneWidget,
        );
        await tester.enterText(
          find.byKey(const Key('org_edit_task_brief_title_field')),
          'Custom Tenant Case Brief',
        );
        await tester.enterText(
          find.byKey(const Key('org_edit_task_brief_url_field')),
          '   ',
        );
        await tester.enterText(
          find.byKey(const Key('org_edit_task_brief_body_field')),
          '   ',
        );
        await tester.tap(find.byKey(const Key('org_edit_task_brief_save_btn')));
        await tester.pumpAndSettle();

        final updatedCloned = studioClient.promptBlocks
            .whereType<TaskDefinitionPromptBlock>()
            .firstWhere((b) => b.id == clonedBrief.id);
        expect(
          updatedCloned.label.translations['en'],
          equals('Custom Tenant Case Brief'),
        );
        expect(updatedCloned.theoryGrounding, isNull);
        expect(updatedCloned.instructionText, isNull);

        // 4. Positive: ADMIN creates a new Task Brief draft and deletes it
        await tester.tap(find.byKey(const Key('org_create_task_brief_btn')));
        await tester.pumpAndSettle();

        expect(find.text('Draft Task Brief'), findsOneWidget);
        final createdDraft = studioClient.promptBlocks
            .whereType<TaskDefinitionPromptBlock>()
            .firstWhere(
              (b) => b.label.translations['en'] == 'Draft Task Brief',
            );

        await tester.tap(
          find.byKey(Key('org_delete_task_brief_btn_${createdDraft.id}')),
        );
        await tester.pumpAndSettle();
        expect(find.text('Draft Task Brief'), findsNothing);

        // 5. Positive: Launching TaskAssignmentConfigDialog via org_new_task_assignment_btn and submitting with taskBriefId
        await tester.tap(find.byKey(const Key('org_new_task_assignment_btn')));
        await tester.pumpAndSettle();

        expect(
          find.byKey(const Key('task_assignment_config_dialog')),
          findsOneWidget,
        );
        expect(
          find.byKey(const Key('task_builder_workflow_dropdown')),
          findsOneWidget,
        );

        final briefSelector = find.byKey(
          const Key('task_builder_task_brief_dropdown'),
        );
        await tester.tap(briefSelector);
        await tester.pumpAndSettle();
        await tester.tap(find.text('Custom Tenant Case Brief').last);
        await tester.pumpAndSettle();

        await tester.enterText(
          find.byKey(const Key('task_builder_single_email_field')),
          'direct_assignee@quorum.ai',
        );
        await tester.tap(find.byKey(const Key('task_builder_submit_btn')));
        await tester.pumpAndSettle();

        expect(execClient.lastCreatedAssignment, isNotNull);
        expect(
          execClient.lastCreatedAssignment!.assignedEmail,
          equals('direct_assignee@quorum.ai'),
        );
        expect(
          execClient.lastCreatedAssignment!.taskBriefId,
          equals(clonedBrief.id),
        );
      },
    );
  });
}

class _FailingUserRepository extends _FakeUserRepository {
  @override
  Future<Either<AppException, Organization>> getOrganization(
    String orgId,
  ) async {
    return Left(AppException.server('Organization backend unavailable'));
  }
}
