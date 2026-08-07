// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'matrix_scorecard_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ReasoningStepDto {

@JsonKey(name: 'step_1_identify_premise') String get step1IdentifyPremise;@JsonKey(name: 'step_2_scan_source') String get step2ScanSource;@JsonKey(name: 'step_3_evaluate_anti_patterns') String get step3EvaluateAntiPatterns;@JsonKey(name: 'step_4_final_conclusion') String get step4FinalConclusion;
/// Create a copy of ReasoningStepDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReasoningStepDtoCopyWith<ReasoningStepDto> get copyWith => _$ReasoningStepDtoCopyWithImpl<ReasoningStepDto>(this as ReasoningStepDto, _$identity);

  /// Serializes this ReasoningStepDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReasoningStepDto(step1IdentifyPremise: $step1IdentifyPremise, step2ScanSource: $step2ScanSource, step3EvaluateAntiPatterns: $step3EvaluateAntiPatterns, step4FinalConclusion: $step4FinalConclusion)';
}


}

/// @nodoc
abstract mixin class $ReasoningStepDtoCopyWith<$Res>  {
  factory $ReasoningStepDtoCopyWith(ReasoningStepDto value, $Res Function(ReasoningStepDto) _then) = _$ReasoningStepDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'step_1_identify_premise') String step1IdentifyPremise,@JsonKey(name: 'step_2_scan_source') String step2ScanSource,@JsonKey(name: 'step_3_evaluate_anti_patterns') String step3EvaluateAntiPatterns,@JsonKey(name: 'step_4_final_conclusion') String step4FinalConclusion
});




}
/// @nodoc
class _$ReasoningStepDtoCopyWithImpl<$Res>
    implements $ReasoningStepDtoCopyWith<$Res> {
  _$ReasoningStepDtoCopyWithImpl(this._self, this._then);

  final ReasoningStepDto _self;
  final $Res Function(ReasoningStepDto) _then;

/// Create a copy of ReasoningStepDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? step1IdentifyPremise = null,Object? step2ScanSource = null,Object? step3EvaluateAntiPatterns = null,Object? step4FinalConclusion = null,}) {
  return _then(_self.copyWith(
step1IdentifyPremise: null == step1IdentifyPremise ? _self.step1IdentifyPremise : step1IdentifyPremise // ignore: cast_nullable_to_non_nullable
as String,step2ScanSource: null == step2ScanSource ? _self.step2ScanSource : step2ScanSource // ignore: cast_nullable_to_non_nullable
as String,step3EvaluateAntiPatterns: null == step3EvaluateAntiPatterns ? _self.step3EvaluateAntiPatterns : step3EvaluateAntiPatterns // ignore: cast_nullable_to_non_nullable
as String,step4FinalConclusion: null == step4FinalConclusion ? _self.step4FinalConclusion : step4FinalConclusion // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [ReasoningStepDto].
extension ReasoningStepDtoPatterns on ReasoningStepDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReasoningStepDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReasoningStepDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReasoningStepDto value)  $default,){
final _that = this;
switch (_that) {
case _ReasoningStepDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReasoningStepDto value)?  $default,){
final _that = this;
switch (_that) {
case _ReasoningStepDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'step_1_identify_premise')  String step1IdentifyPremise, @JsonKey(name: 'step_2_scan_source')  String step2ScanSource, @JsonKey(name: 'step_3_evaluate_anti_patterns')  String step3EvaluateAntiPatterns, @JsonKey(name: 'step_4_final_conclusion')  String step4FinalConclusion)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReasoningStepDto() when $default != null:
return $default(_that.step1IdentifyPremise,_that.step2ScanSource,_that.step3EvaluateAntiPatterns,_that.step4FinalConclusion);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'step_1_identify_premise')  String step1IdentifyPremise, @JsonKey(name: 'step_2_scan_source')  String step2ScanSource, @JsonKey(name: 'step_3_evaluate_anti_patterns')  String step3EvaluateAntiPatterns, @JsonKey(name: 'step_4_final_conclusion')  String step4FinalConclusion)  $default,) {final _that = this;
switch (_that) {
case _ReasoningStepDto():
return $default(_that.step1IdentifyPremise,_that.step2ScanSource,_that.step3EvaluateAntiPatterns,_that.step4FinalConclusion);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'step_1_identify_premise')  String step1IdentifyPremise, @JsonKey(name: 'step_2_scan_source')  String step2ScanSource, @JsonKey(name: 'step_3_evaluate_anti_patterns')  String step3EvaluateAntiPatterns, @JsonKey(name: 'step_4_final_conclusion')  String step4FinalConclusion)?  $default,) {final _that = this;
switch (_that) {
case _ReasoningStepDto() when $default != null:
return $default(_that.step1IdentifyPremise,_that.step2ScanSource,_that.step3EvaluateAntiPatterns,_that.step4FinalConclusion);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReasoningStepDto implements ReasoningStepDto {
  const _ReasoningStepDto({@JsonKey(name: 'step_1_identify_premise') required this.step1IdentifyPremise, @JsonKey(name: 'step_2_scan_source') required this.step2ScanSource, @JsonKey(name: 'step_3_evaluate_anti_patterns') required this.step3EvaluateAntiPatterns, @JsonKey(name: 'step_4_final_conclusion') required this.step4FinalConclusion});
  factory _ReasoningStepDto.fromJson(Map<String, dynamic> json) => _$ReasoningStepDtoFromJson(json);

@override@JsonKey(name: 'step_1_identify_premise') final  String step1IdentifyPremise;
@override@JsonKey(name: 'step_2_scan_source') final  String step2ScanSource;
@override@JsonKey(name: 'step_3_evaluate_anti_patterns') final  String step3EvaluateAntiPatterns;
@override@JsonKey(name: 'step_4_final_conclusion') final  String step4FinalConclusion;

/// Create a copy of ReasoningStepDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReasoningStepDtoCopyWith<_ReasoningStepDto> get copyWith => __$ReasoningStepDtoCopyWithImpl<_ReasoningStepDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReasoningStepDtoToJson(this, );
}



@override
String toString() {
  return 'ReasoningStepDto(step1IdentifyPremise: $step1IdentifyPremise, step2ScanSource: $step2ScanSource, step3EvaluateAntiPatterns: $step3EvaluateAntiPatterns, step4FinalConclusion: $step4FinalConclusion)';
}


}

/// @nodoc
abstract mixin class _$ReasoningStepDtoCopyWith<$Res> implements $ReasoningStepDtoCopyWith<$Res> {
  factory _$ReasoningStepDtoCopyWith(_ReasoningStepDto value, $Res Function(_ReasoningStepDto) _then) = __$ReasoningStepDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'step_1_identify_premise') String step1IdentifyPremise,@JsonKey(name: 'step_2_scan_source') String step2ScanSource,@JsonKey(name: 'step_3_evaluate_anti_patterns') String step3EvaluateAntiPatterns,@JsonKey(name: 'step_4_final_conclusion') String step4FinalConclusion
});




}
/// @nodoc
class __$ReasoningStepDtoCopyWithImpl<$Res>
    implements _$ReasoningStepDtoCopyWith<$Res> {
  __$ReasoningStepDtoCopyWithImpl(this._self, this._then);

  final _ReasoningStepDto _self;
  final $Res Function(_ReasoningStepDto) _then;

/// Create a copy of ReasoningStepDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? step1IdentifyPremise = null,Object? step2ScanSource = null,Object? step3EvaluateAntiPatterns = null,Object? step4FinalConclusion = null,}) {
  return _then(_ReasoningStepDto(
step1IdentifyPremise: null == step1IdentifyPremise ? _self.step1IdentifyPremise : step1IdentifyPremise // ignore: cast_nullable_to_non_nullable
as String,step2ScanSource: null == step2ScanSource ? _self.step2ScanSource : step2ScanSource // ignore: cast_nullable_to_non_nullable
as String,step3EvaluateAntiPatterns: null == step3EvaluateAntiPatterns ? _self.step3EvaluateAntiPatterns : step3EvaluateAntiPatterns // ignore: cast_nullable_to_non_nullable
as String,step4FinalConclusion: null == step4FinalConclusion ? _self.step4FinalConclusion : step4FinalConclusion // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$QuoteEvidenceDto {

 String get quote;@JsonKey(name: 'verified_source_ids') List<String> get verifiedSourceIds;@JsonKey(name: 'unverified_aliases') List<String> get unverifiedAliases;@JsonKey(name: 'is_verified') bool get isVerified;
/// Create a copy of QuoteEvidenceDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$QuoteEvidenceDtoCopyWith<QuoteEvidenceDto> get copyWith => _$QuoteEvidenceDtoCopyWithImpl<QuoteEvidenceDto>(this as QuoteEvidenceDto, _$identity);

  /// Serializes this QuoteEvidenceDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'QuoteEvidenceDto(quote: $quote, verifiedSourceIds: $verifiedSourceIds, unverifiedAliases: $unverifiedAliases, isVerified: $isVerified)';
}


}

/// @nodoc
abstract mixin class $QuoteEvidenceDtoCopyWith<$Res>  {
  factory $QuoteEvidenceDtoCopyWith(QuoteEvidenceDto value, $Res Function(QuoteEvidenceDto) _then) = _$QuoteEvidenceDtoCopyWithImpl;
@useResult
$Res call({
 String quote,@JsonKey(name: 'verified_source_ids') List<String> verifiedSourceIds,@JsonKey(name: 'unverified_aliases') List<String> unverifiedAliases,@JsonKey(name: 'is_verified') bool isVerified
});




}
/// @nodoc
class _$QuoteEvidenceDtoCopyWithImpl<$Res>
    implements $QuoteEvidenceDtoCopyWith<$Res> {
  _$QuoteEvidenceDtoCopyWithImpl(this._self, this._then);

  final QuoteEvidenceDto _self;
  final $Res Function(QuoteEvidenceDto) _then;

/// Create a copy of QuoteEvidenceDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? quote = null,Object? verifiedSourceIds = null,Object? unverifiedAliases = null,Object? isVerified = null,}) {
  return _then(_self.copyWith(
quote: null == quote ? _self.quote : quote // ignore: cast_nullable_to_non_nullable
as String,verifiedSourceIds: null == verifiedSourceIds ? _self.verifiedSourceIds : verifiedSourceIds // ignore: cast_nullable_to_non_nullable
as List<String>,unverifiedAliases: null == unverifiedAliases ? _self.unverifiedAliases : unverifiedAliases // ignore: cast_nullable_to_non_nullable
as List<String>,isVerified: null == isVerified ? _self.isVerified : isVerified // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [QuoteEvidenceDto].
extension QuoteEvidenceDtoPatterns on QuoteEvidenceDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _QuoteEvidenceDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _QuoteEvidenceDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _QuoteEvidenceDto value)  $default,){
final _that = this;
switch (_that) {
case _QuoteEvidenceDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _QuoteEvidenceDto value)?  $default,){
final _that = this;
switch (_that) {
case _QuoteEvidenceDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String quote, @JsonKey(name: 'verified_source_ids')  List<String> verifiedSourceIds, @JsonKey(name: 'unverified_aliases')  List<String> unverifiedAliases, @JsonKey(name: 'is_verified')  bool isVerified)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _QuoteEvidenceDto() when $default != null:
return $default(_that.quote,_that.verifiedSourceIds,_that.unverifiedAliases,_that.isVerified);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String quote, @JsonKey(name: 'verified_source_ids')  List<String> verifiedSourceIds, @JsonKey(name: 'unverified_aliases')  List<String> unverifiedAliases, @JsonKey(name: 'is_verified')  bool isVerified)  $default,) {final _that = this;
switch (_that) {
case _QuoteEvidenceDto():
return $default(_that.quote,_that.verifiedSourceIds,_that.unverifiedAliases,_that.isVerified);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String quote, @JsonKey(name: 'verified_source_ids')  List<String> verifiedSourceIds, @JsonKey(name: 'unverified_aliases')  List<String> unverifiedAliases, @JsonKey(name: 'is_verified')  bool isVerified)?  $default,) {final _that = this;
switch (_that) {
case _QuoteEvidenceDto() when $default != null:
return $default(_that.quote,_that.verifiedSourceIds,_that.unverifiedAliases,_that.isVerified);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _QuoteEvidenceDto implements QuoteEvidenceDto {
  const _QuoteEvidenceDto({required this.quote, @JsonKey(name: 'verified_source_ids') final  List<String> verifiedSourceIds = const [], @JsonKey(name: 'unverified_aliases') final  List<String> unverifiedAliases = const [], @JsonKey(name: 'is_verified') this.isVerified = false}): _verifiedSourceIds = verifiedSourceIds,_unverifiedAliases = unverifiedAliases;
  factory _QuoteEvidenceDto.fromJson(Map<String, dynamic> json) => _$QuoteEvidenceDtoFromJson(json);

@override final  String quote;
 final  List<String> _verifiedSourceIds;
@override@JsonKey(name: 'verified_source_ids') List<String> get verifiedSourceIds {
  if (_verifiedSourceIds is EqualUnmodifiableListView) return _verifiedSourceIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_verifiedSourceIds);
}

 final  List<String> _unverifiedAliases;
@override@JsonKey(name: 'unverified_aliases') List<String> get unverifiedAliases {
  if (_unverifiedAliases is EqualUnmodifiableListView) return _unverifiedAliases;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_unverifiedAliases);
}

@override@JsonKey(name: 'is_verified') final  bool isVerified;

/// Create a copy of QuoteEvidenceDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$QuoteEvidenceDtoCopyWith<_QuoteEvidenceDto> get copyWith => __$QuoteEvidenceDtoCopyWithImpl<_QuoteEvidenceDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$QuoteEvidenceDtoToJson(this, );
}



@override
String toString() {
  return 'QuoteEvidenceDto(quote: $quote, verifiedSourceIds: $verifiedSourceIds, unverifiedAliases: $unverifiedAliases, isVerified: $isVerified)';
}


}

