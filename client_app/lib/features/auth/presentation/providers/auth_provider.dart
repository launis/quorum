import 'package:firebase_auth/firebase_auth.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/features/auth/presentation/providers/firebase_instance_provider.dart';

part 'auth_provider.g.dart';

/// **Authentication Stream Provider**
///
/// Listens to the real-time authentication state changes from Firebase Auth.
///
/// **Business Logic**:
/// - This is the "Heartbeat" of the app's identity system.
/// - It emits [User] (Firebase definition) when logged in, and `null` when logged out.
/// - The Router listens to this provider to trigger redirects (e.g., kicking a user out
///   to the login screen immediately upon logout).
@riverpod
Stream<User?> authState(Ref ref) {
  final auth = ref.watch(firebaseAuthInstanceProvider);
  if (auth == null) return Stream.value(null);
  return auth.authStateChanges();
}
