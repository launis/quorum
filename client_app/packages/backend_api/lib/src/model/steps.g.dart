// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'steps.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$StepsCWProxy {
  Steps dummy(String? dummy);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `Steps(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// Steps(...).copyWith(id: 12, name: "My name")
  /// ````
  Steps call({String? dummy});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfSteps.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfSteps.copyWith.fieldName(...)`
class _$StepsCWProxyImpl implements _$StepsCWProxy {
  const _$StepsCWProxyImpl(this._value);

  final Steps _value;

  @override
  Steps dummy(String? dummy) => this(dummy: dummy);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `Steps(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// Steps(...).copyWith(id: 12, name: "My name")
  /// ````
  Steps call({Object? dummy = const $CopyWithPlaceholder()}) {
    return Steps(
      dummy: dummy == const $CopyWithPlaceholder()
          ? _value.dummy
          // ignore: cast_nullable_to_non_nullable
          : dummy as String?,
    );
  }
}

extension $StepsCopyWith on Steps {
  /// Returns a callable class that can be used as follows: `instanceOfSteps.copyWith(...)` or like so:`instanceOfSteps.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$StepsCWProxy get copyWith => _$StepsCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Steps _$StepsFromJson(Map<String, dynamic> json) =>
    $checkedCreate('Steps', json, ($checkedConvert) {
      final val = Steps(dummy: $checkedConvert('dummy', (v) => v as String?));
      return val;
    });

Map<String, dynamic> _$StepsToJson(Steps instance) => <String, dynamic>{
  'dummy': ?instance.dummy,
};
