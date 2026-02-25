// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'model_options_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ModelOptionsResponseCWProxy {
  ModelOptionsResponse options(Map<String, List<String>> options);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ModelOptionsResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ModelOptionsResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ModelOptionsResponse call({Map<String, List<String>> options});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfModelOptionsResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfModelOptionsResponse.copyWith.fieldName(...)`
class _$ModelOptionsResponseCWProxyImpl
    implements _$ModelOptionsResponseCWProxy {
  const _$ModelOptionsResponseCWProxyImpl(this._value);

  final ModelOptionsResponse _value;

  @override
  ModelOptionsResponse options(Map<String, List<String>> options) =>
      this(options: options);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ModelOptionsResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ModelOptionsResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ModelOptionsResponse call({Object? options = const $CopyWithPlaceholder()}) {
    return ModelOptionsResponse(
      options: options == const $CopyWithPlaceholder()
          ? _value.options
          // ignore: cast_nullable_to_non_nullable
          : options as Map<String, List<String>>,
    );
  }
}

extension $ModelOptionsResponseCopyWith on ModelOptionsResponse {
  /// Returns a callable class that can be used as follows: `instanceOfModelOptionsResponse.copyWith(...)` or like so:`instanceOfModelOptionsResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ModelOptionsResponseCWProxy get copyWith =>
      _$ModelOptionsResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ModelOptionsResponse _$ModelOptionsResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('ModelOptionsResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['options']);
  final val = ModelOptionsResponse(
    options: $checkedConvert(
      'options',
      (v) => (v as Map<String, dynamic>).map(
        (k, e) =>
            MapEntry(k, (e as List<dynamic>).map((e) => e as String).toList()),
      ),
    ),
  );
  return val;
});

Map<String, dynamic> _$ModelOptionsResponseToJson(
  ModelOptionsResponse instance,
) => <String, dynamic>{'options': instance.options};
