// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'llm_provider_config.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$LLMProviderConfigCWProxy {
  LLMProviderConfig id(String id);

  LLMProviderConfig provider(String provider);

  LLMProviderConfig modelName(String modelName);

  LLMProviderConfig apiKey(String? apiKey);

  LLMProviderConfig baseUrl(String? baseUrl);

  LLMProviderConfig temperature(num? temperature);

  LLMProviderConfig tpmLimit(int tpmLimit);

  LLMProviderConfig rpmLimit(int rpmLimit);

  LLMProviderConfig defaultMaxTokens(int? defaultMaxTokens);

  LLMProviderConfig vertexLocation(String? vertexLocation);

  LLMProviderConfig supportsGrounding(bool? supportsGrounding);

  LLMProviderConfig isActive(bool? isActive);

  LLMProviderConfig additionalParams(Map<String, Object>? additionalParams);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `LLMProviderConfig(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// LLMProviderConfig(...).copyWith(id: 12, name: "My name")
  /// ````
  LLMProviderConfig call({
    String id,
    String provider,
    String modelName,
    String? apiKey,
    String? baseUrl,
    num? temperature,
    int tpmLimit,
    int rpmLimit,
    int? defaultMaxTokens,
    String? vertexLocation,
    bool? supportsGrounding,
    bool? isActive,
    Map<String, Object>? additionalParams,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfLLMProviderConfig.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfLLMProviderConfig.copyWith.fieldName(...)`
class _$LLMProviderConfigCWProxyImpl implements _$LLMProviderConfigCWProxy {
  const _$LLMProviderConfigCWProxyImpl(this._value);

  final LLMProviderConfig _value;

  @override
  LLMProviderConfig id(String id) => this(id: id);

  @override
  LLMProviderConfig provider(String provider) => this(provider: provider);

  @override
  LLMProviderConfig modelName(String modelName) => this(modelName: modelName);

  @override
  LLMProviderConfig apiKey(String? apiKey) => this(apiKey: apiKey);

  @override
  LLMProviderConfig baseUrl(String? baseUrl) => this(baseUrl: baseUrl);

  @override
  LLMProviderConfig temperature(num? temperature) =>
      this(temperature: temperature);

  @override
  LLMProviderConfig tpmLimit(int tpmLimit) => this(tpmLimit: tpmLimit);

  @override
  LLMProviderConfig rpmLimit(int rpmLimit) => this(rpmLimit: rpmLimit);

  @override
  LLMProviderConfig defaultMaxTokens(int? defaultMaxTokens) =>
      this(defaultMaxTokens: defaultMaxTokens);

  @override
  LLMProviderConfig vertexLocation(String? vertexLocation) =>
      this(vertexLocation: vertexLocation);

  @override
  LLMProviderConfig supportsGrounding(bool? supportsGrounding) =>
      this(supportsGrounding: supportsGrounding);

  @override
  LLMProviderConfig isActive(bool? isActive) => this(isActive: isActive);

