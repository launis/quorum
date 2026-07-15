// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'synthesis_config_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$SynthesisConfigDto {

@JsonKey(name: 'system_prompt') String? get systemPrompt;@JsonKey(name: 'synthesis_block_id') String? get synthesisBlockId;@JsonKey(name: 'row_explanations_block_id') String? get rowExplanationsBlockId;@JsonKey(name: 'model_strategy') String get modelStrategy;@JsonKey(name: 'length_constraint') int? get lengthConstraint;@JsonKey(name: 'enable_pii_masking') bool get enablePiiMasking;@JsonKey(name: 'omit_empty_sections') bool get omitEmptySections;@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns;
/// Create a copy of SynthesisConfigDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SynthesisConfigDtoCopyWith<SynthesisConfigDto> get copyWith => _$SynthesisConfigDtoCopyWithImpl<SynthesisConfigDto>(this as SynthesisConfigDto, _$identity);

  /// Serializes this SynthesisConfigDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'SynthesisConfigDto(systemPrompt: $systemPrompt, synthesisBlockId: $synthesisBlockId, rowExplanationsBlockId: $rowExplanationsBlockId, modelStrategy: $modelStrategy, lengthConstraint: $lengthConstraint, enablePiiMasking: $enablePiiMasking, omitEmptySections: $omitEmptySections, matrixVisibleColumns: $matrixVisibleColumns)';
}


}

