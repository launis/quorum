import 'dart:async';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/features/admin/data/admin_repository.dart';
import 'package:client_app/features/admin/domain/models/queue_stats.dart';
import 'package:client_app/features/auth/domain/models/user.dart';

part 'admin_providers.g.dart';

/// **Organization Users Provider**
///
/// Fetches the list of users for a given organization.
/// Used in the User Management screen.
@Riverpod(keepAlive: true)
Future<List<User>> orgUsers(Ref ref, String orgId) async {
  final repository = ref.watch(adminRepositoryProvider);
  final result = await repository.getUsersByOrganization(orgId);

  return result.fold((error) => throw error, (users) => users);
}

/// **System Queue Stats Provider**
///
/// Polls the backend for queue statistics every 5 seconds.
/// Used in the Dashboard or Admin Panel header.
@riverpod
Stream<QueueStats> systemQueueStats(Ref ref) {
  final repository = ref.watch(adminRepositoryProvider);

  return Stream.periodic(const Duration(seconds: 5), (tick) {
    // Defines the tick, operation happens inside asyncMap or manual fetch
    return tick;
  }).asyncMap((_) async {
    final result = await repository.getQueueStats();
    return result.fold(
      (error) => throw error, // Stream will emit error event
      (stats) => stats,
    );
  });
}

/// **User Role Controller**
///
/// Manages the state of role update operations.
/// Handles the `updateUserRole` logic and invalidates the user list on success.
@riverpod
class UserRoleController extends _$UserRoleController {
  @override
  FutureOr<void> build() {
    // Initial state is void (idle)
  }

  /// **Update Role**
  ///
  /// Calls the repository to update the user's role.
  /// On success, refreshes the [orgUsersProvider] for the relevant organization.
  Future<void> updateRole({
    required String userId,
    required String newRole,
    required String orgId,
  }) async {
    state = const AsyncLoading();

    final repository = ref.read(adminRepositoryProvider);
    final result = await repository.updateUserRole(userId, newRole);

    result.fold((error) => state = AsyncError(error, StackTrace.current), (_) {
      // Success: Refresh the user list
      ref.invalidate(orgUsersProvider(orgId));
      state = const AsyncData(null);
    });
  }
}