/// @nodoc
abstract mixin class _$QuoteEvidenceDtoCopyWith<$Res> implements $QuoteEvidenceDtoCopyWith<$Res> {
  factory _$QuoteEvidenceDtoCopyWith(_QuoteEvidenceDto value, $Res Function(_QuoteEvidenceDto) _then) = __$QuoteEvidenceDtoCopyWithImpl;
@override @useResult
$Res call({
 String quote,@JsonKey(name: 'verified_source_ids') List<String> verifiedSourceIds,@JsonKey(name: 'unverified_aliases') List<String> unverifiedAliases,@JsonKey(name: 'is_verified') bool isVerified
});




}
/// @nodoc
class __$QuoteEvidenceDtoCopyWithImpl<$Res>
    implements _$QuoteEvidenceDtoCopyWith<$Res> {
  __$QuoteEvidenceDtoCopyWithImpl(this._self, this._then);

  final _QuoteEvidenceDto _self;
  final $Res Function(_QuoteEvidenceDto) _then;

/// Create a copy of QuoteEvidenceDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? quote = null,Object? verifiedSourceIds = null,Object? unverifiedAliases = null,Object? isVerified = null,}) {
  return _then(_QuoteEvidenceDto(
quote: null == quote ? _self.quote : quote // ignore: cast_nullable_to_non_nullable
as String,verifiedSourceIds: null == verifiedSourceIds ? _self._verifiedSourceIds : verifiedSourceIds // ignore: cast_nullable_to_non_nullable
as List<String>,unverifiedAliases: null == unverifiedAliases ? _self._unverifiedAliases : unverifiedAliases // ignore: cast_nullable_to_non_nullable
as List<String>,isVerified: null == isVerified ? _self.isVerified : isVerified // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}


/// @nodoc
mixin _$HumanOverrideDto {

@JsonKey(name: 'new_status') String get newStatus; String get reason;@JsonKey(name: 'evidence_quotes') List<QuoteEvidenceDto> get evidenceQuotes;@JsonKey(name: 'overridden_by') String get overriddenBy;@JsonKey(name: 'overridden_at') DateTime get overriddenAt;
/// Create a copy of HumanOverrideDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$HumanOverrideDtoCopyWith<HumanOverrideDto> get copyWith => _$HumanOverrideDtoCopyWithImpl<HumanOverrideDto>(this as HumanOverrideDto, _$identity);

  /// Serializes this HumanOverrideDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'HumanOverrideDto(newStatus: $newStatus, reason: $reason, evidenceQuotes: $evidenceQuotes, overriddenBy: $overriddenBy, overriddenAt: $overriddenAt)';
}


}

/// @nodoc
abstract mixin class $HumanOverrideDtoCopyWith<$Res>  {
  factory $HumanOverrideDtoCopyWith(HumanOverrideDto value, $Res Function(HumanOverrideDto) _then) = _$HumanOverrideDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'new_status') String newStatus, String reason,@JsonKey(name: 'evidence_quotes') List<QuoteEvidenceDto> evidenceQuotes,@JsonKey(name: 'overridden_by') String overriddenBy,@JsonKey(name: 'overridden_at') DateTime overriddenAt
});




}
/// @nodoc
class _$HumanOverrideDtoCopyWithImpl<$Res>
    implements $HumanOverrideDtoCopyWith<$Res> {
  _$HumanOverrideDtoCopyWithImpl(this._self, this._then);

  final HumanOverrideDto _self;
  final $Res Function(HumanOverrideDto) _then;

/// Create a copy of HumanOverrideDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? newStatus = null,Object? reason = null,Object? evidenceQuotes = null,Object? overriddenBy = null,Object? overriddenAt = null,}) {
  return _then(_self.copyWith(
newStatus: null == newStatus ? _self.newStatus : newStatus // ignore: cast_nullable_to_non_nullable
as String,reason: null == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String,evidenceQuotes: null == evidenceQuotes ? _self.evidenceQuotes : evidenceQuotes // ignore: cast_nullable_to_non_nullable
as List<QuoteEvidenceDto>,overriddenBy: null == overriddenBy ? _self.overriddenBy : overriddenBy // ignore: cast_nullable_to_non_nullable
as String,overriddenAt: null == overriddenAt ? _self.overriddenAt : overriddenAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [HumanOverrideDto].
extension HumanOverrideDtoPatterns on HumanOverrideDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _HumanOverrideDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _HumanOverrideDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _HumanOverrideDto value)  $default,){
final _that = this;
switch (_that) {
case _HumanOverrideDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _HumanOverrideDto value)?  $default,){
final _that = this;
switch (_that) {
case _HumanOverrideDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'new_status')  String newStatus,  String reason, @JsonKey(name: 'evidence_quotes')  List<QuoteEvidenceDto> evidenceQuotes, @JsonKey(name: 'overridden_by')  String overriddenBy, @JsonKey(name: 'overridden_at')  DateTime overriddenAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _HumanOverrideDto() when $default != null:
return $default(_that.newStatus,_that.reason,_that.evidenceQuotes,_that.overriddenBy,_that.overriddenAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'new_status')  String newStatus,  String reason, @JsonKey(name: 'evidence_quotes')  List<QuoteEvidenceDto> evidenceQuotes, @JsonKey(name: 'overridden_by')  String overriddenBy, @JsonKey(name: 'overridden_at')  DateTime overriddenAt)  $default,) {final _that = this;
switch (_that) {
case _HumanOverrideDto():
return $default(_that.newStatus,_that.reason,_that.evidenceQuotes,_that.overriddenBy,_that.overriddenAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'new_status')  String newStatus,  String reason, @JsonKey(name: 'evidence_quotes')  List<QuoteEvidenceDto> evidenceQuotes, @JsonKey(name: 'overridden_by')  String overriddenBy, @JsonKey(name: 'overridden_at')  DateTime overriddenAt)?  $default,) {final _that = this;
switch (_that) {
case _HumanOverrideDto() when $default != null:
return $default(_that.newStatus,_that.reason,_that.evidenceQuotes,_that.overriddenBy,_that.overriddenAt);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _HumanOverrideDto implements HumanOverrideDto {
  const _HumanOverrideDto({@JsonKey(name: 'new_status') required this.newStatus, required this.reason, @JsonKey(name: 'evidence_quotes') required final  List<QuoteEvidenceDto> evidenceQuotes, @JsonKey(name: 'overridden_by') required this.overriddenBy, @JsonKey(name: 'overridden_at') required this.overriddenAt}): _evidenceQuotes = evidenceQuotes;
  factory _HumanOverrideDto.fromJson(Map<String, dynamic> json) => _$HumanOverrideDtoFromJson(json);

@override@JsonKey(name: 'new_status') final  String newStatus;
@override final  String reason;
 final  List<QuoteEvidenceDto> _evidenceQuotes;
@override@JsonKey(name: 'evidence_quotes') List<QuoteEvidenceDto> get evidenceQuotes {
  if (_evidenceQuotes is EqualUnmodifiableListView) return _evidenceQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_evidenceQuotes);
}

@override@JsonKey(name: 'overridden_by') final  String overriddenBy;
@override@JsonKey(name: 'overridden_at') final  DateTime overriddenAt;

/// Create a copy of HumanOverrideDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$HumanOverrideDtoCopyWith<_HumanOverrideDto> get copyWith => __$HumanOverrideDtoCopyWithImpl<_HumanOverrideDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$HumanOverrideDtoToJson(this, );
}



@override
String toString() {
  return 'HumanOverrideDto(newStatus: $newStatus, reason: $reason, evidenceQuotes: $evidenceQuotes, overriddenBy: $overriddenBy, overriddenAt: $overriddenAt)';
}


}

