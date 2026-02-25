// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'usage_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(SystemUsageController)
final systemUsageControllerProvider = SystemUsageControllerProvider._();

final class SystemUsageControllerProvider
    extends $AsyncNotifierProvider<SystemUsageController, UsageReport> {
  SystemUsageControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'systemUsageControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$systemUsageControllerHash();

  @$internal
  @override
  SystemUsageController create() => SystemUsageController();
}

String _$systemUsageControllerHash() =>
    r'a22427670670818d22d92781b928aa93402ef663';

abstract class _$SystemUsageController extends $AsyncNotifier<UsageReport> {
  FutureOr<UsageReport> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<UsageReport>, UsageReport>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<UsageReport>, UsageReport>,
              AsyncValue<UsageReport>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

@ProviderFor(OrganizationUsageController)
final organizationUsageControllerProvider =
    OrganizationUsageControllerFamily._();

final class OrganizationUsageControllerProvider
    extends $AsyncNotifierProvider<OrganizationUsageController, UsageReport> {
  OrganizationUsageControllerProvider._({
    required OrganizationUsageControllerFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'organizationUsageControllerProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$organizationUsageControllerHash();

  @override
  String toString() {
    return r'organizationUsageControllerProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  OrganizationUsageController create() => OrganizationUsageController();

  @override
  bool operator ==(Object other) {
    return other is OrganizationUsageControllerProvider &&
        other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$organizationUsageControllerHash() =>
    r'b0bb054435ecf1d4decc4e40fa9f09e4c03c2a01';

final class OrganizationUsageControllerFamily extends $Family
    with
        $ClassFamilyOverride<
          OrganizationUsageController,
          AsyncValue<UsageReport>,
          UsageReport,
          FutureOr<UsageReport>,
          String
        > {
  OrganizationUsageControllerFamily._()
    : super(
        retry: null,
        name: r'organizationUsageControllerProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  OrganizationUsageControllerProvider call(String orgId) =>
      OrganizationUsageControllerProvider._(argument: orgId, from: this);

  @override
  String toString() => r'organizationUsageControllerProvider';
}

abstract class _$OrganizationUsageController
    extends $AsyncNotifier<UsageReport> {
  late final _$args = ref.$arg as String;
  String get orgId => _$args;

  FutureOr<UsageReport> build(String orgId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<UsageReport>, UsageReport>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<UsageReport>, UsageReport>,
              AsyncValue<UsageReport>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}

@ProviderFor(UserUsageController)
final userUsageControllerProvider = UserUsageControllerProvider._();

final class UserUsageControllerProvider
    extends $AsyncNotifierProvider<UserUsageController, UsageReport> {
  UserUsageControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'userUsageControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$userUsageControllerHash();

  @$internal
  @override
  UserUsageController create() => UserUsageController();
}

String _$userUsageControllerHash() =>
    r'6abd9bc45be58bde4e5f29824f0af1a95ddcaefc';

abstract class _$UserUsageController extends $AsyncNotifier<UsageReport> {
  FutureOr<UsageReport> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<UsageReport>, UsageReport>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<UsageReport>, UsageReport>,
              AsyncValue<UsageReport>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
