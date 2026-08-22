// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'prompt_block.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$TheoryGrounding {

 String get sourceUrl; String? get citationReference;
/// Create a copy of TheoryGrounding
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TheoryGroundingCopyWith<TheoryGrounding> get copyWith => _$TheoryGroundingCopyWithImpl<TheoryGrounding>(this as TheoryGrounding, _$identity);

  /// Serializes this TheoryGrounding to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'TheoryGrounding(sourceUrl: $sourceUrl, citationReference: $citationReference)';
}


}

/// @nodoc
abstract mixin class $TheoryGroundingCopyWith<$Res>  {
  factory $TheoryGroundingCopyWith(TheoryGrounding value, $Res Function(TheoryGrounding) _then) = _$TheoryGroundingCopyWithImpl;
@useResult
$Res call({
 String sourceUrl, String? citationReference
});




}
/// @nodoc
class _$TheoryGroundingCopyWithImpl<$Res>
    implements $TheoryGroundingCopyWith<$Res> {
  _$TheoryGroundingCopyWithImpl(this._self, this._then);

  final TheoryGrounding _self;
  final $Res Function(TheoryGrounding) _then;

/// Create a copy of TheoryGrounding
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? sourceUrl = null,Object? citationReference = freezed,}) {
  return _then(_self.copyWith(
sourceUrl: null == sourceUrl ? _self.sourceUrl : sourceUrl // ignore: cast_nullable_to_non_nullable
as String,citationReference: freezed == citationReference ? _self.citationReference : citationReference // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [TheoryGrounding].
extension TheoryGroundingPatterns on TheoryGrounding {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TheoryGrounding value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TheoryGrounding() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TheoryGrounding value)  $default,){
final _that = this;
switch (_that) {
case _TheoryGrounding():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TheoryGrounding value)?  $default,){
final _that = this;
switch (_that) {
case _TheoryGrounding() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String sourceUrl,  String? citationReference)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TheoryGrounding() when $default != null:
return $default(_that.sourceUrl,_that.citationReference);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String sourceUrl,  String? citationReference)  $default,) {final _that = this;
switch (_that) {
case _TheoryGrounding():
return $default(_that.sourceUrl,_that.citationReference);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String sourceUrl,  String? citationReference)?  $default,) {final _that = this;
switch (_that) {
case _TheoryGrounding() when $default != null:
return $default(_that.sourceUrl,_that.citationReference);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _TheoryGrounding extends TheoryGrounding {
  const _TheoryGrounding({required this.sourceUrl, this.citationReference}): super._();
  factory _TheoryGrounding.fromJson(Map<String, dynamic> json) => _$TheoryGroundingFromJson(json);

@override final  String sourceUrl;
@override final  String? citationReference;

/// Create a copy of TheoryGrounding
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TheoryGroundingCopyWith<_TheoryGrounding> get copyWith => __$TheoryGroundingCopyWithImpl<_TheoryGrounding>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TheoryGroundingToJson(this, );
}



@override
String toString() {
  return 'TheoryGrounding(sourceUrl: $sourceUrl, citationReference: $citationReference)';
}


}

/// @nodoc
abstract mixin class _$TheoryGroundingCopyWith<$Res> implements $TheoryGroundingCopyWith<$Res> {
  factory _$TheoryGroundingCopyWith(_TheoryGrounding value, $Res Function(_TheoryGrounding) _then) = __$TheoryGroundingCopyWithImpl;
@override @useResult
$Res call({
 String sourceUrl, String? citationReference
});




}
/// @nodoc
class __$TheoryGroundingCopyWithImpl<$Res>
    implements _$TheoryGroundingCopyWith<$Res> {
  __$TheoryGroundingCopyWithImpl(this._self, this._then);

  final _TheoryGrounding _self;
  final $Res Function(_TheoryGrounding) _then;

/// Create a copy of TheoryGrounding
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? sourceUrl = null,Object? citationReference = freezed,}) {
  return _then(_TheoryGrounding(
sourceUrl: null == sourceUrl ? _self.sourceUrl : sourceUrl // ignore: cast_nullable_to_non_nullable
as String,citationReference: freezed == citationReference ? _self.citationReference : citationReference // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$AcceptanceCriterion {

 String get instruction;@JsonKey(name: 'requires_contextual_override') bool get requiresContextualOverride;
/// Create a copy of AcceptanceCriterion
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AcceptanceCriterionCopyWith<AcceptanceCriterion> get copyWith => _$AcceptanceCriterionCopyWithImpl<AcceptanceCriterion>(this as AcceptanceCriterion, _$identity);

  /// Serializes this AcceptanceCriterion to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'AcceptanceCriterion(instruction: $instruction, requiresContextualOverride: $requiresContextualOverride)';
}


}

/// @nodoc
abstract mixin class $AcceptanceCriterionCopyWith<$Res>  {
  factory $AcceptanceCriterionCopyWith(AcceptanceCriterion value, $Res Function(AcceptanceCriterion) _then) = _$AcceptanceCriterionCopyWithImpl;
@useResult
$Res call({
 String instruction,@JsonKey(name: 'requires_contextual_override') bool requiresContextualOverride
});




}
/// @nodoc
class _$AcceptanceCriterionCopyWithImpl<$Res>
    implements $AcceptanceCriterionCopyWith<$Res> {
  _$AcceptanceCriterionCopyWithImpl(this._self, this._then);

  final AcceptanceCriterion _self;
  final $Res Function(AcceptanceCriterion) _then;

/// Create a copy of AcceptanceCriterion
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? instruction = null,Object? requiresContextualOverride = null,}) {
  return _then(_self.copyWith(
instruction: null == instruction ? _self.instruction : instruction // ignore: cast_nullable_to_non_nullable
as String,requiresContextualOverride: null == requiresContextualOverride ? _self.requiresContextualOverride : requiresContextualOverride // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [AcceptanceCriterion].
extension AcceptanceCriterionPatterns on AcceptanceCriterion {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AcceptanceCriterion value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AcceptanceCriterion() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AcceptanceCriterion value)  $default,){
final _that = this;
switch (_that) {
case _AcceptanceCriterion():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AcceptanceCriterion value)?  $default,){
final _that = this;
switch (_that) {
case _AcceptanceCriterion() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String instruction, @JsonKey(name: 'requires_contextual_override')  bool requiresContextualOverride)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AcceptanceCriterion() when $default != null:
return $default(_that.instruction,_that.requiresContextualOverride);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String instruction, @JsonKey(name: 'requires_contextual_override')  bool requiresContextualOverride)  $default,) {final _that = this;
switch (_that) {
case _AcceptanceCriterion():
return $default(_that.instruction,_that.requiresContextualOverride);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String instruction, @JsonKey(name: 'requires_contextual_override')  bool requiresContextualOverride)?  $default,) {final _that = this;
switch (_that) {
case _AcceptanceCriterion() when $default != null:
return $default(_that.instruction,_that.requiresContextualOverride);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _AcceptanceCriterion extends AcceptanceCriterion {
  const _AcceptanceCriterion({required this.instruction, @JsonKey(name: 'requires_contextual_override') this.requiresContextualOverride = false}): super._();
  factory _AcceptanceCriterion.fromJson(Map<String, dynamic> json) => _$AcceptanceCriterionFromJson(json);

@override final  String instruction;
@override@JsonKey(name: 'requires_contextual_override') final  bool requiresContextualOverride;

/// Create a copy of AcceptanceCriterion
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AcceptanceCriterionCopyWith<_AcceptanceCriterion> get copyWith => __$AcceptanceCriterionCopyWithImpl<_AcceptanceCriterion>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AcceptanceCriterionToJson(this, );
}



@override
String toString() {
  return 'AcceptanceCriterion(instruction: $instruction, requiresContextualOverride: $requiresContextualOverride)';
}


}

/// @nodoc
abstract mixin class _$AcceptanceCriterionCopyWith<$Res> implements $AcceptanceCriterionCopyWith<$Res> {
  factory _$AcceptanceCriterionCopyWith(_AcceptanceCriterion value, $Res Function(_AcceptanceCriterion) _then) = __$AcceptanceCriterionCopyWithImpl;
@override @useResult
$Res call({
 String instruction,@JsonKey(name: 'requires_contextual_override') bool requiresContextualOverride
});




}
/// @nodoc
class __$AcceptanceCriterionCopyWithImpl<$Res>
    implements _$AcceptanceCriterionCopyWith<$Res> {
  __$AcceptanceCriterionCopyWithImpl(this._self, this._then);

  final _AcceptanceCriterion _self;
  final $Res Function(_AcceptanceCriterion) _then;

/// Create a copy of AcceptanceCriterion
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? instruction = null,Object? requiresContextualOverride = null,}) {
  return _then(_AcceptanceCriterion(
instruction: null == instruction ? _self.instruction : instruction // ignore: cast_nullable_to_non_nullable
as String,requiresContextualOverride: null == requiresContextualOverride ? _self.requiresContextualOverride : requiresContextualOverride // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$AntiPattern {

 String get pattern;@JsonKey(name: 'allows_contextual_excuse') bool get allowsContextualExcuse;
/// Create a copy of AntiPattern
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AntiPatternCopyWith<AntiPattern> get copyWith => _$AntiPatternCopyWithImpl<AntiPattern>(this as AntiPattern, _$identity);

  /// Serializes this AntiPattern to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'AntiPattern(pattern: $pattern, allowsContextualExcuse: $allowsContextualExcuse)';
}


}

/// @nodoc
abstract mixin class $AntiPatternCopyWith<$Res>  {
  factory $AntiPatternCopyWith(AntiPattern value, $Res Function(AntiPattern) _then) = _$AntiPatternCopyWithImpl;
@useResult
$Res call({
 String pattern,@JsonKey(name: 'allows_contextual_excuse') bool allowsContextualExcuse
});




}
/// @nodoc
class _$AntiPatternCopyWithImpl<$Res>
    implements $AntiPatternCopyWith<$Res> {
  _$AntiPatternCopyWithImpl(this._self, this._then);

  final AntiPattern _self;
  final $Res Function(AntiPattern) _then;

/// Create a copy of AntiPattern
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? pattern = null,Object? allowsContextualExcuse = null,}) {
  return _then(_self.copyWith(
pattern: null == pattern ? _self.pattern : pattern // ignore: cast_nullable_to_non_nullable
as String,allowsContextualExcuse: null == allowsContextualExcuse ? _self.allowsContextualExcuse : allowsContextualExcuse // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [AntiPattern].
extension AntiPatternPatterns on AntiPattern {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AntiPattern value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AntiPattern() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AntiPattern value)  $default,){
final _that = this;
switch (_that) {
case _AntiPattern():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AntiPattern value)?  $default,){
final _that = this;
switch (_that) {
case _AntiPattern() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String pattern, @JsonKey(name: 'allows_contextual_excuse')  bool allowsContextualExcuse)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AntiPattern() when $default != null:
return $default(_that.pattern,_that.allowsContextualExcuse);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String pattern, @JsonKey(name: 'allows_contextual_excuse')  bool allowsContextualExcuse)  $default,) {final _that = this;
switch (_that) {
case _AntiPattern():
return $default(_that.pattern,_that.allowsContextualExcuse);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String pattern, @JsonKey(name: 'allows_contextual_excuse')  bool allowsContextualExcuse)?  $default,) {final _that = this;
switch (_that) {
case _AntiPattern() when $default != null:
return $default(_that.pattern,_that.allowsContextualExcuse);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _AntiPattern extends AntiPattern {
  const _AntiPattern({required this.pattern, @JsonKey(name: 'allows_contextual_excuse') this.allowsContextualExcuse = false}): super._();
  factory _AntiPattern.fromJson(Map<String, dynamic> json) => _$AntiPatternFromJson(json);

@override final  String pattern;
@override@JsonKey(name: 'allows_contextual_excuse') final  bool allowsContextualExcuse;

/// Create a copy of AntiPattern
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AntiPatternCopyWith<_AntiPattern> get copyWith => __$AntiPatternCopyWithImpl<_AntiPattern>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AntiPatternToJson(this, );
}



@override
String toString() {
  return 'AntiPattern(pattern: $pattern, allowsContextualExcuse: $allowsContextualExcuse)';
}


}

/// @nodoc
abstract mixin class _$AntiPatternCopyWith<$Res> implements $AntiPatternCopyWith<$Res> {
  factory _$AntiPatternCopyWith(_AntiPattern value, $Res Function(_AntiPattern) _then) = __$AntiPatternCopyWithImpl;
@override @useResult
$Res call({
 String pattern,@JsonKey(name: 'allows_contextual_excuse') bool allowsContextualExcuse
});




}
/// @nodoc
class __$AntiPatternCopyWithImpl<$Res>
    implements _$AntiPatternCopyWith<$Res> {
  __$AntiPatternCopyWithImpl(this._self, this._then);

  final _AntiPattern _self;
  final $Res Function(_AntiPattern) _then;

/// Create a copy of AntiPattern
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? pattern = null,Object? allowsContextualExcuse = null,}) {
  return _then(_AntiPattern(
pattern: null == pattern ? _self.pattern : pattern // ignore: cast_nullable_to_non_nullable
as String,allowsContextualExcuse: null == allowsContextualExcuse ? _self.allowsContextualExcuse : allowsContextualExcuse // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$TDAAssertion {

@JsonKey(name: 'tda_id') String get tdaId;@JsonKey(name: 'concept_description') String get conceptDescription;@JsonKey(name: 'acceptance_criteria') List<AcceptanceCriterion> get acceptanceCriteria;@JsonKey(name: 'anti_patterns') List<AntiPattern> get antiPatterns;@JsonKey(name: 'contrastive_example') String? get contrastiveExample;@JsonKey(name: 'syntactic_anchors') List<String> get syntacticAnchors;@JsonKey(name: 'enforce_pre_flight') bool get enforcePreFlight;@JsonKey(name: 'inverse_evidence') bool get inverseEvidence;@JsonKey(name: 'aggregation_mode') AggregationMode get aggregationMode;@JsonKey(name: 'evaluation_track') EvaluationTrack get evaluationTrack;@JsonKey(name: 'facts_to_find') List<String> get factsToFind;@JsonKey(name: 'logical_expression') String? get logicalExpression;@JsonKey(name: 'high_entropy') bool get highEntropy;@JsonKey(name: 'anchor_target') String? get anchorTarget;@JsonKey(name: 'bounding_box_scope') String get boundingBoxScope;@JsonKey(name: 'extraction_rule') String? get extractionRule;
/// Create a copy of TDAAssertion
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$TDAAssertionCopyWith<TDAAssertion> get copyWith => _$TDAAssertionCopyWithImpl<TDAAssertion>(this as TDAAssertion, _$identity);

  /// Serializes this TDAAssertion to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'TDAAssertion(tdaId: $tdaId, conceptDescription: $conceptDescription, acceptanceCriteria: $acceptanceCriteria, antiPatterns: $antiPatterns, contrastiveExample: $contrastiveExample, syntacticAnchors: $syntacticAnchors, enforcePreFlight: $enforcePreFlight, inverseEvidence: $inverseEvidence, aggregationMode: $aggregationMode, evaluationTrack: $evaluationTrack, factsToFind: $factsToFind, logicalExpression: $logicalExpression, highEntropy: $highEntropy, anchorTarget: $anchorTarget, boundingBoxScope: $boundingBoxScope, extractionRule: $extractionRule)';
}


}

/// @nodoc
abstract mixin class $TDAAssertionCopyWith<$Res>  {
  factory $TDAAssertionCopyWith(TDAAssertion value, $Res Function(TDAAssertion) _then) = _$TDAAssertionCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'tda_id') String tdaId,@JsonKey(name: 'concept_description') String conceptDescription,@JsonKey(name: 'acceptance_criteria') List<AcceptanceCriterion> acceptanceCriteria,@JsonKey(name: 'anti_patterns') List<AntiPattern> antiPatterns,@JsonKey(name: 'contrastive_example') String? contrastiveExample,@JsonKey(name: 'syntactic_anchors') List<String> syntacticAnchors,@JsonKey(name: 'enforce_pre_flight') bool enforcePreFlight,@JsonKey(name: 'inverse_evidence') bool inverseEvidence,@JsonKey(name: 'aggregation_mode') AggregationMode aggregationMode,@JsonKey(name: 'evaluation_track') EvaluationTrack evaluationTrack,@JsonKey(name: 'facts_to_find') List<String> factsToFind,@JsonKey(name: 'logical_expression') String? logicalExpression,@JsonKey(name: 'high_entropy') bool highEntropy,@JsonKey(name: 'anchor_target') String? anchorTarget,@JsonKey(name: 'bounding_box_scope') String boundingBoxScope,@JsonKey(name: 'extraction_rule') String? extractionRule
});




}
/// @nodoc
class _$TDAAssertionCopyWithImpl<$Res>
    implements $TDAAssertionCopyWith<$Res> {
  _$TDAAssertionCopyWithImpl(this._self, this._then);

  final TDAAssertion _self;
  final $Res Function(TDAAssertion) _then;

/// Create a copy of TDAAssertion
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? tdaId = null,Object? conceptDescription = null,Object? acceptanceCriteria = null,Object? antiPatterns = null,Object? contrastiveExample = freezed,Object? syntacticAnchors = null,Object? enforcePreFlight = null,Object? inverseEvidence = null,Object? aggregationMode = null,Object? evaluationTrack = null,Object? factsToFind = null,Object? logicalExpression = freezed,Object? highEntropy = null,Object? anchorTarget = freezed,Object? boundingBoxScope = null,Object? extractionRule = freezed,}) {
  return _then(_self.copyWith(
tdaId: null == tdaId ? _self.tdaId : tdaId // ignore: cast_nullable_to_non_nullable
as String,conceptDescription: null == conceptDescription ? _self.conceptDescription : conceptDescription // ignore: cast_nullable_to_non_nullable
as String,acceptanceCriteria: null == acceptanceCriteria ? _self.acceptanceCriteria : acceptanceCriteria // ignore: cast_nullable_to_non_nullable
as List<AcceptanceCriterion>,antiPatterns: null == antiPatterns ? _self.antiPatterns : antiPatterns // ignore: cast_nullable_to_non_nullable
as List<AntiPattern>,contrastiveExample: freezed == contrastiveExample ? _self.contrastiveExample : contrastiveExample // ignore: cast_nullable_to_non_nullable
as String?,syntacticAnchors: null == syntacticAnchors ? _self.syntacticAnchors : syntacticAnchors // ignore: cast_nullable_to_non_nullable
as List<String>,enforcePreFlight: null == enforcePreFlight ? _self.enforcePreFlight : enforcePreFlight // ignore: cast_nullable_to_non_nullable
as bool,inverseEvidence: null == inverseEvidence ? _self.inverseEvidence : inverseEvidence // ignore: cast_nullable_to_non_nullable
as bool,aggregationMode: null == aggregationMode ? _self.aggregationMode : aggregationMode // ignore: cast_nullable_to_non_nullable
as AggregationMode,evaluationTrack: null == evaluationTrack ? _self.evaluationTrack : evaluationTrack // ignore: cast_nullable_to_non_nullable
as EvaluationTrack,factsToFind: null == factsToFind ? _self.factsToFind : factsToFind // ignore: cast_nullable_to_non_nullable
as List<String>,logicalExpression: freezed == logicalExpression ? _self.logicalExpression : logicalExpression // ignore: cast_nullable_to_non_nullable
as String?,highEntropy: null == highEntropy ? _self.highEntropy : highEntropy // ignore: cast_nullable_to_non_nullable
as bool,anchorTarget: freezed == anchorTarget ? _self.anchorTarget : anchorTarget // ignore: cast_nullable_to_non_nullable
as String?,boundingBoxScope: null == boundingBoxScope ? _self.boundingBoxScope : boundingBoxScope // ignore: cast_nullable_to_non_nullable
as String,extractionRule: freezed == extractionRule ? _self.extractionRule : extractionRule // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [TDAAssertion].
extension TDAAssertionPatterns on TDAAssertion {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _TDAAssertion value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _TDAAssertion() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _TDAAssertion value)  $default,){
final _that = this;
switch (_that) {
case _TDAAssertion():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _TDAAssertion value)?  $default,){
final _that = this;
switch (_that) {
case _TDAAssertion() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'tda_id')  String tdaId, @JsonKey(name: 'concept_description')  String conceptDescription, @JsonKey(name: 'acceptance_criteria')  List<AcceptanceCriterion> acceptanceCriteria, @JsonKey(name: 'anti_patterns')  List<AntiPattern> antiPatterns, @JsonKey(name: 'contrastive_example')  String? contrastiveExample, @JsonKey(name: 'syntactic_anchors')  List<String> syntacticAnchors, @JsonKey(name: 'enforce_pre_flight')  bool enforcePreFlight, @JsonKey(name: 'inverse_evidence')  bool inverseEvidence, @JsonKey(name: 'aggregation_mode')  AggregationMode aggregationMode, @JsonKey(name: 'evaluation_track')  EvaluationTrack evaluationTrack, @JsonKey(name: 'facts_to_find')  List<String> factsToFind, @JsonKey(name: 'logical_expression')  String? logicalExpression, @JsonKey(name: 'high_entropy')  bool highEntropy, @JsonKey(name: 'anchor_target')  String? anchorTarget, @JsonKey(name: 'bounding_box_scope')  String boundingBoxScope, @JsonKey(name: 'extraction_rule')  String? extractionRule)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _TDAAssertion() when $default != null:
return $default(_that.tdaId,_that.conceptDescription,_that.acceptanceCriteria,_that.antiPatterns,_that.contrastiveExample,_that.syntacticAnchors,_that.enforcePreFlight,_that.inverseEvidence,_that.aggregationMode,_that.evaluationTrack,_that.factsToFind,_that.logicalExpression,_that.highEntropy,_that.anchorTarget,_that.boundingBoxScope,_that.extractionRule);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'tda_id')  String tdaId, @JsonKey(name: 'concept_description')  String conceptDescription, @JsonKey(name: 'acceptance_criteria')  List<AcceptanceCriterion> acceptanceCriteria, @JsonKey(name: 'anti_patterns')  List<AntiPattern> antiPatterns, @JsonKey(name: 'contrastive_example')  String? contrastiveExample, @JsonKey(name: 'syntactic_anchors')  List<String> syntacticAnchors, @JsonKey(name: 'enforce_pre_flight')  bool enforcePreFlight, @JsonKey(name: 'inverse_evidence')  bool inverseEvidence, @JsonKey(name: 'aggregation_mode')  AggregationMode aggregationMode, @JsonKey(name: 'evaluation_track')  EvaluationTrack evaluationTrack, @JsonKey(name: 'facts_to_find')  List<String> factsToFind, @JsonKey(name: 'logical_expression')  String? logicalExpression, @JsonKey(name: 'high_entropy')  bool highEntropy, @JsonKey(name: 'anchor_target')  String? anchorTarget, @JsonKey(name: 'bounding_box_scope')  String boundingBoxScope, @JsonKey(name: 'extraction_rule')  String? extractionRule)  $default,) {final _that = this;
switch (_that) {
case _TDAAssertion():
return $default(_that.tdaId,_that.conceptDescription,_that.acceptanceCriteria,_that.antiPatterns,_that.contrastiveExample,_that.syntacticAnchors,_that.enforcePreFlight,_that.inverseEvidence,_that.aggregationMode,_that.evaluationTrack,_that.factsToFind,_that.logicalExpression,_that.highEntropy,_that.anchorTarget,_that.boundingBoxScope,_that.extractionRule);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'tda_id')  String tdaId, @JsonKey(name: 'concept_description')  String conceptDescription, @JsonKey(name: 'acceptance_criteria')  List<AcceptanceCriterion> acceptanceCriteria, @JsonKey(name: 'anti_patterns')  List<AntiPattern> antiPatterns, @JsonKey(name: 'contrastive_example')  String? contrastiveExample, @JsonKey(name: 'syntactic_anchors')  List<String> syntacticAnchors, @JsonKey(name: 'enforce_pre_flight')  bool enforcePreFlight, @JsonKey(name: 'inverse_evidence')  bool inverseEvidence, @JsonKey(name: 'aggregation_mode')  AggregationMode aggregationMode, @JsonKey(name: 'evaluation_track')  EvaluationTrack evaluationTrack, @JsonKey(name: 'facts_to_find')  List<String> factsToFind, @JsonKey(name: 'logical_expression')  String? logicalExpression, @JsonKey(name: 'high_entropy')  bool highEntropy, @JsonKey(name: 'anchor_target')  String? anchorTarget, @JsonKey(name: 'bounding_box_scope')  String boundingBoxScope, @JsonKey(name: 'extraction_rule')  String? extractionRule)?  $default,) {final _that = this;
switch (_that) {
case _TDAAssertion() when $default != null:
return $default(_that.tdaId,_that.conceptDescription,_that.acceptanceCriteria,_that.antiPatterns,_that.contrastiveExample,_that.syntacticAnchors,_that.enforcePreFlight,_that.inverseEvidence,_that.aggregationMode,_that.evaluationTrack,_that.factsToFind,_that.logicalExpression,_that.highEntropy,_that.anchorTarget,_that.boundingBoxScope,_that.extractionRule);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _TDAAssertion extends TDAAssertion {
  const _TDAAssertion({@JsonKey(name: 'tda_id') required this.tdaId, @JsonKey(name: 'concept_description') required this.conceptDescription, @JsonKey(name: 'acceptance_criteria') final  List<AcceptanceCriterion> acceptanceCriteria = const [], @JsonKey(name: 'anti_patterns') final  List<AntiPattern> antiPatterns = const [], @JsonKey(name: 'contrastive_example') this.contrastiveExample, @JsonKey(name: 'syntactic_anchors') final  List<String> syntacticAnchors = const [], @JsonKey(name: 'enforce_pre_flight') this.enforcePreFlight = false, @JsonKey(name: 'inverse_evidence') required this.inverseEvidence, @JsonKey(name: 'aggregation_mode') required this.aggregationMode, @JsonKey(name: 'evaluation_track') this.evaluationTrack = EvaluationTrack.cognitiveJudgement, @JsonKey(name: 'facts_to_find') final  List<String> factsToFind = const [], @JsonKey(name: 'logical_expression') this.logicalExpression, @JsonKey(name: 'high_entropy') this.highEntropy = false, @JsonKey(name: 'anchor_target') this.anchorTarget, @JsonKey(name: 'bounding_box_scope') this.boundingBoxScope = 'paragraph', @JsonKey(name: 'extraction_rule') this.extractionRule}): _acceptanceCriteria = acceptanceCriteria,_antiPatterns = antiPatterns,_syntacticAnchors = syntacticAnchors,_factsToFind = factsToFind,super._();
  factory _TDAAssertion.fromJson(Map<String, dynamic> json) => _$TDAAssertionFromJson(json);

@override@JsonKey(name: 'tda_id') final  String tdaId;
@override@JsonKey(name: 'concept_description') final  String conceptDescription;
 final  List<AcceptanceCriterion> _acceptanceCriteria;
@override@JsonKey(name: 'acceptance_criteria') List<AcceptanceCriterion> get acceptanceCriteria {
  if (_acceptanceCriteria is EqualUnmodifiableListView) return _acceptanceCriteria;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_acceptanceCriteria);
}

 final  List<AntiPattern> _antiPatterns;
@override@JsonKey(name: 'anti_patterns') List<AntiPattern> get antiPatterns {
  if (_antiPatterns is EqualUnmodifiableListView) return _antiPatterns;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_antiPatterns);
}

@override@JsonKey(name: 'contrastive_example') final  String? contrastiveExample;
 final  List<String> _syntacticAnchors;
@override@JsonKey(name: 'syntactic_anchors') List<String> get syntacticAnchors {
  if (_syntacticAnchors is EqualUnmodifiableListView) return _syntacticAnchors;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_syntacticAnchors);
}

