import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/providers/mock_auth_provider.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'auth_controller.g.dart';

/// **Authentication Controller**
///
/// Manages the global authentication state of the application.
@riverpod
class AuthController extends _$AuthController {
  @override
  Stream<User?> build() {
    // 1. Listen to Firebase Auth State
    final authStream = ref.watch(authRepositoryProvider).authStateChanges();
    // 2. Listen to Mock Token
    final mockToken = ref.watch(mockTokenProvider);

    // If Mock Token is present, we prioritize it (or treat as logged in)
    // However, the stream logic handles async mapping.
    // Efficient way:
    // If mockToken is set, we immediately fetch profile and return user.
    // Else, we listen to Firebase.

    if (mockToken != null) {
      // Trigger a fetch!
      return Stream.fromFuture(
        ref.read(userRepositoryProvider).fetchCurrentUser(),
      );
    }

    // 2. Map Firebase User -> Backend User Profile
    return authStream.asyncMap((firebaseUser) async {
      if (firebaseUser == null) return null;

      try {
        // Fetch authoritative profile from backend
        // Note: The AuthInterceptor will automatically attach the token from firebaseUser
        return await ref.read(userRepositoryProvider).fetchCurrentUser();
      } catch (e) {
        // If fetch fails (e.g. backend down or 401), we consider user effectively logged out
        // or in an error state. For the stream, we might return null.
        // Optional: Trigger signOut to clean up Firebase state if the account is invalid.
        return null;
      }
    });
  }

  /// **Sign In**
  ///
  /// Orchestrates the login flow:
  /// 1. Firebase Login
  /// 2. Backend Verification (via Repository)
  /// 3. State update (vi Stream)
  Future<void> signIn(String email, String password) async {
    state =
        const AsyncLoading(); // Optional: indicate loading explicitly if needed

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
  /// **Debug Only**: Log in with a mock token.
  Future<void> debugMockLogin(String uid) async {
    state = const AsyncLoading();

    // 1. Validate with Backend (Ensures user exists and backend accepts it)
    final result = await ref
        .read(authRepositoryProvider)
        .debugSignInWithMockToken(uid);

    result.fold(
      (error) {
        state = AsyncError(error, StackTrace.current);
        throw error;
      },
      (user) {
        // 2. Create the token string
        final token = 'mock-token:$uid';

        // 3. Set Global State (Triggers build() rebuild -> Stream -> User)
        ref.read(mockTokenProvider.notifier).setToken(token);
      },
    );
  }

  Future<void> signOut() async {
    // 1. Clear Mock Token
    ref.read(mockTokenProvider.notifier).setToken(null);

    // 2. Sign out of Firebase
    await ref.read(authRepositoryProvider).signOut();
  }
}
