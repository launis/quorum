// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'agent_run_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$AgentRunResponseCWProxy {
  AgentRunResponse agent(String agent);

  AgentRunResponse result(Object? result);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AgentRunResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AgentRunResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AgentRunResponse call({String agent, Object? result});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfAgentRunResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfAgentRunResponse.copyWith.fieldName(...)`
class _$AgentRunResponseCWProxyImpl implements _$AgentRunResponseCWProxy {
  const _$AgentRunResponseCWProxyImpl(this._value);

  final AgentRunResponse _value;

  @override
  AgentRunResponse agent(String agent) => this(agent: agent);

  @override
  AgentRunResponse result(Object? result) => this(result: result);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AgentRunResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AgentRunResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AgentRunResponse call({
    Object? agent = const $CopyWithPlaceholder(),
    Object? result = const $CopyWithPlaceholder(),
  }) {
    return AgentRunResponse(
      agent: agent == const $CopyWithPlaceholder()
          ? _value.agent
          // ignore: cast_nullable_to_non_nullable
          : agent as String,
      result: result == const $CopyWithPlaceholder()
          ? _value.result
          // ignore: cast_nullable_to_non_nullable
          : result as Object?,
    );
  }
}

extension $AgentRunResponseCopyWith on AgentRunResponse {
  /// Returns a callable class that can be used as follows: `instanceOfAgentRunResponse.copyWith(...)` or like so:`instanceOfAgentRunResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$AgentRunResponseCWProxy get copyWith => _$AgentRunResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AgentRunResponse _$AgentRunResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('AgentRunResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['agent', 'result']);
      final val = AgentRunResponse(
        agent: $checkedConvert('agent', (v) => v as String),
        result: $checkedConvert('result', (v) => v),
      );
      return val;
    });

Map<String, dynamic> _$AgentRunResponseToJson(AgentRunResponse instance) =>
    <String, dynamic>{'agent': instance.agent, 'result': instance.result};