@override@JsonKey(name: 'enforce_pre_flight') final  bool enforcePreFlight;
@override@JsonKey(name: 'inverse_evidence') final  bool inverseEvidence;
@override@JsonKey(name: 'aggregation_mode') final  AggregationMode aggregationMode;
@override@JsonKey(name: 'evaluation_track') final  EvaluationTrack evaluationTrack;
 final  List<String> _factsToFind;
@override@JsonKey(name: 'facts_to_find') List<String> get factsToFind {
  if (_factsToFind is EqualUnmodifiableListView) return _factsToFind;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_factsToFind);
}

@override@JsonKey(name: 'logical_expression') final  String? logicalExpression;
@override@JsonKey(name: 'high_entropy') final  bool highEntropy;
@override@JsonKey(name: 'anchor_target') final  String? anchorTarget;
@override@JsonKey(name: 'bounding_box_scope') final  String boundingBoxScope;
@override@JsonKey(name: 'extraction_rule') final  String? extractionRule;

/// Create a copy of TDAAssertion
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$TDAAssertionCopyWith<_TDAAssertion> get copyWith => __$TDAAssertionCopyWithImpl<_TDAAssertion>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$TDAAssertionToJson(this, );
}



@override
String toString() {
  return 'TDAAssertion(tdaId: $tdaId, conceptDescription: $conceptDescription, acceptanceCriteria: $acceptanceCriteria, antiPatterns: $antiPatterns, contrastiveExample: $contrastiveExample, syntacticAnchors: $syntacticAnchors, enforcePreFlight: $enforcePreFlight, inverseEvidence: $inverseEvidence, aggregationMode: $aggregationMode, evaluationTrack: $evaluationTrack, factsToFind: $factsToFind, logicalExpression: $logicalExpression, highEntropy: $highEntropy, anchorTarget: $anchorTarget, boundingBoxScope: $boundingBoxScope, extractionRule: $extractionRule)';
}


}

