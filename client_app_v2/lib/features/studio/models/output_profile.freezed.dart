// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'output_profile.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$MatrixSynthesisGroup {

 String get id; I18nText get title;@JsonKey(name: 'target_blocks') List<String> get targetBlocks;@JsonKey(name: 'synthesis_directive') String? get synthesisDirective;
/// Create a copy of MatrixSynthesisGroup
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MatrixSynthesisGroupCopyWith<MatrixSynthesisGroup> get copyWith => _$MatrixSynthesisGroupCopyWithImpl<MatrixSynthesisGroup>(this as MatrixSynthesisGroup, _$identity);

  /// Serializes this MatrixSynthesisGroup to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'MatrixSynthesisGroup(id: $id, title: $title, targetBlocks: $targetBlocks, synthesisDirective: $synthesisDirective)';
}


}

/// @nodoc
abstract mixin class $MatrixSynthesisGroupCopyWith<$Res>  {
  factory $MatrixSynthesisGroupCopyWith(MatrixSynthesisGroup value, $Res Function(MatrixSynthesisGroup) _then) = _$MatrixSynthesisGroupCopyWithImpl;
@useResult
$Res call({
 String id, I18nText title,@JsonKey(name: 'target_blocks') List<String> targetBlocks,@JsonKey(name: 'synthesis_directive') String? synthesisDirective
});


$I18nTextCopyWith<$Res> get title;

}
/// @nodoc
class _$MatrixSynthesisGroupCopyWithImpl<$Res>
    implements $MatrixSynthesisGroupCopyWith<$Res> {
  _$MatrixSynthesisGroupCopyWithImpl(this._self, this._then);

  final MatrixSynthesisGroup _self;
  final $Res Function(MatrixSynthesisGroup) _then;

/// Create a copy of MatrixSynthesisGroup
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? title = null,Object? targetBlocks = null,Object? synthesisDirective = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText,targetBlocks: null == targetBlocks ? _self.targetBlocks : targetBlocks // ignore: cast_nullable_to_non_nullable
as List<String>,synthesisDirective: freezed == synthesisDirective ? _self.synthesisDirective : synthesisDirective // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of MatrixSynthesisGroup
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get title {
  
  return $I18nTextCopyWith<$Res>(_self.title, (value) {
    return _then(_self.copyWith(title: value));
  });
}
}


/// Adds pattern-matching-related methods to [MatrixSynthesisGroup].
extension MatrixSynthesisGroupPatterns on MatrixSynthesisGroup {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MatrixSynthesisGroup value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MatrixSynthesisGroup() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MatrixSynthesisGroup value)  $default,){
final _that = this;
switch (_that) {
case _MatrixSynthesisGroup():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MatrixSynthesisGroup value)?  $default,){
final _that = this;
switch (_that) {
case _MatrixSynthesisGroup() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  I18nText title, @JsonKey(name: 'target_blocks')  List<String> targetBlocks, @JsonKey(name: 'synthesis_directive')  String? synthesisDirective)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MatrixSynthesisGroup() when $default != null:
return $default(_that.id,_that.title,_that.targetBlocks,_that.synthesisDirective);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  I18nText title, @JsonKey(name: 'target_blocks')  List<String> targetBlocks, @JsonKey(name: 'synthesis_directive')  String? synthesisDirective)  $default,) {final _that = this;
switch (_that) {
case _MatrixSynthesisGroup():
return $default(_that.id,_that.title,_that.targetBlocks,_that.synthesisDirective);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  I18nText title, @JsonKey(name: 'target_blocks')  List<String> targetBlocks, @JsonKey(name: 'synthesis_directive')  String? synthesisDirective)?  $default,) {final _that = this;
switch (_that) {
case _MatrixSynthesisGroup() when $default != null:
return $default(_that.id,_that.title,_that.targetBlocks,_that.synthesisDirective);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _MatrixSynthesisGroup extends MatrixSynthesisGroup {
  const _MatrixSynthesisGroup({required this.id, required this.title, @JsonKey(name: 'target_blocks') required final  List<String> targetBlocks, @JsonKey(name: 'synthesis_directive') this.synthesisDirective}): _targetBlocks = targetBlocks,super._();
  factory _MatrixSynthesisGroup.fromJson(Map<String, dynamic> json) => _$MatrixSynthesisGroupFromJson(json);

@override final  String id;
@override final  I18nText title;
 final  List<String> _targetBlocks;
@override@JsonKey(name: 'target_blocks') List<String> get targetBlocks {
  if (_targetBlocks is EqualUnmodifiableListView) return _targetBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_targetBlocks);
}

@override@JsonKey(name: 'synthesis_directive') final  String? synthesisDirective;

/// Create a copy of MatrixSynthesisGroup
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MatrixSynthesisGroupCopyWith<_MatrixSynthesisGroup> get copyWith => __$MatrixSynthesisGroupCopyWithImpl<_MatrixSynthesisGroup>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MatrixSynthesisGroupToJson(this, );
}



@override
String toString() {
  return 'MatrixSynthesisGroup(id: $id, title: $title, targetBlocks: $targetBlocks, synthesisDirective: $synthesisDirective)';
}


}

