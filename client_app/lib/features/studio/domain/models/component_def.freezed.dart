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
mixin _$OntologyDimension {

 String get id;@JsonKey(name: 'label') String get name; String get description;@JsonKey(name: 'is_system') bool get isSystem; Map<String, int> get scale;
/// Create a copy of OntologyDimension
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OntologyDimensionCopyWith<OntologyDimension> get copyWith => _$OntologyDimensionCopyWithImpl<OntologyDimension>(this as OntologyDimension, _$identity);

  /// Serializes this OntologyDimension to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is OntologyDimension&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.isSystem, isSystem) || other.isSystem == isSystem)&&const DeepCollectionEquality().equals(other.scale, scale));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,isSystem,const DeepCollectionEquality().hash(scale));

@override
String toString() {
  return 'OntologyDimension(id: $id, name: $name, description: $description, isSystem: $isSystem, scale: $scale)';
}


}

/// @nodoc
abstract mixin class $OntologyDimensionCopyWith<$Res>  {
  factory $OntologyDimensionCopyWith(OntologyDimension value, $Res Function(OntologyDimension) _then) = _$OntologyDimensionCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'label') String name, String description,@JsonKey(name: 'is_system') bool isSystem, Map<String, int> scale
});




}
/// @nodoc
class _$OntologyDimensionCopyWithImpl<$Res>
    implements $OntologyDimensionCopyWith<$Res> {
  _$OntologyDimensionCopyWithImpl(this._self, this._then);

  final OntologyDimension _self;
  final $Res Function(OntologyDimension) _then;

/// Create a copy of OntologyDimension
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = null,Object? isSystem = null,Object? scale = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,isSystem: null == isSystem ? _self.isSystem : isSystem // ignore: cast_nullable_to_non_nullable
as bool,scale: null == scale ? _self.scale : scale // ignore: cast_nullable_to_non_nullable
as Map<String, int>,
  ));
}

}


/// Adds pattern-matching-related methods to [OntologyDimension].
extension OntologyDimensionPatterns on OntologyDimension {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OntologyDimension value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OntologyDimension() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OntologyDimension value)  $default,){
final _that = this;
switch (_that) {
case _OntologyDimension():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OntologyDimension value)?  $default,){
final _that = this;
switch (_that) {
case _OntologyDimension() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'label')  String name,  String description, @JsonKey(name: 'is_system')  bool isSystem,  Map<String, int> scale)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OntologyDimension() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.isSystem,_that.scale);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'label')  String name,  String description, @JsonKey(name: 'is_system')  bool isSystem,  Map<String, int> scale)  $default,) {final _that = this;
switch (_that) {
case _OntologyDimension():
return $default(_that.id,_that.name,_that.description,_that.isSystem,_that.scale);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'label')  String name,  String description, @JsonKey(name: 'is_system')  bool isSystem,  Map<String, int> scale)?  $default,) {final _that = this;
switch (_that) {
case _OntologyDimension() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.isSystem,_that.scale);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _OntologyDimension implements OntologyDimension {
  const _OntologyDimension({required this.id, @JsonKey(name: 'label') required this.name, required this.description, @JsonKey(name: 'is_system') this.isSystem = false, final  Map<String, int> scale = const {}}): _scale = scale;
  factory _OntologyDimension.fromJson(Map<String, dynamic> json) => _$OntologyDimensionFromJson(json);

@override final  String id;
@override@JsonKey(name: 'label') final  String name;
@override final  String description;
@override@JsonKey(name: 'is_system') final  bool isSystem;
 final  Map<String, int> _scale;
@override@JsonKey() Map<String, int> get scale {
  if (_scale is EqualUnmodifiableMapView) return _scale;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_scale);
}


/// Create a copy of OntologyDimension
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OntologyDimensionCopyWith<_OntologyDimension> get copyWith => __$OntologyDimensionCopyWithImpl<_OntologyDimension>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OntologyDimensionToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _OntologyDimension&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&(identical(other.isSystem, isSystem) || other.isSystem == isSystem)&&const DeepCollectionEquality().equals(other._scale, _scale));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,isSystem,const DeepCollectionEquality().hash(_scale));

@override
String toString() {
  return 'OntologyDimension(id: $id, name: $name, description: $description, isSystem: $isSystem, scale: $scale)';
}


}

