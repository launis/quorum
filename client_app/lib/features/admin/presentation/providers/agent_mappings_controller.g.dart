// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'agent_mappings_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(AgentMappingsController)
final agentMappingsControllerProvider = AgentMappingsControllerProvider._();

final class AgentMappingsControllerProvider
    extends
        $AsyncNotifierProvider<
          AgentMappingsController,
          Map<String, ({String name, String? strategyId})>
        > {
  AgentMappingsControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'agentMappingsControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$agentMappingsControllerHash();

  @$internal
  @override
  AgentMappingsController create() => AgentMappingsController();
}

String _$agentMappingsControllerHash() =>
    r'cdb95246986fca5af27906c08bae2d8500b00b6d';

abstract class _$AgentMappingsController
    extends $AsyncNotifier<Map<String, ({String name, String? strategyId})>> {
  FutureOr<Map<String, ({String name, String? strategyId})>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<Map<String, ({String name, String? strategyId})>>,
              Map<String, ({String name, String? strategyId})>
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<Map<String, ({String name, String? strategyId})>>,
                Map<String, ({String name, String? strategyId})>
              >,
              AsyncValue<Map<String, ({String name, String? strategyId})>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