/// @nodoc
abstract mixin class _$MatrixSynthesisGroupCopyWith<$Res> implements $MatrixSynthesisGroupCopyWith<$Res> {
  factory _$MatrixSynthesisGroupCopyWith(_MatrixSynthesisGroup value, $Res Function(_MatrixSynthesisGroup) _then) = __$MatrixSynthesisGroupCopyWithImpl;
@override @useResult
$Res call({
 String id, I18nText title,@JsonKey(name: 'target_blocks') List<String> targetBlocks,@JsonKey(name: 'synthesis_directive') String? synthesisDirective
});


@override $I18nTextCopyWith<$Res> get title;

}
/// @nodoc
class __$MatrixSynthesisGroupCopyWithImpl<$Res>
    implements _$MatrixSynthesisGroupCopyWith<$Res> {
  __$MatrixSynthesisGroupCopyWithImpl(this._self, this._then);

  final _MatrixSynthesisGroup _self;
  final $Res Function(_MatrixSynthesisGroup) _then;

/// Create a copy of MatrixSynthesisGroup
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? title = null,Object? targetBlocks = null,Object? synthesisDirective = freezed,}) {
  return _then(_MatrixSynthesisGroup(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText,targetBlocks: null == targetBlocks ? _self._targetBlocks : targetBlocks // ignore: cast_nullable_to_non_nullable
as List<String>,synthesisDirective: freezed == synthesisDirective ? _self.synthesisDirective : synthesisDirective // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of MatrixSynthesisGroup
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get title {
  
  return $I18nTextCopyWith<$Res>(_self.title, (value) {
    return _then(_self.copyWith(title: value));
  });
}
}


/// @nodoc
mixin _$SynthesisConfigDTO {

@JsonKey(name: 'system_prompt') String? get systemPrompt;@JsonKey(name: 'synthesis_block_id') String? get synthesisBlockId;@JsonKey(name: 'row_explanations_block_id') String? get rowExplanationsBlockId;@JsonKey(name: 'length_constraint') int? get lengthConstraint;@JsonKey(name: 'preamble_text') I18nText? get preambleText;@JsonKey(name: 'tone_instruction') I18nText? get toneInstruction;@JsonKey(name: 'max_quotes_per_matrix') int? get maxQuotesPerMatrix;@JsonKey(name: 'max_unmet_criteria') int? get maxUnmetCriteria;
/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SynthesisConfigDTOCopyWith<SynthesisConfigDTO> get copyWith => _$SynthesisConfigDTOCopyWithImpl<SynthesisConfigDTO>(this as SynthesisConfigDTO, _$identity);

  /// Serializes this SynthesisConfigDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'SynthesisConfigDTO(systemPrompt: $systemPrompt, synthesisBlockId: $synthesisBlockId, rowExplanationsBlockId: $rowExplanationsBlockId, lengthConstraint: $lengthConstraint, preambleText: $preambleText, toneInstruction: $toneInstruction, maxQuotesPerMatrix: $maxQuotesPerMatrix, maxUnmetCriteria: $maxUnmetCriteria)';
}


}

/// @nodoc
abstract mixin class $SynthesisConfigDTOCopyWith<$Res>  {
  factory $SynthesisConfigDTOCopyWith(SynthesisConfigDTO value, $Res Function(SynthesisConfigDTO) _then) = _$SynthesisConfigDTOCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'system_prompt') String? systemPrompt,@JsonKey(name: 'synthesis_block_id') String? synthesisBlockId,@JsonKey(name: 'row_explanations_block_id') String? rowExplanationsBlockId,@JsonKey(name: 'length_constraint') int? lengthConstraint,@JsonKey(name: 'preamble_text') I18nText? preambleText,@JsonKey(name: 'tone_instruction') I18nText? toneInstruction,@JsonKey(name: 'max_quotes_per_matrix') int? maxQuotesPerMatrix,@JsonKey(name: 'max_unmet_criteria') int? maxUnmetCriteria
});


