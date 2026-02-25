// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'step_preview_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$StepPreviewResponseCWProxy {
  StepPreviewResponse systemInstruction(String systemInstruction);

  StepPreviewResponse userPrompt(String userPrompt);

  StepPreviewResponse agentClass(String agentClass);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `StepPreviewResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// StepPreviewResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  StepPreviewResponse call({
    String systemInstruction,
    String userPrompt,
    String agentClass,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfStepPreviewResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfStepPreviewResponse.copyWith.fieldName(...)`
class _$StepPreviewResponseCWProxyImpl implements _$StepPreviewResponseCWProxy {
  const _$StepPreviewResponseCWProxyImpl(this._value);

  final StepPreviewResponse _value;

  @override
  StepPreviewResponse systemInstruction(String systemInstruction) =>
      this(systemInstruction: systemInstruction);

  @override
  StepPreviewResponse userPrompt(String userPrompt) =>
      this(userPrompt: userPrompt);

  @override
  StepPreviewResponse agentClass(String agentClass) =>
      this(agentClass: agentClass);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `StepPreviewResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// StepPreviewResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  StepPreviewResponse call({
    Object? systemInstruction = const $CopyWithPlaceholder(),
    Object? userPrompt = const $CopyWithPlaceholder(),
    Object? agentClass = const $CopyWithPlaceholder(),
  }) {
    return StepPreviewResponse(
      systemInstruction: systemInstruction == const $CopyWithPlaceholder()
          ? _value.systemInstruction
          // ignore: cast_nullable_to_non_nullable
          : systemInstruction as String,
      userPrompt: userPrompt == const $CopyWithPlaceholder()
          ? _value.userPrompt
          // ignore: cast_nullable_to_non_nullable
          : userPrompt as String,
      agentClass: agentClass == const $CopyWithPlaceholder()
          ? _value.agentClass
          // ignore: cast_nullable_to_non_nullable
          : agentClass as String,
    );
  }
}

extension $StepPreviewResponseCopyWith on StepPreviewResponse {
  /// Returns a callable class that can be used as follows: `instanceOfStepPreviewResponse.copyWith(...)` or like so:`instanceOfStepPreviewResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$StepPreviewResponseCWProxy get copyWith =>
      _$StepPreviewResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

StepPreviewResponse _$StepPreviewResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'StepPreviewResponse',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const [
            'system_instruction',
            'user_prompt',
            'agent_class',
          ],
        );
        final val = StepPreviewResponse(
          systemInstruction: $checkedConvert(
            'system_instruction',
            (v) => v as String,
          ),
          userPrompt: $checkedConvert('user_prompt', (v) => v as String),
          agentClass: $checkedConvert('agent_class', (v) => v as String),
        );
        return val;
      },
      fieldKeyMap: const {
        'systemInstruction': 'system_instruction',
        'userPrompt': 'user_prompt',
        'agentClass': 'agent_class',
      },
    );

Map<String, dynamic> _$StepPreviewResponseToJson(
  StepPreviewResponse instance,
) => <String, dynamic>{
  'system_instruction': instance.systemInstruction,
  'user_prompt': instance.userPrompt,
  'agent_class': instance.agentClass,
};