/// @nodoc
abstract mixin class _$HumanOverrideDtoCopyWith<$Res> implements $HumanOverrideDtoCopyWith<$Res> {
  factory _$HumanOverrideDtoCopyWith(_HumanOverrideDto value, $Res Function(_HumanOverrideDto) _then) = __$HumanOverrideDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'new_status') String newStatus, String reason,@JsonKey(name: 'evidence_quotes') List<QuoteEvidenceDto> evidenceQuotes,@JsonKey(name: 'overridden_by') String overriddenBy,@JsonKey(name: 'overridden_at') DateTime overriddenAt
});




}
/// @nodoc
class __$HumanOverrideDtoCopyWithImpl<$Res>
    implements _$HumanOverrideDtoCopyWith<$Res> {
  __$HumanOverrideDtoCopyWithImpl(this._self, this._then);

  final _HumanOverrideDto _self;
  final $Res Function(_HumanOverrideDto) _then;

/// Create a copy of HumanOverrideDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? newStatus = null,Object? reason = null,Object? evidenceQuotes = null,Object? overriddenBy = null,Object? overriddenAt = null,}) {
  return _then(_HumanOverrideDto(
newStatus: null == newStatus ? _self.newStatus : newStatus // ignore: cast_nullable_to_non_nullable
as String,reason: null == reason ? _self.reason : reason // ignore: cast_nullable_to_non_nullable
as String,evidenceQuotes: null == evidenceQuotes ? _self._evidenceQuotes : evidenceQuotes // ignore: cast_nullable_to_non_nullable
as List<QuoteEvidenceDto>,overriddenBy: null == overriddenBy ? _self.overriddenBy : overriddenBy // ignore: cast_nullable_to_non_nullable
as String,overriddenAt: null == overriddenAt ? _self.overriddenAt : overriddenAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}


/// @nodoc
mixin _$ScorecardAtomDto {

@JsonKey(name: 'atom_id') String get atomId; int get level;@JsonKey(name: 'level_name') String get levelName;@JsonKey(name: 'claim_label') String get claimLabel;@JsonKey(name: 'extracted_facts') Map<String, String?> get extractedFacts;@JsonKey(name: 'exact_quotes') List<QuoteEvidenceDto> get exactQuotes;@JsonKey(name: 'internal_logic_en') ReasoningStepDto get internalLogicEn; AtomEvaluationStatus? get status;@JsonKey(name: 'semantic_reasoning') String get semanticReasoning;@JsonKey(name: 'contextual_override') bool get contextualOverride;@JsonKey(name: 'structural_location') String? get structuralLocation;@JsonKey(name: 'human_override') HumanOverrideDto? get humanOverride;@JsonKey(name: 'chart_display_label') String get chartDisplayLabel;@JsonKey(name: 'visual_intent') VisualIntent get visualIntent;
/// Create a copy of ScorecardAtomDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ScorecardAtomDtoCopyWith<ScorecardAtomDto> get copyWith => _$ScorecardAtomDtoCopyWithImpl<ScorecardAtomDto>(this as ScorecardAtomDto, _$identity);

  /// Serializes this ScorecardAtomDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ScorecardAtomDto(atomId: $atomId, level: $level, levelName: $levelName, claimLabel: $claimLabel, extractedFacts: $extractedFacts, exactQuotes: $exactQuotes, internalLogicEn: $internalLogicEn, status: $status, semanticReasoning: $semanticReasoning, contextualOverride: $contextualOverride, structuralLocation: $structuralLocation, humanOverride: $humanOverride, chartDisplayLabel: $chartDisplayLabel, visualIntent: $visualIntent)';
}


}

/// @nodoc
abstract mixin class $ScorecardAtomDtoCopyWith<$Res>  {
  factory $ScorecardAtomDtoCopyWith(ScorecardAtomDto value, $Res Function(ScorecardAtomDto) _then) = _$ScorecardAtomDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'atom_id') String atomId, int level,@JsonKey(name: 'level_name') String levelName,@JsonKey(name: 'claim_label') String claimLabel,@JsonKey(name: 'extracted_facts') Map<String, String?> extractedFacts,@JsonKey(name: 'exact_quotes') List<QuoteEvidenceDto> exactQuotes,@JsonKey(name: 'internal_logic_en') ReasoningStepDto internalLogicEn, AtomEvaluationStatus? status,@JsonKey(name: 'semantic_reasoning') String semanticReasoning,@JsonKey(name: 'contextual_override') bool contextualOverride,@JsonKey(name: 'structural_location') String? structuralLocation,@JsonKey(name: 'human_override') HumanOverrideDto? humanOverride,@JsonKey(name: 'chart_display_label') String chartDisplayLabel,@JsonKey(name: 'visual_intent') VisualIntent visualIntent
});


$ReasoningStepDtoCopyWith<$Res> get internalLogicEn;$HumanOverrideDtoCopyWith<$Res>? get humanOverride;

}
/// @nodoc
class _$ScorecardAtomDtoCopyWithImpl<$Res>
    implements $ScorecardAtomDtoCopyWith<$Res> {
  _$ScorecardAtomDtoCopyWithImpl(this._self, this._then);

  final ScorecardAtomDto _self;
  final $Res Function(ScorecardAtomDto) _then;

/// Create a copy of ScorecardAtomDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? atomId = null,Object? level = null,Object? levelName = null,Object? claimLabel = null,Object? extractedFacts = null,Object? exactQuotes = null,Object? internalLogicEn = null,Object? status = freezed,Object? semanticReasoning = null,Object? contextualOverride = null,Object? structuralLocation = freezed,Object? humanOverride = freezed,Object? chartDisplayLabel = null,Object? visualIntent = null,}) {
  return _then(_self.copyWith(
atomId: null == atomId ? _self.atomId : atomId // ignore: cast_nullable_to_non_nullable
as String,level: null == level ? _self.level : level // ignore: cast_nullable_to_non_nullable
as int,levelName: null == levelName ? _self.levelName : levelName // ignore: cast_nullable_to_non_nullable
as String,claimLabel: null == claimLabel ? _self.claimLabel : claimLabel // ignore: cast_nullable_to_non_nullable
as String,extractedFacts: null == extractedFacts ? _self.extractedFacts : extractedFacts // ignore: cast_nullable_to_non_nullable
as Map<String, String?>,exactQuotes: null == exactQuotes ? _self.exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<QuoteEvidenceDto>,internalLogicEn: null == internalLogicEn ? _self.internalLogicEn : internalLogicEn // ignore: cast_nullable_to_non_nullable
as ReasoningStepDto,status: freezed == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as AtomEvaluationStatus?,semanticReasoning: null == semanticReasoning ? _self.semanticReasoning : semanticReasoning // ignore: cast_nullable_to_non_nullable
as String,contextualOverride: null == contextualOverride ? _self.contextualOverride : contextualOverride // ignore: cast_nullable_to_non_nullable
as bool,structuralLocation: freezed == structuralLocation ? _self.structuralLocation : structuralLocation // ignore: cast_nullable_to_non_nullable
as String?,humanOverride: freezed == humanOverride ? _self.humanOverride : humanOverride // ignore: cast_nullable_to_non_nullable
as HumanOverrideDto?,chartDisplayLabel: null == chartDisplayLabel ? _self.chartDisplayLabel : chartDisplayLabel // ignore: cast_nullable_to_non_nullable
as String,visualIntent: null == visualIntent ? _self.visualIntent : visualIntent // ignore: cast_nullable_to_non_nullable
as VisualIntent,
  ));
}
/// Create a copy of ScorecardAtomDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReasoningStepDtoCopyWith<$Res> get internalLogicEn {
  
  return $ReasoningStepDtoCopyWith<$Res>(_self.internalLogicEn, (value) {
    return _then(_self.copyWith(internalLogicEn: value));
  });
}/// Create a copy of ScorecardAtomDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$HumanOverrideDtoCopyWith<$Res>? get humanOverride {
    if (_self.humanOverride == null) {
    return null;
  }

  return $HumanOverrideDtoCopyWith<$Res>(_self.humanOverride!, (value) {
    return _then(_self.copyWith(humanOverride: value));
  });
}
}


/// Adds pattern-matching-related methods to [ScorecardAtomDto].
extension ScorecardAtomDtoPatterns on ScorecardAtomDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ScorecardAtomDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ScorecardAtomDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ScorecardAtomDto value)  $default,){
final _that = this;
switch (_that) {
case _ScorecardAtomDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ScorecardAtomDto value)?  $default,){
final _that = this;
switch (_that) {
case _ScorecardAtomDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'atom_id')  String atomId,  int level, @JsonKey(name: 'level_name')  String levelName, @JsonKey(name: 'claim_label')  String claimLabel, @JsonKey(name: 'extracted_facts')  Map<String, String?> extractedFacts, @JsonKey(name: 'exact_quotes')  List<QuoteEvidenceDto> exactQuotes, @JsonKey(name: 'internal_logic_en')  ReasoningStepDto internalLogicEn,  AtomEvaluationStatus? status, @JsonKey(name: 'semantic_reasoning')  String semanticReasoning, @JsonKey(name: 'contextual_override')  bool contextualOverride, @JsonKey(name: 'structural_location')  String? structuralLocation, @JsonKey(name: 'human_override')  HumanOverrideDto? humanOverride, @JsonKey(name: 'chart_display_label')  String chartDisplayLabel, @JsonKey(name: 'visual_intent')  VisualIntent visualIntent)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ScorecardAtomDto() when $default != null:
return $default(_that.atomId,_that.level,_that.levelName,_that.claimLabel,_that.extractedFacts,_that.exactQuotes,_that.internalLogicEn,_that.status,_that.semanticReasoning,_that.contextualOverride,_that.structuralLocation,_that.humanOverride,_that.chartDisplayLabel,_that.visualIntent);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'atom_id')  String atomId,  int level, @JsonKey(name: 'level_name')  String levelName, @JsonKey(name: 'claim_label')  String claimLabel, @JsonKey(name: 'extracted_facts')  Map<String, String?> extractedFacts, @JsonKey(name: 'exact_quotes')  List<QuoteEvidenceDto> exactQuotes, @JsonKey(name: 'internal_logic_en')  ReasoningStepDto internalLogicEn,  AtomEvaluationStatus? status, @JsonKey(name: 'semantic_reasoning')  String semanticReasoning, @JsonKey(name: 'contextual_override')  bool contextualOverride, @JsonKey(name: 'structural_location')  String? structuralLocation, @JsonKey(name: 'human_override')  HumanOverrideDto? humanOverride, @JsonKey(name: 'chart_display_label')  String chartDisplayLabel, @JsonKey(name: 'visual_intent')  VisualIntent visualIntent)  $default,) {final _that = this;
switch (_that) {
case _ScorecardAtomDto():
return $default(_that.atomId,_that.level,_that.levelName,_that.claimLabel,_that.extractedFacts,_that.exactQuotes,_that.internalLogicEn,_that.status,_that.semanticReasoning,_that.contextualOverride,_that.structuralLocation,_that.humanOverride,_that.chartDisplayLabel,_that.visualIntent);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'atom_id')  String atomId,  int level, @JsonKey(name: 'level_name')  String levelName, @JsonKey(name: 'claim_label')  String claimLabel, @JsonKey(name: 'extracted_facts')  Map<String, String?> extractedFacts, @JsonKey(name: 'exact_quotes')  List<QuoteEvidenceDto> exactQuotes, @JsonKey(name: 'internal_logic_en')  ReasoningStepDto internalLogicEn,  AtomEvaluationStatus? status, @JsonKey(name: 'semantic_reasoning')  String semanticReasoning, @JsonKey(name: 'contextual_override')  bool contextualOverride, @JsonKey(name: 'structural_location')  String? structuralLocation, @JsonKey(name: 'human_override')  HumanOverrideDto? humanOverride, @JsonKey(name: 'chart_display_label')  String chartDisplayLabel, @JsonKey(name: 'visual_intent')  VisualIntent visualIntent)?  $default,) {final _that = this;
switch (_that) {
case _ScorecardAtomDto() when $default != null:
return $default(_that.atomId,_that.level,_that.levelName,_that.claimLabel,_that.extractedFacts,_that.exactQuotes,_that.internalLogicEn,_that.status,_that.semanticReasoning,_that.contextualOverride,_that.structuralLocation,_that.humanOverride,_that.chartDisplayLabel,_that.visualIntent);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ScorecardAtomDto implements ScorecardAtomDto {
  const _ScorecardAtomDto({@JsonKey(name: 'atom_id') required this.atomId, required this.level, @JsonKey(name: 'level_name') required this.levelName, @JsonKey(name: 'claim_label') required this.claimLabel, @JsonKey(name: 'extracted_facts') required final  Map<String, String?> extractedFacts, @JsonKey(name: 'exact_quotes') required final  List<QuoteEvidenceDto> exactQuotes, @JsonKey(name: 'internal_logic_en') required this.internalLogicEn, this.status, @JsonKey(name: 'semantic_reasoning') required this.semanticReasoning, @JsonKey(name: 'contextual_override') required this.contextualOverride, @JsonKey(name: 'structural_location') this.structuralLocation, @JsonKey(name: 'human_override') this.humanOverride, @JsonKey(name: 'chart_display_label') required this.chartDisplayLabel, @JsonKey(name: 'visual_intent') required this.visualIntent}): _extractedFacts = extractedFacts,_exactQuotes = exactQuotes;
  factory _ScorecardAtomDto.fromJson(Map<String, dynamic> json) => _$ScorecardAtomDtoFromJson(json);

@override@JsonKey(name: 'atom_id') final  String atomId;
@override final  int level;
@override@JsonKey(name: 'level_name') final  String levelName;
@override@JsonKey(name: 'claim_label') final  String claimLabel;
 final  Map<String, String?> _extractedFacts;
@override@JsonKey(name: 'extracted_facts') Map<String, String?> get extractedFacts {
  if (_extractedFacts is EqualUnmodifiableMapView) return _extractedFacts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_extractedFacts);
}

 final  List<QuoteEvidenceDto> _exactQuotes;
@override@JsonKey(name: 'exact_quotes') List<QuoteEvidenceDto> get exactQuotes {
  if (_exactQuotes is EqualUnmodifiableListView) return _exactQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_exactQuotes);
}

@override@JsonKey(name: 'internal_logic_en') final  ReasoningStepDto internalLogicEn;
@override final  AtomEvaluationStatus? status;
@override@JsonKey(name: 'semantic_reasoning') final  String semanticReasoning;
@override@JsonKey(name: 'contextual_override') final  bool contextualOverride;
@override@JsonKey(name: 'structural_location') final  String? structuralLocation;
@override@JsonKey(name: 'human_override') final  HumanOverrideDto? humanOverride;
@override@JsonKey(name: 'chart_display_label') final  String chartDisplayLabel;
@override@JsonKey(name: 'visual_intent') final  VisualIntent visualIntent;

/// Create a copy of ScorecardAtomDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ScorecardAtomDtoCopyWith<_ScorecardAtomDto> get copyWith => __$ScorecardAtomDtoCopyWithImpl<_ScorecardAtomDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ScorecardAtomDtoToJson(this, );
}