/// @nodoc
abstract mixin class _$TDAAssertionCopyWith<$Res> implements $TDAAssertionCopyWith<$Res> {
  factory _$TDAAssertionCopyWith(_TDAAssertion value, $Res Function(_TDAAssertion) _then) = __$TDAAssertionCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'tda_id') String tdaId,@JsonKey(name: 'concept_description') String conceptDescription,@JsonKey(name: 'acceptance_criteria') List<AcceptanceCriterion> acceptanceCriteria,@JsonKey(name: 'anti_patterns') List<AntiPattern> antiPatterns,@JsonKey(name: 'contrastive_example') String? contrastiveExample,@JsonKey(name: 'syntactic_anchors') List<String> syntacticAnchors,@JsonKey(name: 'enforce_pre_flight') bool enforcePreFlight,@JsonKey(name: 'inverse_evidence') bool inverseEvidence,@JsonKey(name: 'aggregation_mode') AggregationMode aggregationMode,@JsonKey(name: 'evaluation_track') EvaluationTrack evaluationTrack,@JsonKey(name: 'facts_to_find') List<String> factsToFind,@JsonKey(name: 'logical_expression') String? logicalExpression,@JsonKey(name: 'high_entropy') bool highEntropy,@JsonKey(name: 'anchor_target') String? anchorTarget,@JsonKey(name: 'bounding_box_scope') String boundingBoxScope,@JsonKey(name: 'extraction_rule') String? extractionRule
});




}
/// @nodoc
class __$TDAAssertionCopyWithImpl<$Res>
    implements _$TDAAssertionCopyWith<$Res> {
  __$TDAAssertionCopyWithImpl(this._self, this._then);

  final _TDAAssertion _self;
  final $Res Function(_TDAAssertion) _then;

/// Create a copy of TDAAssertion
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? tdaId = null,Object? conceptDescription = null,Object? acceptanceCriteria = null,Object? antiPatterns = null,Object? contrastiveExample = freezed,Object? syntacticAnchors = null,Object? enforcePreFlight = null,Object? inverseEvidence = null,Object? aggregationMode = null,Object? evaluationTrack = null,Object? factsToFind = null,Object? logicalExpression = freezed,Object? highEntropy = null,Object? anchorTarget = freezed,Object? boundingBoxScope = null,Object? extractionRule = freezed,}) {
  return _then(_TDAAssertion(
tdaId: null == tdaId ? _self.tdaId : tdaId // ignore: cast_nullable_to_non_nullable
as String,conceptDescription: null == conceptDescription ? _self.conceptDescription : conceptDescription // ignore: cast_nullable_to_non_nullable
as String,acceptanceCriteria: null == acceptanceCriteria ? _self._acceptanceCriteria : acceptanceCriteria // ignore: cast_nullable_to_non_nullable
as List<AcceptanceCriterion>,antiPatterns: null == antiPatterns ? _self._antiPatterns : antiPatterns // ignore: cast_nullable_to_non_nullable
as List<AntiPattern>,contrastiveExample: freezed == contrastiveExample ? _self.contrastiveExample : contrastiveExample // ignore: cast_nullable_to_non_nullable
as String?,syntacticAnchors: null == syntacticAnchors ? _self._syntacticAnchors : syntacticAnchors // ignore: cast_nullable_to_non_nullable
as List<String>,enforcePreFlight: null == enforcePreFlight ? _self.enforcePreFlight : enforcePreFlight // ignore: cast_nullable_to_non_nullable
as bool,inverseEvidence: null == inverseEvidence ? _self.inverseEvidence : inverseEvidence // ignore: cast_nullable_to_non_nullable
as bool,aggregationMode: null == aggregationMode ? _self.aggregationMode : aggregationMode // ignore: cast_nullable_to_non_nullable
as AggregationMode,evaluationTrack: null == evaluationTrack ? _self.evaluationTrack : evaluationTrack // ignore: cast_nullable_to_non_nullable
as EvaluationTrack,factsToFind: null == factsToFind ? _self._factsToFind : factsToFind // ignore: cast_nullable_to_non_nullable
as List<String>,logicalExpression: freezed == logicalExpression ? _self.logicalExpression : logicalExpression // ignore: cast_nullable_to_non_nullable
as String?,highEntropy: null == highEntropy ? _self.highEntropy : highEntropy // ignore: cast_nullable_to_non_nullable
as bool,anchorTarget: freezed == anchorTarget ? _self.anchorTarget : anchorTarget // ignore: cast_nullable_to_non_nullable
as String?,boundingBoxScope: null == boundingBoxScope ? _self.boundingBoxScope : boundingBoxScope // ignore: cast_nullable_to_non_nullable
as String,extractionRule: freezed == extractionRule ? _self.extractionRule : extractionRule // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$MatrixClaim {

 I18nText get label; String get aiDescription;@JsonKey(name: 'tda_assertions') List<TDAAssertion> get tdaAssertions;
/// Create a copy of MatrixClaim
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MatrixClaimCopyWith<MatrixClaim> get copyWith => _$MatrixClaimCopyWithImpl<MatrixClaim>(this as MatrixClaim, _$identity);

  /// Serializes this MatrixClaim to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'MatrixClaim(label: $label, aiDescription: $aiDescription, tdaAssertions: $tdaAssertions)';
}


}

/// @nodoc
abstract mixin class $MatrixClaimCopyWith<$Res>  {
  factory $MatrixClaimCopyWith(MatrixClaim value, $Res Function(MatrixClaim) _then) = _$MatrixClaimCopyWithImpl;
@useResult
$Res call({
 I18nText label, String aiDescription,@JsonKey(name: 'tda_assertions') List<TDAAssertion> tdaAssertions
});


$I18nTextCopyWith<$Res> get label;

}
/// @nodoc
class _$MatrixClaimCopyWithImpl<$Res>
    implements $MatrixClaimCopyWith<$Res> {
  _$MatrixClaimCopyWithImpl(this._self, this._then);

  final MatrixClaim _self;
  final $Res Function(MatrixClaim) _then;

/// Create a copy of MatrixClaim
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? label = null,Object? aiDescription = null,Object? tdaAssertions = null,}) {
  return _then(_self.copyWith(
label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,aiDescription: null == aiDescription ? _self.aiDescription : aiDescription // ignore: cast_nullable_to_non_nullable
as String,tdaAssertions: null == tdaAssertions ? _self.tdaAssertions : tdaAssertions // ignore: cast_nullable_to_non_nullable
as List<TDAAssertion>,
  ));
}
/// Create a copy of MatrixClaim
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get label {
  
  return $I18nTextCopyWith<$Res>(_self.label, (value) {
    return _then(_self.copyWith(label: value));
  });
}
}


