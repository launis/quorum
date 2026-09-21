// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'mcp_gateways_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Controller managing the MCP Gateways strictly using immutable Freezed models.
/// Implements Optimistic UI principles where possible.

@ProviderFor(McpGatewaysController)
final mcpGatewaysControllerProvider = McpGatewaysControllerProvider._();

/// Controller managing the MCP Gateways strictly using immutable Freezed models.
/// Implements Optimistic UI principles where possible.
final class McpGatewaysControllerProvider
    extends $AsyncNotifierProvider<McpGatewaysController, List<McpGateway>> {
  /// Controller managing the MCP Gateways strictly using immutable Freezed models.
  /// Implements Optimistic UI principles where possible.
  McpGatewaysControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'mcpGatewaysControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$mcpGatewaysControllerHash();

  @$internal
  @override
  McpGatewaysController create() => McpGatewaysController();
}

String _$mcpGatewaysControllerHash() =>
    r'708b01bdc76d4e830bdc0f815e2aaba293ca7e53';

/// Controller managing the MCP Gateways strictly using immutable Freezed models.
/// Implements Optimistic UI principles where possible.

abstract class _$McpGatewaysController
    extends $AsyncNotifier<List<McpGateway>> {
  FutureOr<List<McpGateway>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<List<McpGateway>>, List<McpGateway>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<McpGateway>>, List<McpGateway>>,
              AsyncValue<List<McpGateway>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// Fetches a single MCP Gateway natively by ID

@ProviderFor(mcpGatewayById)
final mcpGatewayByIdProvider = McpGatewayByIdFamily._();

/// Fetches a single MCP Gateway natively by ID

final class McpGatewayByIdProvider
    extends
        $FunctionalProvider<
          AsyncValue<McpGateway>,
          McpGateway,
          FutureOr<McpGateway>
        >
    with $FutureModifier<McpGateway>, $FutureProvider<McpGateway> {
  /// Fetches a single MCP Gateway natively by ID
  McpGatewayByIdProvider._({
    required McpGatewayByIdFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'mcpGatewayByIdProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$mcpGatewayByIdHash();

  @override
  String toString() {
    return r'mcpGatewayByIdProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<McpGateway> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<McpGateway> create(Ref ref) {
    final argument = this.argument as String;
    return mcpGatewayById(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is McpGatewayByIdProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$mcpGatewayByIdHash() => r'7132534f0c48cc702979df5800d26a0484f00634';

/// Fetches a single MCP Gateway natively by ID

final class McpGatewayByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<McpGateway>, String> {
  McpGatewayByIdFamily._()
    : super(
        retry: null,
        name: r'mcpGatewayByIdProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches a single MCP Gateway natively by ID

  McpGatewayByIdProvider call(String id) =>
      McpGatewayByIdProvider._(argument: id, from: this);

  @override
  String toString() => r'mcpGatewayByIdProvider';
}

@ProviderFor(McpGatewayForm)
final mcpGatewayFormProvider = McpGatewayFormFamily._();

final class McpGatewayFormProvider
    extends $AsyncNotifierProvider<McpGatewayForm, McpGateway> {
  McpGatewayFormProvider._({
    required McpGatewayFormFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'mcpGatewayFormProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$mcpGatewayFormHash();

  @override
  String toString() {
    return r'mcpGatewayFormProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  McpGatewayForm create() => McpGatewayForm();

  @override
  bool operator ==(Object other) {
    return other is McpGatewayFormProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$mcpGatewayFormHash() => r'677dec4bc474bcb3a92b078bec0e3d3f10d0719b';

final class McpGatewayFormFamily extends $Family
    with
        $ClassFamilyOverride<
          McpGatewayForm,
          AsyncValue<McpGateway>,
          McpGateway,
          FutureOr<McpGateway>,
          String
        > {
  McpGatewayFormFamily._()
    : super(
        retry: null,
        name: r'mcpGatewayFormProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  McpGatewayFormProvider call(String gatewayId) =>
      McpGatewayFormProvider._(argument: gatewayId, from: this);

  @override
  String toString() => r'mcpGatewayFormProvider';
}

abstract class _$McpGatewayForm extends $AsyncNotifier<McpGateway> {
  late final _$args = ref.$arg as String;
  String get gatewayId => _$args;

  FutureOr<McpGateway> build(String gatewayId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<McpGateway>, McpGateway>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<McpGateway>, McpGateway>,
              AsyncValue<McpGateway>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