$I18nTextCopyWith<$Res>? get preambleText;$I18nTextCopyWith<$Res>? get toneInstruction;

}
/// @nodoc
class _$SynthesisConfigDTOCopyWithImpl<$Res>
    implements $SynthesisConfigDTOCopyWith<$Res> {
  _$SynthesisConfigDTOCopyWithImpl(this._self, this._then);

  final SynthesisConfigDTO _self;
  final $Res Function(SynthesisConfigDTO) _then;

/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? systemPrompt = freezed,Object? synthesisBlockId = freezed,Object? rowExplanationsBlockId = freezed,Object? lengthConstraint = freezed,Object? preambleText = freezed,Object? toneInstruction = freezed,Object? maxQuotesPerMatrix = freezed,Object? maxUnmetCriteria = freezed,}) {
  return _then(_self.copyWith(
systemPrompt: freezed == systemPrompt ? _self.systemPrompt : systemPrompt // ignore: cast_nullable_to_non_nullable
as String?,synthesisBlockId: freezed == synthesisBlockId ? _self.synthesisBlockId : synthesisBlockId // ignore: cast_nullable_to_non_nullable
as String?,rowExplanationsBlockId: freezed == rowExplanationsBlockId ? _self.rowExplanationsBlockId : rowExplanationsBlockId // ignore: cast_nullable_to_non_nullable
as String?,lengthConstraint: freezed == lengthConstraint ? _self.lengthConstraint : lengthConstraint // ignore: cast_nullable_to_non_nullable
as int?,preambleText: freezed == preambleText ? _self.preambleText : preambleText // ignore: cast_nullable_to_non_nullable
as I18nText?,toneInstruction: freezed == toneInstruction ? _self.toneInstruction : toneInstruction // ignore: cast_nullable_to_non_nullable
as I18nText?,maxQuotesPerMatrix: freezed == maxQuotesPerMatrix ? _self.maxQuotesPerMatrix : maxQuotesPerMatrix // ignore: cast_nullable_to_non_nullable
as int?,maxUnmetCriteria: freezed == maxUnmetCriteria ? _self.maxUnmetCriteria : maxUnmetCriteria // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}
/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get preambleText {
    if (_self.preambleText == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.preambleText!, (value) {
    return _then(_self.copyWith(preambleText: value));
  });
}/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get toneInstruction {
    if (_self.toneInstruction == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.toneInstruction!, (value) {
    return _then(_self.copyWith(toneInstruction: value));
  });
}
}


/// Adds pattern-matching-related methods to [SynthesisConfigDTO].
extension SynthesisConfigDTOPatterns on SynthesisConfigDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SynthesisConfigDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SynthesisConfigDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SynthesisConfigDTO value)  $default,){
final _that = this;
switch (_that) {
case _SynthesisConfigDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SynthesisConfigDTO value)?  $default,){
final _that = this;
switch (_that) {
case _SynthesisConfigDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'system_prompt')  String? systemPrompt, @JsonKey(name: 'synthesis_block_id')  String? synthesisBlockId, @JsonKey(name: 'row_explanations_block_id')  String? rowExplanationsBlockId, @JsonKey(name: 'length_constraint')  int? lengthConstraint, @JsonKey(name: 'preamble_text')  I18nText? preambleText, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction, @JsonKey(name: 'max_quotes_per_matrix')  int? maxQuotesPerMatrix, @JsonKey(name: 'max_unmet_criteria')  int? maxUnmetCriteria)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SynthesisConfigDTO() when $default != null:
return $default(_that.systemPrompt,_that.synthesisBlockId,_that.rowExplanationsBlockId,_that.lengthConstraint,_that.preambleText,_that.toneInstruction,_that.maxQuotesPerMatrix,_that.maxUnmetCriteria);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'system_prompt')  String? systemPrompt, @JsonKey(name: 'synthesis_block_id')  String? synthesisBlockId, @JsonKey(name: 'row_explanations_block_id')  String? rowExplanationsBlockId, @JsonKey(name: 'length_constraint')  int? lengthConstraint, @JsonKey(name: 'preamble_text')  I18nText? preambleText, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction, @JsonKey(name: 'max_quotes_per_matrix')  int? maxQuotesPerMatrix, @JsonKey(name: 'max_unmet_criteria')  int? maxUnmetCriteria)  $default,) {final _that = this;
switch (_that) {
case _SynthesisConfigDTO():
return $default(_that.systemPrompt,_that.synthesisBlockId,_that.rowExplanationsBlockId,_that.lengthConstraint,_that.preambleText,_that.toneInstruction,_that.maxQuotesPerMatrix,_that.maxUnmetCriteria);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'system_prompt')  String? systemPrompt, @JsonKey(name: 'synthesis_block_id')  String? synthesisBlockId, @JsonKey(name: 'row_explanations_block_id')  String? rowExplanationsBlockId, @JsonKey(name: 'length_constraint')  int? lengthConstraint, @JsonKey(name: 'preamble_text')  I18nText? preambleText, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction, @JsonKey(name: 'max_quotes_per_matrix')  int? maxQuotesPerMatrix, @JsonKey(name: 'max_unmet_criteria')  int? maxUnmetCriteria)?  $default,) {final _that = this;
switch (_that) {
case _SynthesisConfigDTO() when $default != null:
return $default(_that.systemPrompt,_that.synthesisBlockId,_that.rowExplanationsBlockId,_that.lengthConstraint,_that.preambleText,_that.toneInstruction,_that.maxQuotesPerMatrix,_that.maxUnmetCriteria);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _SynthesisConfigDTO extends SynthesisConfigDTO {
  const _SynthesisConfigDTO({@JsonKey(name: 'system_prompt') this.systemPrompt, @JsonKey(name: 'synthesis_block_id') this.synthesisBlockId, @JsonKey(name: 'row_explanations_block_id') this.rowExplanationsBlockId, @JsonKey(name: 'length_constraint') this.lengthConstraint, @JsonKey(name: 'preamble_text') this.preambleText, @JsonKey(name: 'tone_instruction') this.toneInstruction, @JsonKey(name: 'max_quotes_per_matrix') this.maxQuotesPerMatrix, @JsonKey(name: 'max_unmet_criteria') this.maxUnmetCriteria}): super._();
  factory _SynthesisConfigDTO.fromJson(Map<String, dynamic> json) => _$SynthesisConfigDTOFromJson(json);

@override@JsonKey(name: 'system_prompt') final  String? systemPrompt;
@override@JsonKey(name: 'synthesis_block_id') final  String? synthesisBlockId;
@override@JsonKey(name: 'row_explanations_block_id') final  String? rowExplanationsBlockId;
@override@JsonKey(name: 'length_constraint') final  int? lengthConstraint;
@override@JsonKey(name: 'preamble_text') final  I18nText? preambleText;
@override@JsonKey(name: 'tone_instruction') final  I18nText? toneInstruction;
@override@JsonKey(name: 'max_quotes_per_matrix') final  int? maxQuotesPerMatrix;
@override@JsonKey(name: 'max_unmet_criteria') final  int? maxUnmetCriteria;

/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SynthesisConfigDTOCopyWith<_SynthesisConfigDTO> get copyWith => __$SynthesisConfigDTOCopyWithImpl<_SynthesisConfigDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SynthesisConfigDTOToJson(this, );
}



@override
String toString() {
  return 'SynthesisConfigDTO(systemPrompt: $systemPrompt, synthesisBlockId: $synthesisBlockId, rowExplanationsBlockId: $rowExplanationsBlockId, lengthConstraint: $lengthConstraint, preambleText: $preambleText, toneInstruction: $toneInstruction, maxQuotesPerMatrix: $maxQuotesPerMatrix, maxUnmetCriteria: $maxUnmetCriteria)';
}


}

/// @nodoc
abstract mixin class _$SynthesisConfigDTOCopyWith<$Res> implements $SynthesisConfigDTOCopyWith<$Res> {
  factory _$SynthesisConfigDTOCopyWith(_SynthesisConfigDTO value, $Res Function(_SynthesisConfigDTO) _then) = __$SynthesisConfigDTOCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'system_prompt') String? systemPrompt,@JsonKey(name: 'synthesis_block_id') String? synthesisBlockId,@JsonKey(name: 'row_explanations_block_id') String? rowExplanationsBlockId,@JsonKey(name: 'length_constraint') int? lengthConstraint,@JsonKey(name: 'preamble_text') I18nText? preambleText,@JsonKey(name: 'tone_instruction') I18nText? toneInstruction,@JsonKey(name: 'max_quotes_per_matrix') int? maxQuotesPerMatrix,@JsonKey(name: 'max_unmet_criteria') int? maxUnmetCriteria
});


