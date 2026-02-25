// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'fusion_rule_dto.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$FusionRuleDTOCWProxy {
  FusionRuleDTO compositeStepId(String compositeStepId);

  FusionRuleDTO name(String name);

  FusionRuleDTO replacesComponents(List<String> replacesComponents);

  FusionRuleDTO minSteps(int minSteps);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `FusionRuleDTO(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// FusionRuleDTO(...).copyWith(id: 12, name: "My name")
  /// ````
  FusionRuleDTO call({
    String compositeStepId,
    String name,
    List<String> replacesComponents,
    int minSteps,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfFusionRuleDTO.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfFusionRuleDTO.copyWith.fieldName(...)`
class _$FusionRuleDTOCWProxyImpl implements _$FusionRuleDTOCWProxy {
  const _$FusionRuleDTOCWProxyImpl(this._value);

  final FusionRuleDTO _value;

  @override
  FusionRuleDTO compositeStepId(String compositeStepId) =>
      this(compositeStepId: compositeStepId);

  @override
  FusionRuleDTO name(String name) => this(name: name);

  @override
  FusionRuleDTO replacesComponents(List<String> replacesComponents) =>
      this(replacesComponents: replacesComponents);

  @override
  FusionRuleDTO minSteps(int minSteps) => this(minSteps: minSteps);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `FusionRuleDTO(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// FusionRuleDTO(...).copyWith(id: 12, name: "My name")
  /// ````
  FusionRuleDTO call({
    Object? compositeStepId = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? replacesComponents = const $CopyWithPlaceholder(),
    Object? minSteps = const $CopyWithPlaceholder(),
  }) {
    return FusionRuleDTO(
      compositeStepId: compositeStepId == const $CopyWithPlaceholder()
          ? _value.compositeStepId
          // ignore: cast_nullable_to_non_nullable
          : compositeStepId as String,
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
      replacesComponents: replacesComponents == const $CopyWithPlaceholder()
          ? _value.replacesComponents
          // ignore: cast_nullable_to_non_nullable
          : replacesComponents as List<String>,
      minSteps: minSteps == const $CopyWithPlaceholder()
          ? _value.minSteps
          // ignore: cast_nullable_to_non_nullable
          : minSteps as int,
    );
  }
}

extension $FusionRuleDTOCopyWith on FusionRuleDTO {
  /// Returns a callable class that can be used as follows: `instanceOfFusionRuleDTO.copyWith(...)` or like so:`instanceOfFusionRuleDTO.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$FusionRuleDTOCWProxy get copyWith => _$FusionRuleDTOCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

FusionRuleDTO _$FusionRuleDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'FusionRuleDTO',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const [
            'composite_step_id',
            'name',
            'replaces_components',
            'min_steps',
          ],
        );
        final val = FusionRuleDTO(
          compositeStepId: $checkedConvert(
            'composite_step_id',
            (v) => v as String,
          ),
          name: $checkedConvert('name', (v) => v as String),
          replacesComponents: $checkedConvert(
            'replaces_components',
            (v) => (v as List<dynamic>).map((e) => e as String).toList(),
          ),
          minSteps: $checkedConvert('min_steps', (v) => (v as num).toInt()),
        );
        return val;
      },
      fieldKeyMap: const {
        'compositeStepId': 'composite_step_id',
        'replacesComponents': 'replaces_components',
        'minSteps': 'min_steps',
      },
    );

Map<String, dynamic> _$FusionRuleDTOToJson(FusionRuleDTO instance) =>
    <String, dynamic>{
      'composite_step_id': instance.compositeStepId,
      'name': instance.name,
      'replaces_components': instance.replacesComponents,
      'min_steps': instance.minSteps,
    };