/// Adds pattern-matching-related methods to [MatrixClaim].
extension MatrixClaimPatterns on MatrixClaim {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MatrixClaim value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MatrixClaim() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MatrixClaim value)  $default,){
final _that = this;
switch (_that) {
case _MatrixClaim():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MatrixClaim value)?  $default,){
final _that = this;
switch (_that) {
case _MatrixClaim() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( I18nText label,  String aiDescription, @JsonKey(name: 'tda_assertions')  List<TDAAssertion> tdaAssertions)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MatrixClaim() when $default != null:
return $default(_that.label,_that.aiDescription,_that.tdaAssertions);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( I18nText label,  String aiDescription, @JsonKey(name: 'tda_assertions')  List<TDAAssertion> tdaAssertions)  $default,) {final _that = this;
switch (_that) {
case _MatrixClaim():
return $default(_that.label,_that.aiDescription,_that.tdaAssertions);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( I18nText label,  String aiDescription, @JsonKey(name: 'tda_assertions')  List<TDAAssertion> tdaAssertions)?  $default,) {final _that = this;
switch (_that) {
case _MatrixClaim() when $default != null:
return $default(_that.label,_that.aiDescription,_that.tdaAssertions);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _MatrixClaim extends MatrixClaim {
  const _MatrixClaim({required this.label, required this.aiDescription, @JsonKey(name: 'tda_assertions') final  List<TDAAssertion> tdaAssertions = const []}): _tdaAssertions = tdaAssertions,super._();
  factory _MatrixClaim.fromJson(Map<String, dynamic> json) => _$MatrixClaimFromJson(json);

@override final  I18nText label;
@override final  String aiDescription;
 final  List<TDAAssertion> _tdaAssertions;
@override@JsonKey(name: 'tda_assertions') List<TDAAssertion> get tdaAssertions {
  if (_tdaAssertions is EqualUnmodifiableListView) return _tdaAssertions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_tdaAssertions);
}


/// Create a copy of MatrixClaim
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MatrixClaimCopyWith<_MatrixClaim> get copyWith => __$MatrixClaimCopyWithImpl<_MatrixClaim>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MatrixClaimToJson(this, );
}



@override
String toString() {
  return 'MatrixClaim(label: $label, aiDescription: $aiDescription, tdaAssertions: $tdaAssertions)';
}


}

/// @nodoc
abstract mixin class _$MatrixClaimCopyWith<$Res> implements $MatrixClaimCopyWith<$Res> {
  factory _$MatrixClaimCopyWith(_MatrixClaim value, $Res Function(_MatrixClaim) _then) = __$MatrixClaimCopyWithImpl;
@override @useResult
$Res call({
 I18nText label, String aiDescription,@JsonKey(name: 'tda_assertions') List<TDAAssertion> tdaAssertions
});


@override $I18nTextCopyWith<$Res> get label;

}
/// @nodoc
class __$MatrixClaimCopyWithImpl<$Res>
    implements _$MatrixClaimCopyWith<$Res> {
  __$MatrixClaimCopyWithImpl(this._self, this._then);

  final _MatrixClaim _self;
  final $Res Function(_MatrixClaim) _then;

/// Create a copy of MatrixClaim
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? label = null,Object? aiDescription = null,Object? tdaAssertions = null,}) {
  return _then(_MatrixClaim(
label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,aiDescription: null == aiDescription ? _self.aiDescription : aiDescription // ignore: cast_nullable_to_non_nullable
as String,tdaAssertions: null == tdaAssertions ? _self._tdaAssertions : tdaAssertions // ignore: cast_nullable_to_non_nullable
as List<TDAAssertion>,
  ));
}

/// Create a copy of MatrixClaim
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get label {
  
  return $I18nTextCopyWith<$Res>(_self.label, (value) {
    return _then(_self.copyWith(label: value));
  });
}
}