/// @nodoc
abstract mixin class _$OntologyDimensionCopyWith<$Res> implements $OntologyDimensionCopyWith<$Res> {
  factory _$OntologyDimensionCopyWith(_OntologyDimension value, $Res Function(_OntologyDimension) _then) = __$OntologyDimensionCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'label') String name, String description,@JsonKey(name: 'is_system') bool isSystem, Map<String, int> scale
});




}
/// @nodoc
class __$OntologyDimensionCopyWithImpl<$Res>
    implements _$OntologyDimensionCopyWith<$Res> {
  __$OntologyDimensionCopyWithImpl(this._self, this._then);

  final _OntologyDimension _self;
  final $Res Function(_OntologyDimension) _then;

/// Create a copy of OntologyDimension
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = null,Object? isSystem = null,Object? scale = null,}) {
  return _then(_OntologyDimension(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,isSystem: null == isSystem ? _self.isSystem : isSystem // ignore: cast_nullable_to_non_nullable
as bool,scale: null == scale ? _self._scale : scale // ignore: cast_nullable_to_non_nullable
as Map<String, int>,
  ));
}


}


/// @nodoc
mixin _$MatrixCriterion {

@JsonKey(name: 'id') String get dimensionId; String get label;@JsonKey(name: 'instruction') String get prompt; Map<String, String> get anchors; double get weight;
/// Create a copy of MatrixCriterion
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MatrixCriterionCopyWith<MatrixCriterion> get copyWith => _$MatrixCriterionCopyWithImpl<MatrixCriterion>(this as MatrixCriterion, _$identity);

  /// Serializes this MatrixCriterion to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MatrixCriterion&&(identical(other.dimensionId, dimensionId) || other.dimensionId == dimensionId)&&(identical(other.label, label) || other.label == label)&&(identical(other.prompt, prompt) || other.prompt == prompt)&&const DeepCollectionEquality().equals(other.anchors, anchors)&&(identical(other.weight, weight) || other.weight == weight));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,dimensionId,label,prompt,const DeepCollectionEquality().hash(anchors),weight);

@override
String toString() {
  return 'MatrixCriterion(dimensionId: $dimensionId, label: $label, prompt: $prompt, anchors: $anchors, weight: $weight)';
}


}

/// @nodoc
abstract mixin class $MatrixCriterionCopyWith<$Res>  {
  factory $MatrixCriterionCopyWith(MatrixCriterion value, $Res Function(MatrixCriterion) _then) = _$MatrixCriterionCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'id') String dimensionId, String label,@JsonKey(name: 'instruction') String prompt, Map<String, String> anchors, double weight
});




}
/// @nodoc
class _$MatrixCriterionCopyWithImpl<$Res>
    implements $MatrixCriterionCopyWith<$Res> {
  _$MatrixCriterionCopyWithImpl(this._self, this._then);

  final MatrixCriterion _self;
  final $Res Function(MatrixCriterion) _then;

/// Create a copy of MatrixCriterion
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? dimensionId = null,Object? label = null,Object? prompt = null,Object? anchors = null,Object? weight = null,}) {
  return _then(_self.copyWith(
dimensionId: null == dimensionId ? _self.dimensionId : dimensionId // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,prompt: null == prompt ? _self.prompt : prompt // ignore: cast_nullable_to_non_nullable
as String,anchors: null == anchors ? _self.anchors : anchors // ignore: cast_nullable_to_non_nullable
as Map<String, String>,weight: null == weight ? _self.weight : weight // ignore: cast_nullable_to_non_nullable
as double,
  ));
}

}


/// Adds pattern-matching-related methods to [MatrixCriterion].
extension MatrixCriterionPatterns on MatrixCriterion {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MatrixCriterion value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MatrixCriterion() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MatrixCriterion value)  $default,){
final _that = this;
switch (_that) {
case _MatrixCriterion():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MatrixCriterion value)?  $default,){
final _that = this;
switch (_that) {
case _MatrixCriterion() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'id')  String dimensionId,  String label, @JsonKey(name: 'instruction')  String prompt,  Map<String, String> anchors,  double weight)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MatrixCriterion() when $default != null:
return $default(_that.dimensionId,_that.label,_that.prompt,_that.anchors,_that.weight);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'id')  String dimensionId,  String label, @JsonKey(name: 'instruction')  String prompt,  Map<String, String> anchors,  double weight)  $default,) {final _that = this;
switch (_that) {
case _MatrixCriterion():
return $default(_that.dimensionId,_that.label,_that.prompt,_that.anchors,_that.weight);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'id')  String dimensionId,  String label, @JsonKey(name: 'instruction')  String prompt,  Map<String, String> anchors,  double weight)?  $default,) {final _that = this;
switch (_that) {
case _MatrixCriterion() when $default != null:
return $default(_that.dimensionId,_that.label,_that.prompt,_that.anchors,_that.weight);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MatrixCriterion implements MatrixCriterion {
  const _MatrixCriterion({@JsonKey(name: 'id') required this.dimensionId, this.label = '', @JsonKey(name: 'instruction') this.prompt = '', final  Map<String, String> anchors = const {}, this.weight = 1.0}): _anchors = anchors;
  factory _MatrixCriterion.fromJson(Map<String, dynamic> json) => _$MatrixCriterionFromJson(json);

@override@JsonKey(name: 'id') final  String dimensionId;
@override@JsonKey() final  String label;
@override@JsonKey(name: 'instruction') final  String prompt;
 final  Map<String, String> _anchors;
@override@JsonKey() Map<String, String> get anchors {
  if (_anchors is EqualUnmodifiableMapView) return _anchors;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_anchors);
}

@override@JsonKey() final  double weight;

/// Create a copy of MatrixCriterion
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MatrixCriterionCopyWith<_MatrixCriterion> get copyWith => __$MatrixCriterionCopyWithImpl<_MatrixCriterion>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MatrixCriterionToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _MatrixCriterion&&(identical(other.dimensionId, dimensionId) || other.dimensionId == dimensionId)&&(identical(other.label, label) || other.label == label)&&(identical(other.prompt, prompt) || other.prompt == prompt)&&const DeepCollectionEquality().equals(other._anchors, _anchors)&&(identical(other.weight, weight) || other.weight == weight));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,dimensionId,label,prompt,const DeepCollectionEquality().hash(_anchors),weight);

