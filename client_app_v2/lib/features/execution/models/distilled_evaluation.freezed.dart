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
mixin _$DistilledExtensionValue {

 String? get stringValue; double? get numberValue; bool? get boolValue; List<String>? get stringListValue;
/// Create a copy of DistilledExtensionValue
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DistilledExtensionValueCopyWith<DistilledExtensionValue> get copyWith => _$DistilledExtensionValueCopyWithImpl<DistilledExtensionValue>(this as DistilledExtensionValue, _$identity);

  /// Serializes this DistilledExtensionValue to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is DistilledExtensionValue&&(identical(other.stringValue, stringValue) || other.stringValue == stringValue)&&(identical(other.numberValue, numberValue) || other.numberValue == numberValue)&&(identical(other.boolValue, boolValue) || other.boolValue == boolValue)&&const DeepCollectionEquality().equals(other.stringListValue, stringListValue));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,stringValue,numberValue,boolValue,const DeepCollectionEquality().hash(stringListValue));

@override
String toString() {
  return 'DistilledExtensionValue(stringValue: $stringValue, numberValue: $numberValue, boolValue: $boolValue, stringListValue: $stringListValue)';
}


}

/// @nodoc
abstract mixin class $DistilledExtensionValueCopyWith<$Res>  {
  factory $DistilledExtensionValueCopyWith(DistilledExtensionValue value, $Res Function(DistilledExtensionValue) _then) = _$DistilledExtensionValueCopyWithImpl;
@useResult
$Res call({
 String? stringValue, double? numberValue, bool? boolValue, List<String>? stringListValue
});




}
/// @nodoc
class _$DistilledExtensionValueCopyWithImpl<$Res>
    implements $DistilledExtensionValueCopyWith<$Res> {
  _$DistilledExtensionValueCopyWithImpl(this._self, this._then);

  final DistilledExtensionValue _self;
  final $Res Function(DistilledExtensionValue) _then;

/// Create a copy of DistilledExtensionValue
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? stringValue = freezed,Object? numberValue = freezed,Object? boolValue = freezed,Object? stringListValue = freezed,}) {
  return _then(_self.copyWith(
stringValue: freezed == stringValue ? _self.stringValue : stringValue // ignore: cast_nullable_to_non_nullable
as String?,numberValue: freezed == numberValue ? _self.numberValue : numberValue // ignore: cast_nullable_to_non_nullable
as double?,boolValue: freezed == boolValue ? _self.boolValue : boolValue // ignore: cast_nullable_to_non_nullable
as bool?,stringListValue: freezed == stringListValue ? _self.stringListValue : stringListValue // ignore: cast_nullable_to_non_nullable
as List<String>?,
  ));
}

}


/// Adds pattern-matching-related methods to [DistilledExtensionValue].
extension DistilledExtensionValuePatterns on DistilledExtensionValue {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DistilledExtensionValue value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DistilledExtensionValue() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DistilledExtensionValue value)  $default,){
final _that = this;
switch (_that) {
case _DistilledExtensionValue():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DistilledExtensionValue value)?  $default,){
final _that = this;
switch (_that) {
case _DistilledExtensionValue() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? stringValue,  double? numberValue,  bool? boolValue,  List<String>? stringListValue)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DistilledExtensionValue() when $default != null:
return $default(_that.stringValue,_that.numberValue,_that.boolValue,_that.stringListValue);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? stringValue,  double? numberValue,  bool? boolValue,  List<String>? stringListValue)  $default,) {final _that = this;
switch (_that) {
case _DistilledExtensionValue():
return $default(_that.stringValue,_that.numberValue,_that.boolValue,_that.stringListValue);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? stringValue,  double? numberValue,  bool? boolValue,  List<String>? stringListValue)?  $default,) {final _that = this;
switch (_that) {
case _DistilledExtensionValue() when $default != null:
return $default(_that.stringValue,_that.numberValue,_that.boolValue,_that.stringListValue);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true, fieldRename: FieldRename.snake)
class _DistilledExtensionValue extends DistilledExtensionValue {
  const _DistilledExtensionValue({this.stringValue, this.numberValue, this.boolValue, final  List<String>? stringListValue}): _stringListValue = stringListValue,super._();
  factory _DistilledExtensionValue.fromJson(Map<String, dynamic> json) => _$DistilledExtensionValueFromJson(json);

@override final  String? stringValue;
@override final  double? numberValue;
@override final  bool? boolValue;
 final  List<String>? _stringListValue;
@override List<String>? get stringListValue {
  final value = _stringListValue;
  if (value == null) return null;
  if (_stringListValue is EqualUnmodifiableListView) return _stringListValue;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}


/// Create a copy of DistilledExtensionValue
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DistilledExtensionValueCopyWith<_DistilledExtensionValue> get copyWith => __$DistilledExtensionValueCopyWithImpl<_DistilledExtensionValue>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DistilledExtensionValueToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _DistilledExtensionValue&&(identical(other.stringValue, stringValue) || other.stringValue == stringValue)&&(identical(other.numberValue, numberValue) || other.numberValue == numberValue)&&(identical(other.boolValue, boolValue) || other.boolValue == boolValue)&&const DeepCollectionEquality().equals(other._stringListValue, _stringListValue));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,stringValue,numberValue,boolValue,const DeepCollectionEquality().hash(_stringListValue));

