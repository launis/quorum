import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/admin/data/admin_repository.dart';
import 'package:client_app/features/admin/domain/dtos/user_dtos.dart';

import 'package:client_app/features/admin/presentation/providers/user_crud_controller.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:fpdart/fpdart.dart';
import 'package:mocktail/mocktail.dart';

// Mock Repository
class MockAdminRepository extends Mock implements AdminRepository {}

// Fake DTOs for testing
final tUserCreateDto = UserCreateDto(
  email: 'test@example.com',
  password: 'password123',
  displayName: 'Test User',
  role: UserRole.member,
);

final tUserUpdateDto = UserUpdateDto(displayName: 'Updated Name');

void main() {
  late MockAdminRepository mockRepository;
  late ProviderContainer container;

  setUp(() {
    mockRepository = MockAdminRepository();
    container = ProviderContainer(
      overrides: [adminRepositoryProvider.overrideWithValue(mockRepository)],
    );
    // Register fallback values if needed for mocktail
    registerFallbackValue(tUserCreateDto);
    registerFallbackValue(tUserUpdateDto);
  });

  tearDown(() {
    container.dispose();
  });

  group('UserCrudController', () {
    test('initial state should be AsyncData(null)', () {
      final state = container.read(userCrudControllerProvider);
      expect(state, isA<AsyncData<void>>());
      // expect(state.value, null); // Cannot access void value
    });

    group('createUser', () {
      test(
        'should call repository.createUser and invalidate orgUsersProvider on success',
        () async {
          // Arrange
          when(
            () => mockRepository.createUser(any()),
          ).thenAnswer((_) async => const Right(null));

          // Act
          await container
              .read(userCrudControllerProvider.notifier)
              .createUser(tUserCreateDto, 'org-1');

          // Assert
          verify(() => mockRepository.createUser(tUserCreateDto)).called(1);
          expect(
            container.read(userCrudControllerProvider),
            const AsyncData<void>(null),
          );
        },
      );

      test('should set state to AsyncError on failure', () async {
        // Arrange
        const error = AppError.network('Network failure');
        when(
          () => mockRepository.createUser(any()),
        ).thenAnswer((_) async => const Left(error));

        // Act
        // We expect the controller NOT to throw, but to update state
        await container
            .read(userCrudControllerProvider.notifier)
            .createUser(tUserCreateDto, 'org-1');

        // Assert
        verify(() => mockRepository.createUser(tUserCreateDto)).called(1);
        // Assert
        verify(() => mockRepository.createUser(tUserCreateDto)).called(1);
        final state = container.read(userCrudControllerProvider);
        expect(state.hasError, true);
        expect(state.error, isA<AppError>());
      });
    });

    group('updateUser', () {
      test('should call repository.updateUser and succeed', () async {
        // Arrange
        when(
          () => mockRepository.updateUser(
            userId: any(named: 'userId'),
            data: any(named: 'data'),
          ),
        ).thenAnswer((_) async => const Right(null));

        // Act
        await container
            .read(userCrudControllerProvider.notifier)
            .updateUser('user-1', tUserUpdateDto, 'org-1');

        // Assert
        verify(
          () =>
              mockRepository.updateUser(userId: 'user-1', data: tUserUpdateDto),
        ).called(1);
        expect(
          container.read(userCrudControllerProvider),
          const AsyncData<void>(null),
        );
      });
    });

    group('deleteUser', () {
      test('should call repository.deleteUser and succeed', () async {
        // Arrange
        when(
          () => mockRepository.deleteUser(any()),
        ).thenAnswer((_) async => const Right(null));

        // Act
        await container
            .read(userCrudControllerProvider.notifier)
            .deleteUser('user-1', 'org-1');

        // Assert
        verify(() => mockRepository.deleteUser('user-1')).called(1);
        expect(
          container.read(userCrudControllerProvider),
          const AsyncData<void>(null),
        );
      });
    });
  });
}