/// @nodoc
abstract mixin class $SynthesisConfigDtoCopyWith<$Res>  {
  factory $SynthesisConfigDtoCopyWith(SynthesisConfigDto value, $Res Function(SynthesisConfigDto) _then) = _$SynthesisConfigDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'system_prompt') String? systemPrompt,@JsonKey(name: 'synthesis_block_id') String? synthesisBlockId,@JsonKey(name: 'row_explanations_block_id') String? rowExplanationsBlockId,@JsonKey(name: 'model_strategy') String modelStrategy,@JsonKey(name: 'length_constraint') int? lengthConstraint,@JsonKey(name: 'enable_pii_masking') bool enablePiiMasking,@JsonKey(name: 'omit_empty_sections') bool omitEmptySections,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns
});




}
/// @nodoc
class _$SynthesisConfigDtoCopyWithImpl<$Res>
    implements $SynthesisConfigDtoCopyWith<$Res> {
  _$SynthesisConfigDtoCopyWithImpl(this._self, this._then);

  final SynthesisConfigDto _self;
  final $Res Function(SynthesisConfigDto) _then;

/// Create a copy of SynthesisConfigDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? systemPrompt = freezed,Object? synthesisBlockId = freezed,Object? rowExplanationsBlockId = freezed,Object? modelStrategy = null,Object? lengthConstraint = freezed,Object? enablePiiMasking = null,Object? omitEmptySections = null,Object? matrixVisibleColumns = null,}) {
  return _then(_self.copyWith(
systemPrompt: freezed == systemPrompt ? _self.systemPrompt : systemPrompt // ignore: cast_nullable_to_non_nullable
as String?,synthesisBlockId: freezed == synthesisBlockId ? _self.synthesisBlockId : synthesisBlockId // ignore: cast_nullable_to_non_nullable
as String?,rowExplanationsBlockId: freezed == rowExplanationsBlockId ? _self.rowExplanationsBlockId : rowExplanationsBlockId // ignore: cast_nullable_to_non_nullable
as String?,modelStrategy: null == modelStrategy ? _self.modelStrategy : modelStrategy // ignore: cast_nullable_to_non_nullable
as String,lengthConstraint: freezed == lengthConstraint ? _self.lengthConstraint : lengthConstraint // ignore: cast_nullable_to_non_nullable
as int?,enablePiiMasking: null == enablePiiMasking ? _self.enablePiiMasking : enablePiiMasking // ignore: cast_nullable_to_non_nullable
as bool,omitEmptySections: null == omitEmptySections ? _self.omitEmptySections : omitEmptySections // ignore: cast_nullable_to_non_nullable
as bool,matrixVisibleColumns: null == matrixVisibleColumns ? _self.matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

}


/// Adds pattern-matching-related methods to [SynthesisConfigDto].
extension SynthesisConfigDtoPatterns on SynthesisConfigDto {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SynthesisConfigDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SynthesisConfigDto() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SynthesisConfigDto value)  $default,){
final _that = this;
switch (_that) {
case _SynthesisConfigDto():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SynthesisConfigDto value)?  $default,){
final _that = this;
switch (_that) {
case _SynthesisConfigDto() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'system_prompt')  String? systemPrompt, @JsonKey(name: 'synthesis_block_id')  String? synthesisBlockId, @JsonKey(name: 'row_explanations_block_id')  String? rowExplanationsBlockId, @JsonKey(name: 'model_strategy')  String modelStrategy, @JsonKey(name: 'length_constraint')  int? lengthConstraint, @JsonKey(name: 'enable_pii_masking')  bool enablePiiMasking, @JsonKey(name: 'omit_empty_sections')  bool omitEmptySections, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SynthesisConfigDto() when $default != null:
return $default(_that.systemPrompt,_that.synthesisBlockId,_that.rowExplanationsBlockId,_that.modelStrategy,_that.lengthConstraint,_that.enablePiiMasking,_that.omitEmptySections,_that.matrixVisibleColumns);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'system_prompt')  String? systemPrompt, @JsonKey(name: 'synthesis_block_id')  String? synthesisBlockId, @JsonKey(name: 'row_explanations_block_id')  String? rowExplanationsBlockId, @JsonKey(name: 'model_strategy')  String modelStrategy, @JsonKey(name: 'length_constraint')  int? lengthConstraint, @JsonKey(name: 'enable_pii_masking')  bool enablePiiMasking, @JsonKey(name: 'omit_empty_sections')  bool omitEmptySections, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns)  $default,) {final _that = this;
switch (_that) {
case _SynthesisConfigDto():
return $default(_that.systemPrompt,_that.synthesisBlockId,_that.rowExplanationsBlockId,_that.modelStrategy,_that.lengthConstraint,_that.enablePiiMasking,_that.omitEmptySections,_that.matrixVisibleColumns);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'system_prompt')  String? systemPrompt, @JsonKey(name: 'synthesis_block_id')  String? synthesisBlockId, @JsonKey(name: 'row_explanations_block_id')  String? rowExplanationsBlockId, @JsonKey(name: 'model_strategy')  String modelStrategy, @JsonKey(name: 'length_constraint')  int? lengthConstraint, @JsonKey(name: 'enable_pii_masking')  bool enablePiiMasking, @JsonKey(name: 'omit_empty_sections')  bool omitEmptySections, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns)?  $default,) {final _that = this;
switch (_that) {
case _SynthesisConfigDto() when $default != null:
return $default(_that.systemPrompt,_that.synthesisBlockId,_that.rowExplanationsBlockId,_that.modelStrategy,_that.lengthConstraint,_that.enablePiiMasking,_that.omitEmptySections,_that.matrixVisibleColumns);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: false)
class _SynthesisConfigDto implements SynthesisConfigDto {
  const _SynthesisConfigDto({@JsonKey(name: 'system_prompt') this.systemPrompt, @JsonKey(name: 'synthesis_block_id') this.synthesisBlockId, @JsonKey(name: 'row_explanations_block_id') this.rowExplanationsBlockId, @JsonKey(name: 'model_strategy') this.modelStrategy = 'synthesis', @JsonKey(name: 'length_constraint') this.lengthConstraint, @JsonKey(name: 'enable_pii_masking') this.enablePiiMasking = false, @JsonKey(name: 'omit_empty_sections') this.omitEmptySections = true, @JsonKey(name: 'matrix_visible_columns') final  List<String> matrixVisibleColumns = const []}): _matrixVisibleColumns = matrixVisibleColumns;
  factory _SynthesisConfigDto.fromJson(Map<String, dynamic> json) => _$SynthesisConfigDtoFromJson(json);

@override@JsonKey(name: 'system_prompt') final  String? systemPrompt;
@override@JsonKey(name: 'synthesis_block_id') final  String? synthesisBlockId;
@override@JsonKey(name: 'row_explanations_block_id') final  String? rowExplanationsBlockId;
@override@JsonKey(name: 'model_strategy') final  String modelStrategy;
@override@JsonKey(name: 'length_constraint') final  int? lengthConstraint;
@override@JsonKey(name: 'enable_pii_masking') final  bool enablePiiMasking;
@override@JsonKey(name: 'omit_empty_sections') final  bool omitEmptySections;
 final  List<String> _matrixVisibleColumns;
@override@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns {
  if (_matrixVisibleColumns is EqualUnmodifiableListView) return _matrixVisibleColumns;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_matrixVisibleColumns);
}


/// Create a copy of SynthesisConfigDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SynthesisConfigDtoCopyWith<_SynthesisConfigDto> get copyWith => __$SynthesisConfigDtoCopyWithImpl<_SynthesisConfigDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SynthesisConfigDtoToJson(this, );
}



