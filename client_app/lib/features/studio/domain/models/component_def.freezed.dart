// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'component_def.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$StudioComponentDef {

 String get id; String get name; String get type; String? get description; Map<String, dynamic> get content;
/// Create a copy of StudioComponentDef
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StudioComponentDefCopyWith<StudioComponentDef> get copyWith => _$StudioComponentDefCopyWithImpl<StudioComponentDef>(this as StudioComponentDef, _$identity);

  /// Serializes this StudioComponentDef to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is StudioComponentDef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.content, content));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,type,description,const DeepCollectionEquality().hash(content));

@override
String toString() {
  return 'StudioComponentDef(id: $id, name: $name, type: $type, description: $description, content: $content)';
}


}

/// @nodoc
abstract mixin class $StudioComponentDefCopyWith<$Res>  {
  factory $StudioComponentDefCopyWith(StudioComponentDef value, $Res Function(StudioComponentDef) _then) = _$StudioComponentDefCopyWithImpl;
@useResult
$Res call({
 String id, String name, String type, String? description, Map<String, dynamic> content
});




}
/// @nodoc
class _$StudioComponentDefCopyWithImpl<$Res>
    implements $StudioComponentDefCopyWith<$Res> {
  _$StudioComponentDefCopyWithImpl(this._self, this._then);

  final StudioComponentDef _self;
  final $Res Function(StudioComponentDef) _then;

/// Create a copy of StudioComponentDef
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? type = null,Object? description = freezed,Object? content = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,content: null == content ? _self.content : content // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [StudioComponentDef].
extension StudioComponentDefPatterns on StudioComponentDef {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StudioComponentDef value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StudioComponentDef() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StudioComponentDef value)  $default,){
final _that = this;
switch (_that) {
case _StudioComponentDef():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StudioComponentDef value)?  $default,){
final _that = this;
switch (_that) {
case _StudioComponentDef() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String type,  String? description,  Map<String, dynamic> content)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StudioComponentDef() when $default != null:
return $default(_that.id,_that.name,_that.type,_that.description,_that.content);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String type,  String? description,  Map<String, dynamic> content)  $default,) {final _that = this;
switch (_that) {
case _StudioComponentDef():
return $default(_that.id,_that.name,_that.type,_that.description,_that.content);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String type,  String? description,  Map<String, dynamic> content)?  $default,) {final _that = this;
switch (_that) {
case _StudioComponentDef() when $default != null:
return $default(_that.id,_that.name,_that.type,_that.description,_that.content);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _StudioComponentDef extends StudioComponentDef {
  const _StudioComponentDef({required this.id, required this.name, required this.type, this.description, required final  Map<String, dynamic> content}): _content = content,super._();
  factory _StudioComponentDef.fromJson(Map<String, dynamic> json) => _$StudioComponentDefFromJson(json);

@override final  String id;
@override final  String name;
@override final  String type;
@override final  String? description;
 final  Map<String, dynamic> _content;
@override Map<String, dynamic> get content {
  if (_content is EqualUnmodifiableMapView) return _content;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_content);
}


/// Create a copy of StudioComponentDef
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StudioComponentDefCopyWith<_StudioComponentDef> get copyWith => __$StudioComponentDefCopyWithImpl<_StudioComponentDef>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StudioComponentDefToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _StudioComponentDef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.type, type) || other.type == type)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._content, _content));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,type,description,const DeepCollectionEquality().hash(_content));

@override
String toString() {
  return 'StudioComponentDef(id: $id, name: $name, type: $type, description: $description, content: $content)';
}


}

/// @nodoc
abstract mixin class _$StudioComponentDefCopyWith<$Res> implements $StudioComponentDefCopyWith<$Res> {
  factory _$StudioComponentDefCopyWith(_StudioComponentDef value, $Res Function(_StudioComponentDef) _then) = __$StudioComponentDefCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String type, String? description, Map<String, dynamic> content
});




}
/// @nodoc
class __$StudioComponentDefCopyWithImpl<$Res>
    implements _$StudioComponentDefCopyWith<$Res> {
  __$StudioComponentDefCopyWithImpl(this._self, this._then);

  final _StudioComponentDef _self;
  final $Res Function(_StudioComponentDef) _then;

/// Create a copy of StudioComponentDef
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? type = null,Object? description = freezed,Object? content = null,}) {
  return _then(_StudioComponentDef(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,content: null == content ? _self._content : content // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
