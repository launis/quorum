// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'admin_repository.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Admin Repository**
///
/// Handles data operations for the Admin Panel.
/// Strictly follows the functional error handling pattern using [Either].
///
/// **Dependencies**:
/// - ApiClient: For making HTTP requests.

@ProviderFor(adminRepository)
final adminRepositoryProvider = AdminRepositoryProvider._();

/// **Admin Repository**
///
/// Handles data operations for the Admin Panel.
/// Strictly follows the functional error handling pattern using [Either].
///
/// **Dependencies**:
/// - ApiClient: For making HTTP requests.

final class AdminRepositoryProvider
    extends
        $FunctionalProvider<AdminRepository, AdminRepository, AdminRepository>
    with $Provider<AdminRepository> {
  /// **Admin Repository**
  ///
  /// Handles data operations for the Admin Panel.
  /// Strictly follows the functional error handling pattern using [Either].
  ///
  /// **Dependencies**:
  /// - ApiClient: For making HTTP requests.
  AdminRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'adminRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$adminRepositoryHash();

  @$internal
  @override
  $ProviderElement<AdminRepository> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  AdminRepository create(Ref ref) {
    return adminRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AdminRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AdminRepository>(value),
    );
  }
}

String _$adminRepositoryHash() => r'f2f0ea1b844e9c3ad5e562dd8c89e24a2122aa3e';
