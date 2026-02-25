// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'body_clone_step_builder_steps_clone_post.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$BodyCloneStepBuilderStepsClonePostCWProxy {
  BodyCloneStepBuilderStepsClonePost sourceStepId(String sourceStepId);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BodyCloneStepBuilderStepsClonePost(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BodyCloneStepBuilderStepsClonePost(...).copyWith(id: 12, name: "My name")
  /// ````
  BodyCloneStepBuilderStepsClonePost call({String sourceStepId});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfBodyCloneStepBuilderStepsClonePost.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfBodyCloneStepBuilderStepsClonePost.copyWith.fieldName(...)`
class _$BodyCloneStepBuilderStepsClonePostCWProxyImpl
    implements _$BodyCloneStepBuilderStepsClonePostCWProxy {
  const _$BodyCloneStepBuilderStepsClonePostCWProxyImpl(this._value);

  final BodyCloneStepBuilderStepsClonePost _value;

  @override
  BodyCloneStepBuilderStepsClonePost sourceStepId(String sourceStepId) =>
      this(sourceStepId: sourceStepId);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `BodyCloneStepBuilderStepsClonePost(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// BodyCloneStepBuilderStepsClonePost(...).copyWith(id: 12, name: "My name")
  /// ````
  BodyCloneStepBuilderStepsClonePost call({
    Object? sourceStepId = const $CopyWithPlaceholder(),
  }) {
    return BodyCloneStepBuilderStepsClonePost(
      sourceStepId: sourceStepId == const $CopyWithPlaceholder()
          ? _value.sourceStepId
          // ignore: cast_nullable_to_non_nullable
          : sourceStepId as String,
    );
  }
}

extension $BodyCloneStepBuilderStepsClonePostCopyWith
    on BodyCloneStepBuilderStepsClonePost {
  /// Returns a callable class that can be used as follows: `instanceOfBodyCloneStepBuilderStepsClonePost.copyWith(...)` or like so:`instanceOfBodyCloneStepBuilderStepsClonePost.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$BodyCloneStepBuilderStepsClonePostCWProxy get copyWith =>
      _$BodyCloneStepBuilderStepsClonePostCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

BodyCloneStepBuilderStepsClonePost _$BodyCloneStepBuilderStepsClonePostFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'BodyCloneStepBuilderStepsClonePost',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['source_step_id']);
    final val = BodyCloneStepBuilderStepsClonePost(
      sourceStepId: $checkedConvert('source_step_id', (v) => v as String),
    );
    return val;
  },
  fieldKeyMap: const {'sourceStepId': 'source_step_id'},
);

Map<String, dynamic> _$BodyCloneStepBuilderStepsClonePostToJson(
  BodyCloneStepBuilderStepsClonePost instance,
) => <String, dynamic>{'source_step_id': instance.sourceStepId};
