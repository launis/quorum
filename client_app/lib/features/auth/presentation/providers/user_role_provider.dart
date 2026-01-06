import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/providers/auth_provider.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'user_role_provider.g.dart';

/// **User Role Provider (The Brain)**
///
/// Determines the effective [UserRole] of the currently signed-in user by syncing
/// with the backend.
///
/// **Business Logic**:
/// 1.  **Watch Auth**: Listens to [authStateProvider]. If no user is signed in, returns `null`.
/// 2.  **Fetch Profile**: If a user exists, it calls [UserRepository.fetchCurrentUser].
/// 3.  **Caching**: Riverpod caches this future, preventing redundant API calls on rebuilds.
/// 4.  **Security**: The Router uses *this* specific provider (not just authState) to
///     decide if the user can enter `/admin`.
///
/// **Returns**:
/// - [AsyncValue.data(User)] if authenticated and profile loaded.
/// - [AsyncValue.loading] while fetching profile.
/// - [AsyncValue.error] if backend sync fails (Router should handle "Access Denied" or Retry).
/// - `null` (conceptually, or error) if logged out.
@riverpod
Future<User?> currentUserProfile(Ref ref) async {
  // 1. Check basic Auth State
  final authUser = await ref.watch(authStateProvider.future);
  if (authUser == null) {
    return null;
  }

  // 2. Sync with Backend to get Role
  // The 'authState' provider gives us the Firebase User (identity).
  // The 'userRepository' gives us the Domain User (permissions).
  final repo = ref.watch(userRepositoryProvider);
  return repo.fetchCurrentUser();
}
