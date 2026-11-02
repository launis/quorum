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
  Organization organization = const Organization(
    id: 'org_01960000000070008000000000000001',
    name: 'Quorum Enterprise Ltd',
    contactEmail: 'ops@quorum.ai',
    quotaLimit: 5000.0,
    tpmLimit: 250000,
    rpmLimit: 120,
  );
  OrganizationUpdateDto? lastUpdatedOrganization;
  TenantSecretCreateDto? lastSavedSecret;

  @override
  Future<Either<AppException, Organization>> getOrganization(
    String orgId,
  ) async {
    return Right(organization);
  }

  @override
  Future<Either<AppException, Organization>> updateOrganization(
    String orgId,
    OrganizationUpdateDto payload,
  ) async {
    lastUpdatedOrganization = payload;
    organization = organization.copyWith(
      name: payload.name ?? organization.name,
      contactEmail: payload.contactEmail ?? organization.contactEmail,
    );
    return Right(organization);
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
    return const Right([
      User(
        id: 'usr_01960000000070008000000000000001',
        email: 'admin@quorum.ai',
        role: UserRole.admin,
        organizationId: 'org_01960000000070008000000000000001',
      ),
      User(
        id: 'usr_01960000000070008000000000000002',
        email: 'member@quorum.ai',
        role: UserRole.member,
        organizationId: 'org_01960000000070008000000000000001',
      ),
    ]);
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
  });
}

class _FailingUserRepository extends _FakeUserRepository {
  @override
  Future<Either<AppException, Organization>> getOrganization(
    String orgId,
  ) async {
    return Left(
      AppException.server('Organization backend unavailable'),
    );
  }
}