/// @nodoc
mixin _$MatrixRow {

 I18nText get label; String get aiDescription;
/// Create a copy of MatrixRow
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MatrixRowCopyWith<MatrixRow> get copyWith => _$MatrixRowCopyWithImpl<MatrixRow>(this as MatrixRow, _$identity);

  /// Serializes this MatrixRow to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'MatrixRow(label: $label, aiDescription: $aiDescription)';
}


}

/// @nodoc
abstract mixin class $MatrixRowCopyWith<$Res>  {
  factory $MatrixRowCopyWith(MatrixRow value, $Res Function(MatrixRow) _then) = _$MatrixRowCopyWithImpl;
@useResult
$Res call({
 I18nText label, String aiDescription
});


$I18nTextCopyWith<$Res> get label;

}
/// @nodoc
class _$MatrixRowCopyWithImpl<$Res>
    implements $MatrixRowCopyWith<$Res> {
  _$MatrixRowCopyWithImpl(this._self, this._then);

  final MatrixRow _self;
  final $Res Function(MatrixRow) _then;

/// Create a copy of MatrixRow
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? label = null,Object? aiDescription = null,}) {
  return _then(_self.copyWith(
label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,aiDescription: null == aiDescription ? _self.aiDescription : aiDescription // ignore: cast_nullable_to_non_nullable
as String,
  ));
}
/// Create a copy of MatrixRow
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get label {
  
  return $I18nTextCopyWith<$Res>(_self.label, (value) {
    return _then(_self.copyWith(label: value));
  });
}
}


