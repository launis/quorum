import 'dart:async';
import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/admin/data/admin_repository.dart';
import 'package:client_app/features/admin/domain/dtos/user_dtos.dart';
import 'package:client_app/features/admin/presentation/providers/admin_providers.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'user_crud_controller.g.dart';

/// **User CRUD Controller**
///
/// Manages the state of user creation, update, and deletion operations.
/// Uses riverpod_generator for type-safe provider generation.
@riverpod
class UserCrudController extends _$UserCrudController {
  @override
  FutureOr<void> build() {
    // Initial state is idle (null)
    return null;
  }

  /// **Create User**
  Future<void> createUser(UserCreateDto dto, String orgId) async {
    state = const AsyncLoading();
    final repository = ref.read(adminRepositoryProvider);
    final result = await repository.createUser(dto);

    state = result.fold(
      (AppError error) => AsyncError(error, StackTrace.current),
      (_) {
        ref.invalidate(orgUsersProvider(orgId));
        return const AsyncData(null);
      },
    );
  }

  /// **Update User**
  Future<void> updateUser(
    String userId,
    UserUpdateDto dto,
    String orgId,
  ) async {
    state = const AsyncLoading();
    final repository = ref.read(adminRepositoryProvider);
    final result = await repository.updateUser(userId: userId, data: dto);

    state = result.fold(
      (AppError error) => AsyncError(error, StackTrace.current),
      (_) {
        ref.invalidate(orgUsersProvider(orgId));
        return const AsyncData(null);
      },
    );
  }

  /// **Delete User**
  Future<void> deleteUser(String userId, String orgId) async {
    state = const AsyncLoading();
    final repository = ref.read(adminRepositoryProvider);
    final result = await repository.deleteUser(userId);

    state = result.fold(
      (AppError error) => AsyncError(error, StackTrace.current),
      (_) {
        ref.invalidate(orgUsersProvider(orgId));
        return const AsyncData(null);
      },
    );
  }
}
