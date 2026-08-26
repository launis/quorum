// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'mcp_gateways_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Controller managing the MCP Gateways strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

@ProviderFor(McpGatewaysController)
final mcpGatewaysControllerProvider = McpGatewaysControllerProvider._();

/// Controller managing the MCP Gateways strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
final class McpGatewaysControllerProvider
    extends
        $AsyncNotifierProvider<
          McpGatewaysController,
          List<Map<String, dynamic>>
        > {
  /// Controller managing the MCP Gateways strictly using `Map<String, dynamic>`.
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
    r'511b7e4dacf2e759add24319a779fe7fab6d0d19';

/// Controller managing the MCP Gateways strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

abstract class _$McpGatewaysController
    extends $AsyncNotifier<List<Map<String, dynamic>>> {
  FutureOr<List<Map<String, dynamic>>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<List<Map<String, dynamic>>>,
              List<Map<String, dynamic>>
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<List<Map<String, dynamic>>>,
                List<Map<String, dynamic>>
              >,
              AsyncValue<List<Map<String, dynamic>>>,
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
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>
        >
    with
        $FutureModifier<Map<String, dynamic>>,
        $FutureProvider<Map<String, dynamic>> {
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
  $FutureProviderElement<Map<String, dynamic>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<Map<String, dynamic>> create(Ref ref) {
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

String _$mcpGatewayByIdHash() => r'2f60b17d0fd6b12c7588177f8bb6845de1baac23';

/// Fetches a single MCP Gateway natively by ID

final class McpGatewayByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Map<String, dynamic>>, String> {
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
    extends $AsyncNotifierProvider<McpGatewayForm, Map<String, dynamic>> {
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

String _$mcpGatewayFormHash() => r'2b6c84b9d8d1cee7cae4e1c113c5ceef1a53ea6e';

final class McpGatewayFormFamily extends $Family
    with
        $ClassFamilyOverride<
          McpGatewayForm,
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>,
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

abstract class _$McpGatewayForm extends $AsyncNotifier<Map<String, dynamic>> {
  late final _$args = ref.$arg as String;
  String get gatewayId => _$args;

  FutureOr<Map<String, dynamic>> build(String gatewayId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<AsyncValue<Map<String, dynamic>>, Map<String, dynamic>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<Map<String, dynamic>>,
                Map<String, dynamic>
              >,
              AsyncValue<Map<String, dynamic>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}
