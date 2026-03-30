import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/presentation/providers/mock_user_provider.dart';
import 'dart:async';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/providers/mock_auth_provider.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'auth_controller.g.dart';

/// **Authentication Controller**
///
/// Manages the global authentication state of the application.
@riverpod
class AuthController extends _$AuthController {
  @override
  FutureOr<User?> build() async {
    // 0. Check for Mock User (Priority)
    final mockUser = ref.watch(mockUserProvider);
    if (mockUser != null) {
      return mockUser;
    }

    // 1. Await Firebase Auth state explicitly since Riverpod v2 stream watching is better
    // Wait, let's just use regular Future mapping for MVP
    final firebaseUser = await ref
        .watch(authRepositoryProvider)
        .authStateChanges()
        .first;
    if (firebaseUser == null) return null;

    final result = await ref.read(userRepositoryProvider).fetchCurrentUser();
    return result.fold((error) => null, (user) => user);
  }

  /// **Sign In**
  ///
  /// Orchestrates the login flow:
  /// 1. Firebase Login
  /// 2. Backend Verification (via Repository)
  /// 3. State update (vi Stream)
  Future<void> signIn(String email, String password) async {
    state = const AsyncLoading();

    // We delegate to repo. The stream will update automatically.
    // However, we want to await the full flow to catch errors.
    final result = await ref
        .read(authRepositoryProvider)
        .signInWithEmailAndPassword(email, password);

    result.fold(
      (error) {
        state = AsyncError(error, StackTrace.current);
        throw error; // Rethrow as requested so UI can show snackbar/dialog if it catches it
      },
      (user) {
        // Success! The stream will emit the new user automatically.
        // We don't need to manually set state here unless we want to force it.
      },
    );
  }

  /// **Debug Only**: Log in with a mock token.
  Future<void> debugMockLogin(String id) async {
    state = const AsyncLoading();

    // 1. Validate with Backend
    final result = await ref
        .read(authRepositoryProvider)
        .debugSignInWithMockToken(id);

    result.fold(
      (error) {
        state = AsyncError(error, StackTrace.current);
        throw error;
      },
      (user) {
        // 2. Set MOCK USER directly (Bypass redundant fetch)
        ref.read(mockUserProvider.notifier).setUser(user);

        // 3. Set Token for Interceptor
        final token = 'mock-token:$id';
        ref.read(mockTokenProvider.notifier).setToken(token);

        // 4. Force State Update (Ensure Router sees it immediately)
        state = AsyncData(user);
      },
    );
  }

  Future<void> signOut() async {
    // 1. Clear Mock Token
    ref.read(mockTokenProvider.notifier).setToken(null);
    ref.read(mockUserProvider.notifier).setUser(null);

    // 2. Sign out of Firebase
    await ref.read(authRepositoryProvider).signOut();
  }
}