@override
String toString() {
  return 'ScorecardAtomDto(atomId: $atomId, level: $level, levelName: $levelName, claimLabel: $claimLabel, extractedFacts: $extractedFacts, exactQuotes: $exactQuotes, internalLogicEn: $internalLogicEn, status: $status, semanticReasoning: $semanticReasoning, contextualOverride: $contextualOverride, structuralLocation: $structuralLocation, humanOverride: $humanOverride, chartDisplayLabel: $chartDisplayLabel, visualIntent: $visualIntent)';
}


}

/// @nodoc
abstract mixin class _$ScorecardAtomDtoCopyWith<$Res> implements $ScorecardAtomDtoCopyWith<$Res> {
  factory _$ScorecardAtomDtoCopyWith(_ScorecardAtomDto value, $Res Function(_ScorecardAtomDto) _then) = __$ScorecardAtomDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'atom_id') String atomId, int level,@JsonKey(name: 'level_name') String levelName,@JsonKey(name: 'claim_label') String claimLabel,@JsonKey(name: 'extracted_facts') Map<String, String?> extractedFacts,@JsonKey(name: 'exact_quotes') List<QuoteEvidenceDto> exactQuotes,@JsonKey(name: 'internal_logic_en') ReasoningStepDto internalLogicEn, AtomEvaluationStatus? status,@JsonKey(name: 'semantic_reasoning') String semanticReasoning,@JsonKey(name: 'contextual_override') bool contextualOverride,@JsonKey(name: 'structural_location') String? structuralLocation,@JsonKey(name: 'human_override') HumanOverrideDto? humanOverride,@JsonKey(name: 'chart_display_label') String chartDisplayLabel,@JsonKey(name: 'visual_intent') VisualIntent visualIntent
});


@override $ReasoningStepDtoCopyWith<$Res> get internalLogicEn;@override $HumanOverrideDtoCopyWith<$Res>? get humanOverride;

}
/// @nodoc
class __$ScorecardAtomDtoCopyWithImpl<$Res>
    implements _$ScorecardAtomDtoCopyWith<$Res> {
  __$ScorecardAtomDtoCopyWithImpl(this._self, this._then);

  final _ScorecardAtomDto _self;
  final $Res Function(_ScorecardAtomDto) _then;

/// Create a copy of ScorecardAtomDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? atomId = null,Object? level = null,Object? levelName = null,Object? claimLabel = null,Object? extractedFacts = null,Object? exactQuotes = null,Object? internalLogicEn = null,Object? status = freezed,Object? semanticReasoning = null,Object? contextualOverride = null,Object? structuralLocation = freezed,Object? humanOverride = freezed,Object? chartDisplayLabel = null,Object? visualIntent = null,}) {
  return _then(_ScorecardAtomDto(
atomId: null == atomId ? _self.atomId : atomId // ignore: cast_nullable_to_non_nullable
as String,level: null == level ? _self.level : level // ignore: cast_nullable_to_non_nullable
as int,levelName: null == levelName ? _self.levelName : levelName // ignore: cast_nullable_to_non_nullable
as String,claimLabel: null == claimLabel ? _self.claimLabel : claimLabel // ignore: cast_nullable_to_non_nullable
as String,extractedFacts: null == extractedFacts ? _self._extractedFacts : extractedFacts // ignore: cast_nullable_to_non_nullable
as Map<String, String?>,exactQuotes: null == exactQuotes ? _self._exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<QuoteEvidenceDto>,internalLogicEn: null == internalLogicEn ? _self.internalLogicEn : internalLogicEn // ignore: cast_nullable_to_non_nullable
as ReasoningStepDto,status: freezed == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as AtomEvaluationStatus?,semanticReasoning: null == semanticReasoning ? _self.semanticReasoning : semanticReasoning // ignore: cast_nullable_to_non_nullable
as String,contextualOverride: null == contextualOverride ? _self.contextualOverride : contextualOverride // ignore: cast_nullable_to_non_nullable
as bool,structuralLocation: freezed == structuralLocation ? _self.structuralLocation : structuralLocation // ignore: cast_nullable_to_non_nullable
as String?,humanOverride: freezed == humanOverride ? _self.humanOverride : humanOverride // ignore: cast_nullable_to_non_nullable
as HumanOverrideDto?,chartDisplayLabel: null == chartDisplayLabel ? _self.chartDisplayLabel : chartDisplayLabel // ignore: cast_nullable_to_non_nullable
as String,visualIntent: null == visualIntent ? _self.visualIntent : visualIntent // ignore: cast_nullable_to_non_nullable
as VisualIntent,
  ));
}

/// Create a copy of ScorecardAtomDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReasoningStepDtoCopyWith<$Res> get internalLogicEn {
  
  return $ReasoningStepDtoCopyWith<$Res>(_self.internalLogicEn, (value) {
    return _then(_self.copyWith(internalLogicEn: value));
  });
}/// Create a copy of ScorecardAtomDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$HumanOverrideDtoCopyWith<$Res>? get humanOverride {
    if (_self.humanOverride == null) {
    return null;
  }

  return $HumanOverrideDtoCopyWith<$Res>(_self.humanOverride!, (value) {
    return _then(_self.copyWith(humanOverride: value));
  });
}
}


/// @nodoc
mixin _$McpAuditTraceDto {

 String? get id;@JsonKey(name: 'tool_id') String get toolId;@JsonKey(name: 'step_name') String get stepName;@JsonKey(name: 'claim_text') String? get claimText; String get query;@JsonKey(name: 'knowledge_gap') String get knowledgeGap;@JsonKey(name: 'search_rationale') String get searchRationale; String get reasoning;@JsonKey(name: 'response_summary') String get responseSummary;@JsonKey(name: 'source_urls') List<String> get sourceUrls;@JsonKey(name: 'impacted_axis_names') List<String> get impactedAxisNames; String? get timestamp;@JsonKey(name: 'duration_ms') int get durationMs;
/// Create a copy of McpAuditTraceDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$McpAuditTraceDtoCopyWith<McpAuditTraceDto> get copyWith => _$McpAuditTraceDtoCopyWithImpl<McpAuditTraceDto>(this as McpAuditTraceDto, _$identity);

  /// Serializes this McpAuditTraceDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'McpAuditTraceDto(id: $id, toolId: $toolId, stepName: $stepName, claimText: $claimText, query: $query, knowledgeGap: $knowledgeGap, searchRationale: $searchRationale, reasoning: $reasoning, responseSummary: $responseSummary, sourceUrls: $sourceUrls, impactedAxisNames: $impactedAxisNames, timestamp: $timestamp, durationMs: $durationMs)';
}


}

