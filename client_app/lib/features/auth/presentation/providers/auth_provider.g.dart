// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Authentication Stream Provider**
///
/// Listens to the real-time authentication state changes from Firebase Auth.
///
/// **Business Logic**:
/// - This is the "Heartbeat" of the app's identity system.
/// - It emits [User] (Firebase definition) when logged in, and `null` when logged out.
/// - The Router listens to this provider to trigger redirects (e.g., kicking a user out
///   to the login screen immediately upon logout).

@ProviderFor(authState)
final authStateProvider = AuthStateProvider._();

/// **Authentication Stream Provider**
///
/// Listens to the real-time authentication state changes from Firebase Auth.
///
/// **Business Logic**:
/// - This is the "Heartbeat" of the app's identity system.
/// - It emits [User] (Firebase definition) when logged in, and `null` when logged out.
/// - The Router listens to this provider to trigger redirects (e.g., kicking a user out
///   to the login screen immediately upon logout).

final class AuthStateProvider
    extends $FunctionalProvider<AsyncValue<User?>, User?, Stream<User?>>
    with $FutureModifier<User?>, $StreamProvider<User?> {
  /// **Authentication Stream Provider**
  ///
  /// Listens to the real-time authentication state changes from Firebase Auth.
  ///
  /// **Business Logic**:
  /// - This is the "Heartbeat" of the app's identity system.
  /// - It emits [User] (Firebase definition) when logged in, and `null` when logged out.
  /// - The Router listens to this provider to trigger redirects (e.g., kicking a user out
  ///   to the login screen immediately upon logout).
  AuthStateProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'authStateProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$authStateHash();

  @$internal
  @override
  $StreamProviderElement<User?> $createElement($ProviderPointer pointer) =>
      $StreamProviderElement(pointer);

  @override
  Stream<User?> create(Ref ref) {
    return authState(ref);
  }
}

String _$authStateHash() => r'd5770286de15bb7b75b291d0fdc7a367b07650f6';
