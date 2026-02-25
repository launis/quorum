// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'playground_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PlaygroundRequestCWProxy {
  PlaygroundRequest systemInstruction(String systemInstruction);

  PlaygroundRequest userMessage(String userMessage);

  PlaygroundRequest variables(Map<String, String>? variables);

  PlaygroundRequest modelParams(Map<String, Object>? modelParams);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PlaygroundRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PlaygroundRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  PlaygroundRequest call({
    String systemInstruction,
    String userMessage,
    Map<String, String>? variables,
    Map<String, Object>? modelParams,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPlaygroundRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPlaygroundRequest.copyWith.fieldName(...)`
class _$PlaygroundRequestCWProxyImpl implements _$PlaygroundRequestCWProxy {
  const _$PlaygroundRequestCWProxyImpl(this._value);

  final PlaygroundRequest _value;

  @override
  PlaygroundRequest systemInstruction(String systemInstruction) =>
      this(systemInstruction: systemInstruction);

  @override
  PlaygroundRequest userMessage(String userMessage) =>
      this(userMessage: userMessage);

  @override
  PlaygroundRequest variables(Map<String, String>? variables) =>
      this(variables: variables);

  @override
  PlaygroundRequest modelParams(Map<String, Object>? modelParams) =>
      this(modelParams: modelParams);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PlaygroundRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PlaygroundRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  PlaygroundRequest call({
    Object? systemInstruction = const $CopyWithPlaceholder(),
    Object? userMessage = const $CopyWithPlaceholder(),
    Object? variables = const $CopyWithPlaceholder(),
    Object? modelParams = const $CopyWithPlaceholder(),
  }) {
    return PlaygroundRequest(
      systemInstruction: systemInstruction == const $CopyWithPlaceholder()
          ? _value.systemInstruction
          // ignore: cast_nullable_to_non_nullable
          : systemInstruction as String,
      userMessage: userMessage == const $CopyWithPlaceholder()
          ? _value.userMessage
          // ignore: cast_nullable_to_non_nullable
          : userMessage as String,
      variables: variables == const $CopyWithPlaceholder()
          ? _value.variables
          // ignore: cast_nullable_to_non_nullable
          : variables as Map<String, String>?,
      modelParams: modelParams == const $CopyWithPlaceholder()
          ? _value.modelParams
          // ignore: cast_nullable_to_non_nullable
          : modelParams as Map<String, Object>?,
    );
  }
}

extension $PlaygroundRequestCopyWith on PlaygroundRequest {
  /// Returns a callable class that can be used as follows: `instanceOfPlaygroundRequest.copyWith(...)` or like so:`instanceOfPlaygroundRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PlaygroundRequestCWProxy get copyWith =>
      _$PlaygroundRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PlaygroundRequest _$PlaygroundRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'PlaygroundRequest',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const ['system_instruction', 'user_message'],
        );
        final val = PlaygroundRequest(
          systemInstruction: $checkedConvert(
            'system_instruction',
            (v) => v as String,
          ),
          userMessage: $checkedConvert('user_message', (v) => v as String),
          variables: $checkedConvert(
            'variables',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as String),
            ),
          ),
          modelParams: $checkedConvert(
            'model_params',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'systemInstruction': 'system_instruction',
        'userMessage': 'user_message',
        'modelParams': 'model_params',
      },
    );

Map<String, dynamic> _$PlaygroundRequestToJson(PlaygroundRequest instance) =>
    <String, dynamic>{
      'system_instruction': instance.systemInstruction,
      'user_message': instance.userMessage,
      'variables': ?instance.variables,
      'model_params': ?instance.modelParams,
    };
