// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_role_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
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

@ProviderFor(currentUserProfile)
final currentUserProfileProvider = CurrentUserProfileProvider._();

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

final class CurrentUserProfileProvider
    extends $FunctionalProvider<AsyncValue<User?>, User?, FutureOr<User?>>
    with $FutureModifier<User?>, $FutureProvider<User?> {
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
  CurrentUserProfileProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'currentUserProfileProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$currentUserProfileHash();

  @$internal
  @override
  $FutureProviderElement<User?> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<User?> create(Ref ref) {
    return currentUserProfile(ref);
  }
}

String _$currentUserProfileHash() =>
    r'd499a26f61dbf3a6364c392f2580027285fb990e';