/// Adds pattern-matching-related methods to [MatrixRow].
extension MatrixRowPatterns on MatrixRow {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MatrixRow value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MatrixRow() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MatrixRow value)  $default,){
final _that = this;
switch (_that) {
case _MatrixRow():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MatrixRow value)?  $default,){
final _that = this;
switch (_that) {
case _MatrixRow() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( I18nText label,  String aiDescription)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MatrixRow() when $default != null:
return $default(_that.label,_that.aiDescription);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( I18nText label,  String aiDescription)  $default,) {final _that = this;
switch (_that) {
case _MatrixRow():
return $default(_that.label,_that.aiDescription);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( I18nText label,  String aiDescription)?  $default,) {final _that = this;
switch (_that) {
case _MatrixRow() when $default != null:
return $default(_that.label,_that.aiDescription);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _MatrixRow extends MatrixRow {
  const _MatrixRow({required this.label, required this.aiDescription}): super._();
  factory _MatrixRow.fromJson(Map<String, dynamic> json) => _$MatrixRowFromJson(json);

@override final  I18nText label;
@override final  String aiDescription;

/// Create a copy of MatrixRow
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MatrixRowCopyWith<_MatrixRow> get copyWith => __$MatrixRowCopyWithImpl<_MatrixRow>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MatrixRowToJson(this, );
}



@override
String toString() {
  return 'MatrixRow(label: $label, aiDescription: $aiDescription)';
}


}

/// @nodoc
abstract mixin class _$MatrixRowCopyWith<$Res> implements $MatrixRowCopyWith<$Res> {
  factory _$MatrixRowCopyWith(_MatrixRow value, $Res Function(_MatrixRow) _then) = __$MatrixRowCopyWithImpl;
@override @useResult
$Res call({
 I18nText label, String aiDescription
});


@override $I18nTextCopyWith<$Res> get label;

}
/// @nodoc
class __$MatrixRowCopyWithImpl<$Res>
    implements _$MatrixRowCopyWith<$Res> {
  __$MatrixRowCopyWithImpl(this._self, this._then);

  final _MatrixRow _self;
  final $Res Function(_MatrixRow) _then;

/// Create a copy of MatrixRow
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? label = null,Object? aiDescription = null,}) {
  return _then(_MatrixRow(
label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,aiDescription: null == aiDescription ? _self.aiDescription : aiDescription // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

/// Create a copy of MatrixRow
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get label {
  
  return $I18nTextCopyWith<$Res>(_self.label, (value) {
    return _then(_self.copyWith(label: value));
  });
}
}


/// @nodoc
mixin _$MatrixScale {

 int get score; I18nText? get name; String get aiLabel; List<MatrixClaim> get claims;
/// Create a copy of MatrixScale
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MatrixScaleCopyWith<MatrixScale> get copyWith => _$MatrixScaleCopyWithImpl<MatrixScale>(this as MatrixScale, _$identity);

  /// Serializes this MatrixScale to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'MatrixScale(score: $score, name: $name, aiLabel: $aiLabel, claims: $claims)';
}


}

/// @nodoc
abstract mixin class $MatrixScaleCopyWith<$Res>  {
  factory $MatrixScaleCopyWith(MatrixScale value, $Res Function(MatrixScale) _then) = _$MatrixScaleCopyWithImpl;
@useResult
$Res call({
 int score, I18nText? name, String aiLabel, List<MatrixClaim> claims
});


$I18nTextCopyWith<$Res>? get name;

}
/// @nodoc
class _$MatrixScaleCopyWithImpl<$Res>
    implements $MatrixScaleCopyWith<$Res> {
  _$MatrixScaleCopyWithImpl(this._self, this._then);

  final MatrixScale _self;
  final $Res Function(MatrixScale) _then;

/// Create a copy of MatrixScale
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? score = null,Object? name = freezed,Object? aiLabel = null,Object? claims = null,}) {
  return _then(_self.copyWith(
score: null == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as int,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText?,aiLabel: null == aiLabel ? _self.aiLabel : aiLabel // ignore: cast_nullable_to_non_nullable
as String,claims: null == claims ? _self.claims : claims // ignore: cast_nullable_to_non_nullable
as List<MatrixClaim>,
  ));
}
/// Create a copy of MatrixScale
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get name {
    if (_self.name == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.name!, (value) {
    return _then(_self.copyWith(name: value));
  });
}
}


/// Adds pattern-matching-related methods to [MatrixScale].
extension MatrixScalePatterns on MatrixScale {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MatrixScale value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MatrixScale() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MatrixScale value)  $default,){
final _that = this;
switch (_that) {
case _MatrixScale():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MatrixScale value)?  $default,){
final _that = this;
switch (_that) {
case _MatrixScale() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int score,  I18nText? name,  String aiLabel,  List<MatrixClaim> claims)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MatrixScale() when $default != null:
return $default(_that.score,_that.name,_that.aiLabel,_that.claims);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int score,  I18nText? name,  String aiLabel,  List<MatrixClaim> claims)  $default,) {final _that = this;
switch (_that) {
case _MatrixScale():
return $default(_that.score,_that.name,_that.aiLabel,_that.claims);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int score,  I18nText? name,  String aiLabel,  List<MatrixClaim> claims)?  $default,) {final _that = this;
switch (_that) {
case _MatrixScale() when $default != null:
return $default(_that.score,_that.name,_that.aiLabel,_that.claims);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _MatrixScale extends MatrixScale {
  const _MatrixScale({required this.score, this.name, required this.aiLabel, required final  List<MatrixClaim> claims}): _claims = claims,super._();
  factory _MatrixScale.fromJson(Map<String, dynamic> json) => _$MatrixScaleFromJson(json);

@override final  int score;
@override final  I18nText? name;
@override final  String aiLabel;
 final  List<MatrixClaim> _claims;
@override List<MatrixClaim> get claims {
  if (_claims is EqualUnmodifiableListView) return _claims;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_claims);
}


/// Create a copy of MatrixScale
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MatrixScaleCopyWith<_MatrixScale> get copyWith => __$MatrixScaleCopyWithImpl<_MatrixScale>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MatrixScaleToJson(this, );
}



@override
String toString() {
  return 'MatrixScale(score: $score, name: $name, aiLabel: $aiLabel, claims: $claims)';
}


}

/// @nodoc
abstract mixin class _$MatrixScaleCopyWith<$Res> implements $MatrixScaleCopyWith<$Res> {
  factory _$MatrixScaleCopyWith(_MatrixScale value, $Res Function(_MatrixScale) _then) = __$MatrixScaleCopyWithImpl;
@override @useResult
$Res call({
 int score, I18nText? name, String aiLabel, List<MatrixClaim> claims
});


@override $I18nTextCopyWith<$Res>? get name;

}
/// @nodoc
class __$MatrixScaleCopyWithImpl<$Res>
    implements _$MatrixScaleCopyWith<$Res> {
  __$MatrixScaleCopyWithImpl(this._self, this._then);

  final _MatrixScale _self;
  final $Res Function(_MatrixScale) _then;

/// Create a copy of MatrixScale
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? score = null,Object? name = freezed,Object? aiLabel = null,Object? claims = null,}) {
  return _then(_MatrixScale(
score: null == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as int,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText?,aiLabel: null == aiLabel ? _self.aiLabel : aiLabel // ignore: cast_nullable_to_non_nullable
as String,claims: null == claims ? _self._claims : claims // ignore: cast_nullable_to_non_nullable
as List<MatrixClaim>,
  ));
}

/// Create a copy of MatrixScale
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get name {
    if (_self.name == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.name!, (value) {
    return _then(_self.copyWith(name: value));
  });
}
}