/// @nodoc
abstract mixin class $McpAuditTraceDtoCopyWith<$Res>  {
  factory $McpAuditTraceDtoCopyWith(McpAuditTraceDto value, $Res Function(McpAuditTraceDto) _then) = _$McpAuditTraceDtoCopyWithImpl;
@useResult
$Res call({
 String? id,@JsonKey(name: 'tool_id') String toolId,@JsonKey(name: 'step_name') String stepName,@JsonKey(name: 'claim_text') String? claimText, String query,@JsonKey(name: 'knowledge_gap') String knowledgeGap,@JsonKey(name: 'search_rationale') String searchRationale, String reasoning,@JsonKey(name: 'response_summary') String responseSummary,@JsonKey(name: 'source_urls') List<String> sourceUrls,@JsonKey(name: 'impacted_axis_names') List<String> impactedAxisNames, String? timestamp,@JsonKey(name: 'duration_ms') int durationMs
});




}
/// @nodoc
class _$McpAuditTraceDtoCopyWithImpl<$Res>
    implements $McpAuditTraceDtoCopyWith<$Res> {
  _$McpAuditTraceDtoCopyWithImpl(this._self, this._then);

  final McpAuditTraceDto _self;
  final $Res Function(McpAuditTraceDto) _then;

/// Create a copy of McpAuditTraceDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = freezed,Object? toolId = null,Object? stepName = null,Object? claimText = freezed,Object? query = null,Object? knowledgeGap = null,Object? searchRationale = null,Object? reasoning = null,Object? responseSummary = null,Object? sourceUrls = null,Object? impactedAxisNames = null,Object? timestamp = freezed,Object? durationMs = null,}) {
  return _then(_self.copyWith(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,toolId: null == toolId ? _self.toolId : toolId // ignore: cast_nullable_to_non_nullable
as String,stepName: null == stepName ? _self.stepName : stepName // ignore: cast_nullable_to_non_nullable
as String,claimText: freezed == claimText ? _self.claimText : claimText // ignore: cast_nullable_to_non_nullable
as String?,query: null == query ? _self.query : query // ignore: cast_nullable_to_non_nullable
as String,knowledgeGap: null == knowledgeGap ? _self.knowledgeGap : knowledgeGap // ignore: cast_nullable_to_non_nullable
as String,searchRationale: null == searchRationale ? _self.searchRationale : searchRationale // ignore: cast_nullable_to_non_nullable
as String,reasoning: null == reasoning ? _self.reasoning : reasoning // ignore: cast_nullable_to_non_nullable
as String,responseSummary: null == responseSummary ? _self.responseSummary : responseSummary // ignore: cast_nullable_to_non_nullable
as String,sourceUrls: null == sourceUrls ? _self.sourceUrls : sourceUrls // ignore: cast_nullable_to_non_nullable
as List<String>,impactedAxisNames: null == impactedAxisNames ? _self.impactedAxisNames : impactedAxisNames // ignore: cast_nullable_to_non_nullable
as List<String>,timestamp: freezed == timestamp ? _self.timestamp : timestamp // ignore: cast_nullable_to_non_nullable
as String?,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [McpAuditTraceDto].
extension McpAuditTraceDtoPatterns on McpAuditTraceDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _McpAuditTraceDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _McpAuditTraceDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _McpAuditTraceDto value)  $default,){
final _that = this;
switch (_that) {
case _McpAuditTraceDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _McpAuditTraceDto value)?  $default,){
final _that = this;
switch (_that) {
case _McpAuditTraceDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? id, @JsonKey(name: 'tool_id')  String toolId, @JsonKey(name: 'step_name')  String stepName, @JsonKey(name: 'claim_text')  String? claimText,  String query, @JsonKey(name: 'knowledge_gap')  String knowledgeGap, @JsonKey(name: 'search_rationale')  String searchRationale,  String reasoning, @JsonKey(name: 'response_summary')  String responseSummary, @JsonKey(name: 'source_urls')  List<String> sourceUrls, @JsonKey(name: 'impacted_axis_names')  List<String> impactedAxisNames,  String? timestamp, @JsonKey(name: 'duration_ms')  int durationMs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _McpAuditTraceDto() when $default != null:
return $default(_that.id,_that.toolId,_that.stepName,_that.claimText,_that.query,_that.knowledgeGap,_that.searchRationale,_that.reasoning,_that.responseSummary,_that.sourceUrls,_that.impactedAxisNames,_that.timestamp,_that.durationMs);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? id, @JsonKey(name: 'tool_id')  String toolId, @JsonKey(name: 'step_name')  String stepName, @JsonKey(name: 'claim_text')  String? claimText,  String query, @JsonKey(name: 'knowledge_gap')  String knowledgeGap, @JsonKey(name: 'search_rationale')  String searchRationale,  String reasoning, @JsonKey(name: 'response_summary')  String responseSummary, @JsonKey(name: 'source_urls')  List<String> sourceUrls, @JsonKey(name: 'impacted_axis_names')  List<String> impactedAxisNames,  String? timestamp, @JsonKey(name: 'duration_ms')  int durationMs)  $default,) {final _that = this;
switch (_that) {
case _McpAuditTraceDto():
return $default(_that.id,_that.toolId,_that.stepName,_that.claimText,_that.query,_that.knowledgeGap,_that.searchRationale,_that.reasoning,_that.responseSummary,_that.sourceUrls,_that.impactedAxisNames,_that.timestamp,_that.durationMs);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? id, @JsonKey(name: 'tool_id')  String toolId, @JsonKey(name: 'step_name')  String stepName, @JsonKey(name: 'claim_text')  String? claimText,  String query, @JsonKey(name: 'knowledge_gap')  String knowledgeGap, @JsonKey(name: 'search_rationale')  String searchRationale,  String reasoning, @JsonKey(name: 'response_summary')  String responseSummary, @JsonKey(name: 'source_urls')  List<String> sourceUrls, @JsonKey(name: 'impacted_axis_names')  List<String> impactedAxisNames,  String? timestamp, @JsonKey(name: 'duration_ms')  int durationMs)?  $default,) {final _that = this;
switch (_that) {
case _McpAuditTraceDto() when $default != null:
return $default(_that.id,_that.toolId,_that.stepName,_that.claimText,_that.query,_that.knowledgeGap,_that.searchRationale,_that.reasoning,_that.responseSummary,_that.sourceUrls,_that.impactedAxisNames,_that.timestamp,_that.durationMs);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _McpAuditTraceDto implements McpAuditTraceDto {
  const _McpAuditTraceDto({this.id, @JsonKey(name: 'tool_id') required this.toolId, @JsonKey(name: 'step_name') required this.stepName, @JsonKey(name: 'claim_text') this.claimText, required this.query, @JsonKey(name: 'knowledge_gap') this.knowledgeGap = '', @JsonKey(name: 'search_rationale') this.searchRationale = '', this.reasoning = '', @JsonKey(name: 'response_summary') this.responseSummary = '', @JsonKey(name: 'source_urls') final  List<String> sourceUrls = const [], @JsonKey(name: 'impacted_axis_names') final  List<String> impactedAxisNames = const [], this.timestamp, @JsonKey(name: 'duration_ms') this.durationMs = 0}): _sourceUrls = sourceUrls,_impactedAxisNames = impactedAxisNames;
  factory _McpAuditTraceDto.fromJson(Map<String, dynamic> json) => _$McpAuditTraceDtoFromJson(json);

@override final  String? id;
@override@JsonKey(name: 'tool_id') final  String toolId;
@override@JsonKey(name: 'step_name') final  String stepName;
@override@JsonKey(name: 'claim_text') final  String? claimText;
@override final  String query;
@override@JsonKey(name: 'knowledge_gap') final  String knowledgeGap;
@override@JsonKey(name: 'search_rationale') final  String searchRationale;
@override@JsonKey() final  String reasoning;
@override@JsonKey(name: 'response_summary') final  String responseSummary;
 final  List<String> _sourceUrls;
@override@JsonKey(name: 'source_urls') List<String> get sourceUrls {
  if (_sourceUrls is EqualUnmodifiableListView) return _sourceUrls;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_sourceUrls);
}

 final  List<String> _impactedAxisNames;
@override@JsonKey(name: 'impacted_axis_names') List<String> get impactedAxisNames {
  if (_impactedAxisNames is EqualUnmodifiableListView) return _impactedAxisNames;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_impactedAxisNames);
}

@override final  String? timestamp;
@override@JsonKey(name: 'duration_ms') final  int durationMs;

/// Create a copy of McpAuditTraceDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$McpAuditTraceDtoCopyWith<_McpAuditTraceDto> get copyWith => __$McpAuditTraceDtoCopyWithImpl<_McpAuditTraceDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$McpAuditTraceDtoToJson(this, );
}



@override
String toString() {
  return 'McpAuditTraceDto(id: $id, toolId: $toolId, stepName: $stepName, claimText: $claimText, query: $query, knowledgeGap: $knowledgeGap, searchRationale: $searchRationale, reasoning: $reasoning, responseSummary: $responseSummary, sourceUrls: $sourceUrls, impactedAxisNames: $impactedAxisNames, timestamp: $timestamp, durationMs: $durationMs)';
}


}