@override $I18nTextCopyWith<$Res>? get preambleText;@override $I18nTextCopyWith<$Res>? get toneInstruction;

}
/// @nodoc
class __$SynthesisConfigDTOCopyWithImpl<$Res>
    implements _$SynthesisConfigDTOCopyWith<$Res> {
  __$SynthesisConfigDTOCopyWithImpl(this._self, this._then);

  final _SynthesisConfigDTO _self;
  final $Res Function(_SynthesisConfigDTO) _then;

/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? systemPrompt = freezed,Object? synthesisBlockId = freezed,Object? rowExplanationsBlockId = freezed,Object? lengthConstraint = freezed,Object? preambleText = freezed,Object? toneInstruction = freezed,Object? maxQuotesPerMatrix = freezed,Object? maxUnmetCriteria = freezed,}) {
  return _then(_SynthesisConfigDTO(
systemPrompt: freezed == systemPrompt ? _self.systemPrompt : systemPrompt // ignore: cast_nullable_to_non_nullable
as String?,synthesisBlockId: freezed == synthesisBlockId ? _self.synthesisBlockId : synthesisBlockId // ignore: cast_nullable_to_non_nullable
as String?,rowExplanationsBlockId: freezed == rowExplanationsBlockId ? _self.rowExplanationsBlockId : rowExplanationsBlockId // ignore: cast_nullable_to_non_nullable
as String?,lengthConstraint: freezed == lengthConstraint ? _self.lengthConstraint : lengthConstraint // ignore: cast_nullable_to_non_nullable
as int?,preambleText: freezed == preambleText ? _self.preambleText : preambleText // ignore: cast_nullable_to_non_nullable
as I18nText?,toneInstruction: freezed == toneInstruction ? _self.toneInstruction : toneInstruction // ignore: cast_nullable_to_non_nullable
as I18nText?,maxQuotesPerMatrix: freezed == maxQuotesPerMatrix ? _self.maxQuotesPerMatrix : maxQuotesPerMatrix // ignore: cast_nullable_to_non_nullable
as int?,maxUnmetCriteria: freezed == maxUnmetCriteria ? _self.maxUnmetCriteria : maxUnmetCriteria // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get preambleText {
    if (_self.preambleText == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.preambleText!, (value) {
    return _then(_self.copyWith(preambleText: value));
  });
}/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get toneInstruction {
    if (_self.toneInstruction == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.toneInstruction!, (value) {
    return _then(_self.copyWith(toneInstruction: value));
  });
}
}


/// @nodoc
mixin _$OutputProfile {

@StrictOpaqueIdConverter() String get id; String get slug;@StrictOpaqueIdConverter() String get workflowId; String? get organizationId; I18nText get name; I18nText? get description;@JsonKey(name: 'user_role_label') I18nText? get userRoleLabel;@JsonKey(name: 'custom_preface') I18nText? get customPreface; List<String> get visibleMetadata; List<XaiExtensionType> get visibleBlockExtensions; List<XaiExtensionType> get visibleWorkflowExtensions;@JsonKey(name: 'max_extension_items') int get maxExtensionItems;@JsonKey(name: 'display_scale') DisplayScale get displayScale;@JsonKey(name: 'custom_scale_min') double? get customScaleMin;@JsonKey(name: 'custom_scale_max') double? get customScaleMax;@JsonKey(name: 'strictness_level') int? get strictnessLevel;@JsonKey(name: 'scoring_strategy') ScoringStrategy? get scoringStrategy;@JsonKey(name: 'tone_instruction') I18nText? get toneInstruction; String? get language;@JsonKey(name: 'matrix_synthesis_groups') List<MatrixSynthesisGroup> get matrixSynthesisGroups;@JsonKey(name: 'content_blocks') List<SduiBlockDTO> get contentBlocks;@JsonKey(name: 'target_block_order') List<TargetBlockType> get targetBlockOrder; SynthesisConfigDTO? get synthesis;@JsonKey(name: 'performativity_detector_step_id') String? get performativityDetectorStepId;
/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OutputProfileCopyWith<OutputProfile> get copyWith => _$OutputProfileCopyWithImpl<OutputProfile>(this as OutputProfile, _$identity);

  /// Serializes this OutputProfile to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'OutputProfile(id: $id, slug: $slug, workflowId: $workflowId, organizationId: $organizationId, name: $name, description: $description, userRoleLabel: $userRoleLabel, customPreface: $customPreface, visibleMetadata: $visibleMetadata, visibleBlockExtensions: $visibleBlockExtensions, visibleWorkflowExtensions: $visibleWorkflowExtensions, maxExtensionItems: $maxExtensionItems, displayScale: $displayScale, customScaleMin: $customScaleMin, customScaleMax: $customScaleMax, strictnessLevel: $strictnessLevel, scoringStrategy: $scoringStrategy, toneInstruction: $toneInstruction, language: $language, matrixSynthesisGroups: $matrixSynthesisGroups, contentBlocks: $contentBlocks, targetBlockOrder: $targetBlockOrder, synthesis: $synthesis, performativityDetectorStepId: $performativityDetectorStepId)';
}


}

