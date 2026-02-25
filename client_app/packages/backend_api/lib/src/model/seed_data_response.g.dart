// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'seed_data_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$SeedDataResponseCWProxy {
  SeedDataResponse components(List<Map<String, Object>> components);

  SeedDataResponse steps(List<Map<String, Object>> steps);

  SeedDataResponse workflows(List<Map<String, Object>> workflows);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SeedDataResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SeedDataResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  SeedDataResponse call({
    List<Map<String, Object>> components,
    List<Map<String, Object>> steps,
    List<Map<String, Object>> workflows,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfSeedDataResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfSeedDataResponse.copyWith.fieldName(...)`
class _$SeedDataResponseCWProxyImpl implements _$SeedDataResponseCWProxy {
  const _$SeedDataResponseCWProxyImpl(this._value);

  final SeedDataResponse _value;

  @override
  SeedDataResponse components(List<Map<String, Object>> components) =>
      this(components: components);

  @override
  SeedDataResponse steps(List<Map<String, Object>> steps) => this(steps: steps);

  @override
  SeedDataResponse workflows(List<Map<String, Object>> workflows) =>
      this(workflows: workflows);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `SeedDataResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// SeedDataResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  SeedDataResponse call({
    Object? components = const $CopyWithPlaceholder(),
    Object? steps = const $CopyWithPlaceholder(),
    Object? workflows = const $CopyWithPlaceholder(),
  }) {
    return SeedDataResponse(
      components: components == const $CopyWithPlaceholder()
          ? _value.components
          // ignore: cast_nullable_to_non_nullable
          : components as List<Map<String, Object>>,
      steps: steps == const $CopyWithPlaceholder()
          ? _value.steps
          // ignore: cast_nullable_to_non_nullable
          : steps as List<Map<String, Object>>,
      workflows: workflows == const $CopyWithPlaceholder()
          ? _value.workflows
          // ignore: cast_nullable_to_non_nullable
          : workflows as List<Map<String, Object>>,
    );
  }
}

extension $SeedDataResponseCopyWith on SeedDataResponse {
  /// Returns a callable class that can be used as follows: `instanceOfSeedDataResponse.copyWith(...)` or like so:`instanceOfSeedDataResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$SeedDataResponseCWProxy get copyWith => _$SeedDataResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

SeedDataResponse _$SeedDataResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('SeedDataResponse', json, ($checkedConvert) {
      $checkKeys(
        json,
        requiredKeys: const ['components', 'steps', 'workflows'],
      );
      final val = SeedDataResponse(
        components: $checkedConvert(
          'components',
          (v) => (v as List<dynamic>)
              .map(
                (e) => (e as Map<String, dynamic>).map(
                  (k, e) => MapEntry(k, e as Object),
                ),
              )
              .toList(),
        ),
        steps: $checkedConvert(
          'steps',
          (v) => (v as List<dynamic>)
              .map(
                (e) => (e as Map<String, dynamic>).map(
                  (k, e) => MapEntry(k, e as Object),
                ),
              )
              .toList(),
        ),
        workflows: $checkedConvert(
          'workflows',
          (v) => (v as List<dynamic>)
              .map(
                (e) => (e as Map<String, dynamic>).map(
                  (k, e) => MapEntry(k, e as Object),
                ),
              )
              .toList(),
        ),
      );
      return val;
    });

Map<String, dynamic> _$SeedDataResponseToJson(SeedDataResponse instance) =>
    <String, dynamic>{
      'components': instance.components,
      'steps': instance.steps,
      'workflows': instance.workflows,
    };
