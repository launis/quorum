// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user_role_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(userRole)
final userRoleProvider = UserRoleProvider._();

final class UserRoleProvider
    extends $FunctionalProvider<UserRole, UserRole, UserRole>
    with $Provider<UserRole> {
  UserRoleProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'userRoleProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$userRoleHash();

  @$internal
  @override
  $ProviderElement<UserRole> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  UserRole create(Ref ref) {
    return userRole(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(UserRole value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<UserRole>(value),
    );
  }
}

String _$userRoleHash() => r'b3aaf5455c780d74b893f240e8dea5e0402d7133';