/// @nodoc
abstract mixin class $OutputProfileCopyWith<$Res>  {
  factory $OutputProfileCopyWith(OutputProfile value, $Res Function(OutputProfile) _then) = _$OutputProfileCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug,@StrictOpaqueIdConverter() String workflowId, String? organizationId, I18nText name, I18nText? description,@JsonKey(name: 'user_role_label') I18nText? userRoleLabel,@JsonKey(name: 'custom_preface') I18nText? customPreface, List<String> visibleMetadata, List<XaiExtensionType> visibleBlockExtensions, List<XaiExtensionType> visibleWorkflowExtensions,@JsonKey(name: 'max_extension_items') int maxExtensionItems,@JsonKey(name: 'display_scale') DisplayScale displayScale,@JsonKey(name: 'custom_scale_min') double? customScaleMin,@JsonKey(name: 'custom_scale_max') double? customScaleMax,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,@JsonKey(name: 'tone_instruction') I18nText? toneInstruction, String? language,@JsonKey(name: 'matrix_synthesis_groups') List<MatrixSynthesisGroup> matrixSynthesisGroups,@JsonKey(name: 'content_blocks') List<SduiBlockDTO> contentBlocks,@JsonKey(name: 'target_block_order') List<TargetBlockType> targetBlockOrder, SynthesisConfigDTO? synthesis,@JsonKey(name: 'performativity_detector_step_id') String? performativityDetectorStepId
});


