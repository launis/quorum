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

 String get sourceUrl; String get citationReference;
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
 String sourceUrl, String citationReference
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
@pragma('vm:prefer-inline') @override $Res call({Object? sourceUrl = null,Object? citationReference = null,}) {
  return _then(_self.copyWith(
sourceUrl: null == sourceUrl ? _self.sourceUrl : sourceUrl // ignore: cast_nullable_to_non_nullable
as String,citationReference: null == citationReference ? _self.citationReference : citationReference // ignore: cast_nullable_to_non_nullable
as String,
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String sourceUrl,  String citationReference)?  $default,{required TResult orElse(),}) {final _that = this;
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String sourceUrl,  String citationReference)  $default,) {final _that = this;
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String sourceUrl,  String citationReference)?  $default,) {final _that = this;
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
  const _TheoryGrounding({required this.sourceUrl, required this.citationReference}): super._();
  factory _TheoryGrounding.fromJson(Map<String, dynamic> json) => _$TheoryGroundingFromJson(json);

@override final  String sourceUrl;
@override final  String citationReference;

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
 String sourceUrl, String citationReference
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
@override @pragma('vm:prefer-inline') $Res call({Object? sourceUrl = null,Object? citationReference = null,}) {
  return _then(_TheoryGrounding(
sourceUrl: null == sourceUrl ? _self.sourceUrl : sourceUrl // ignore: cast_nullable_to_non_nullable
as String,citationReference: null == citationReference ? _self.citationReference : citationReference // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$MatrixClaim {

 I18nText get label; String get aiDescription; List<String>? get microAtoms;
/// Create a copy of MatrixClaim
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MatrixClaimCopyWith<MatrixClaim> get copyWith => _$MatrixClaimCopyWithImpl<MatrixClaim>(this as MatrixClaim, _$identity);

  /// Serializes this MatrixClaim to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'MatrixClaim(label: $label, aiDescription: $aiDescription, microAtoms: $microAtoms)';
}


}

/// @nodoc
abstract mixin class $MatrixClaimCopyWith<$Res>  {
  factory $MatrixClaimCopyWith(MatrixClaim value, $Res Function(MatrixClaim) _then) = _$MatrixClaimCopyWithImpl;
@useResult
$Res call({
 I18nText label, String aiDescription, List<String>? microAtoms
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
@pragma('vm:prefer-inline') @override $Res call({Object? label = null,Object? aiDescription = null,Object? microAtoms = freezed,}) {
  return _then(_self.copyWith(
label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,aiDescription: null == aiDescription ? _self.aiDescription : aiDescription // ignore: cast_nullable_to_non_nullable
as String,microAtoms: freezed == microAtoms ? _self.microAtoms : microAtoms // ignore: cast_nullable_to_non_nullable
as List<String>?,
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( I18nText label,  String aiDescription,  List<String>? microAtoms)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MatrixClaim() when $default != null:
return $default(_that.label,_that.aiDescription,_that.microAtoms);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( I18nText label,  String aiDescription,  List<String>? microAtoms)  $default,) {final _that = this;
switch (_that) {
case _MatrixClaim():
return $default(_that.label,_that.aiDescription,_that.microAtoms);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( I18nText label,  String aiDescription,  List<String>? microAtoms)?  $default,) {final _that = this;
switch (_that) {
case _MatrixClaim() when $default != null:
return $default(_that.label,_that.aiDescription,_that.microAtoms);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _MatrixClaim extends MatrixClaim {
  const _MatrixClaim({required this.label, required this.aiDescription, final  List<String>? microAtoms}): _microAtoms = microAtoms,super._();
  factory _MatrixClaim.fromJson(Map<String, dynamic> json) => _$MatrixClaimFromJson(json);

@override final  I18nText label;
@override final  String aiDescription;
 final  List<String>? _microAtoms;
@override List<String>? get microAtoms {
  final value = _microAtoms;
  if (value == null) return null;
  if (_microAtoms is EqualUnmodifiableListView) return _microAtoms;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
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
  return 'MatrixClaim(label: $label, aiDescription: $aiDescription, microAtoms: $microAtoms)';
}


}

/// @nodoc
abstract mixin class _$MatrixClaimCopyWith<$Res> implements $MatrixClaimCopyWith<$Res> {
  factory _$MatrixClaimCopyWith(_MatrixClaim value, $Res Function(_MatrixClaim) _then) = __$MatrixClaimCopyWithImpl;
@override @useResult
$Res call({
 I18nText label, String aiDescription, List<String>? microAtoms
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
@override @pragma('vm:prefer-inline') $Res call({Object? label = null,Object? aiDescription = null,Object? microAtoms = freezed,}) {
  return _then(_MatrixClaim(
label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as I18nText,aiDescription: null == aiDescription ? _self.aiDescription : aiDescription // ignore: cast_nullable_to_non_nullable
as String,microAtoms: freezed == microAtoms ? _self._microAtoms : microAtoms // ignore: cast_nullable_to_non_nullable
as List<String>?,
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

@StrictOpaqueIdConverter() String get id; String get slug; String? get organizationId; I18nText get label; I18nText get description; String? get aiDescription; String get categoryId; bool get isEvaluative; BlockDataType get type; bool get allowDecimals; List<String> get outputExtensions; TheoryGrounding? get theoryGrounding; int? get scaleMin; int? get scaleMax;@JsonKey(includeToJson: false) int? get computedMin;@JsonKey(includeToJson: false) int? get computedMax; List<MatrixScale>? get scales; List<MatrixRow>? get rows; List<I18nText>? get columns;
/// Create a copy of PromptBlock
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PromptBlockCopyWith<PromptBlock> get copyWith => _$PromptBlockCopyWithImpl<PromptBlock>(this as PromptBlock, _$identity);

  /// Serializes this PromptBlock to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'PromptBlock(id: $id, slug: $slug, organizationId: $organizationId, label: $label, description: $description, aiDescription: $aiDescription, categoryId: $categoryId, isEvaluative: $isEvaluative, type: $type, allowDecimals: $allowDecimals, outputExtensions: $outputExtensions, theoryGrounding: $theoryGrounding, scaleMin: $scaleMin, scaleMax: $scaleMax, computedMin: $computedMin, computedMax: $computedMax, scales: $scales, rows: $rows, columns: $columns)';
}


}

/// @nodoc
abstract mixin class $PromptBlockCopyWith<$Res>  {
  factory $PromptBlockCopyWith(PromptBlock value, $Res Function(PromptBlock) _then) = _$PromptBlockCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, String? organizationId, I18nText label, I18nText description, String? aiDescription, String categoryId, bool isEvaluative, BlockDataType type, bool allowDecimals, List<String> outputExtensions, TheoryGrounding? theoryGrounding, int? scaleMin, int? scaleMax,@JsonKey(includeToJson: false) int? computedMin,@JsonKey(includeToJson: false) int? computedMax, List<MatrixScale>? scales, List<MatrixRow>? rows, List<I18nText>? columns
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
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? organizationId = freezed,Object? label = null,Object? description = null,Object? aiDescription = freezed,Object? categoryId = null,Object? isEvaluative = null,Object? type = null,Object? allowDecimals = null,Object? outputExtensions = null,Object? theoryGrounding = freezed,Object? scaleMin = freezed,Object? scaleMax = freezed,Object? computedMin = freezed,Object? computedMax = freezed,Object? scales = freezed,Object? rows = freezed,Object? columns = freezed,}) {
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
as TheoryGrounding?,scaleMin: freezed == scaleMin ? _self.scaleMin : scaleMin // ignore: cast_nullable_to_non_nullable
as int?,scaleMax: freezed == scaleMax ? _self.scaleMax : scaleMax // ignore: cast_nullable_to_non_nullable
as int?,computedMin: freezed == computedMin ? _self.computedMin : computedMin // ignore: cast_nullable_to_non_nullable
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  String? organizationId,  I18nText label,  I18nText description,  String? aiDescription,  String categoryId,  bool isEvaluative,  BlockDataType type,  bool allowDecimals,  List<String> outputExtensions,  TheoryGrounding? theoryGrounding,  int? scaleMin,  int? scaleMax, @JsonKey(includeToJson: false)  int? computedMin, @JsonKey(includeToJson: false)  int? computedMax,  List<MatrixScale>? scales,  List<MatrixRow>? rows,  List<I18nText>? columns)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PromptBlock() when $default != null:
return $default(_that.id,_that.slug,_that.organizationId,_that.label,_that.description,_that.aiDescription,_that.categoryId,_that.isEvaluative,_that.type,_that.allowDecimals,_that.outputExtensions,_that.theoryGrounding,_that.scaleMin,_that.scaleMax,_that.computedMin,_that.computedMax,_that.scales,_that.rows,_that.columns);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug,  String? organizationId,  I18nText label,  I18nText description,  String? aiDescription,  String categoryId,  bool isEvaluative,  BlockDataType type,  bool allowDecimals,  List<String> outputExtensions,  TheoryGrounding? theoryGrounding,  int? scaleMin,  int? scaleMax, @JsonKey(includeToJson: false)  int? computedMin, @JsonKey(includeToJson: false)  int? computedMax,  List<MatrixScale>? scales,  List<MatrixRow>? rows,  List<I18nText>? columns)  $default,) {final _that = this;
switch (_that) {
case _PromptBlock():
return $default(_that.id,_that.slug,_that.organizationId,_that.label,_that.description,_that.aiDescription,_that.categoryId,_that.isEvaluative,_that.type,_that.allowDecimals,_that.outputExtensions,_that.theoryGrounding,_that.scaleMin,_that.scaleMax,_that.computedMin,_that.computedMax,_that.scales,_that.rows,_that.columns);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug,  String? organizationId,  I18nText label,  I18nText description,  String? aiDescription,  String categoryId,  bool isEvaluative,  BlockDataType type,  bool allowDecimals,  List<String> outputExtensions,  TheoryGrounding? theoryGrounding,  int? scaleMin,  int? scaleMax, @JsonKey(includeToJson: false)  int? computedMin, @JsonKey(includeToJson: false)  int? computedMax,  List<MatrixScale>? scales,  List<MatrixRow>? rows,  List<I18nText>? columns)?  $default,) {final _that = this;
switch (_that) {
case _PromptBlock() when $default != null:
return $default(_that.id,_that.slug,_that.organizationId,_that.label,_that.description,_that.aiDescription,_that.categoryId,_that.isEvaluative,_that.type,_that.allowDecimals,_that.outputExtensions,_that.theoryGrounding,_that.scaleMin,_that.scaleMax,_that.computedMin,_that.computedMax,_that.scales,_that.rows,_that.columns);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _PromptBlock extends PromptBlock {
  const _PromptBlock({@StrictOpaqueIdConverter() required this.id, required this.slug, this.organizationId, required this.label, required this.description, this.aiDescription, this.categoryId = 'system', this.isEvaluative = true, this.type = BlockDataType.stringType, this.allowDecimals = false, final  List<String> outputExtensions = const [], this.theoryGrounding, this.scaleMin, this.scaleMax, @JsonKey(includeToJson: false) this.computedMin, @JsonKey(includeToJson: false) this.computedMax, final  List<MatrixScale>? scales, final  List<MatrixRow>? rows, final  List<I18nText>? columns}): _outputExtensions = outputExtensions,_scales = scales,_rows = rows,_columns = columns,super._();
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
@override final  int? scaleMin;
@override final  int? scaleMax;
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
  return 'PromptBlock(id: $id, slug: $slug, organizationId: $organizationId, label: $label, description: $description, aiDescription: $aiDescription, categoryId: $categoryId, isEvaluative: $isEvaluative, type: $type, allowDecimals: $allowDecimals, outputExtensions: $outputExtensions, theoryGrounding: $theoryGrounding, scaleMin: $scaleMin, scaleMax: $scaleMax, computedMin: $computedMin, computedMax: $computedMax, scales: $scales, rows: $rows, columns: $columns)';
}


}

/// @nodoc
abstract mixin class _$PromptBlockCopyWith<$Res> implements $PromptBlockCopyWith<$Res> {
  factory _$PromptBlockCopyWith(_PromptBlock value, $Res Function(_PromptBlock) _then) = __$PromptBlockCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug, String? organizationId, I18nText label, I18nText description, String? aiDescription, String categoryId, bool isEvaluative, BlockDataType type, bool allowDecimals, List<String> outputExtensions, TheoryGrounding? theoryGrounding, int? scaleMin, int? scaleMax,@JsonKey(includeToJson: false) int? computedMin,@JsonKey(includeToJson: false) int? computedMax, List<MatrixScale>? scales, List<MatrixRow>? rows, List<I18nText>? columns
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? organizationId = freezed,Object? label = null,Object? description = null,Object? aiDescription = freezed,Object? categoryId = null,Object? isEvaluative = null,Object? type = null,Object? allowDecimals = null,Object? outputExtensions = null,Object? theoryGrounding = freezed,Object? scaleMin = freezed,Object? scaleMax = freezed,Object? computedMin = freezed,Object? computedMax = freezed,Object? scales = freezed,Object? rows = freezed,Object? columns = freezed,}) {
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
as TheoryGrounding?,scaleMin: freezed == scaleMin ? _self.scaleMin : scaleMin // ignore: cast_nullable_to_non_nullable
as int?,scaleMax: freezed == scaleMax ? _self.scaleMax : scaleMax // ignore: cast_nullable_to_non_nullable
as int?,computedMin: freezed == computedMin ? _self.computedMin : computedMin // ignore: cast_nullable_to_non_nullable
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