@override
String toString() {
  return 'MatrixCriterion(dimensionId: $dimensionId, label: $label, prompt: $prompt, anchors: $anchors, weight: $weight)';
}


}

/// @nodoc
abstract mixin class _$MatrixCriterionCopyWith<$Res> implements $MatrixCriterionCopyWith<$Res> {
  factory _$MatrixCriterionCopyWith(_MatrixCriterion value, $Res Function(_MatrixCriterion) _then) = __$MatrixCriterionCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'id') String dimensionId, String label,@JsonKey(name: 'instruction') String prompt, Map<String, String> anchors, double weight
});




}
/// @nodoc
class __$MatrixCriterionCopyWithImpl<$Res>
    implements _$MatrixCriterionCopyWith<$Res> {
  __$MatrixCriterionCopyWithImpl(this._self, this._then);

  final _MatrixCriterion _self;
  final $Res Function(_MatrixCriterion) _then;

/// Create a copy of MatrixCriterion
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? dimensionId = null,Object? label = null,Object? prompt = null,Object? anchors = null,Object? weight = null,}) {
  return _then(_MatrixCriterion(
dimensionId: null == dimensionId ? _self.dimensionId : dimensionId // ignore: cast_nullable_to_non_nullable
as String,label: null == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String,prompt: null == prompt ? _self.prompt : prompt // ignore: cast_nullable_to_non_nullable
as String,anchors: null == anchors ? _self._anchors : anchors // ignore: cast_nullable_to_non_nullable
as Map<String, String>,weight: null == weight ? _self.weight : weight // ignore: cast_nullable_to_non_nullable
as double,
  ));
}


}


/// @nodoc
mixin _$MatrixDef {

 String get id; String get name; String get description; Map<String, int> get scale;@JsonKey(name: 'role_description') String? get roleDescription; List<MatrixCriterion> get criteria;
/// Create a copy of MatrixDef
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MatrixDefCopyWith<MatrixDef> get copyWith => _$MatrixDefCopyWithImpl<MatrixDef>(this as MatrixDef, _$identity);

  /// Serializes this MatrixDef to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is MatrixDef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.scale, scale)&&(identical(other.roleDescription, roleDescription) || other.roleDescription == roleDescription)&&const DeepCollectionEquality().equals(other.criteria, criteria));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,const DeepCollectionEquality().hash(scale),roleDescription,const DeepCollectionEquality().hash(criteria));

@override
String toString() {
  return 'MatrixDef(id: $id, name: $name, description: $description, scale: $scale, roleDescription: $roleDescription, criteria: $criteria)';
}


}

/// @nodoc
abstract mixin class $MatrixDefCopyWith<$Res>  {
  factory $MatrixDefCopyWith(MatrixDef value, $Res Function(MatrixDef) _then) = _$MatrixDefCopyWithImpl;
@useResult
$Res call({
 String id, String name, String description, Map<String, int> scale,@JsonKey(name: 'role_description') String? roleDescription, List<MatrixCriterion> criteria
});




}
/// @nodoc
class _$MatrixDefCopyWithImpl<$Res>
    implements $MatrixDefCopyWith<$Res> {
  _$MatrixDefCopyWithImpl(this._self, this._then);

  final MatrixDef _self;
  final $Res Function(MatrixDef) _then;

/// Create a copy of MatrixDef
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? name = null,Object? description = null,Object? scale = null,Object? roleDescription = freezed,Object? criteria = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,scale: null == scale ? _self.scale : scale // ignore: cast_nullable_to_non_nullable
as Map<String, int>,roleDescription: freezed == roleDescription ? _self.roleDescription : roleDescription // ignore: cast_nullable_to_non_nullable
as String?,criteria: null == criteria ? _self.criteria : criteria // ignore: cast_nullable_to_non_nullable
as List<MatrixCriterion>,
  ));
}

}