$I18nTextCopyWith<$Res> get name;$I18nTextCopyWith<$Res>? get description;$I18nTextCopyWith<$Res>? get userRoleLabel;$I18nTextCopyWith<$Res>? get customPreface;$I18nTextCopyWith<$Res>? get toneInstruction;$SynthesisConfigDTOCopyWith<$Res>? get synthesis;

}
/// @nodoc
class _$OutputProfileCopyWithImpl<$Res>
    implements $OutputProfileCopyWith<$Res> {
  _$OutputProfileCopyWithImpl(this._self, this._then);

  final OutputProfile _self;
  final $Res Function(OutputProfile) _then;

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? workflowId = null,Object? organizationId = freezed,Object? name = null,Object? description = freezed,Object? userRoleLabel = freezed,Object? customPreface = freezed,Object? visibleMetadata = null,Object? visibleBlockExtensions = null,Object? visibleWorkflowExtensions = null,Object? maxExtensionItems = null,Object? displayScale = null,Object? customScaleMin = freezed,Object? customScaleMax = freezed,Object? strictnessLevel = freezed,Object? scoringStrategy = freezed,Object? toneInstruction = freezed,Object? language = freezed,Object? matrixSynthesisGroups = null,Object? contentBlocks = null,Object? targetBlockOrder = null,Object? synthesis = freezed,Object? performativityDetectorStepId = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,userRoleLabel: freezed == userRoleLabel ? _self.userRoleLabel : userRoleLabel // ignore: cast_nullable_to_non_nullable
as I18nText?,customPreface: freezed == customPreface ? _self.customPreface : customPreface // ignore: cast_nullable_to_non_nullable
as I18nText?,visibleMetadata: null == visibleMetadata ? _self.visibleMetadata : visibleMetadata // ignore: cast_nullable_to_non_nullable
as List<String>,visibleBlockExtensions: null == visibleBlockExtensions ? _self.visibleBlockExtensions : visibleBlockExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,visibleWorkflowExtensions: null == visibleWorkflowExtensions ? _self.visibleWorkflowExtensions : visibleWorkflowExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,maxExtensionItems: null == maxExtensionItems ? _self.maxExtensionItems : maxExtensionItems // ignore: cast_nullable_to_non_nullable
as int,displayScale: null == displayScale ? _self.displayScale : displayScale // ignore: cast_nullable_to_non_nullable
as DisplayScale,customScaleMin: freezed == customScaleMin ? _self.customScaleMin : customScaleMin // ignore: cast_nullable_to_non_nullable
as double?,customScaleMax: freezed == customScaleMax ? _self.customScaleMax : customScaleMax // ignore: cast_nullable_to_non_nullable
as double?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy?,toneInstruction: freezed == toneInstruction ? _self.toneInstruction : toneInstruction // ignore: cast_nullable_to_non_nullable
as I18nText?,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String?,matrixSynthesisGroups: null == matrixSynthesisGroups ? _self.matrixSynthesisGroups : matrixSynthesisGroups // ignore: cast_nullable_to_non_nullable
as List<MatrixSynthesisGroup>,contentBlocks: null == contentBlocks ? _self.contentBlocks : contentBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,targetBlockOrder: null == targetBlockOrder ? _self.targetBlockOrder : targetBlockOrder // ignore: cast_nullable_to_non_nullable
as List<TargetBlockType>,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as SynthesisConfigDTO?,performativityDetectorStepId: freezed == performativityDetectorStepId ? _self.performativityDetectorStepId : performativityDetectorStepId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get description {
    if (_self.description == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.description!, (value) {
    return _then(_self.copyWith(description: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get userRoleLabel {
    if (_self.userRoleLabel == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.userRoleLabel!, (value) {
    return _then(_self.copyWith(userRoleLabel: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get customPreface {
    if (_self.customPreface == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.customPreface!, (value) {
    return _then(_self.copyWith(customPreface: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get toneInstruction {
    if (_self.toneInstruction == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.toneInstruction!, (value) {
    return _then(_self.copyWith(toneInstruction: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SynthesisConfigDTOCopyWith<$Res>? get synthesis {
    if (_self.synthesis == null) {
    return null;
  }

  return $SynthesisConfigDTOCopyWith<$Res>(_self.synthesis!, (value) {
    return _then(_self.copyWith(synthesis: value));
  });
}
}


/// Adds pattern-matching-related methods to [OutputProfile].
extension OutputProfilePatterns on OutputProfile {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OutputProfile value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OutputProfile value)  $default,){
final _that = this;
switch (_that) {
case _OutputProfile():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OutputProfile value)?  $default,){
final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()  String workflowId,  String? organizationId,  I18nText name,  I18nText? description, @JsonKey(name: 'user_role_label')  I18nText? userRoleLabel, @JsonKey(name: 'custom_preface')  I18nText? customPreface,  List<String> visibleMetadata,  List<XaiExtensionType> visibleBlockExtensions,  List<XaiExtensionType> visibleWorkflowExtensions, @JsonKey(name: 'max_extension_items')  int maxExtensionItems, @JsonKey(name: 'display_scale')  DisplayScale displayScale, @JsonKey(name: 'custom_scale_min')  double? customScaleMin, @JsonKey(name: 'custom_scale_max')  double? customScaleMax, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction,  String? language, @JsonKey(name: 'matrix_synthesis_groups')  List<MatrixSynthesisGroup> matrixSynthesisGroups, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks, @JsonKey(name: 'target_block_order')  List<TargetBlockType> targetBlockOrder,  SynthesisConfigDTO? synthesis, @JsonKey(name: 'performativity_detector_step_id')  String? performativityDetectorStepId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
return $default(_that.id,_that.slug,_that.workflowId,_that.organizationId,_that.name,_that.description,_that.userRoleLabel,_that.customPreface,_that.visibleMetadata,_that.visibleBlockExtensions,_that.visibleWorkflowExtensions,_that.maxExtensionItems,_that.displayScale,_that.customScaleMin,_that.customScaleMax,_that.strictnessLevel,_that.scoringStrategy,_that.toneInstruction,_that.language,_that.matrixSynthesisGroups,_that.contentBlocks,_that.targetBlockOrder,_that.synthesis,_that.performativityDetectorStepId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()  String workflowId,  String? organizationId,  I18nText name,  I18nText? description, @JsonKey(name: 'user_role_label')  I18nText? userRoleLabel, @JsonKey(name: 'custom_preface')  I18nText? customPreface,  List<String> visibleMetadata,  List<XaiExtensionType> visibleBlockExtensions,  List<XaiExtensionType> visibleWorkflowExtensions, @JsonKey(name: 'max_extension_items')  int maxExtensionItems, @JsonKey(name: 'display_scale')  DisplayScale displayScale, @JsonKey(name: 'custom_scale_min')  double? customScaleMin, @JsonKey(name: 'custom_scale_max')  double? customScaleMax, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction,  String? language, @JsonKey(name: 'matrix_synthesis_groups')  List<MatrixSynthesisGroup> matrixSynthesisGroups, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks, @JsonKey(name: 'target_block_order')  List<TargetBlockType> targetBlockOrder,  SynthesisConfigDTO? synthesis, @JsonKey(name: 'performativity_detector_step_id')  String? performativityDetectorStepId)  $default,) {final _that = this;
switch (_that) {
case _OutputProfile():
return $default(_that.id,_that.slug,_that.workflowId,_that.organizationId,_that.name,_that.description,_that.userRoleLabel,_that.customPreface,_that.visibleMetadata,_that.visibleBlockExtensions,_that.visibleWorkflowExtensions,_that.maxExtensionItems,_that.displayScale,_that.customScaleMin,_that.customScaleMax,_that.strictnessLevel,_that.scoringStrategy,_that.toneInstruction,_that.language,_that.matrixSynthesisGroups,_that.contentBlocks,_that.targetBlockOrder,_that.synthesis,_that.performativityDetectorStepId);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()  String workflowId,  String? organizationId,  I18nText name,  I18nText? description, @JsonKey(name: 'user_role_label')  I18nText? userRoleLabel, @JsonKey(name: 'custom_preface')  I18nText? customPreface,  List<String> visibleMetadata,  List<XaiExtensionType> visibleBlockExtensions,  List<XaiExtensionType> visibleWorkflowExtensions, @JsonKey(name: 'max_extension_items')  int maxExtensionItems, @JsonKey(name: 'display_scale')  DisplayScale displayScale, @JsonKey(name: 'custom_scale_min')  double? customScaleMin, @JsonKey(name: 'custom_scale_max')  double? customScaleMax, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction,  String? language, @JsonKey(name: 'matrix_synthesis_groups')  List<MatrixSynthesisGroup> matrixSynthesisGroups, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks, @JsonKey(name: 'target_block_order')  List<TargetBlockType> targetBlockOrder,  SynthesisConfigDTO? synthesis, @JsonKey(name: 'performativity_detector_step_id')  String? performativityDetectorStepId)?  $default,) {final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
return $default(_that.id,_that.slug,_that.workflowId,_that.organizationId,_that.name,_that.description,_that.userRoleLabel,_that.customPreface,_that.visibleMetadata,_that.visibleBlockExtensions,_that.visibleWorkflowExtensions,_that.maxExtensionItems,_that.displayScale,_that.customScaleMin,_that.customScaleMax,_that.strictnessLevel,_that.scoringStrategy,_that.toneInstruction,_that.language,_that.matrixSynthesisGroups,_that.contentBlocks,_that.targetBlockOrder,_that.synthesis,_that.performativityDetectorStepId);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _OutputProfile extends OutputProfile {
  const _OutputProfile({@StrictOpaqueIdConverter() required this.id, this.slug = '', @StrictOpaqueIdConverter() required this.workflowId, this.organizationId, required this.name, this.description, @JsonKey(name: 'user_role_label') this.userRoleLabel, @JsonKey(name: 'custom_preface') this.customPreface, final  List<String> visibleMetadata = const ['date', 'organization'], final  List<XaiExtensionType> visibleBlockExtensions = const [], final  List<XaiExtensionType> visibleWorkflowExtensions = const [], @JsonKey(name: 'max_extension_items') this.maxExtensionItems = 3, @JsonKey(name: 'display_scale') this.displayScale = DisplayScale.original, @JsonKey(name: 'custom_scale_min') this.customScaleMin, @JsonKey(name: 'custom_scale_max') this.customScaleMax, @JsonKey(name: 'strictness_level') this.strictnessLevel, @JsonKey(name: 'scoring_strategy') this.scoringStrategy, @JsonKey(name: 'tone_instruction') this.toneInstruction, this.language, @JsonKey(name: 'matrix_synthesis_groups') final  List<MatrixSynthesisGroup> matrixSynthesisGroups = const [], @JsonKey(name: 'content_blocks') final  List<SduiBlockDTO> contentBlocks = const [], @JsonKey(name: 'target_block_order') final  List<TargetBlockType> targetBlockOrder = const [TargetBlockType.metadataBlock, TargetBlockType.executiveSummaryBlock, TargetBlockType.synthesisTextBlock, TargetBlockType.matrixGraphsBlock, TargetBlockType.groupedExtensionsBlock, TargetBlockType.penaltiesBlock, TargetBlockType.matrixSummaryTableBlock, TargetBlockType.varianceValidationBlock, TargetBlockType.authenticityEvaluationBlock, TargetBlockType.printableSourcesBlock, TargetBlockType.globalScoreBlock, TargetBlockType.auditTrailBlock], this.synthesis, @JsonKey(name: 'performativity_detector_step_id') this.performativityDetectorStepId}): _visibleMetadata = visibleMetadata,_visibleBlockExtensions = visibleBlockExtensions,_visibleWorkflowExtensions = visibleWorkflowExtensions,_matrixSynthesisGroups = matrixSynthesisGroups,_contentBlocks = contentBlocks,_targetBlockOrder = targetBlockOrder,super._();
  factory _OutputProfile.fromJson(Map<String, dynamic> json) => _$OutputProfileFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override@JsonKey() final  String slug;
@override@StrictOpaqueIdConverter() final  String workflowId;
@override final  String? organizationId;
@override final  I18nText name;
@override final  I18nText? description;
@override@JsonKey(name: 'user_role_label') final  I18nText? userRoleLabel;
@override@JsonKey(name: 'custom_preface') final  I18nText? customPreface;
 final  List<String> _visibleMetadata;
@override@JsonKey() List<String> get visibleMetadata {
  if (_visibleMetadata is EqualUnmodifiableListView) return _visibleMetadata;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleMetadata);
}

 final  List<XaiExtensionType> _visibleBlockExtensions;
@override@JsonKey() List<XaiExtensionType> get visibleBlockExtensions {
  if (_visibleBlockExtensions is EqualUnmodifiableListView) return _visibleBlockExtensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleBlockExtensions);
}

 final  List<XaiExtensionType> _visibleWorkflowExtensions;
@override@JsonKey() List<XaiExtensionType> get visibleWorkflowExtensions {
  if (_visibleWorkflowExtensions is EqualUnmodifiableListView) return _visibleWorkflowExtensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleWorkflowExtensions);
}

@override@JsonKey(name: 'max_extension_items') final  int maxExtensionItems;
@override@JsonKey(name: 'display_scale') final  DisplayScale displayScale;
@override@JsonKey(name: 'custom_scale_min') final  double? customScaleMin;
@override@JsonKey(name: 'custom_scale_max') final  double? customScaleMax;
@override@JsonKey(name: 'strictness_level') final  int? strictnessLevel;
@override@JsonKey(name: 'scoring_strategy') final  ScoringStrategy? scoringStrategy;
@override@JsonKey(name: 'tone_instruction') final  I18nText? toneInstruction;
@override final  String? language;
 final  List<MatrixSynthesisGroup> _matrixSynthesisGroups;
@override@JsonKey(name: 'matrix_synthesis_groups') List<MatrixSynthesisGroup> get matrixSynthesisGroups {
  if (_matrixSynthesisGroups is EqualUnmodifiableListView) return _matrixSynthesisGroups;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_matrixSynthesisGroups);
}

 final  List<SduiBlockDTO> _contentBlocks;
@override@JsonKey(name: 'content_blocks') List<SduiBlockDTO> get contentBlocks {
  if (_contentBlocks is EqualUnmodifiableListView) return _contentBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_contentBlocks);
}

 final  List<TargetBlockType> _targetBlockOrder;
@override@JsonKey(name: 'target_block_order') List<TargetBlockType> get targetBlockOrder {
  if (_targetBlockOrder is EqualUnmodifiableListView) return _targetBlockOrder;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_targetBlockOrder);
}

@override final  SynthesisConfigDTO? synthesis;
@override@JsonKey(name: 'performativity_detector_step_id') final  String? performativityDetectorStepId;

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OutputProfileCopyWith<_OutputProfile> get copyWith => __$OutputProfileCopyWithImpl<_OutputProfile>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OutputProfileToJson(this, );
}



@override
String toString() {
  return 'OutputProfile(id: $id, slug: $slug, workflowId: $workflowId, organizationId: $organizationId, name: $name, description: $description, userRoleLabel: $userRoleLabel, customPreface: $customPreface, visibleMetadata: $visibleMetadata, visibleBlockExtensions: $visibleBlockExtensions, visibleWorkflowExtensions: $visibleWorkflowExtensions, maxExtensionItems: $maxExtensionItems, displayScale: $displayScale, customScaleMin: $customScaleMin, customScaleMax: $customScaleMax, strictnessLevel: $strictnessLevel, scoringStrategy: $scoringStrategy, toneInstruction: $toneInstruction, language: $language, matrixSynthesisGroups: $matrixSynthesisGroups, contentBlocks: $contentBlocks, targetBlockOrder: $targetBlockOrder, synthesis: $synthesis, performativityDetectorStepId: $performativityDetectorStepId)';
}


}

/// @nodoc
abstract mixin class _$OutputProfileCopyWith<$Res> implements $OutputProfileCopyWith<$Res> {
  factory _$OutputProfileCopyWith(_OutputProfile value, $Res Function(_OutputProfile) _then) = __$OutputProfileCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug,@StrictOpaqueIdConverter() String workflowId, String? organizationId, I18nText name, I18nText? description,@JsonKey(name: 'user_role_label') I18nText? userRoleLabel,@JsonKey(name: 'custom_preface') I18nText? customPreface, List<String> visibleMetadata, List<XaiExtensionType> visibleBlockExtensions, List<XaiExtensionType> visibleWorkflowExtensions,@JsonKey(name: 'max_extension_items') int maxExtensionItems,@JsonKey(name: 'display_scale') DisplayScale displayScale,@JsonKey(name: 'custom_scale_min') double? customScaleMin,@JsonKey(name: 'custom_scale_max') double? customScaleMax,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,@JsonKey(name: 'tone_instruction') I18nText? toneInstruction, String? language,@JsonKey(name: 'matrix_synthesis_groups') List<MatrixSynthesisGroup> matrixSynthesisGroups,@JsonKey(name: 'content_blocks') List<SduiBlockDTO> contentBlocks,@JsonKey(name: 'target_block_order') List<TargetBlockType> targetBlockOrder, SynthesisConfigDTO? synthesis,@JsonKey(name: 'performativity_detector_step_id') String? performativityDetectorStepId
});


@override $I18nTextCopyWith<$Res> get name;@override $I18nTextCopyWith<$Res>? get description;@override $I18nTextCopyWith<$Res>? get userRoleLabel;@override $I18nTextCopyWith<$Res>? get customPreface;@override $I18nTextCopyWith<$Res>? get toneInstruction;@override $SynthesisConfigDTOCopyWith<$Res>? get synthesis;

}
/// @nodoc
class __$OutputProfileCopyWithImpl<$Res>
    implements _$OutputProfileCopyWith<$Res> {
  __$OutputProfileCopyWithImpl(this._self, this._then);

  final _OutputProfile _self;
  final $Res Function(_OutputProfile) _then;

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? workflowId = null,Object? organizationId = freezed,Object? name = null,Object? description = freezed,Object? userRoleLabel = freezed,Object? customPreface = freezed,Object? visibleMetadata = null,Object? visibleBlockExtensions = null,Object? visibleWorkflowExtensions = null,Object? maxExtensionItems = null,Object? displayScale = null,Object? customScaleMin = freezed,Object? customScaleMax = freezed,Object? strictnessLevel = freezed,Object? scoringStrategy = freezed,Object? toneInstruction = freezed,Object? language = freezed,Object? matrixSynthesisGroups = null,Object? contentBlocks = null,Object? targetBlockOrder = null,Object? synthesis = freezed,Object? performativityDetectorStepId = freezed,}) {
  return _then(_OutputProfile(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,userRoleLabel: freezed == userRoleLabel ? _self.userRoleLabel : userRoleLabel // ignore: cast_nullable_to_non_nullable
as I18nText?,customPreface: freezed == customPreface ? _self.customPreface : customPreface // ignore: cast_nullable_to_non_nullable
as I18nText?,visibleMetadata: null == visibleMetadata ? _self._visibleMetadata : visibleMetadata // ignore: cast_nullable_to_non_nullable
as List<String>,visibleBlockExtensions: null == visibleBlockExtensions ? _self._visibleBlockExtensions : visibleBlockExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,visibleWorkflowExtensions: null == visibleWorkflowExtensions ? _self._visibleWorkflowExtensions : visibleWorkflowExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,maxExtensionItems: null == maxExtensionItems ? _self.maxExtensionItems : maxExtensionItems // ignore: cast_nullable_to_non_nullable
as int,displayScale: null == displayScale ? _self.displayScale : displayScale // ignore: cast_nullable_to_non_nullable
as DisplayScale,customScaleMin: freezed == customScaleMin ? _self.customScaleMin : customScaleMin // ignore: cast_nullable_to_non_nullable
as double?,customScaleMax: freezed == customScaleMax ? _self.customScaleMax : customScaleMax // ignore: cast_nullable_to_non_nullable
as double?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy?,toneInstruction: freezed == toneInstruction ? _self.toneInstruction : toneInstruction // ignore: cast_nullable_to_non_nullable
as I18nText?,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String?,matrixSynthesisGroups: null == matrixSynthesisGroups ? _self._matrixSynthesisGroups : matrixSynthesisGroups // ignore: cast_nullable_to_non_nullable
as List<MatrixSynthesisGroup>,contentBlocks: null == contentBlocks ? _self._contentBlocks : contentBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,targetBlockOrder: null == targetBlockOrder ? _self._targetBlockOrder : targetBlockOrder // ignore: cast_nullable_to_non_nullable
as List<TargetBlockType>,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as SynthesisConfigDTO?,performativityDetectorStepId: freezed == performativityDetectorStepId ? _self.performativityDetectorStepId : performativityDetectorStepId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get description {
    if (_self.description == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.description!, (value) {
    return _then(_self.copyWith(description: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get userRoleLabel {
    if (_self.userRoleLabel == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.userRoleLabel!, (value) {
    return _then(_self.copyWith(userRoleLabel: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get customPreface {
    if (_self.customPreface == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.customPreface!, (value) {
    return _then(_self.copyWith(customPreface: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get toneInstruction {
    if (_self.toneInstruction == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.toneInstruction!, (value) {
    return _then(_self.copyWith(toneInstruction: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SynthesisConfigDTOCopyWith<$Res>? get synthesis {
    if (_self.synthesis == null) {
    return null;
  }

  return $SynthesisConfigDTOCopyWith<$Res>(_self.synthesis!, (value) {
    return _then(_self.copyWith(synthesis: value));
  });
}
}

// dart format on
