// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'workflow.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$Workflow {

 String get id; String get name; String get description; List<String> get steps;@JsonKey(name: 'organization_id') String? get organizationId;@JsonKey(name: 'is_public') bool get isPublic;
/// Create a copy of Workflow
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowCopyWith<Workflow> get copyWith => _$WorkflowCopyWithImpl<Workflow>(this as Workflow, _$identity);

  /// Serializes this Workflow to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is Workflow&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.steps, steps)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.isPublic, isPublic) || other.isPublic == isPublic));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,const DeepCollectionEquality().hash(steps),organizationId,isPublic);

@override
String toString() {
  return 'Workflow(id: $id, name: $name, description: $description, steps: $steps, organizationId: $organizationId, isPublic: $isPublic)';
}


}

/// @nodoc
abstract mixin class $WorkflowCopyWith<$Res>  {
  factory $WorkflowCopyWith(Workflow value, $Res Function(Workflow) _then) = _$WorkflowCopyWithImpl;
@useResult
$Res call({
 String id, String name, String description, List<String> steps,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'is_public') bool isPublic
});




}
/// @nodoc
class _$WorkflowCopyWithImpl<$Res>
    implements $WorkflowCopyWith<$Res> {
  _$WorkflowCopyWithImpl(this._self, this._then);

  final Workflow _self;
  final $Res Function(Workflow) _then;

/// Create a copy of Workflow
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = null,Object? steps = null,Object? organizationId = freezed,Object? isPublic = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,steps: null == steps ? _self.steps : steps // ignore: cast_nullable_to_non_nullable
as List<String>,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,isPublic: null == isPublic ? _self.isPublic : isPublic // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

}


/// Adds pattern-matching-related methods to [Workflow].
extension WorkflowPatterns on Workflow {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _Workflow value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _Workflow() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _Workflow value)  $default,){
final _that = this;
switch (_that) {
case _Workflow():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _Workflow value)?  $default,){
final _that = this;
switch (_that) {
case _Workflow() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String description,  List<String> steps, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'is_public')  bool isPublic)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _Workflow() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.steps,_that.organizationId,_that.isPublic);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String description,  List<String> steps, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'is_public')  bool isPublic)  $default,) {final _that = this;
switch (_that) {
case _Workflow():
return $default(_that.id,_that.name,_that.description,_that.steps,_that.organizationId,_that.isPublic);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String description,  List<String> steps, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'is_public')  bool isPublic)?  $default,) {final _that = this;
switch (_that) {
case _Workflow() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.steps,_that.organizationId,_that.isPublic);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _Workflow implements Workflow {
  const _Workflow({required this.id, required this.name, this.description = '', final  List<String> steps = const [], @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'is_public') this.isPublic = false}): _steps = steps;
  factory _Workflow.fromJson(Map<String, dynamic> json) => _$WorkflowFromJson(json);

@override final  String id;
@override final  String name;
@override@JsonKey() final  String description;
 final  List<String> _steps;
@override@JsonKey() List<String> get steps {
  if (_steps is EqualUnmodifiableListView) return _steps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_steps);
}

@override@JsonKey(name: 'organization_id') final  String? organizationId;
@override@JsonKey(name: 'is_public') final  bool isPublic;

/// Create a copy of Workflow
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WorkflowCopyWith<_Workflow> get copyWith => __$WorkflowCopyWithImpl<_Workflow>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$WorkflowToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _Workflow&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._steps, _steps)&&(identical(other.organizationId, organizationId) || other.organizationId == organizationId)&&(identical(other.isPublic, isPublic) || other.isPublic == isPublic));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,const DeepCollectionEquality().hash(_steps),organizationId,isPublic);

@override
String toString() {
  return 'Workflow(id: $id, name: $name, description: $description, steps: $steps, organizationId: $organizationId, isPublic: $isPublic)';
}


}

/// @nodoc
abstract mixin class _$WorkflowCopyWith<$Res> implements $WorkflowCopyWith<$Res> {
  factory _$WorkflowCopyWith(_Workflow value, $Res Function(_Workflow) _then) = __$WorkflowCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String description, List<String> steps,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'is_public') bool isPublic
});




}
/// @nodoc
class __$WorkflowCopyWithImpl<$Res>
    implements _$WorkflowCopyWith<$Res> {
  __$WorkflowCopyWithImpl(this._self, this._then);

  final _Workflow _self;
  final $Res Function(_Workflow) _then;

/// Create a copy of Workflow
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = null,Object? steps = null,Object? organizationId = freezed,Object? isPublic = null,}) {
  return _then(_Workflow(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,steps: null == steps ? _self._steps : steps // ignore: cast_nullable_to_non_nullable
as List<String>,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,isPublic: null == isPublic ? _self.isPublic : isPublic // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}


}

// dart format on
