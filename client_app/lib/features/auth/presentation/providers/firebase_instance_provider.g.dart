// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'firebase_instance_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Firebase Auth Instance Provider**
///
/// Centralizes access to the `FirebaseAuth` instance.
/// Wraps initialization in a try-catch block to support Mock/Offline modes causing
/// "NonInitializedError" when Firebase is not active.
///
/// **Returns**:
/// - [FirebaseAuth] instance if initialized.
/// - `null` if Firebase is missing/failed.

@ProviderFor(firebaseAuthInstance)
final firebaseAuthInstanceProvider = FirebaseAuthInstanceProvider._();

/// **Firebase Auth Instance Provider**
///
/// Centralizes access to the `FirebaseAuth` instance.
/// Wraps initialization in a try-catch block to support Mock/Offline modes causing
/// "NonInitializedError" when Firebase is not active.
///
/// **Returns**:
/// - [FirebaseAuth] instance if initialized.
/// - `null` if Firebase is missing/failed.

final class FirebaseAuthInstanceProvider
    extends $FunctionalProvider<FirebaseAuth?, FirebaseAuth?, FirebaseAuth?>
    with $Provider<FirebaseAuth?> {
  /// **Firebase Auth Instance Provider**
  ///
  /// Centralizes access to the `FirebaseAuth` instance.
  /// Wraps initialization in a try-catch block to support Mock/Offline modes causing
  /// "NonInitializedError" when Firebase is not active.
  ///
  /// **Returns**:
  /// - [FirebaseAuth] instance if initialized.
  /// - `null` if Firebase is missing/failed.
  FirebaseAuthInstanceProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'firebaseAuthInstanceProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$firebaseAuthInstanceHash();

  @$internal
  @override
  $ProviderElement<FirebaseAuth?> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  FirebaseAuth? create(Ref ref) {
    return firebaseAuthInstance(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(FirebaseAuth? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<FirebaseAuth?>(value),
    );
  }
}

String _$firebaseAuthInstanceHash() =>
    r'9c205f4fc9d510f362c60970ec8597d6a98bce4f';