@override
String toString() {
  return 'DistilledExtensionValue(stringValue: $stringValue, numberValue: $numberValue, boolValue: $boolValue, stringListValue: $stringListValue)';
}


}

/// @nodoc
abstract mixin class _$DistilledExtensionValueCopyWith<$Res> implements $DistilledExtensionValueCopyWith<$Res> {
  factory _$DistilledExtensionValueCopyWith(_DistilledExtensionValue value, $Res Function(_DistilledExtensionValue) _then) = __$DistilledExtensionValueCopyWithImpl;
@override @useResult
$Res call({
 String? stringValue, double? numberValue, bool? boolValue, List<String>? stringListValue
});




}
/// @nodoc
class __$DistilledExtensionValueCopyWithImpl<$Res>
    implements _$DistilledExtensionValueCopyWith<$Res> {
  __$DistilledExtensionValueCopyWithImpl(this._self, this._then);

  final _DistilledExtensionValue _self;
  final $Res Function(_DistilledExtensionValue) _then;

/// Create a copy of DistilledExtensionValue
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? stringValue = freezed,Object? numberValue = freezed,Object? boolValue = freezed,Object? stringListValue = freezed,}) {
  return _then(_DistilledExtensionValue(
stringValue: freezed == stringValue ? _self.stringValue : stringValue // ignore: cast_nullable_to_non_nullable
as String?,numberValue: freezed == numberValue ? _self.numberValue : numberValue // ignore: cast_nullable_to_non_nullable
as double?,boolValue: freezed == boolValue ? _self.boolValue : boolValue // ignore: cast_nullable_to_non_nullable
as bool?,stringListValue: freezed == stringListValue ? _self._stringListValue : stringListValue // ignore: cast_nullable_to_non_nullable
as List<String>?,
  ));
}


}


/// @nodoc
mixin _$DistilledEvaluation {

 String? get atomId; List<String> get exactQuotes; String? get semanticReasoning; String? get status;@DistilledExtensionValueConverter() Map<String, DistilledExtensionValue>? get extensions; List<String> get dependsOnTdaIds; List<String> get shortCircuitReasonTdaIds; bool get isInverseEvidence; int get topologicalOutDegree;
/// Create a copy of DistilledEvaluation
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DistilledEvaluationCopyWith<DistilledEvaluation> get copyWith => _$DistilledEvaluationCopyWithImpl<DistilledEvaluation>(this as DistilledEvaluation, _$identity);

  /// Serializes this DistilledEvaluation to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'DistilledEvaluation(atomId: $atomId, exactQuotes: $exactQuotes, semanticReasoning: $semanticReasoning, status: $status, extensions: $extensions, dependsOnTdaIds: $dependsOnTdaIds, shortCircuitReasonTdaIds: $shortCircuitReasonTdaIds, isInverseEvidence: $isInverseEvidence, topologicalOutDegree: $topologicalOutDegree)';
}


}

