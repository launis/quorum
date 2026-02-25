// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'provider_list_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ProviderListResponseCWProxy {
  ProviderListResponse strategies(Map<String, String> strategies);

  ProviderListResponse apiKeysSet(Map<String, bool> apiKeysSet);

  ProviderListResponse availableModels(
    Map<String, List<String>>? availableModels,
  );

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ProviderListResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ProviderListResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ProviderListResponse call({
    Map<String, String> strategies,
    Map<String, bool> apiKeysSet,
    Map<String, List<String>>? availableModels,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfProviderListResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfProviderListResponse.copyWith.fieldName(...)`
class _$ProviderListResponseCWProxyImpl
    implements _$ProviderListResponseCWProxy {
  const _$ProviderListResponseCWProxyImpl(this._value);

  final ProviderListResponse _value;

  @override
  ProviderListResponse strategies(Map<String, String> strategies) =>
      this(strategies: strategies);

  @override
  ProviderListResponse apiKeysSet(Map<String, bool> apiKeysSet) =>
      this(apiKeysSet: apiKeysSet);

  @override
  ProviderListResponse availableModels(
    Map<String, List<String>>? availableModels,
  ) => this(availableModels: availableModels);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ProviderListResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ProviderListResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ProviderListResponse call({
    Object? strategies = const $CopyWithPlaceholder(),
    Object? apiKeysSet = const $CopyWithPlaceholder(),
    Object? availableModels = const $CopyWithPlaceholder(),
  }) {
    return ProviderListResponse(
      strategies: strategies == const $CopyWithPlaceholder()
          ? _value.strategies
          // ignore: cast_nullable_to_non_nullable
          : strategies as Map<String, String>,
      apiKeysSet: apiKeysSet == const $CopyWithPlaceholder()
          ? _value.apiKeysSet
          // ignore: cast_nullable_to_non_nullable
          : apiKeysSet as Map<String, bool>,
      availableModels: availableModels == const $CopyWithPlaceholder()
          ? _value.availableModels
          // ignore: cast_nullable_to_non_nullable
          : availableModels as Map<String, List<String>>?,
    );
  }
}

extension $ProviderListResponseCopyWith on ProviderListResponse {
  /// Returns a callable class that can be used as follows: `instanceOfProviderListResponse.copyWith(...)` or like so:`instanceOfProviderListResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ProviderListResponseCWProxy get copyWith =>
      _$ProviderListResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ProviderListResponse _$ProviderListResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'ProviderListResponse',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['strategies', 'api_keys_set']);
    final val = ProviderListResponse(
      strategies: $checkedConvert(
        'strategies',
        (v) => Map<String, String>.from(v as Map),
      ),
      apiKeysSet: $checkedConvert(
        'api_keys_set',
        (v) => Map<String, bool>.from(v as Map),
      ),
      availableModels: $checkedConvert(
        'available_models',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(
            k,
            (e as List<dynamic>).map((e) => e as String).toList(),
          ),
        ),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'apiKeysSet': 'api_keys_set',
    'availableModels': 'available_models',
  },
);

Map<String, dynamic> _$ProviderListResponseToJson(
  ProviderListResponse instance,
) => <String, dynamic>{
  'strategies': instance.strategies,
  'api_keys_set': instance.apiKeysSet,
  'available_models': ?instance.availableModels,
};