/// @nodoc
abstract mixin class _$McpAuditTraceDtoCopyWith<$Res> implements $McpAuditTraceDtoCopyWith<$Res> {
  factory _$McpAuditTraceDtoCopyWith(_McpAuditTraceDto value, $Res Function(_McpAuditTraceDto) _then) = __$McpAuditTraceDtoCopyWithImpl;
@override @useResult
$Res call({
 String? id,@JsonKey(name: 'tool_id') String toolId,@JsonKey(name: 'step_name') String stepName,@JsonKey(name: 'claim_text') String? claimText, String query,@JsonKey(name: 'knowledge_gap') String knowledgeGap,@JsonKey(name: 'search_rationale') String searchRationale, String reasoning,@JsonKey(name: 'response_summary') String responseSummary,@JsonKey(name: 'source_urls') List<String> sourceUrls,@JsonKey(name: 'impacted_axis_names') List<String> impactedAxisNames, String? timestamp,@JsonKey(name: 'duration_ms') int durationMs
});




}
/// @nodoc
class __$McpAuditTraceDtoCopyWithImpl<$Res>
    implements _$McpAuditTraceDtoCopyWith<$Res> {
  __$McpAuditTraceDtoCopyWithImpl(this._self, this._then);

  final _McpAuditTraceDto _self;
  final $Res Function(_McpAuditTraceDto) _then;

/// Create a copy of McpAuditTraceDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? toolId = null,Object? stepName = null,Object? claimText = freezed,Object? query = null,Object? knowledgeGap = null,Object? searchRationale = null,Object? reasoning = null,Object? responseSummary = null,Object? sourceUrls = null,Object? impactedAxisNames = null,Object? timestamp = freezed,Object? durationMs = null,}) {
  return _then(_McpAuditTraceDto(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,toolId: null == toolId ? _self.toolId : toolId // ignore: cast_nullable_to_non_nullable
as String,stepName: null == stepName ? _self.stepName : stepName // ignore: cast_nullable_to_non_nullable
as String,claimText: freezed == claimText ? _self.claimText : claimText // ignore: cast_nullable_to_non_nullable
as String?,query: null == query ? _self.query : query // ignore: cast_nullable_to_non_nullable
as String,knowledgeGap: null == knowledgeGap ? _self.knowledgeGap : knowledgeGap // ignore: cast_nullable_to_non_nullable
as String,searchRationale: null == searchRationale ? _self.searchRationale : searchRationale // ignore: cast_nullable_to_non_nullable
as String,reasoning: null == reasoning ? _self.reasoning : reasoning // ignore: cast_nullable_to_non_nullable
as String,responseSummary: null == responseSummary ? _self.responseSummary : responseSummary // ignore: cast_nullable_to_non_nullable
as String,sourceUrls: null == sourceUrls ? _self._sourceUrls : sourceUrls // ignore: cast_nullable_to_non_nullable
as List<String>,impactedAxisNames: null == impactedAxisNames ? _self._impactedAxisNames : impactedAxisNames // ignore: cast_nullable_to_non_nullable
as List<String>,timestamp: freezed == timestamp ? _self.timestamp : timestamp // ignore: cast_nullable_to_non_nullable
as String?,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$MatrixScorecardRowDto {

@JsonKey(name: 'block_id') String get blockId; String get name;@JsonKey(name: 'label_i18n') I18nText get labelI18n; String? get description; double? get score;@JsonKey(name: 'score_display_label') String? get scoreDisplayLabel;@JsonKey(name: 'scale_min') double? get scaleMin;@JsonKey(name: 'scale_max') double? get scaleMax;@JsonKey(name: 'normalized_score') double? get normalizedScore;@JsonKey(name: 'true_atoms') int? get trueAtoms;@JsonKey(name: 'total_atoms') int? get totalAtoms;@JsonKey(name: 'row_explanation') String get rowExplanation;@JsonKey(name: 'cited_source_id') String? get citedSourceId;@JsonKey(name: 'cited_text_quote') String? get citedTextQuote;@JsonKey(name: 'cited_web_citation') String? get citedWebCitation;@JsonKey(name: 'evidence_type') EvidenceType? get evidenceType;@JsonKey(name: 'tda_state') TDAState? get tdaState; double? get confidence;@JsonKey(name: 'inner_sdui_blocks') List<SduiBlockDTO> get innerSduiBlocks;@JsonKey(name: 'level_breakdown') Map<String, String>? get levelBreakdown;@JsonKey(name: 'level_names') Map<String, String>? get levelNames;@JsonKey(name: 'ui_boundary_labels') Map<String, String>? get uiBoundaryLabels;@JsonKey(name: 'ui_plot_ratio') double? get uiPlotRatio;@JsonKey(name: 'is_evaluative') bool get isEvaluative;@JsonKey(name: 'contextual_override') bool? get contextualOverride;@JsonKey(name: 'semantic_reasoning') String? get semanticReasoning;@JsonKey(name: 'evaluated_atoms') List<ScorecardAtomDto> get evaluatedAtoms;@JsonKey(name: 'clustered_row_sources') List<McpAuditTraceDto> get clusteredRowSources;@JsonKey(name: 'used_evidence_ids') List<String> get usedEvidenceIds;
/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MatrixScorecardRowDtoCopyWith<MatrixScorecardRowDto> get copyWith => _$MatrixScorecardRowDtoCopyWithImpl<MatrixScorecardRowDto>(this as MatrixScorecardRowDto, _$identity);

  /// Serializes this MatrixScorecardRowDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'MatrixScorecardRowDto(blockId: $blockId, name: $name, labelI18n: $labelI18n, description: $description, score: $score, scoreDisplayLabel: $scoreDisplayLabel, scaleMin: $scaleMin, scaleMax: $scaleMax, normalizedScore: $normalizedScore, trueAtoms: $trueAtoms, totalAtoms: $totalAtoms, rowExplanation: $rowExplanation, citedSourceId: $citedSourceId, citedTextQuote: $citedTextQuote, citedWebCitation: $citedWebCitation, evidenceType: $evidenceType, tdaState: $tdaState, confidence: $confidence, innerSduiBlocks: $innerSduiBlocks, levelBreakdown: $levelBreakdown, levelNames: $levelNames, uiBoundaryLabels: $uiBoundaryLabels, uiPlotRatio: $uiPlotRatio, isEvaluative: $isEvaluative, contextualOverride: $contextualOverride, semanticReasoning: $semanticReasoning, evaluatedAtoms: $evaluatedAtoms, clusteredRowSources: $clusteredRowSources, usedEvidenceIds: $usedEvidenceIds)';
}


}

/// @nodoc
abstract mixin class $MatrixScorecardRowDtoCopyWith<$Res>  {
  factory $MatrixScorecardRowDtoCopyWith(MatrixScorecardRowDto value, $Res Function(MatrixScorecardRowDto) _then) = _$MatrixScorecardRowDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'block_id') String blockId, String name,@JsonKey(name: 'label_i18n') I18nText labelI18n, String? description, double? score,@JsonKey(name: 'score_display_label') String? scoreDisplayLabel,@JsonKey(name: 'scale_min') double? scaleMin,@JsonKey(name: 'scale_max') double? scaleMax,@JsonKey(name: 'normalized_score') double? normalizedScore,@JsonKey(name: 'true_atoms') int? trueAtoms,@JsonKey(name: 'total_atoms') int? totalAtoms,@JsonKey(name: 'row_explanation') String rowExplanation,@JsonKey(name: 'cited_source_id') String? citedSourceId,@JsonKey(name: 'cited_text_quote') String? citedTextQuote,@JsonKey(name: 'cited_web_citation') String? citedWebCitation,@JsonKey(name: 'evidence_type') EvidenceType? evidenceType,@JsonKey(name: 'tda_state') TDAState? tdaState, double? confidence,@JsonKey(name: 'inner_sdui_blocks') List<SduiBlockDTO> innerSduiBlocks,@JsonKey(name: 'level_breakdown') Map<String, String>? levelBreakdown,@JsonKey(name: 'level_names') Map<String, String>? levelNames,@JsonKey(name: 'ui_boundary_labels') Map<String, String>? uiBoundaryLabels,@JsonKey(name: 'ui_plot_ratio') double? uiPlotRatio,@JsonKey(name: 'is_evaluative') bool isEvaluative,@JsonKey(name: 'contextual_override') bool? contextualOverride,@JsonKey(name: 'semantic_reasoning') String? semanticReasoning,@JsonKey(name: 'evaluated_atoms') List<ScorecardAtomDto> evaluatedAtoms,@JsonKey(name: 'clustered_row_sources') List<McpAuditTraceDto> clusteredRowSources,@JsonKey(name: 'used_evidence_ids') List<String> usedEvidenceIds
});