/// @nodoc
abstract mixin class $DistilledEvaluationCopyWith<$Res>  {
  factory $DistilledEvaluationCopyWith(DistilledEvaluation value, $Res Function(DistilledEvaluation) _then) = _$DistilledEvaluationCopyWithImpl;
@useResult
$Res call({
 String? atomId, List<String> exactQuotes, String? semanticReasoning, String? status,@DistilledExtensionValueConverter() Map<String, DistilledExtensionValue>? extensions, List<String> dependsOnTdaIds, List<String> shortCircuitReasonTdaIds, bool isInverseEvidence, int topologicalOutDegree
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
@pragma('vm:prefer-inline') @override $Res call({Object? atomId = freezed,Object? exactQuotes = null,Object? semanticReasoning = freezed,Object? status = freezed,Object? extensions = freezed,Object? dependsOnTdaIds = null,Object? shortCircuitReasonTdaIds = null,Object? isInverseEvidence = null,Object? topologicalOutDegree = null,}) {
  return _then(_self.copyWith(
atomId: freezed == atomId ? _self.atomId : atomId // ignore: cast_nullable_to_non_nullable
as String?,exactQuotes: null == exactQuotes ? _self.exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,semanticReasoning: freezed == semanticReasoning ? _self.semanticReasoning : semanticReasoning // ignore: cast_nullable_to_non_nullable
as String?,status: freezed == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String?,extensions: freezed == extensions ? _self.extensions : extensions // ignore: cast_nullable_to_non_nullable
as Map<String, DistilledExtensionValue>?,dependsOnTdaIds: null == dependsOnTdaIds ? _self.dependsOnTdaIds : dependsOnTdaIds // ignore: cast_nullable_to_non_nullable
as List<String>,shortCircuitReasonTdaIds: null == shortCircuitReasonTdaIds ? _self.shortCircuitReasonTdaIds : shortCircuitReasonTdaIds // ignore: cast_nullable_to_non_nullable
as List<String>,isInverseEvidence: null == isInverseEvidence ? _self.isInverseEvidence : isInverseEvidence // ignore: cast_nullable_to_non_nullable
as bool,topologicalOutDegree: null == topologicalOutDegree ? _self.topologicalOutDegree : topologicalOutDegree // ignore: cast_nullable_to_non_nullable
as int,
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? atomId,  List<String> exactQuotes,  String? semanticReasoning,  String? status, @DistilledExtensionValueConverter()  Map<String, DistilledExtensionValue>? extensions,  List<String> dependsOnTdaIds,  List<String> shortCircuitReasonTdaIds,  bool isInverseEvidence,  int topologicalOutDegree)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DistilledEvaluation() when $default != null:
return $default(_that.atomId,_that.exactQuotes,_that.semanticReasoning,_that.status,_that.extensions,_that.dependsOnTdaIds,_that.shortCircuitReasonTdaIds,_that.isInverseEvidence,_that.topologicalOutDegree);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? atomId,  List<String> exactQuotes,  String? semanticReasoning,  String? status, @DistilledExtensionValueConverter()  Map<String, DistilledExtensionValue>? extensions,  List<String> dependsOnTdaIds,  List<String> shortCircuitReasonTdaIds,  bool isInverseEvidence,  int topologicalOutDegree)  $default,) {final _that = this;
switch (_that) {
case _DistilledEvaluation():
return $default(_that.atomId,_that.exactQuotes,_that.semanticReasoning,_that.status,_that.extensions,_that.dependsOnTdaIds,_that.shortCircuitReasonTdaIds,_that.isInverseEvidence,_that.topologicalOutDegree);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? atomId,  List<String> exactQuotes,  String? semanticReasoning,  String? status, @DistilledExtensionValueConverter()  Map<String, DistilledExtensionValue>? extensions,  List<String> dependsOnTdaIds,  List<String> shortCircuitReasonTdaIds,  bool isInverseEvidence,  int topologicalOutDegree)?  $default,) {final _that = this;
switch (_that) {
case _DistilledEvaluation() when $default != null:
return $default(_that.atomId,_that.exactQuotes,_that.semanticReasoning,_that.status,_that.extensions,_that.dependsOnTdaIds,_that.shortCircuitReasonTdaIds,_that.isInverseEvidence,_that.topologicalOutDegree);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true, fieldRename: FieldRename.snake)
class _DistilledEvaluation implements DistilledEvaluation {
  const _DistilledEvaluation({this.atomId, required final  List<String> exactQuotes, this.semanticReasoning, this.status, @DistilledExtensionValueConverter() final  Map<String, DistilledExtensionValue>? extensions, final  List<String> dependsOnTdaIds = const [], final  List<String> shortCircuitReasonTdaIds = const [], this.isInverseEvidence = false, this.topologicalOutDegree = 0}): _exactQuotes = exactQuotes,_extensions = extensions,_dependsOnTdaIds = dependsOnTdaIds,_shortCircuitReasonTdaIds = shortCircuitReasonTdaIds;
  factory _DistilledEvaluation.fromJson(Map<String, dynamic> json) => _$DistilledEvaluationFromJson(json);

@override final  String? atomId;
 final  List<String> _exactQuotes;
@override List<String> get exactQuotes {
  if (_exactQuotes is EqualUnmodifiableListView) return _exactQuotes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_exactQuotes);
}

@override final  String? semanticReasoning;
@override final  String? status;
 final  Map<String, DistilledExtensionValue>? _extensions;
@override@DistilledExtensionValueConverter() Map<String, DistilledExtensionValue>? get extensions {
  final value = _extensions;
  if (value == null) return null;
  if (_extensions is EqualUnmodifiableMapView) return _extensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  List<String> _dependsOnTdaIds;
@override@JsonKey() List<String> get dependsOnTdaIds {
  if (_dependsOnTdaIds is EqualUnmodifiableListView) return _dependsOnTdaIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_dependsOnTdaIds);
}

 final  List<String> _shortCircuitReasonTdaIds;
@override@JsonKey() List<String> get shortCircuitReasonTdaIds {
  if (_shortCircuitReasonTdaIds is EqualUnmodifiableListView) return _shortCircuitReasonTdaIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_shortCircuitReasonTdaIds);
}

@override@JsonKey() final  bool isInverseEvidence;
@override@JsonKey() final  int topologicalOutDegree;

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
String toString() {
  return 'DistilledEvaluation(atomId: $atomId, exactQuotes: $exactQuotes, semanticReasoning: $semanticReasoning, status: $status, extensions: $extensions, dependsOnTdaIds: $dependsOnTdaIds, shortCircuitReasonTdaIds: $shortCircuitReasonTdaIds, isInverseEvidence: $isInverseEvidence, topologicalOutDegree: $topologicalOutDegree)';
}


}

/// @nodoc
abstract mixin class _$DistilledEvaluationCopyWith<$Res> implements $DistilledEvaluationCopyWith<$Res> {
  factory _$DistilledEvaluationCopyWith(_DistilledEvaluation value, $Res Function(_DistilledEvaluation) _then) = __$DistilledEvaluationCopyWithImpl;
@override @useResult
$Res call({
 String? atomId, List<String> exactQuotes, String? semanticReasoning, String? status,@DistilledExtensionValueConverter() Map<String, DistilledExtensionValue>? extensions, List<String> dependsOnTdaIds, List<String> shortCircuitReasonTdaIds, bool isInverseEvidence, int topologicalOutDegree
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
@override @pragma('vm:prefer-inline') $Res call({Object? atomId = freezed,Object? exactQuotes = null,Object? semanticReasoning = freezed,Object? status = freezed,Object? extensions = freezed,Object? dependsOnTdaIds = null,Object? shortCircuitReasonTdaIds = null,Object? isInverseEvidence = null,Object? topologicalOutDegree = null,}) {
  return _then(_DistilledEvaluation(
atomId: freezed == atomId ? _self.atomId : atomId // ignore: cast_nullable_to_non_nullable
as String?,exactQuotes: null == exactQuotes ? _self._exactQuotes : exactQuotes // ignore: cast_nullable_to_non_nullable
as List<String>,semanticReasoning: freezed == semanticReasoning ? _self.semanticReasoning : semanticReasoning // ignore: cast_nullable_to_non_nullable
as String?,status: freezed == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String?,extensions: freezed == extensions ? _self._extensions : extensions // ignore: cast_nullable_to_non_nullable
as Map<String, DistilledExtensionValue>?,dependsOnTdaIds: null == dependsOnTdaIds ? _self._dependsOnTdaIds : dependsOnTdaIds // ignore: cast_nullable_to_non_nullable
as List<String>,shortCircuitReasonTdaIds: null == shortCircuitReasonTdaIds ? _self._shortCircuitReasonTdaIds : shortCircuitReasonTdaIds // ignore: cast_nullable_to_non_nullable
as List<String>,isInverseEvidence: null == isInverseEvidence ? _self.isInverseEvidence : isInverseEvidence // ignore: cast_nullable_to_non_nullable
as bool,topologicalOutDegree: null == topologicalOutDegree ? _self.topologicalOutDegree : topologicalOutDegree // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}

// dart format on
