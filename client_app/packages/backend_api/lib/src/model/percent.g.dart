// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'percent.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PercentCWProxy {
  Percent dummy(String? dummy);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `Percent(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// Percent(...).copyWith(id: 12, name: "My name")
  /// ````
  Percent call({String? dummy});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPercent.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPercent.copyWith.fieldName(...)`
class _$PercentCWProxyImpl implements _$PercentCWProxy {
  const _$PercentCWProxyImpl(this._value);

  final Percent _value;

  @override
  Percent dummy(String? dummy) => this(dummy: dummy);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `Percent(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// Percent(...).copyWith(id: 12, name: "My name")
  /// ````
  Percent call({Object? dummy = const $CopyWithPlaceholder()}) {
    return Percent(
      dummy: dummy == const $CopyWithPlaceholder()
          ? _value.dummy
          // ignore: cast_nullable_to_non_nullable
          : dummy as String?,
    );
  }
}

extension $PercentCopyWith on Percent {
  /// Returns a callable class that can be used as follows: `instanceOfPercent.copyWith(...)` or like so:`instanceOfPercent.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PercentCWProxy get copyWith => _$PercentCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Percent _$PercentFromJson(Map<String, dynamic> json) =>
    $checkedCreate('Percent', json, ($checkedConvert) {
      final val = Percent(dummy: $checkedConvert('dummy', (v) => v as String?));
      return val;
    });

Map<String, dynamic> _$PercentToJson(Percent instance) => <String, dynamic>{
  'dummy': ?instance.dummy,
};