$I18nTextCopyWith<$Res> get labelI18n;$TDAStateCopyWith<$Res>? get tdaState;

}
/// @nodoc
class _$MatrixScorecardRowDtoCopyWithImpl<$Res>
    implements $MatrixScorecardRowDtoCopyWith<$Res> {
  _$MatrixScorecardRowDtoCopyWithImpl(this._self, this._then);

  final MatrixScorecardRowDto _self;
  final $Res Function(MatrixScorecardRowDto) _then;

/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? blockId = null,Object? name = null,Object? labelI18n = null,Object? description = freezed,Object? score = freezed,Object? scoreDisplayLabel = freezed,Object? scaleMin = freezed,Object? scaleMax = freezed,Object? normalizedScore = freezed,Object? trueAtoms = freezed,Object? totalAtoms = freezed,Object? rowExplanation = null,Object? citedSourceId = freezed,Object? citedTextQuote = freezed,Object? citedWebCitation = freezed,Object? evidenceType = freezed,Object? tdaState = freezed,Object? confidence = freezed,Object? innerSduiBlocks = null,Object? levelBreakdown = freezed,Object? levelNames = freezed,Object? uiBoundaryLabels = freezed,Object? uiPlotRatio = freezed,Object? isEvaluative = null,Object? contextualOverride = freezed,Object? semanticReasoning = freezed,Object? evaluatedAtoms = null,Object? clusteredRowSources = null,Object? usedEvidenceIds = null,}) {
  return _then(_self.copyWith(
blockId: null == blockId ? _self.blockId : blockId // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,labelI18n: null == labelI18n ? _self.labelI18n : labelI18n // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,score: freezed == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as double?,scoreDisplayLabel: freezed == scoreDisplayLabel ? _self.scoreDisplayLabel : scoreDisplayLabel // ignore: cast_nullable_to_non_nullable
as String?,scaleMin: freezed == scaleMin ? _self.scaleMin : scaleMin // ignore: cast_nullable_to_non_nullable
as double?,scaleMax: freezed == scaleMax ? _self.scaleMax : scaleMax // ignore: cast_nullable_to_non_nullable
as double?,normalizedScore: freezed == normalizedScore ? _self.normalizedScore : normalizedScore // ignore: cast_nullable_to_non_nullable
as double?,trueAtoms: freezed == trueAtoms ? _self.trueAtoms : trueAtoms // ignore: cast_nullable_to_non_nullable
as int?,totalAtoms: freezed == totalAtoms ? _self.totalAtoms : totalAtoms // ignore: cast_nullable_to_non_nullable
as int?,rowExplanation: null == rowExplanation ? _self.rowExplanation : rowExplanation // ignore: cast_nullable_to_non_nullable
as String,citedSourceId: freezed == citedSourceId ? _self.citedSourceId : citedSourceId // ignore: cast_nullable_to_non_nullable
as String?,citedTextQuote: freezed == citedTextQuote ? _self.citedTextQuote : citedTextQuote // ignore: cast_nullable_to_non_nullable
as String?,citedWebCitation: freezed == citedWebCitation ? _self.citedWebCitation : citedWebCitation // ignore: cast_nullable_to_non_nullable
as String?,evidenceType: freezed == evidenceType ? _self.evidenceType : evidenceType // ignore: cast_nullable_to_non_nullable
as EvidenceType?,tdaState: freezed == tdaState ? _self.tdaState : tdaState // ignore: cast_nullable_to_non_nullable
as TDAState?,confidence: freezed == confidence ? _self.confidence : confidence // ignore: cast_nullable_to_non_nullable
as double?,innerSduiBlocks: null == innerSduiBlocks ? _self.innerSduiBlocks : innerSduiBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,levelBreakdown: freezed == levelBreakdown ? _self.levelBreakdown : levelBreakdown // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,levelNames: freezed == levelNames ? _self.levelNames : levelNames // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,uiBoundaryLabels: freezed == uiBoundaryLabels ? _self.uiBoundaryLabels : uiBoundaryLabels // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,uiPlotRatio: freezed == uiPlotRatio ? _self.uiPlotRatio : uiPlotRatio // ignore: cast_nullable_to_non_nullable
as double?,isEvaluative: null == isEvaluative ? _self.isEvaluative : isEvaluative // ignore: cast_nullable_to_non_nullable
as bool,contextualOverride: freezed == contextualOverride ? _self.contextualOverride : contextualOverride // ignore: cast_nullable_to_non_nullable
as bool?,semanticReasoning: freezed == semanticReasoning ? _self.semanticReasoning : semanticReasoning // ignore: cast_nullable_to_non_nullable
as String?,evaluatedAtoms: null == evaluatedAtoms ? _self.evaluatedAtoms : evaluatedAtoms // ignore: cast_nullable_to_non_nullable
as List<ScorecardAtomDto>,clusteredRowSources: null == clusteredRowSources ? _self.clusteredRowSources : clusteredRowSources // ignore: cast_nullable_to_non_nullable
as List<McpAuditTraceDto>,usedEvidenceIds: null == usedEvidenceIds ? _self.usedEvidenceIds : usedEvidenceIds // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}
/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get labelI18n {
  
  return $I18nTextCopyWith<$Res>(_self.labelI18n, (value) {
    return _then(_self.copyWith(labelI18n: value));
  });
}/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$TDAStateCopyWith<$Res>? get tdaState {
    if (_self.tdaState == null) {
    return null;
  }

  return $TDAStateCopyWith<$Res>(_self.tdaState!, (value) {
    return _then(_self.copyWith(tdaState: value));
  });
}
}


/// Adds pattern-matching-related methods to [MatrixScorecardRowDto].
extension MatrixScorecardRowDtoPatterns on MatrixScorecardRowDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MatrixScorecardRowDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MatrixScorecardRowDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MatrixScorecardRowDto value)  $default,){
final _that = this;
switch (_that) {
case _MatrixScorecardRowDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MatrixScorecardRowDto value)?  $default,){
final _that = this;
switch (_that) {
case _MatrixScorecardRowDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'block_id')  String blockId,  String name, @JsonKey(name: 'label_i18n')  I18nText labelI18n,  String? description,  double? score, @JsonKey(name: 'score_display_label')  String? scoreDisplayLabel, @JsonKey(name: 'scale_min')  double? scaleMin, @JsonKey(name: 'scale_max')  double? scaleMax, @JsonKey(name: 'normalized_score')  double? normalizedScore, @JsonKey(name: 'true_atoms')  int? trueAtoms, @JsonKey(name: 'total_atoms')  int? totalAtoms, @JsonKey(name: 'row_explanation')  String rowExplanation, @JsonKey(name: 'cited_source_id')  String? citedSourceId, @JsonKey(name: 'cited_text_quote')  String? citedTextQuote, @JsonKey(name: 'cited_web_citation')  String? citedWebCitation, @JsonKey(name: 'evidence_type')  EvidenceType? evidenceType, @JsonKey(name: 'tda_state')  TDAState? tdaState,  double? confidence, @JsonKey(name: 'inner_sdui_blocks')  List<SduiBlockDTO> innerSduiBlocks, @JsonKey(name: 'level_breakdown')  Map<String, String>? levelBreakdown, @JsonKey(name: 'level_names')  Map<String, String>? levelNames, @JsonKey(name: 'ui_boundary_labels')  Map<String, String>? uiBoundaryLabels, @JsonKey(name: 'ui_plot_ratio')  double? uiPlotRatio, @JsonKey(name: 'is_evaluative')  bool isEvaluative, @JsonKey(name: 'contextual_override')  bool? contextualOverride, @JsonKey(name: 'semantic_reasoning')  String? semanticReasoning, @JsonKey(name: 'evaluated_atoms')  List<ScorecardAtomDto> evaluatedAtoms, @JsonKey(name: 'clustered_row_sources')  List<McpAuditTraceDto> clusteredRowSources, @JsonKey(name: 'used_evidence_ids')  List<String> usedEvidenceIds)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MatrixScorecardRowDto() when $default != null:
return $default(_that.blockId,_that.name,_that.labelI18n,_that.description,_that.score,_that.scoreDisplayLabel,_that.scaleMin,_that.scaleMax,_that.normalizedScore,_that.trueAtoms,_that.totalAtoms,_that.rowExplanation,_that.citedSourceId,_that.citedTextQuote,_that.citedWebCitation,_that.evidenceType,_that.tdaState,_that.confidence,_that.innerSduiBlocks,_that.levelBreakdown,_that.levelNames,_that.uiBoundaryLabels,_that.uiPlotRatio,_that.isEvaluative,_that.contextualOverride,_that.semanticReasoning,_that.evaluatedAtoms,_that.clusteredRowSources,_that.usedEvidenceIds);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'block_id')  String blockId,  String name, @JsonKey(name: 'label_i18n')  I18nText labelI18n,  String? description,  double? score, @JsonKey(name: 'score_display_label')  String? scoreDisplayLabel, @JsonKey(name: 'scale_min')  double? scaleMin, @JsonKey(name: 'scale_max')  double? scaleMax, @JsonKey(name: 'normalized_score')  double? normalizedScore, @JsonKey(name: 'true_atoms')  int? trueAtoms, @JsonKey(name: 'total_atoms')  int? totalAtoms, @JsonKey(name: 'row_explanation')  String rowExplanation, @JsonKey(name: 'cited_source_id')  String? citedSourceId, @JsonKey(name: 'cited_text_quote')  String? citedTextQuote, @JsonKey(name: 'cited_web_citation')  String? citedWebCitation, @JsonKey(name: 'evidence_type')  EvidenceType? evidenceType, @JsonKey(name: 'tda_state')  TDAState? tdaState,  double? confidence, @JsonKey(name: 'inner_sdui_blocks')  List<SduiBlockDTO> innerSduiBlocks, @JsonKey(name: 'level_breakdown')  Map<String, String>? levelBreakdown, @JsonKey(name: 'level_names')  Map<String, String>? levelNames, @JsonKey(name: 'ui_boundary_labels')  Map<String, String>? uiBoundaryLabels, @JsonKey(name: 'ui_plot_ratio')  double? uiPlotRatio, @JsonKey(name: 'is_evaluative')  bool isEvaluative, @JsonKey(name: 'contextual_override')  bool? contextualOverride, @JsonKey(name: 'semantic_reasoning')  String? semanticReasoning, @JsonKey(name: 'evaluated_atoms')  List<ScorecardAtomDto> evaluatedAtoms, @JsonKey(name: 'clustered_row_sources')  List<McpAuditTraceDto> clusteredRowSources, @JsonKey(name: 'used_evidence_ids')  List<String> usedEvidenceIds)  $default,) {final _that = this;
switch (_that) {
case _MatrixScorecardRowDto():
return $default(_that.blockId,_that.name,_that.labelI18n,_that.description,_that.score,_that.scoreDisplayLabel,_that.scaleMin,_that.scaleMax,_that.normalizedScore,_that.trueAtoms,_that.totalAtoms,_that.rowExplanation,_that.citedSourceId,_that.citedTextQuote,_that.citedWebCitation,_that.evidenceType,_that.tdaState,_that.confidence,_that.innerSduiBlocks,_that.levelBreakdown,_that.levelNames,_that.uiBoundaryLabels,_that.uiPlotRatio,_that.isEvaluative,_that.contextualOverride,_that.semanticReasoning,_that.evaluatedAtoms,_that.clusteredRowSources,_that.usedEvidenceIds);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'block_id')  String blockId,  String name, @JsonKey(name: 'label_i18n')  I18nText labelI18n,  String? description,  double? score, @JsonKey(name: 'score_display_label')  String? scoreDisplayLabel, @JsonKey(name: 'scale_min')  double? scaleMin, @JsonKey(name: 'scale_max')  double? scaleMax, @JsonKey(name: 'normalized_score')  double? normalizedScore, @JsonKey(name: 'true_atoms')  int? trueAtoms, @JsonKey(name: 'total_atoms')  int? totalAtoms, @JsonKey(name: 'row_explanation')  String rowExplanation, @JsonKey(name: 'cited_source_id')  String? citedSourceId, @JsonKey(name: 'cited_text_quote')  String? citedTextQuote, @JsonKey(name: 'cited_web_citation')  String? citedWebCitation, @JsonKey(name: 'evidence_type')  EvidenceType? evidenceType, @JsonKey(name: 'tda_state')  TDAState? tdaState,  double? confidence, @JsonKey(name: 'inner_sdui_blocks')  List<SduiBlockDTO> innerSduiBlocks, @JsonKey(name: 'level_breakdown')  Map<String, String>? levelBreakdown, @JsonKey(name: 'level_names')  Map<String, String>? levelNames, @JsonKey(name: 'ui_boundary_labels')  Map<String, String>? uiBoundaryLabels, @JsonKey(name: 'ui_plot_ratio')  double? uiPlotRatio, @JsonKey(name: 'is_evaluative')  bool isEvaluative, @JsonKey(name: 'contextual_override')  bool? contextualOverride, @JsonKey(name: 'semantic_reasoning')  String? semanticReasoning, @JsonKey(name: 'evaluated_atoms')  List<ScorecardAtomDto> evaluatedAtoms, @JsonKey(name: 'clustered_row_sources')  List<McpAuditTraceDto> clusteredRowSources, @JsonKey(name: 'used_evidence_ids')  List<String> usedEvidenceIds)?  $default,) {final _that = this;
switch (_that) {
case _MatrixScorecardRowDto() when $default != null:
return $default(_that.blockId,_that.name,_that.labelI18n,_that.description,_that.score,_that.scoreDisplayLabel,_that.scaleMin,_that.scaleMax,_that.normalizedScore,_that.trueAtoms,_that.totalAtoms,_that.rowExplanation,_that.citedSourceId,_that.citedTextQuote,_that.citedWebCitation,_that.evidenceType,_that.tdaState,_that.confidence,_that.innerSduiBlocks,_that.levelBreakdown,_that.levelNames,_that.uiBoundaryLabels,_that.uiPlotRatio,_that.isEvaluative,_that.contextualOverride,_that.semanticReasoning,_that.evaluatedAtoms,_that.clusteredRowSources,_that.usedEvidenceIds);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _MatrixScorecardRowDto extends MatrixScorecardRowDto {
  const _MatrixScorecardRowDto({@JsonKey(name: 'block_id') required this.blockId, required this.name, @JsonKey(name: 'label_i18n') required this.labelI18n, this.description, this.score, @JsonKey(name: 'score_display_label') this.scoreDisplayLabel, @JsonKey(name: 'scale_min') this.scaleMin, @JsonKey(name: 'scale_max') this.scaleMax, @JsonKey(name: 'normalized_score') this.normalizedScore, @JsonKey(name: 'true_atoms') this.trueAtoms, @JsonKey(name: 'total_atoms') this.totalAtoms, @JsonKey(name: 'row_explanation') this.rowExplanation = '', @JsonKey(name: 'cited_source_id') this.citedSourceId, @JsonKey(name: 'cited_text_quote') this.citedTextQuote, @JsonKey(name: 'cited_web_citation') this.citedWebCitation, @JsonKey(name: 'evidence_type') this.evidenceType, @JsonKey(name: 'tda_state') this.tdaState, this.confidence, @JsonKey(name: 'inner_sdui_blocks') final  List<SduiBlockDTO> innerSduiBlocks = const [], @JsonKey(name: 'level_breakdown') final  Map<String, String>? levelBreakdown, @JsonKey(name: 'level_names') final  Map<String, String>? levelNames, @JsonKey(name: 'ui_boundary_labels') final  Map<String, String>? uiBoundaryLabels, @JsonKey(name: 'ui_plot_ratio') this.uiPlotRatio, @JsonKey(name: 'is_evaluative') this.isEvaluative = true, @JsonKey(name: 'contextual_override') this.contextualOverride, @JsonKey(name: 'semantic_reasoning') this.semanticReasoning, @JsonKey(name: 'evaluated_atoms') final  List<ScorecardAtomDto> evaluatedAtoms = const [], @JsonKey(name: 'clustered_row_sources') final  List<McpAuditTraceDto> clusteredRowSources = const [], @JsonKey(name: 'used_evidence_ids') final  List<String> usedEvidenceIds = const []}): _innerSduiBlocks = innerSduiBlocks,_levelBreakdown = levelBreakdown,_levelNames = levelNames,_uiBoundaryLabels = uiBoundaryLabels,_evaluatedAtoms = evaluatedAtoms,_clusteredRowSources = clusteredRowSources,_usedEvidenceIds = usedEvidenceIds,super._();
  factory _MatrixScorecardRowDto.fromJson(Map<String, dynamic> json) => _$MatrixScorecardRowDtoFromJson(json);

@override@JsonKey(name: 'block_id') final  String blockId;
@override final  String name;
@override@JsonKey(name: 'label_i18n') final  I18nText labelI18n;
@override final  String? description;
@override final  double? score;
@override@JsonKey(name: 'score_display_label') final  String? scoreDisplayLabel;
@override@JsonKey(name: 'scale_min') final  double? scaleMin;
@override@JsonKey(name: 'scale_max') final  double? scaleMax;
@override@JsonKey(name: 'normalized_score') final  double? normalizedScore;
@override@JsonKey(name: 'true_atoms') final  int? trueAtoms;
@override@JsonKey(name: 'total_atoms') final  int? totalAtoms;
@override@JsonKey(name: 'row_explanation') final  String rowExplanation;
@override@JsonKey(name: 'cited_source_id') final  String? citedSourceId;
@override@JsonKey(name: 'cited_text_quote') final  String? citedTextQuote;
@override@JsonKey(name: 'cited_web_citation') final  String? citedWebCitation;
@override@JsonKey(name: 'evidence_type') final  EvidenceType? evidenceType;
@override@JsonKey(name: 'tda_state') final  TDAState? tdaState;
@override final  double? confidence;
 final  List<SduiBlockDTO> _innerSduiBlocks;
@override@JsonKey(name: 'inner_sdui_blocks') List<SduiBlockDTO> get innerSduiBlocks {
  if (_innerSduiBlocks is EqualUnmodifiableListView) return _innerSduiBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_innerSduiBlocks);
}

 final  Map<String, String>? _levelBreakdown;
@override@JsonKey(name: 'level_breakdown') Map<String, String>? get levelBreakdown {
  final value = _levelBreakdown;
  if (value == null) return null;
  if (_levelBreakdown is EqualUnmodifiableMapView) return _levelBreakdown;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, String>? _levelNames;
@override@JsonKey(name: 'level_names') Map<String, String>? get levelNames {
  final value = _levelNames;
  if (value == null) return null;
  if (_levelNames is EqualUnmodifiableMapView) return _levelNames;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  Map<String, String>? _uiBoundaryLabels;
@override@JsonKey(name: 'ui_boundary_labels') Map<String, String>? get uiBoundaryLabels {
  final value = _uiBoundaryLabels;
  if (value == null) return null;
  if (_uiBoundaryLabels is EqualUnmodifiableMapView) return _uiBoundaryLabels;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'ui_plot_ratio') final  double? uiPlotRatio;
@override@JsonKey(name: 'is_evaluative') final  bool isEvaluative;
@override@JsonKey(name: 'contextual_override') final  bool? contextualOverride;
@override@JsonKey(name: 'semantic_reasoning') final  String? semanticReasoning;
 final  List<ScorecardAtomDto> _evaluatedAtoms;
@override@JsonKey(name: 'evaluated_atoms') List<ScorecardAtomDto> get evaluatedAtoms {
  if (_evaluatedAtoms is EqualUnmodifiableListView) return _evaluatedAtoms;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_evaluatedAtoms);
}

 final  List<McpAuditTraceDto> _clusteredRowSources;
@override@JsonKey(name: 'clustered_row_sources') List<McpAuditTraceDto> get clusteredRowSources {
  if (_clusteredRowSources is EqualUnmodifiableListView) return _clusteredRowSources;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_clusteredRowSources);
}

 final  List<String> _usedEvidenceIds;
@override@JsonKey(name: 'used_evidence_ids') List<String> get usedEvidenceIds {
  if (_usedEvidenceIds is EqualUnmodifiableListView) return _usedEvidenceIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_usedEvidenceIds);
}


/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MatrixScorecardRowDtoCopyWith<_MatrixScorecardRowDto> get copyWith => __$MatrixScorecardRowDtoCopyWithImpl<_MatrixScorecardRowDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MatrixScorecardRowDtoToJson(this, );
}



