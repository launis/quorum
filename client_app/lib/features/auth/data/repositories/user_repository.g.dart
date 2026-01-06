// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_repository.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **User Repository Provider**
///
/// Exposes the [UserRepository] to the dependency injection system.
/// Uses the authenticated [apiClientProvider].

@ProviderFor(userRepository)
final userRepositoryProvider = UserRepositoryProvider._();

/// **User Repository Provider**
///
/// Exposes the [UserRepository] to the dependency injection system.
/// Uses the authenticated [apiClientProvider].

final class UserRepositoryProvider
    extends $FunctionalProvider<UserRepository, UserRepository, UserRepository>
    with $Provider<UserRepository> {
  /// **User Repository Provider**
  ///
  /// Exposes the [UserRepository] to the dependency injection system.
  /// Uses the authenticated [apiClientProvider].
  UserRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'userRepositoryProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$userRepositoryHash();

  @$internal
  @override
  $ProviderElement<UserRepository> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  UserRepository create(Ref ref) {
    return userRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(UserRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<UserRepository>(value),
    );
  }
}

String _$userRepositoryHash() => r'827710bacb7cd582dbf9d749c54fb446ecc85629';
