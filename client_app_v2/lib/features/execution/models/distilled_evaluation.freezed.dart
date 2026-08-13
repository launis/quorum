// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'distilled_evaluation.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$DistilledEvaluation {

 String? get atomId; List<String> get exactQuotes; String? get semanticReasoning; Map<String, dynamic>? get extensions;
/// Create a copy of DistilledEvaluation
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DistilledEvaluationCopyWith<DistilledEvaluation> get copyWith => _$DistilledEvaluationCopyWithImpl<DistilledEvaluation>(this as DistilledEvaluation, _$identity);

  /// Serializes this DistilledEvaluation to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DistilledEvaluation&&(identical(other.atomId, atomId) || other.atomId == atomId)&&const DeepCollectionEquality().equals(other.exactQuotes, exactQuotes)&&(identical(other.semanticReasoning, semanticReasoning) || other.semanticReasoning == semanticReasoning)&&const DeepCollectionEquality().equals(other.extensions, extensions));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,atomId,const DeepCollectionEquality().hash(exactQuotes),semanticReasoning,const DeepCollectionEquality().hash(extensions));

@override
String toString() {
  return 'DistilledEvaluation(atomId: $atomId, exactQuotes: $exactQuotes, semanticReasoning: $semanticReasoning, extensions: $extensions)';
}


}

/// @nodoc
abstract mixin class $DistilledEvaluationCopyWith<$Res>  {
  factory $DistilledEvaluationCopyWith(DistilledEvaluation value, $Res Function(DistilledEvaluation) _then) = _$DistilledEvaluationCopyWithImpl;
@useResult
$Res call({
 String? atomId, List<String> exactQuotes, String? semanticReasoning, Map<String, dynamic>? extensions
});




}
/// @nodoc
class _$DistilledEvaluationCopyWithImpl<$Res>
    implements $DistilledEvaluationCopyWith<$Res> {
  _$DistilledEvaluationCopyWithImpl(this._self, this._then);

  final DistilledEvaluation _self;
  final $Res Function(DistilledEvaluation) _then;

/// Create a copy of DistilledEvaluation
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? atomId = freezed,Object? exactQuotes = null,Object? semanticReasoning = freezed,Object? extensions = freezed,}) {
  return _then(_self.copyWith(
atomId: freezed == atomId ? _self.atomId : atomId // ignore: cast_nullable_to_non_nullable
as String?,exactQuotes: null == exactQuotes ? _self.exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,semanticReasoning: freezed == semanticReasoning ? _self.semanticReasoning : semanticReasoning // ignore: cast_nullable_to_non_nullable
as String?,extensions: freezed == extensions ? _self.extensions : extensions // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}

}


/// Adds pattern-matching-related methods to [DistilledEvaluation].
extension DistilledEvaluationPatterns on DistilledEvaluation {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DistilledEvaluation value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DistilledEvaluation() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DistilledEvaluation value)  $default,){
final _that = this;
switch (_that) {
case _DistilledEvaluation():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DistilledEvaluation value)?  $default,){
final _that = this;
switch (_that) {
case _DistilledEvaluation() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? atomId,  List<String> exactQuotes,  String? semanticReasoning,  Map<String, dynamic>? extensions)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DistilledEvaluation() when $default != null:
return $default(_that.atomId,_that.exactQuotes,_that.semanticReasoning,_that.extensions);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? atomId,  List<String> exactQuotes,  String? semanticReasoning,  Map<String, dynamic>? extensions)  $default,) {final _that = this;
switch (_that) {
case _DistilledEvaluation():
return $default(_that.atomId,_that.exactQuotes,_that.semanticReasoning,_that.extensions);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? atomId,  List<String> exactQuotes,  String? semanticReasoning,  Map<String, dynamic>? extensions)?  $default,) {final _that = this;
switch (_that) {
case _DistilledEvaluation() when $default != null:
return $default(_that.atomId,_that.exactQuotes,_that.semanticReasoning,_that.extensions);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true, fieldRename: FieldRename.snake)
class _DistilledEvaluation implements DistilledEvaluation {
  const _DistilledEvaluation({this.atomId, final  List<String> exactQuotes = const [], this.semanticReasoning, final  Map<String, dynamic>? extensions}): _exactQuotes = exactQuotes,_extensions = extensions;
  factory _DistilledEvaluation.fromJson(Map<String, dynamic> json) => _$DistilledEvaluationFromJson(json);

@override final  String? atomId;
 final  List<String> _exactQuotes;
@override@JsonKey() List<String> get exactQuotes {
  if (_exactQuotes is EqualUnmodifiableListView) return _exactQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_exactQuotes);
}

@override final  String? semanticReasoning;
 final  Map<String, dynamic>? _extensions;
@override Map<String, dynamic>? get extensions {
  final value = _extensions;
  if (value == null) return null;
  if (_extensions is EqualUnmodifiableMapView) return _extensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}


/// Create a copy of DistilledEvaluation
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DistilledEvaluationCopyWith<_DistilledEvaluation> get copyWith => __$DistilledEvaluationCopyWithImpl<_DistilledEvaluation>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DistilledEvaluationToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DistilledEvaluation&&(identical(other.atomId, atomId) || other.atomId == atomId)&&const DeepCollectionEquality().equals(other._exactQuotes, _exactQuotes)&&(identical(other.semanticReasoning, semanticReasoning) || other.semanticReasoning == semanticReasoning)&&const DeepCollectionEquality().equals(other._extensions, _extensions));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,atomId,const DeepCollectionEquality().hash(_exactQuotes),semanticReasoning,const DeepCollectionEquality().hash(_extensions));

@override
String toString() {
  return 'DistilledEvaluation(atomId: $atomId, exactQuotes: $exactQuotes, semanticReasoning: $semanticReasoning, extensions: $extensions)';
}


}

/// @nodoc
abstract mixin class _$DistilledEvaluationCopyWith<$Res> implements $DistilledEvaluationCopyWith<$Res> {
  factory _$DistilledEvaluationCopyWith(_DistilledEvaluation value, $Res Function(_DistilledEvaluation) _then) = __$DistilledEvaluationCopyWithImpl;
@override @useResult
$Res call({
 String? atomId, List<String> exactQuotes, String? semanticReasoning, Map<String, dynamic>? extensions
});




}
/// @nodoc
class __$DistilledEvaluationCopyWithImpl<$Res>
    implements _$DistilledEvaluationCopyWith<$Res> {
  __$DistilledEvaluationCopyWithImpl(this._self, this._then);

  final _DistilledEvaluation _self;
  final $Res Function(_DistilledEvaluation) _then;

/// Create a copy of DistilledEvaluation
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? atomId = freezed,Object? exactQuotes = null,Object? semanticReasoning = freezed,Object? extensions = freezed,}) {
  return _then(_DistilledEvaluation(
atomId: freezed == atomId ? _self.atomId : atomId // ignore: cast_nullable_to_non_nullable
as String?,exactQuotes: null == exactQuotes ? _self._exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,semanticReasoning: freezed == semanticReasoning ? _self.semanticReasoning : semanticReasoning // ignore: cast_nullable_to_non_nullable
as String?,extensions: freezed == extensions ? _self._extensions : extensions // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,
  ));
}


}

// dart format on
