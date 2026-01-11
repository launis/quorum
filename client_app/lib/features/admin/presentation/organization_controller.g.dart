// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(OrganizationList)
final organizationListProvider = OrganizationListProvider._();

final class OrganizationListProvider
    extends $AsyncNotifierProvider<OrganizationList, List<Organization>> {
  OrganizationListProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'organizationListProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$organizationListHash();

  @$internal
  @override
  OrganizationList create() => OrganizationList();
}

String _$organizationListHash() => r'6923275a5c5b669ffffd0c1e82b9dad3a08e8a02';

abstract class _$OrganizationList extends $AsyncNotifier<List<Organization>> {
  FutureOr<List<Organization>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<List<Organization>>, List<Organization>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<Organization>>, List<Organization>>,
              AsyncValue<List<Organization>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