/// @nodoc
mixin _$PromptBlock {

@StrictOpaqueIdConverter() String get id; String get slug; String? get organizationId; I18nText get label; I18nText get description; String? get aiDescription; String get categoryId; bool get isEvaluative; BlockDataType get type; bool get allowDecimals; List<String> get outputExtensions; TheoryGrounding? get theoryGrounding;@JsonKey(name: 'allow_contextual_override') bool get allowContextualOverride;@JsonKey(name: 'is_lightweight_protocol') bool get isLightweightProtocol;@JsonKey(includeToJson: false) int? get computedMin;@JsonKey(includeToJson: false) int? get computedMax; List<MatrixScale>? get scales; List<MatrixRow>? get rows; List<I18nText>? get columns;
/// Create a copy of PromptBlock
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PromptBlockCopyWith<PromptBlock> get copyWith => _$PromptBlockCopyWithImpl<PromptBlock>(this as PromptBlock, _$identity);

  /// Serializes this PromptBlock to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'PromptBlock(id: $id, slug: $slug, organizationId: $organizationId, label: $label, description: $description, aiDescription: $aiDescription, categoryId: $categoryId, isEvaluative: $isEvaluative, type: $type, allowDecimals: $allowDecimals, outputExtensions: $outputExtensions, theoryGrounding: $theoryGrounding, allowContextualOverride: $allowContextualOverride, isLightweightProtocol: $isLightweightProtocol, computedMin: $computedMin, computedMax: $computedMax, scales: $scales, rows: $rows, columns: $columns)';
}


}

/// @nodoc
abstract mixin class $PromptBlockCopyWith<$Res>  {
  factory $PromptBlockCopyWith(PromptBlock value, $Res Function(PromptBlock) _then) = _$PromptBlockCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, String? organizationId, I18nText label, I18nText description, String? aiDescription, String categoryId, bool isEvaluative, BlockDataType type, bool allowDecimals, List<String> outputExtensions, TheoryGrounding? theoryGrounding,@JsonKey(name: 'allow_contextual_override') bool allowContextualOverride,@JsonKey(name: 'is_lightweight_protocol') bool isLightweightProtocol,@JsonKey(includeToJson: false) int? computedMin,@JsonKey(includeToJson: false) int? computedMax, List<MatrixScale>? scales, List<MatrixRow>? rows, List<I18nText>? columns
});


$I18nTextCopyWith<$Res> get label;$I18nTextCopyWith<$Res> get description;$TheoryGroundingCopyWith<$Res>? get theoryGrounding;

}
/// @nodoc
class _$PromptBlockCopyWithImpl<$Res>
    implements $PromptBlockCopyWith<$Res> {
  _$PromptBlockCopyWithImpl(this._self, this._then);

  final PromptBlock _self;
  final $Res Function(PromptBlock) _then;

/// Create a copy of PromptBlock
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? organizationId = freezed,Object? label = null,Object? description = null,Object? aiDescription = freezed,Object? categoryId = null,Object? isEvaluative = null,Object? type = null,Object? allowDecimals = null,Object? outputExtensions = null,Object? theoryGrounding = freezed,Object? allowContextualOverride = null,Object? isLightweightProtocol = null,Object? computedMin = freezed,Object? computedMax = freezed,Object? scales = freezed,Object? rows = freezed,Object? columns = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText,aiDescription: freezed == aiDescription ? _self.aiDescription : aiDescription // ignore: cast_nullable_to_non_nullable
as String?,categoryId: null == categoryId ? _self.categoryId : categoryId // ignore: cast_nullable_to_non_nullable
as String,isEvaluative: null == isEvaluative ? _self.isEvaluative : isEvaluative // ignore: cast_nullable_to_non_nullable
as bool,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as BlockDataType,allowDecimals: null == allowDecimals ? _self.allowDecimals : allowDecimals // ignore: cast_nullable_to_non_nullable
as bool,outputExtensions: null == outputExtensions ? _self.outputExtensions : outputExtensions // ignore: cast_nullable_to_non_nullable
as List<String>,theoryGrounding: freezed == theoryGrounding ? _self.theoryGrounding : theoryGrounding // ignore: cast_nullable_to_non_nullable
as TheoryGrounding?,allowContextualOverride: null == allowContextualOverride ? _self.allowContextualOverride : allowContextualOverride // ignore: cast_nullable_to_non_nullable
as bool,isLightweightProtocol: null == isLightweightProtocol ? _self.isLightweightProtocol : isLightweightProtocol // ignore: cast_nullable_to_non_nullable
as bool,computedMin: freezed == computedMin ? _self.computedMin : computedMin // ignore: cast_nullable_to_non_nullable
as int?,computedMax: freezed == computedMax ? _self.computedMax : computedMax // ignore: cast_nullable_to_non_nullable
as int?,scales: freezed == scales ? _self.scales : scales // ignore: cast_nullable_to_non_nullable
as List<MatrixScale>?,rows: freezed == rows ? _self.rows : rows // ignore: cast_nullable_to_non_nullable
as List<MatrixRow>?,columns: freezed == columns ? _self.columns : columns // ignore: cast_nullable_to_non_nullable
as List<I18nText>?,
  ));
}
/// Create a copy of PromptBlock
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get label {
  
  return $I18nTextCopyWith<$Res>(_self.label, (value) {
    return _then(_self.copyWith(label: value));
  });
}/// Create a copy of PromptBlock
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get description {
  
  return $I18nTextCopyWith<$Res>(_self.description, (value) {
    return _then(_self.copyWith(description: value));
  });
}/// Create a copy of PromptBlock
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$TheoryGroundingCopyWith<$Res>? get theoryGrounding {
    if (_self.theoryGrounding == null) {
    return null;
  }

  return $TheoryGroundingCopyWith<$Res>(_self.theoryGrounding!, (value) {
    return _then(_self.copyWith(theoryGrounding: value));
  });
}
}


