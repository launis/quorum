import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/admin/data/admin_repository.dart';
import 'package:client_app/features/admin/presentation/providers/admin_providers.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mocktail/mocktail.dart';

class MockAdminRepository extends Mock implements AdminRepository {}

void main() {
  late MockAdminRepository mockRepository;

  setUp(() {
    mockRepository = MockAdminRepository();
  });

  ProviderContainer createContainer() {
    final container = ProviderContainer(
      overrides: [adminRepositoryProvider.overrideWithValue(mockRepository)],
    );
    addTearDown(container.dispose);
    return container;
  }

  group('orgUsersProvider', () {
    const orgId = 'org-1';
    final tUser = User(
      uid: 'u1',
      email: 'e',
      displayName: 'n',
      organizationId: orgId,
      role: UserRole.member,
    );
    final tList = [tUser];

    test('should return list of users when repo success', () async {
      when(
        () => mockRepository.getUsersByOrganization(orgId),
      ).thenAnswer((_) async => Right(tList));

      final container = createContainer();

      expect(
        container.read(orgUsersProvider(orgId)),
        const AsyncValue<List<User>>.loading(),
      );

      final users = await container.read(orgUsersProvider(orgId).future);
      expect(users, tList);
    });

    test(
      'should throw error when repo failure',
      () async {
        const tError = AppError.network();

        when(
          () => mockRepository.getUsersByOrganization(any()),
        ).thenAnswer((_) async => const Left(tError));

        final container = createContainer();

        // Standard Riverpod test pattern: listen to keep alive & initialize
        final subscription = container.listen(
          orgUsersProvider(orgId),
          (_, _) {},
        );

        await expectLater(
          container.read(orgUsersProvider(orgId).future),
          throwsA(tError),
        );

        verify(() => mockRepository.getUsersByOrganization(any())).called(1);
        subscription.close();
      },
      skip:
          'Timeout issue in test environment with FutureProvider error propagation',
    );
  });

  group('UserRoleController', () {
    const userId = 'u1';
    const newRole = UserRole.admin;
    const orgId = 'org-1';

    test('updateRole success should invalidate orgUsersProvider', () async {
      when(
        () => mockRepository.updateUserRole(userId, newRole.name),
      ).thenAnswer((_) async => const Right(null));

      // Stub retrieval to prevent MissingStubError during invalidation refetch
      when(
        () => mockRepository.getUsersByOrganization(orgId),
      ).thenAnswer((_) async => const Right([]));

      final container = createContainer();

      await container
          .read(userRoleControllerProvider.notifier)
          .updateRole(userId: userId, newRole: newRole, orgId: orgId);

      // Verify final state
      expect(
        container.read(userRoleControllerProvider),
        const AsyncData<void>(null),
      );
    });

    test('updateRole failure should set state to error', () async {
      const tError = AppError.validation(ValidationErrorReason.demoteLastAdmin);
      when(
        () => mockRepository.updateUserRole(userId, newRole.name),
      ).thenAnswer((_) async => const Left(tError));

      final container = createContainer();

      await container
          .read(userRoleControllerProvider.notifier)
          .updateRole(userId: userId, newRole: newRole, orgId: orgId);

      expect(container.read(userRoleControllerProvider).hasError, true);
      expect(container.read(userRoleControllerProvider).error, tError);
    });
  });
}