/// Adds pattern-matching-related methods to [MatrixDef].
extension MatrixDefPatterns on MatrixDef {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MatrixDef value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MatrixDef() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MatrixDef value)  $default,){
final _that = this;
switch (_that) {
case _MatrixDef():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MatrixDef value)?  $default,){
final _that = this;
switch (_that) {
case _MatrixDef() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String name,  String description,  Map<String, int> scale, @JsonKey(name: 'role_description')  String? roleDescription,  List<MatrixCriterion> criteria)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MatrixDef() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.scale,_that.roleDescription,_that.criteria);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String name,  String description,  Map<String, int> scale, @JsonKey(name: 'role_description')  String? roleDescription,  List<MatrixCriterion> criteria)  $default,) {final _that = this;
switch (_that) {
case _MatrixDef():
return $default(_that.id,_that.name,_that.description,_that.scale,_that.roleDescription,_that.criteria);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String name,  String description,  Map<String, int> scale, @JsonKey(name: 'role_description')  String? roleDescription,  List<MatrixCriterion> criteria)?  $default,) {final _that = this;
switch (_that) {
case _MatrixDef() when $default != null:
return $default(_that.id,_that.name,_that.description,_that.scale,_that.roleDescription,_that.criteria);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _MatrixDef implements MatrixDef {
  const _MatrixDef({required this.id, required this.name, required this.description, required final  Map<String, int> scale, @JsonKey(name: 'role_description') this.roleDescription, final  List<MatrixCriterion> criteria = const []}): _scale = scale,_criteria = criteria;
  factory _MatrixDef.fromJson(Map<String, dynamic> json) => _$MatrixDefFromJson(json);

@override final  String id;
@override final  String name;
@override final  String description;
 final  Map<String, int> _scale;
@override Map<String, int> get scale {
  if (_scale is EqualUnmodifiableMapView) return _scale;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_scale);
}

@override@JsonKey(name: 'role_description') final  String? roleDescription;
 final  List<MatrixCriterion> _criteria;
@override@JsonKey() List<MatrixCriterion> get criteria {
  if (_criteria is EqualUnmodifiableListView) return _criteria;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_criteria);
}


/// Create a copy of MatrixDef
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MatrixDefCopyWith<_MatrixDef> get copyWith => __$MatrixDefCopyWithImpl<_MatrixDef>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MatrixDefToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _MatrixDef&&(identical(other.id, id) || other.id == id)&&(identical(other.name, name) || other.name == name)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._scale, _scale)&&(identical(other.roleDescription, roleDescription) || other.roleDescription == roleDescription)&&const DeepCollectionEquality().equals(other._criteria, _criteria));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,name,description,const DeepCollectionEquality().hash(_scale),roleDescription,const DeepCollectionEquality().hash(_criteria));

@override
String toString() {
  return 'MatrixDef(id: $id, name: $name, description: $description, scale: $scale, roleDescription: $roleDescription, criteria: $criteria)';
}


}

/// @nodoc
abstract mixin class _$MatrixDefCopyWith<$Res> implements $MatrixDefCopyWith<$Res> {
  factory _$MatrixDefCopyWith(_MatrixDef value, $Res Function(_MatrixDef) _then) = __$MatrixDefCopyWithImpl;
@override @useResult
$Res call({
 String id, String name, String description, Map<String, int> scale,@JsonKey(name: 'role_description') String? roleDescription, List<MatrixCriterion> criteria
});




}
/// @nodoc
class __$MatrixDefCopyWithImpl<$Res>
    implements _$MatrixDefCopyWith<$Res> {
  __$MatrixDefCopyWithImpl(this._self, this._then);

  final _MatrixDef _self;
  final $Res Function(_MatrixDef) _then;

/// Create a copy of MatrixDef
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? name = null,Object? description = null,Object? scale = null,Object? roleDescription = freezed,Object? criteria = null,}) {
  return _then(_MatrixDef(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,scale: null == scale ? _self._scale : scale // ignore: cast_nullable_to_non_nullable
as Map<String, int>,roleDescription: freezed == roleDescription ? _self.roleDescription : roleDescription // ignore: cast_nullable_to_non_nullable
as String?,criteria: null == criteria ? _self._criteria : criteria // ignore: cast_nullable_to_non_nullable
as List<MatrixCriterion>,
  ));
}


}


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
