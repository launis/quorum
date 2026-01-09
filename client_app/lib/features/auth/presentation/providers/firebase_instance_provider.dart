import 'package:firebase_auth/firebase_auth.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'firebase_instance_provider.g.dart';

/// **Firebase Auth Instance Provider**
///
/// Centralizes access to the `FirebaseAuth` instance.
/// Wraps initialization in a try-catch block to support Mock/Offline modes causing
/// "NonInitializedError" when Firebase is not active.
///
/// **Returns**:
/// - [FirebaseAuth] instance if initialized.
/// - `null` if Firebase is missing/failed.
@riverpod
FirebaseAuth? firebaseAuthInstance(Ref ref) {
  try {
    return FirebaseAuth.instance;
  } catch (_) {
    return null;
  }
}