@override
String toString() {
  return 'MatrixScorecardRowDto(blockId: $blockId, name: $name, labelI18n: $labelI18n, description: $description, score: $score, scoreDisplayLabel: $scoreDisplayLabel, scaleMin: $scaleMin, scaleMax: $scaleMax, normalizedScore: $normalizedScore, trueAtoms: $trueAtoms, totalAtoms: $totalAtoms, rowExplanation: $rowExplanation, citedSourceId: $citedSourceId, citedTextQuote: $citedTextQuote, citedWebCitation: $citedWebCitation, evidenceType: $evidenceType, tdaState: $tdaState, confidence: $confidence, innerSduiBlocks: $innerSduiBlocks, levelBreakdown: $levelBreakdown, levelNames: $levelNames, uiBoundaryLabels: $uiBoundaryLabels, uiPlotRatio: $uiPlotRatio, isEvaluative: $isEvaluative, contextualOverride: $contextualOverride, semanticReasoning: $semanticReasoning, evaluatedAtoms: $evaluatedAtoms, clusteredRowSources: $clusteredRowSources, usedEvidenceIds: $usedEvidenceIds)';
}


}

/// @nodoc
abstract mixin class _$MatrixScorecardRowDtoCopyWith<$Res> implements $MatrixScorecardRowDtoCopyWith<$Res> {
  factory _$MatrixScorecardRowDtoCopyWith(_MatrixScorecardRowDto value, $Res Function(_MatrixScorecardRowDto) _then) = __$MatrixScorecardRowDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'block_id') String blockId, String name,@JsonKey(name: 'label_i18n') I18nText labelI18n, String? description, double? score,@JsonKey(name: 'score_display_label') String? scoreDisplayLabel,@JsonKey(name: 'scale_min') double? scaleMin,@JsonKey(name: 'scale_max') double? scaleMax,@JsonKey(name: 'normalized_score') double? normalizedScore,@JsonKey(name: 'true_atoms') int? trueAtoms,@JsonKey(name: 'total_atoms') int? totalAtoms,@JsonKey(name: 'row_explanation') String rowExplanation,@JsonKey(name: 'cited_source_id') String? citedSourceId,@JsonKey(name: 'cited_text_quote') String? citedTextQuote,@JsonKey(name: 'cited_web_citation') String? citedWebCitation,@JsonKey(name: 'evidence_type') EvidenceType? evidenceType,@JsonKey(name: 'tda_state') TDAState? tdaState, double? confidence,@JsonKey(name: 'inner_sdui_blocks') List<SduiBlockDTO> innerSduiBlocks,@JsonKey(name: 'level_breakdown') Map<String, String>? levelBreakdown,@JsonKey(name: 'level_names') Map<String, String>? levelNames,@JsonKey(name: 'ui_boundary_labels') Map<String, String>? uiBoundaryLabels,@JsonKey(name: 'ui_plot_ratio') double? uiPlotRatio,@JsonKey(name: 'is_evaluative') bool isEvaluative,@JsonKey(name: 'contextual_override') bool? contextualOverride,@JsonKey(name: 'semantic_reasoning') String? semanticReasoning,@JsonKey(name: 'evaluated_atoms') List<ScorecardAtomDto> evaluatedAtoms,@JsonKey(name: 'clustered_row_sources') List<McpAuditTraceDto> clusteredRowSources,@JsonKey(name: 'used_evidence_ids') List<String> usedEvidenceIds
});


@override $I18nTextCopyWith<$Res> get labelI18n;@override $TDAStateCopyWith<$Res>? get tdaState;

}
/// @nodoc
class __$MatrixScorecardRowDtoCopyWithImpl<$Res>
    implements _$MatrixScorecardRowDtoCopyWith<$Res> {
  __$MatrixScorecardRowDtoCopyWithImpl(this._self, this._then);

  final _MatrixScorecardRowDto _self;
  final $Res Function(_MatrixScorecardRowDto) _then;

/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? blockId = null,Object? name = null,Object? labelI18n = null,Object? description = freezed,Object? score = freezed,Object? scoreDisplayLabel = freezed,Object? scaleMin = freezed,Object? scaleMax = freezed,Object? normalizedScore = freezed,Object? trueAtoms = freezed,Object? totalAtoms = freezed,Object? rowExplanation = null,Object? citedSourceId = freezed,Object? citedTextQuote = freezed,Object? citedWebCitation = freezed,Object? evidenceType = freezed,Object? tdaState = freezed,Object? confidence = freezed,Object? innerSduiBlocks = null,Object? levelBreakdown = freezed,Object? levelNames = freezed,Object? uiBoundaryLabels = freezed,Object? uiPlotRatio = freezed,Object? isEvaluative = null,Object? contextualOverride = freezed,Object? semanticReasoning = freezed,Object? evaluatedAtoms = null,Object? clusteredRowSources = null,Object? usedEvidenceIds = null,}) {
  return _then(_MatrixScorecardRowDto(
blockId: null == blockId ? _self.blockId : blockId // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,labelI18n: null == labelI18n ? _self.labelI18n : labelI18n // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,score: freezed == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as double?,scoreDisplayLabel: freezed == scoreDisplayLabel ? _self.scoreDisplayLabel : scoreDisplayLabel // ignore: cast_nullable_to_non_nullable
as String?,scaleMin: freezed == scaleMin ? _self.scaleMin : scaleMin // ignore: cast_nullable_to_non_nullable
as double?,scaleMax: freezed == scaleMax ? _self.scaleMax : scaleMax // ignore: cast_nullable_to_non_nullable
as double?,normalizedScore: freezed == normalizedScore ? _self.normalizedScore : normalizedScore // ignore: cast_nullable_to_non_nullable
as double?,trueAtoms: freezed == trueAtoms ? _self.trueAtoms : trueAtoms // ignore: cast_nullable_to_non_nullable
as int?,totalAtoms: freezed == totalAtoms ? _self.totalAtoms : totalAtoms // ignore: cast_nullable_to_non_nullable
as int?,rowExplanation: null == rowExplanation ? _self.rowExplanation : rowExplanation // ignore: cast_nullable_to_non_nullable
as String,citedSourceId: freezed == citedSourceId ? _self.citedSourceId : citedSourceId // ignore: cast_nullable_to_non_nullable
as String?,citedTextQuote: freezed == citedTextQuote ? _self.citedTextQuote : citedTextQuote // ignore: cast_nullable_to_non_nullable
as String?,citedWebCitation: freezed == citedWebCitation ? _self.citedWebCitation : citedWebCitation // ignore: cast_nullable_to_non_nullable
as String?,evidenceType: freezed == evidenceType ? _self.evidenceType : evidenceType // ignore: cast_nullable_to_non_nullable
as EvidenceType?,tdaState: freezed == tdaState ? _self.tdaState : tdaState // ignore: cast_nullable_to_non_nullable
as TDAState?,confidence: freezed == confidence ? _self.confidence : confidence // ignore: cast_nullable_to_non_nullable
as double?,innerSduiBlocks: null == innerSduiBlocks ? _self._innerSduiBlocks : innerSduiBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,levelBreakdown: freezed == levelBreakdown ? _self._levelBreakdown : levelBreakdown // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,levelNames: freezed == levelNames ? _self._levelNames : levelNames // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,uiBoundaryLabels: freezed == uiBoundaryLabels ? _self._uiBoundaryLabels : uiBoundaryLabels // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,uiPlotRatio: freezed == uiPlotRatio ? _self.uiPlotRatio : uiPlotRatio // ignore: cast_nullable_to_non_nullable
as double?,isEvaluative: null == isEvaluative ? _self.isEvaluative : isEvaluative // ignore: cast_nullable_to_non_nullable
as bool,contextualOverride: freezed == contextualOverride ? _self.contextualOverride : contextualOverride // ignore: cast_nullable_to_non_nullable
as bool?,semanticReasoning: freezed == semanticReasoning ? _self.semanticReasoning : semanticReasoning // ignore: cast_nullable_to_non_nullable
as String?,evaluatedAtoms: null == evaluatedAtoms ? _self._evaluatedAtoms : evaluatedAtoms // ignore: cast_nullable_to_non_nullable
as List<ScorecardAtomDto>,clusteredRowSources: null == clusteredRowSources ? _self._clusteredRowSources : clusteredRowSources // ignore: cast_nullable_to_non_nullable
as List<McpAuditTraceDto>,usedEvidenceIds: null == usedEvidenceIds ? _self._usedEvidenceIds : usedEvidenceIds // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get labelI18n {
  
  return $I18nTextCopyWith<$Res>(_self.labelI18n, (value) {
    return _then(_self.copyWith(labelI18n: value));
  });
}/// Create a copy of MatrixScorecardRowDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$TDAStateCopyWith<$Res>? get tdaState {
    if (_self.tdaState == null) {
    return null;
  }

  return $TDAStateCopyWith<$Res>(_self.tdaState!, (value) {
    return _then(_self.copyWith(tdaState: value));
  });
}
}

// dart format on
