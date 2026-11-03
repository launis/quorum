import 'dart:async';

import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/features/settings/domain/models/tenant_secret_dto.dart';
import 'package:client_app/features/settings/presentation/organization_iam_settings_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/router/scaffold_with_nav.dart';
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

  @override
  Future<Either<AppException, List<TenantSecretResponseDto>>> listSecrets(
    String orgId,
  ) async {
    return Right([
      TenantSecretResponseDto(
        id: 'sec_01960000000070008000000000000001',
        organizationId: orgId,
        scope: SecretScope.llmProvider,
        targetIdentifier: 'openai',
        storageMode: SecretStorageMode.envelopeKms,
        configured: true,
        maskedHint: '****abcd',
        kekVersion: 'v1',
        updatedAt: DateTime.utc(2026, 11, 1),
      ),
    ]);
  }

  @override
  Future<Either<AppException, TenantSecretResponseDto>> upsertSecret(
    String orgId,
    TenantSecretCreateDto payload,
  ) async {
    lastSavedSecret = payload;
    return Right(
      TenantSecretResponseDto(
        id: 'sec_01960000000070008000000000000002',
        organizationId: orgId,
        scope: payload.scope,
        targetIdentifier: payload.targetIdentifier,
        storageMode: SecretStorageMode.envelopeKms,
        configured: true,
        maskedHint: '****9999',
        kekVersion: 'v1',
        updatedAt: DateTime.utc(2026, 11, 2),
      ),
    );
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _FakeExecutionClient implements ExecutionClient {
  @override
  Future<List<ExecutionAssignmentResponseDto>> listAssignments({
    String? batchId,
  }) async {
    return [
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
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

Widget _buildIamViewForRole({
  required User user,
  required _FakeUserRepository userRepo,
  required _FakeExecutionClient execClient,
}) {
  return ProviderScope(
    key: UniqueKey(),
    overrides: [
      authControllerProvider.overrideWith(() => _StubAuthController(user)),
      userRepositoryProvider.overrideWithValue(userRepo),
      executionClientProvider.overrideWithValue(execClient),
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
