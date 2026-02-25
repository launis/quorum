// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'location_inner.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$LocationInnerCWProxy {
  LocationInner dummy(String? dummy);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `LocationInner(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// LocationInner(...).copyWith(id: 12, name: "My name")
  /// ````
  LocationInner call({String? dummy});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfLocationInner.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfLocationInner.copyWith.fieldName(...)`
class _$LocationInnerCWProxyImpl implements _$LocationInnerCWProxy {
  const _$LocationInnerCWProxyImpl(this._value);

  final LocationInner _value;

  @override
  LocationInner dummy(String? dummy) => this(dummy: dummy);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `LocationInner(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// LocationInner(...).copyWith(id: 12, name: "My name")
  /// ````
  LocationInner call({Object? dummy = const $CopyWithPlaceholder()}) {
    return LocationInner(
      dummy: dummy == const $CopyWithPlaceholder()
          ? _value.dummy
          // ignore: cast_nullable_to_non_nullable
          : dummy as String?,
    );
  }
}

extension $LocationInnerCopyWith on LocationInner {
  /// Returns a callable class that can be used as follows: `instanceOfLocationInner.copyWith(...)` or like so:`instanceOfLocationInner.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$LocationInnerCWProxy get copyWith => _$LocationInnerCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

LocationInner _$LocationInnerFromJson(Map<String, dynamic> json) =>
    $checkedCreate('LocationInner', json, ($checkedConvert) {
      final val = LocationInner(
        dummy: $checkedConvert('dummy', (v) => v as String?),
      );
      return val;
    });

Map<String, dynamic> _$LocationInnerToJson(LocationInner instance) =>
    <String, dynamic>{'dummy': ?instance.dummy};
