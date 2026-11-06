// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization_iam_settings_view.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(availableMcpGateways)
final availableMcpGatewaysProvider = AvailableMcpGatewaysProvider._();

final class AvailableMcpGatewaysProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<McpGateway>>,
          List<McpGateway>,
          FutureOr<List<McpGateway>>
        >
    with $FutureModifier<List<McpGateway>>, $FutureProvider<List<McpGateway>> {
  AvailableMcpGatewaysProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'availableMcpGatewaysProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$availableMcpGatewaysHash();

  @$internal
  @override
  $FutureProviderElement<List<McpGateway>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<McpGateway>> create(Ref ref) {
    return availableMcpGateways(ref);
  }
}

String _$availableMcpGatewaysHash() =>
    r'1d646403e8d7213f924d688b4aa5ca0f3124ce6b';

@ProviderFor(availableOrganizations)
final availableOrganizationsProvider = AvailableOrganizationsProvider._();

final class AvailableOrganizationsProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<Organization>>,
          List<Organization>,
          FutureOr<List<Organization>>
        >
    with
        $FutureModifier<List<Organization>>,
        $FutureProvider<List<Organization>> {
  AvailableOrganizationsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'availableOrganizationsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$availableOrganizationsHash();

  @$internal
  @override
  $FutureProviderElement<List<Organization>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<Organization>> create(Ref ref) {
    return availableOrganizations(ref);
  }
}

String _$availableOrganizationsHash() =>
    r'606a98fd4b45e0a11c05644ebed2c35d5270992b';

@ProviderFor(organizationProfile)
final organizationProfileProvider = OrganizationProfileFamily._();

final class OrganizationProfileProvider
    extends
        $FunctionalProvider<
          AsyncValue<Organization>,
          Organization,
          FutureOr<Organization>
        >
    with $FutureModifier<Organization>, $FutureProvider<Organization> {
  OrganizationProfileProvider._({
    required OrganizationProfileFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'organizationProfileProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$organizationProfileHash();

  @override
  String toString() {
    return r'organizationProfileProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<Organization> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<Organization> create(Ref ref) {
    final argument = this.argument as String;
    return organizationProfile(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is OrganizationProfileProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$organizationProfileHash() =>
    r'720cb45bdbccb1040c3a31bac8944a1d7a6b9fc8';

final class OrganizationProfileFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Organization>, String> {
  OrganizationProfileFamily._()
    : super(
        retry: null,
        name: r'organizationProfileProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  OrganizationProfileProvider call(String orgId) =>
      OrganizationProfileProvider._(argument: orgId, from: this);

  @override
  String toString() => r'organizationProfileProvider';
}

@ProviderFor(organizationAssignments)
final organizationAssignmentsProvider = OrganizationAssignmentsProvider._();

final class OrganizationAssignmentsProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<ExecutionAssignmentResponseDto>>,
          List<ExecutionAssignmentResponseDto>,
          FutureOr<List<ExecutionAssignmentResponseDto>>
        >
    with
        $FutureModifier<List<ExecutionAssignmentResponseDto>>,
        $FutureProvider<List<ExecutionAssignmentResponseDto>> {
  OrganizationAssignmentsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'organizationAssignmentsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$organizationAssignmentsHash();

  @$internal
  @override
  $FutureProviderElement<List<ExecutionAssignmentResponseDto>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<ExecutionAssignmentResponseDto>> create(Ref ref) {
    return organizationAssignments(ref);
  }
}

String _$organizationAssignmentsHash() =>
    r'6ac82fd238913aee444f446f5e301fb5978a42e5';

@ProviderFor(organizationInvitations)
final organizationInvitationsProvider = OrganizationInvitationsFamily._();

final class OrganizationInvitationsProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<InvitationResponseDto>>,
          List<InvitationResponseDto>,
          FutureOr<List<InvitationResponseDto>>
        >
    with
        $FutureModifier<List<InvitationResponseDto>>,
        $FutureProvider<List<InvitationResponseDto>> {
  OrganizationInvitationsProvider._({
    required OrganizationInvitationsFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'organizationInvitationsProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$organizationInvitationsHash();

  @override
  String toString() {
    return r'organizationInvitationsProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<List<InvitationResponseDto>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<InvitationResponseDto>> create(Ref ref) {
    final argument = this.argument as String;
    return organizationInvitations(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is OrganizationInvitationsProvider &&
        other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$organizationInvitationsHash() =>
    r'ff8411e981aba90931248a056daca3fb3ed34c7a';

final class OrganizationInvitationsFamily extends $Family
    with
        $FunctionalFamilyOverride<
          FutureOr<List<InvitationResponseDto>>,
          String
        > {
  OrganizationInvitationsFamily._()
    : super(
        retry: null,
        name: r'organizationInvitationsProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  OrganizationInvitationsProvider call(String orgId) =>
      OrganizationInvitationsProvider._(argument: orgId, from: this);

  @override
  String toString() => r'organizationInvitationsProvider';
}

@ProviderFor(organizationMembers)
final organizationMembersProvider = OrganizationMembersProvider._();

final class OrganizationMembersProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<User>>,
          List<User>,
          FutureOr<List<User>>
        >
    with $FutureModifier<List<User>>, $FutureProvider<List<User>> {
  OrganizationMembersProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'organizationMembersProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$organizationMembersHash();

  @$internal
  @override
  $FutureProviderElement<List<User>> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<List<User>> create(Ref ref) {
    return organizationMembers(ref);
  }
}

String _$organizationMembersHash() =>
    r'526ade184e334a5112f9f8d0bcfcad11608c08e6';

@ProviderFor(organizationSecrets)
final organizationSecretsProvider = OrganizationSecretsFamily._();

final class OrganizationSecretsProvider
    extends
        $FunctionalProvider<
          AsyncValue<List<TenantSecretResponseDto>>,
          List<TenantSecretResponseDto>,
          FutureOr<List<TenantSecretResponseDto>>
        >
    with
        $FutureModifier<List<TenantSecretResponseDto>>,
        $FutureProvider<List<TenantSecretResponseDto>> {
  OrganizationSecretsProvider._({
    required OrganizationSecretsFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'organizationSecretsProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$organizationSecretsHash();

  @override
  String toString() {
    return r'organizationSecretsProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<List<TenantSecretResponseDto>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<List<TenantSecretResponseDto>> create(Ref ref) {
    final argument = this.argument as String;
    return organizationSecrets(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is OrganizationSecretsProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$organizationSecretsHash() =>
    r'09e7ec86175ca43adb929986593cc4632caafec0';

final class OrganizationSecretsFamily extends $Family
    with
        $FunctionalFamilyOverride<
          FutureOr<List<TenantSecretResponseDto>>,
          String
        > {
  OrganizationSecretsFamily._()
    : super(
        retry: null,
        name: r'organizationSecretsProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  OrganizationSecretsProvider call(String orgId) =>
      OrganizationSecretsProvider._(argument: orgId, from: this);

  @override
  String toString() => r'organizationSecretsProvider';
}
