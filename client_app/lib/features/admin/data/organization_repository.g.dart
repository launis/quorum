// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization_repository.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(organizationRepository)
final organizationRepositoryProvider = OrganizationRepositoryProvider._();

final class OrganizationRepositoryProvider
    extends
        $FunctionalProvider<
          OrganizationRepository,
          OrganizationRepository,
          OrganizationRepository
        >
    with $Provider<OrganizationRepository> {
  OrganizationRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'organizationRepositoryProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$organizationRepositoryHash();

  @$internal
  @override
  $ProviderElement<OrganizationRepository> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  OrganizationRepository create(Ref ref) {
    return organizationRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(OrganizationRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<OrganizationRepository>(value),
    );
  }
}

String _$organizationRepositoryHash() =>
    r'edc75f46b96cc7e3c3470cb1412e4864f6ad9fed';
