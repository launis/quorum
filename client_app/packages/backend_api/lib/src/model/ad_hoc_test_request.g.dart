// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ad_hoc_test_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$AdHocTestRequestCWProxy {
  AdHocTestRequest provider(String provider);

  AdHocTestRequest apiKey(String? apiKey);

  AdHocTestRequest systemInstruction(String systemInstruction);

  AdHocTestRequest userPrompt(String userPrompt);

  AdHocTestRequest modelParams(Map<String, Object>? modelParams);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AdHocTestRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AdHocTestRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  AdHocTestRequest call({
    String provider,
    String? apiKey,
    String systemInstruction,
    String userPrompt,
    Map<String, Object>? modelParams,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfAdHocTestRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfAdHocTestRequest.copyWith.fieldName(...)`
class _$AdHocTestRequestCWProxyImpl implements _$AdHocTestRequestCWProxy {
  const _$AdHocTestRequestCWProxyImpl(this._value);

  final AdHocTestRequest _value;

  @override
  AdHocTestRequest provider(String provider) => this(provider: provider);

  @override
  AdHocTestRequest apiKey(String? apiKey) => this(apiKey: apiKey);

  @override
  AdHocTestRequest systemInstruction(String systemInstruction) =>
      this(systemInstruction: systemInstruction);

  @override
  AdHocTestRequest userPrompt(String userPrompt) =>
      this(userPrompt: userPrompt);

  @override
  AdHocTestRequest modelParams(Map<String, Object>? modelParams) =>
      this(modelParams: modelParams);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AdHocTestRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AdHocTestRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  AdHocTestRequest call({
    Object? provider = const $CopyWithPlaceholder(),
    Object? apiKey = const $CopyWithPlaceholder(),
    Object? systemInstruction = const $CopyWithPlaceholder(),
    Object? userPrompt = const $CopyWithPlaceholder(),
    Object? modelParams = const $CopyWithPlaceholder(),
  }) {
    return AdHocTestRequest(
      provider: provider == const $CopyWithPlaceholder()
          ? _value.provider
          // ignore: cast_nullable_to_non_nullable
          : provider as String,
      apiKey: apiKey == const $CopyWithPlaceholder()
          ? _value.apiKey
          // ignore: cast_nullable_to_non_nullable
          : apiKey as String?,
      systemInstruction: systemInstruction == const $CopyWithPlaceholder()
          ? _value.systemInstruction
          // ignore: cast_nullable_to_non_nullable
          : systemInstruction as String,
      userPrompt: userPrompt == const $CopyWithPlaceholder()
          ? _value.userPrompt
          // ignore: cast_nullable_to_non_nullable
          : userPrompt as String,
      modelParams: modelParams == const $CopyWithPlaceholder()
          ? _value.modelParams
          // ignore: cast_nullable_to_non_nullable
          : modelParams as Map<String, Object>?,
    );
  }
}

extension $AdHocTestRequestCopyWith on AdHocTestRequest {
  /// Returns a callable class that can be used as follows: `instanceOfAdHocTestRequest.copyWith(...)` or like so:`instanceOfAdHocTestRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$AdHocTestRequestCWProxy get copyWith => _$AdHocTestRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AdHocTestRequest _$AdHocTestRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'AdHocTestRequest',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const ['provider', 'system_instruction', 'user_prompt'],
        );
        final val = AdHocTestRequest(
          provider: $checkedConvert('provider', (v) => v as String),
          apiKey: $checkedConvert('api_key', (v) => v as String?),
          systemInstruction: $checkedConvert(
            'system_instruction',
            (v) => v as String,
          ),
          userPrompt: $checkedConvert('user_prompt', (v) => v as String),
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
        'apiKey': 'api_key',
        'systemInstruction': 'system_instruction',
        'userPrompt': 'user_prompt',
        'modelParams': 'model_params',
      },
    );

Map<String, dynamic> _$AdHocTestRequestToJson(AdHocTestRequest instance) =>
    <String, dynamic>{
      'provider': instance.provider,
      'api_key': ?instance.apiKey,
      'system_instruction': instance.systemInstruction,
      'user_prompt': instance.userPrompt,
      'model_params': ?instance.modelParams,
    };
