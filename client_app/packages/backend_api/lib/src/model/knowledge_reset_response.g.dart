// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'knowledge_reset_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$KnowledgeResetResponseCWProxy {
  KnowledgeResetResponse message(String message);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `KnowledgeResetResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// KnowledgeResetResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  KnowledgeResetResponse call({String message});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfKnowledgeResetResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfKnowledgeResetResponse.copyWith.fieldName(...)`
class _$KnowledgeResetResponseCWProxyImpl
    implements _$KnowledgeResetResponseCWProxy {
  const _$KnowledgeResetResponseCWProxyImpl(this._value);

  final KnowledgeResetResponse _value;

  @override
  KnowledgeResetResponse message(String message) => this(message: message);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `KnowledgeResetResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// KnowledgeResetResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  KnowledgeResetResponse call({
    Object? message = const $CopyWithPlaceholder(),
  }) {
    return KnowledgeResetResponse(
      message: message == const $CopyWithPlaceholder()
          ? _value.message
          // ignore: cast_nullable_to_non_nullable
          : message as String,
    );
  }
}

extension $KnowledgeResetResponseCopyWith on KnowledgeResetResponse {
  /// Returns a callable class that can be used as follows: `instanceOfKnowledgeResetResponse.copyWith(...)` or like so:`instanceOfKnowledgeResetResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$KnowledgeResetResponseCWProxy get copyWith =>
      _$KnowledgeResetResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

KnowledgeResetResponse _$KnowledgeResetResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('KnowledgeResetResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['message']);
  final val = KnowledgeResetResponse(
    message: $checkedConvert('message', (v) => v as String),
  );
  return val;
});

Map<String, dynamic> _$KnowledgeResetResponseToJson(
  KnowledgeResetResponse instance,
) => <String, dynamic>{'message': instance.message};
