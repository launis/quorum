// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'completion_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$CompletionRequestCWProxy {
  CompletionRequest prompt(String prompt);

  CompletionRequest systemInstruction(String? systemInstruction);

  CompletionRequest modelStrategy(String? modelStrategy);

  CompletionRequest responseSchema(Map<String, Object>? responseSchema);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CompletionRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CompletionRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  CompletionRequest call({
    String prompt,
    String? systemInstruction,
    String? modelStrategy,
    Map<String, Object>? responseSchema,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfCompletionRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfCompletionRequest.copyWith.fieldName(...)`
class _$CompletionRequestCWProxyImpl implements _$CompletionRequestCWProxy {
  const _$CompletionRequestCWProxyImpl(this._value);

  final CompletionRequest _value;

  @override
  CompletionRequest prompt(String prompt) => this(prompt: prompt);

  @override
  CompletionRequest systemInstruction(String? systemInstruction) =>
      this(systemInstruction: systemInstruction);

  @override
  CompletionRequest modelStrategy(String? modelStrategy) =>
      this(modelStrategy: modelStrategy);

  @override
  CompletionRequest responseSchema(Map<String, Object>? responseSchema) =>
      this(responseSchema: responseSchema);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CompletionRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CompletionRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  CompletionRequest call({
    Object? prompt = const $CopyWithPlaceholder(),
    Object? systemInstruction = const $CopyWithPlaceholder(),
    Object? modelStrategy = const $CopyWithPlaceholder(),
    Object? responseSchema = const $CopyWithPlaceholder(),
  }) {
    return CompletionRequest(
      prompt: prompt == const $CopyWithPlaceholder()
          ? _value.prompt
          // ignore: cast_nullable_to_non_nullable
          : prompt as String,
      systemInstruction: systemInstruction == const $CopyWithPlaceholder()
          ? _value.systemInstruction
          // ignore: cast_nullable_to_non_nullable
          : systemInstruction as String?,
      modelStrategy: modelStrategy == const $CopyWithPlaceholder()
          ? _value.modelStrategy
          // ignore: cast_nullable_to_non_nullable
          : modelStrategy as String?,
      responseSchema: responseSchema == const $CopyWithPlaceholder()
          ? _value.responseSchema
          // ignore: cast_nullable_to_non_nullable
          : responseSchema as Map<String, Object>?,
    );
  }
}

extension $CompletionRequestCopyWith on CompletionRequest {
  /// Returns a callable class that can be used as follows: `instanceOfCompletionRequest.copyWith(...)` or like so:`instanceOfCompletionRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$CompletionRequestCWProxy get copyWith =>
      _$CompletionRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CompletionRequest _$CompletionRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'CompletionRequest',
      json,
      ($checkedConvert) {
        $checkKeys(json, requiredKeys: const ['prompt']);
        final val = CompletionRequest(
          prompt: $checkedConvert('prompt', (v) => v as String),
          systemInstruction: $checkedConvert(
            'system_instruction',
            (v) => v as String?,
          ),
          modelStrategy: $checkedConvert(
            'model_strategy',
            (v) => v as String? ?? 'fast',
          ),
          responseSchema: $checkedConvert(
            'response_schema',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'systemInstruction': 'system_instruction',
        'modelStrategy': 'model_strategy',
        'responseSchema': 'response_schema',
      },
    );

Map<String, dynamic> _$CompletionRequestToJson(CompletionRequest instance) =>
    <String, dynamic>{
      'prompt': instance.prompt,
      'system_instruction': ?instance.systemInstruction,
      'model_strategy': ?instance.modelStrategy,
      'response_schema': ?instance.responseSchema,
    };