/// Adds pattern-matching-related methods to [PromptBlock].
extension PromptBlockPatterns on PromptBlock {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PromptBlock value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PromptBlock() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PromptBlock value)  $default,){
final _that = this;
switch (_that) {
case _PromptBlock():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PromptBlock value)?  $default,){
final _that = this;
switch (_that) {
case _PromptBlock() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  String? organizationId,  I18nText label,  I18nText description,  String? aiDescription,  String categoryId,  bool isEvaluative,  BlockDataType type,  bool allowDecimals,  List<String> outputExtensions,  TheoryGrounding? theoryGrounding, @JsonKey(name: 'allow_contextual_override')  bool allowContextualOverride, @JsonKey(name: 'is_lightweight_protocol')  bool isLightweightProtocol, @JsonKey(includeToJson: false)  int? computedMin, @JsonKey(includeToJson: false)  int? computedMax,  List<MatrixScale>? scales,  List<MatrixRow>? rows,  List<I18nText>? columns)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PromptBlock() when $default != null:
return $default(_that.id,_that.slug,_that.organizationId,_that.label,_that.description,_that.aiDescription,_that.categoryId,_that.isEvaluative,_that.type,_that.allowDecimals,_that.outputExtensions,_that.theoryGrounding,_that.allowContextualOverride,_that.isLightweightProtocol,_that.computedMin,_that.computedMax,_that.scales,_that.rows,_that.columns);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  String? organizationId,  I18nText label,  I18nText description,  String? aiDescription,  String categoryId,  bool isEvaluative,  BlockDataType type,  bool allowDecimals,  List<String> outputExtensions,  TheoryGrounding? theoryGrounding, @JsonKey(name: 'allow_contextual_override')  bool allowContextualOverride, @JsonKey(name: 'is_lightweight_protocol')  bool isLightweightProtocol, @JsonKey(includeToJson: false)  int? computedMin, @JsonKey(includeToJson: false)  int? computedMax,  List<MatrixScale>? scales,  List<MatrixRow>? rows,  List<I18nText>? columns)  $default,) {final _that = this;
switch (_that) {
case _PromptBlock():
return $default(_that.id,_that.slug,_that.organizationId,_that.label,_that.description,_that.aiDescription,_that.categoryId,_that.isEvaluative,_that.type,_that.allowDecimals,_that.outputExtensions,_that.theoryGrounding,_that.allowContextualOverride,_that.isLightweightProtocol,_that.computedMin,_that.computedMax,_that.scales,_that.rows,_that.columns);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug,  String? organizationId,  I18nText label,  I18nText description,  String? aiDescription,  String categoryId,  bool isEvaluative,  BlockDataType type,  bool allowDecimals,  List<String> outputExtensions,  TheoryGrounding? theoryGrounding, @JsonKey(name: 'allow_contextual_override')  bool allowContextualOverride, @JsonKey(name: 'is_lightweight_protocol')  bool isLightweightProtocol, @JsonKey(includeToJson: false)  int? computedMin, @JsonKey(includeToJson: false)  int? computedMax,  List<MatrixScale>? scales,  List<MatrixRow>? rows,  List<I18nText>? columns)?  $default,) {final _that = this;
switch (_that) {
case _PromptBlock() when $default != null:
return $default(_that.id,_that.slug,_that.organizationId,_that.label,_that.description,_that.aiDescription,_that.categoryId,_that.isEvaluative,_that.type,_that.allowDecimals,_that.outputExtensions,_that.theoryGrounding,_that.allowContextualOverride,_that.isLightweightProtocol,_that.computedMin,_that.computedMax,_that.scales,_that.rows,_that.columns);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _PromptBlock extends PromptBlock {
  const _PromptBlock({@StrictOpaqueIdConverter() required this.id, required this.slug, this.organizationId, required this.label, required this.description, this.aiDescription, this.categoryId = 'system', this.isEvaluative = true, this.type = BlockDataType.stringType, this.allowDecimals = false, final  List<String> outputExtensions = const [], this.theoryGrounding, @JsonKey(name: 'allow_contextual_override') this.allowContextualOverride = false, @JsonKey(name: 'is_lightweight_protocol') this.isLightweightProtocol = false, @JsonKey(includeToJson: false) this.computedMin, @JsonKey(includeToJson: false) this.computedMax, final  List<MatrixScale>? scales, final  List<MatrixRow>? rows, final  List<I18nText>? columns}): _outputExtensions = outputExtensions,_scales = scales,_rows = rows,_columns = columns,super._();
  factory _PromptBlock.fromJson(Map<String, dynamic> json) => _$PromptBlockFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override final  String slug;
@override final  String? organizationId;
@override final  I18nText label;
@override final  I18nText description;
@override final  String? aiDescription;
@override@JsonKey() final  String categoryId;
@override@JsonKey() final  bool isEvaluative;
@override@JsonKey() final  BlockDataType type;
@override@JsonKey() final  bool allowDecimals;
 final  List<String> _outputExtensions;
@override@JsonKey() List<String> get outputExtensions {
  if (_outputExtensions is EqualUnmodifiableListView) return _outputExtensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_outputExtensions);
}

@override final  TheoryGrounding? theoryGrounding;
@override@JsonKey(name: 'allow_contextual_override') final  bool allowContextualOverride;
@override@JsonKey(name: 'is_lightweight_protocol') final  bool isLightweightProtocol;
@override@JsonKey(includeToJson: false) final  int? computedMin;
@override@JsonKey(includeToJson: false) final  int? computedMax;
 final  List<MatrixScale>? _scales;
@override List<MatrixScale>? get scales {
  final value = _scales;
  if (value == null) return null;
  if (_scales is EqualUnmodifiableListView) return _scales;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

 final  List<MatrixRow>? _rows;
@override List<MatrixRow>? get rows {
  final value = _rows;
  if (value == null) return null;
  if (_rows is EqualUnmodifiableListView) return _rows;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

 final  List<I18nText>? _columns;
@override List<I18nText>? get columns {
  final value = _columns;
  if (value == null) return null;
  if (_columns is EqualUnmodifiableListView) return _columns;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}


/// Create a copy of PromptBlock
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PromptBlockCopyWith<_PromptBlock> get copyWith => __$PromptBlockCopyWithImpl<_PromptBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PromptBlockToJson(this, );
}



@override
String toString() {
  return 'PromptBlock(id: $id, slug: $slug, organizationId: $organizationId, label: $label, description: $description, aiDescription: $aiDescription, categoryId: $categoryId, isEvaluative: $isEvaluative, type: $type, allowDecimals: $allowDecimals, outputExtensions: $outputExtensions, theoryGrounding: $theoryGrounding, allowContextualOverride: $allowContextualOverride, isLightweightProtocol: $isLightweightProtocol, computedMin: $computedMin, computedMax: $computedMax, scales: $scales, rows: $rows, columns: $columns)';
}


}

/// @nodoc
abstract mixin class _$PromptBlockCopyWith<$Res> implements $PromptBlockCopyWith<$Res> {
  factory _$PromptBlockCopyWith(_PromptBlock value, $Res Function(_PromptBlock) _then) = __$PromptBlockCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, String? organizationId, I18nText label, I18nText description, String? aiDescription, String categoryId, bool isEvaluative, BlockDataType type, bool allowDecimals, List<String> outputExtensions, TheoryGrounding? theoryGrounding,@JsonKey(name: 'allow_contextual_override') bool allowContextualOverride,@JsonKey(name: 'is_lightweight_protocol') bool isLightweightProtocol,@JsonKey(includeToJson: false) int? computedMin,@JsonKey(includeToJson: false) int? computedMax, List<MatrixScale>? scales, List<MatrixRow>? rows, List<I18nText>? columns
});


@override $I18nTextCopyWith<$Res> get label;@override $I18nTextCopyWith<$Res> get description;@override $TheoryGroundingCopyWith<$Res>? get theoryGrounding;

}
/// @nodoc
class __$PromptBlockCopyWithImpl<$Res>
    implements _$PromptBlockCopyWith<$Res> {
  __$PromptBlockCopyWithImpl(this._self, this._then);

  final _PromptBlock _self;
  final $Res Function(_PromptBlock) _then;

/// Create a copy of PromptBlock
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? organizationId = freezed,Object? label = null,Object? description = null,Object? aiDescription = freezed,Object? categoryId = null,Object? isEvaluative = null,Object? type = null,Object? allowDecimals = null,Object? outputExtensions = null,Object? theoryGrounding = freezed,Object? allowContextualOverride = null,Object? isLightweightProtocol = null,Object? computedMin = freezed,Object? computedMax = freezed,Object? scales = freezed,Object? rows = freezed,Object? columns = freezed,}) {
  return _then(_PromptBlock(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText,aiDescription: freezed == aiDescription ? _self.aiDescription : aiDescription // ignore: cast_nullable_to_non_nullable
as String?,categoryId: null == categoryId ? _self.categoryId : categoryId // ignore: cast_nullable_to_non_nullable
as String,isEvaluative: null == isEvaluative ? _self.isEvaluative : isEvaluative // ignore: cast_nullable_to_non_nullable
as bool,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as BlockDataType,allowDecimals: null == allowDecimals ? _self.allowDecimals : allowDecimals // ignore: cast_nullable_to_non_nullable
as bool,outputExtensions: null == outputExtensions ? _self._outputExtensions : outputExtensions // ignore: cast_nullable_to_non_nullable
as List<String>,theoryGrounding: freezed == theoryGrounding ? _self.theoryGrounding : theoryGrounding // ignore: cast_nullable_to_non_nullable
as TheoryGrounding?,allowContextualOverride: null == allowContextualOverride ? _self.allowContextualOverride : allowContextualOverride // ignore: cast_nullable_to_non_nullable
as bool,isLightweightProtocol: null == isLightweightProtocol ? _self.isLightweightProtocol : isLightweightProtocol // ignore: cast_nullable_to_non_nullable
as bool,computedMin: freezed == computedMin ? _self.computedMin : computedMin // ignore: cast_nullable_to_non_nullable
as int?,computedMax: freezed == computedMax ? _self.computedMax : computedMax // ignore: cast_nullable_to_non_nullable
as int?,scales: freezed == scales ? _self._scales : scales // ignore: cast_nullable_to_non_nullable
as List<MatrixScale>?,rows: freezed == rows ? _self._rows : rows // ignore: cast_nullable_to_non_nullable
as List<MatrixRow>?,columns: freezed == columns ? _self._columns : columns // ignore: cast_nullable_to_non_nullable
as List<I18nText>?,
  ));
}

/// Create a copy of PromptBlock
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get label {
  
  return $I18nTextCopyWith<$Res>(_self.label, (value) {
    return _then(_self.copyWith(label: value));
  });
}/// Create a copy of PromptBlock
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get description {
  
  return $I18nTextCopyWith<$Res>(_self.description, (value) {
    return _then(_self.copyWith(description: value));
  });
}/// Create a copy of PromptBlock
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$TheoryGroundingCopyWith<$Res>? get theoryGrounding {
    if (_self.theoryGrounding == null) {
    return null;
  }

  return $TheoryGroundingCopyWith<$Res>(_self.theoryGrounding!, (value) {
    return _then(_self.copyWith(theoryGrounding: value));
  });
}
}

// dart format on
