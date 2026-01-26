// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'workflow_summary.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$WorkflowSummary {

 String get id; String get name; String? get description; DateTime get updatedAt;
/// Create a copy of WorkflowSummary
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowSummaryCopyWith<WorkflowSummary> get copyWith => _$WorkflowSummaryCopyWithImpl<WorkflowSummary>(this as WorkflowSummary, _$identity);

  /// Serializes this WorkflowSummary to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is WorkflowSummary&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,updatedAt);

@override
String toString() {
  return 'WorkflowSummary(id: $id, name: $name, description: $description, updatedAt: $updatedAt)';
}


}

/// @nodoc
abstract mixin class $WorkflowSummaryCopyWith<$Res>  {
  factory $WorkflowSummaryCopyWith(WorkflowSummary value, $Res Function(WorkflowSummary) _then) = _$WorkflowSummaryCopyWithImpl;
@useResult
$Res call({
 String id, String name, String? description, DateTime updatedAt
});




}
/// @nodoc
class _$WorkflowSummaryCopyWithImpl<$Res>
    implements $WorkflowSummaryCopyWith<$Res> {
  _$WorkflowSummaryCopyWithImpl(this._self, this._then);

  final WorkflowSummary _self;
  final $Res Function(WorkflowSummary) _then;

/// Create a copy of WorkflowSummary
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? updatedAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [WorkflowSummary].
extension WorkflowSummaryPatterns on WorkflowSummary {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WorkflowSummary value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WorkflowSummary() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WorkflowSummary value)  $default,){
final _that = this;
switch (_that) {
case _WorkflowSummary():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WorkflowSummary value)?  $default,){
final _that = this;
switch (_that) {
case _WorkflowSummary() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String? description,  DateTime updatedAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WorkflowSummary() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.updatedAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String? description,  DateTime updatedAt)  $default,) {final _that = this;
switch (_that) {
case _WorkflowSummary():
return $default(_that.id,_that.name,_that.description,_that.updatedAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String? description,  DateTime updatedAt)?  $default,) {final _that = this;
switch (_that) {
case _WorkflowSummary() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.updatedAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _WorkflowSummary implements WorkflowSummary {
  const _WorkflowSummary({required this.id, required this.name, this.description, required this.updatedAt});
  factory _WorkflowSummary.fromJson(Map<String, dynamic> json) => _$WorkflowSummaryFromJson(json);

@override final  String id;
@override final  String name;
@override final  String? description;
@override final  DateTime updatedAt;

/// Create a copy of WorkflowSummary
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WorkflowSummaryCopyWith<_WorkflowSummary> get copyWith => __$WorkflowSummaryCopyWithImpl<_WorkflowSummary>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$WorkflowSummaryToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _WorkflowSummary&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.updatedAt, updatedAt) || other.updatedAt == updatedAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,updatedAt);

@override
String toString() {
  return 'WorkflowSummary(id: $id, name: $name, description: $description, updatedAt: $updatedAt)';
}


}

/// @nodoc
abstract mixin class _$WorkflowSummaryCopyWith<$Res> implements $WorkflowSummaryCopyWith<$Res> {
  factory _$WorkflowSummaryCopyWith(_WorkflowSummary value, $Res Function(_WorkflowSummary) _then) = __$WorkflowSummaryCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String? description, DateTime updatedAt
});




}
/// @nodoc
class __$WorkflowSummaryCopyWithImpl<$Res>
    implements _$WorkflowSummaryCopyWith<$Res> {
  __$WorkflowSummaryCopyWithImpl(this._self, this._then);

  final _WorkflowSummary _self;
  final $Res Function(_WorkflowSummary) _then;

/// Create a copy of WorkflowSummary
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = freezed,Object? updatedAt = null,}) {
  return _then(_WorkflowSummary(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}

// dart format on