@override
String toString() {
  return 'SynthesisConfigDto(systemPrompt: $systemPrompt, synthesisBlockId: $synthesisBlockId, rowExplanationsBlockId: $rowExplanationsBlockId, modelStrategy: $modelStrategy, lengthConstraint: $lengthConstraint, enablePiiMasking: $enablePiiMasking, omitEmptySections: $omitEmptySections, matrixVisibleColumns: $matrixVisibleColumns)';
}


}

/// @nodoc
abstract mixin class _$SynthesisConfigDtoCopyWith<$Res> implements $SynthesisConfigDtoCopyWith<$Res> {
  factory _$SynthesisConfigDtoCopyWith(_SynthesisConfigDto value, $Res Function(_SynthesisConfigDto) _then) = __$SynthesisConfigDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'system_prompt') String? systemPrompt,@JsonKey(name: 'synthesis_block_id') String? synthesisBlockId,@JsonKey(name: 'row_explanations_block_id') String? rowExplanationsBlockId,@JsonKey(name: 'model_strategy') String modelStrategy,@JsonKey(name: 'length_constraint') int? lengthConstraint,@JsonKey(name: 'enable_pii_masking') bool enablePiiMasking,@JsonKey(name: 'omit_empty_sections') bool omitEmptySections,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns
});




}
/// @nodoc
class __$SynthesisConfigDtoCopyWithImpl<$Res>
    implements _$SynthesisConfigDtoCopyWith<$Res> {
  __$SynthesisConfigDtoCopyWithImpl(this._self, this._then);

  final _SynthesisConfigDto _self;
  final $Res Function(_SynthesisConfigDto) _then;

/// Create a copy of SynthesisConfigDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? systemPrompt = freezed,Object? synthesisBlockId = freezed,Object? rowExplanationsBlockId = freezed,Object? modelStrategy = null,Object? lengthConstraint = freezed,Object? enablePiiMasking = null,Object? omitEmptySections = null,Object? matrixVisibleColumns = null,}) {
  return _then(_SynthesisConfigDto(
systemPrompt: freezed == systemPrompt ? _self.systemPrompt : systemPrompt // ignore: cast_nullable_to_non_nullable
as String?,synthesisBlockId: freezed == synthesisBlockId ? _self.synthesisBlockId : synthesisBlockId // ignore: cast_nullable_to_non_nullable
as String?,rowExplanationsBlockId: freezed == rowExplanationsBlockId ? _self.rowExplanationsBlockId : rowExplanationsBlockId // ignore: cast_nullable_to_non_nullable
as String?,modelStrategy: null == modelStrategy ? _self.modelStrategy : modelStrategy // ignore: cast_nullable_to_non_nullable
as String,lengthConstraint: freezed == lengthConstraint ? _self.lengthConstraint : lengthConstraint // ignore: cast_nullable_to_non_nullable
as int?,enablePiiMasking: null == enablePiiMasking ? _self.enablePiiMasking : enablePiiMasking // ignore: cast_nullable_to_non_nullable
as bool,omitEmptySections: null == omitEmptySections ? _self.omitEmptySections : omitEmptySections // ignore: cast_nullable_to_non_nullable
as bool,matrixVisibleColumns: null == matrixVisibleColumns ? _self._matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}


}

// dart format on