  @override
  LLMProviderConfig additionalParams(Map<String, Object>? additionalParams) =>
      this(additionalParams: additionalParams);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `LLMProviderConfig(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// LLMProviderConfig(...).copyWith(id: 12, name: "My name")
  /// ````
  LLMProviderConfig call({
    Object? id = const $CopyWithPlaceholder(),
    Object? provider = const $CopyWithPlaceholder(),
    Object? modelName = const $CopyWithPlaceholder(),
    Object? apiKey = const $CopyWithPlaceholder(),
    Object? baseUrl = const $CopyWithPlaceholder(),
    Object? temperature = const $CopyWithPlaceholder(),
    Object? tpmLimit = const $CopyWithPlaceholder(),
    Object? rpmLimit = const $CopyWithPlaceholder(),
    Object? defaultMaxTokens = const $CopyWithPlaceholder(),
    Object? vertexLocation = const $CopyWithPlaceholder(),
    Object? supportsGrounding = const $CopyWithPlaceholder(),
    Object? isActive = const $CopyWithPlaceholder(),
    Object? additionalParams = const $CopyWithPlaceholder(),
  }) {
    return LLMProviderConfig(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
      provider: provider == const $CopyWithPlaceholder()
          ? _value.provider
          // ignore: cast_nullable_to_non_nullable
          : provider as String,
      modelName: modelName == const $CopyWithPlaceholder()
          ? _value.modelName
          // ignore: cast_nullable_to_non_nullable
          : modelName as String,
      apiKey: apiKey == const $CopyWithPlaceholder()
          ? _value.apiKey
          // ignore: cast_nullable_to_non_nullable
          : apiKey as String?,
      baseUrl: baseUrl == const $CopyWithPlaceholder()
          ? _value.baseUrl
          // ignore: cast_nullable_to_non_nullable
          : baseUrl as String?,
      temperature: temperature == const $CopyWithPlaceholder()
          ? _value.temperature
          // ignore: cast_nullable_to_non_nullable
          : temperature as num?,
      tpmLimit: tpmLimit == const $CopyWithPlaceholder()
          ? _value.tpmLimit
          // ignore: cast_nullable_to_non_nullable
          : tpmLimit as int,
      rpmLimit: rpmLimit == const $CopyWithPlaceholder()
          ? _value.rpmLimit
          // ignore: cast_nullable_to_non_nullable
          : rpmLimit as int,
      defaultMaxTokens: defaultMaxTokens == const $CopyWithPlaceholder()
          ? _value.defaultMaxTokens
          // ignore: cast_nullable_to_non_nullable
          : defaultMaxTokens as int?,
      vertexLocation: vertexLocation == const $CopyWithPlaceholder()
          ? _value.vertexLocation
          // ignore: cast_nullable_to_non_nullable
          : vertexLocation as String?,
      supportsGrounding: supportsGrounding == const $CopyWithPlaceholder()
          ? _value.supportsGrounding
          // ignore: cast_nullable_to_non_nullable
          : supportsGrounding as bool?,
      isActive: isActive == const $CopyWithPlaceholder()
          ? _value.isActive
          // ignore: cast_nullable_to_non_nullable
          : isActive as bool?,
      additionalParams: additionalParams == const $CopyWithPlaceholder()
          ? _value.additionalParams
          // ignore: cast_nullable_to_non_nullable
          : additionalParams as Map<String, Object>?,
    );
  }
}

extension $LLMProviderConfigCopyWith on LLMProviderConfig {
  /// Returns a callable class that can be used as follows: `instanceOfLLMProviderConfig.copyWith(...)` or like so:`instanceOfLLMProviderConfig.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$LLMProviderConfigCWProxy get copyWith =>
      _$LLMProviderConfigCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

LLMProviderConfig _$LLMProviderConfigFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'LLMProviderConfig',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const [
            'id',
            'provider',
            'model_name',
            'tpm_limit',
            'rpm_limit',
          ],
        );
        final val = LLMProviderConfig(
          id: $checkedConvert('id', (v) => v as String),
          provider: $checkedConvert('provider', (v) => v as String),
          modelName: $checkedConvert('model_name', (v) => v as String),
          apiKey: $checkedConvert('api_key', (v) => v as String?),
          baseUrl: $checkedConvert('base_url', (v) => v as String?),
          temperature: $checkedConvert('temperature', (v) => v as num? ?? 0.7),
          tpmLimit: $checkedConvert('tpm_limit', (v) => (v as num).toInt()),
          rpmLimit: $checkedConvert('rpm_limit', (v) => (v as num).toInt()),
          defaultMaxTokens: $checkedConvert(
            'default_max_tokens',
            (v) => (v as num?)?.toInt(),
          ),
          vertexLocation: $checkedConvert(
            'vertex_location',
            (v) => v as String?,
          ),
          supportsGrounding: $checkedConvert(
            'supports_grounding',
            (v) => v as bool? ?? false,
          ),
          isActive: $checkedConvert('is_active', (v) => v as bool? ?? true),
          additionalParams: $checkedConvert(
            'additional_params',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'modelName': 'model_name',
        'apiKey': 'api_key',
        'baseUrl': 'base_url',
        'tpmLimit': 'tpm_limit',
        'rpmLimit': 'rpm_limit',
        'defaultMaxTokens': 'default_max_tokens',
        'vertexLocation': 'vertex_location',
        'supportsGrounding': 'supports_grounding',
        'isActive': 'is_active',
        'additionalParams': 'additional_params',
      },
    );

Map<String, dynamic> _$LLMProviderConfigToJson(LLMProviderConfig instance) =>
    <String, dynamic>{
      'id': instance.id,
      'provider': instance.provider,
      'model_name': instance.modelName,
      'api_key': ?instance.apiKey,
      'base_url': ?instance.baseUrl,
      'temperature': ?instance.temperature,
      'tpm_limit': instance.tpmLimit,
      'rpm_limit': instance.rpmLimit,
      'default_max_tokens': ?instance.defaultMaxTokens,
      'vertex_location': ?instance.vertexLocation,
      'supports_grounding': ?instance.supportsGrounding,
      'is_active': ?instance.isActive,
      'additional_params': ?instance.additionalParams,
    };
