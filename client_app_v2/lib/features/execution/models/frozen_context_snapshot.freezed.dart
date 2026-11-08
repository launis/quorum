// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'frozen_context_snapshot.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$InjectedTheoryManifestDto {

 Map<String, String> get theories;
/// Create a copy of InjectedTheoryManifestDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$InjectedTheoryManifestDtoCopyWith<InjectedTheoryManifestDto> get copyWith => _$InjectedTheoryManifestDtoCopyWithImpl<InjectedTheoryManifestDto>(this as InjectedTheoryManifestDto, _$identity);

  /// Serializes this InjectedTheoryManifestDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'InjectedTheoryManifestDto(theories: $theories)';
}


}

/// @nodoc
abstract mixin class $InjectedTheoryManifestDtoCopyWith<$Res>  {
  factory $InjectedTheoryManifestDtoCopyWith(InjectedTheoryManifestDto value, $Res Function(InjectedTheoryManifestDto) _then) = _$InjectedTheoryManifestDtoCopyWithImpl;
@useResult
$Res call({
 Map<String, String> theories
});




}
/// @nodoc
class _$InjectedTheoryManifestDtoCopyWithImpl<$Res>
    implements $InjectedTheoryManifestDtoCopyWith<$Res> {
  _$InjectedTheoryManifestDtoCopyWithImpl(this._self, this._then);

  final InjectedTheoryManifestDto _self;
  final $Res Function(InjectedTheoryManifestDto) _then;

/// Create a copy of InjectedTheoryManifestDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? theories = null,}) {
  return _then(_self.copyWith(
theories: null == theories ? _self.theories : theories // ignore: cast_nullable_to_non_nullable
as Map<String, String>,
  ));
}

}


/// Adds pattern-matching-related methods to [InjectedTheoryManifestDto].
extension InjectedTheoryManifestDtoPatterns on InjectedTheoryManifestDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _InjectedTheoryManifestDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _InjectedTheoryManifestDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _InjectedTheoryManifestDto value)  $default,){
final _that = this;
switch (_that) {
case _InjectedTheoryManifestDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _InjectedTheoryManifestDto value)?  $default,){
final _that = this;
switch (_that) {
case _InjectedTheoryManifestDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( Map<String, String> theories)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _InjectedTheoryManifestDto() when $default != null:
return $default(_that.theories);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( Map<String, String> theories)  $default,) {final _that = this;
switch (_that) {
case _InjectedTheoryManifestDto():
return $default(_that.theories);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( Map<String, String> theories)?  $default,) {final _that = this;
switch (_that) {
case _InjectedTheoryManifestDto() when $default != null:
return $default(_that.theories);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _InjectedTheoryManifestDto extends InjectedTheoryManifestDto {
  const _InjectedTheoryManifestDto({final  Map<String, String> theories = const <String, String>{}}): _theories = theories,super._();
  factory _InjectedTheoryManifestDto.fromJson(Map<String, dynamic> json) => _$InjectedTheoryManifestDtoFromJson(json);

 final  Map<String, String> _theories;
@override@JsonKey() Map<String, String> get theories {
  if (_theories is EqualUnmodifiableMapView) return _theories;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_theories);
}


/// Create a copy of InjectedTheoryManifestDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$InjectedTheoryManifestDtoCopyWith<_InjectedTheoryManifestDto> get copyWith => __$InjectedTheoryManifestDtoCopyWithImpl<_InjectedTheoryManifestDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$InjectedTheoryManifestDtoToJson(this, );
}



@override
String toString() {
  return 'InjectedTheoryManifestDto(theories: $theories)';
}


}

/// @nodoc
abstract mixin class _$InjectedTheoryManifestDtoCopyWith<$Res> implements $InjectedTheoryManifestDtoCopyWith<$Res> {
  factory _$InjectedTheoryManifestDtoCopyWith(_InjectedTheoryManifestDto value, $Res Function(_InjectedTheoryManifestDto) _then) = __$InjectedTheoryManifestDtoCopyWithImpl;
@override @useResult
$Res call({
 Map<String, String> theories
});




}
/// @nodoc
class __$InjectedTheoryManifestDtoCopyWithImpl<$Res>
    implements _$InjectedTheoryManifestDtoCopyWith<$Res> {
  __$InjectedTheoryManifestDtoCopyWithImpl(this._self, this._then);

  final _InjectedTheoryManifestDto _self;
  final $Res Function(_InjectedTheoryManifestDto) _then;

/// Create a copy of InjectedTheoryManifestDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? theories = null,}) {
  return _then(_InjectedTheoryManifestDto(
theories: null == theories ? _self._theories : theories // ignore: cast_nullable_to_non_nullable
as Map<String, String>,
  ));
}


}


/// @nodoc
mixin _$SchemaManifestNodeDto {

 String? get type; String? get title; String? get description; Map<String, SchemaManifestNodeDto> get properties; List<String> get required;@JsonKey(name: 'additionalProperties') bool? get additionalProperties; String? get format;
/// Create a copy of SchemaManifestNodeDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SchemaManifestNodeDtoCopyWith<SchemaManifestNodeDto> get copyWith => _$SchemaManifestNodeDtoCopyWithImpl<SchemaManifestNodeDto>(this as SchemaManifestNodeDto, _$identity);

  /// Serializes this SchemaManifestNodeDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'SchemaManifestNodeDto(type: $type, title: $title, description: $description, properties: $properties, required: $required, additionalProperties: $additionalProperties, format: $format)';
}


}

/// @nodoc
abstract mixin class $SchemaManifestNodeDtoCopyWith<$Res>  {
  factory $SchemaManifestNodeDtoCopyWith(SchemaManifestNodeDto value, $Res Function(SchemaManifestNodeDto) _then) = _$SchemaManifestNodeDtoCopyWithImpl;
@useResult
$Res call({
 String? type, String? title, String? description, Map<String, SchemaManifestNodeDto> properties, List<String> required,@JsonKey(name: 'additionalProperties') bool? additionalProperties, String? format
});




}
/// @nodoc
class _$SchemaManifestNodeDtoCopyWithImpl<$Res>
    implements $SchemaManifestNodeDtoCopyWith<$Res> {
  _$SchemaManifestNodeDtoCopyWithImpl(this._self, this._then);

  final SchemaManifestNodeDto _self;
  final $Res Function(SchemaManifestNodeDto) _then;

/// Create a copy of SchemaManifestNodeDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? type = freezed,Object? title = freezed,Object? description = freezed,Object? properties = null,Object? required = null,Object? additionalProperties = freezed,Object? format = freezed,}) {
  return _then(_self.copyWith(
type: freezed == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,properties: null == properties ? _self.properties : properties // ignore: cast_nullable_to_non_nullable
as Map<String, SchemaManifestNodeDto>,required: null == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as List<String>,additionalProperties: freezed == additionalProperties ? _self.additionalProperties : additionalProperties // ignore: cast_nullable_to_non_nullable
as bool?,format: freezed == format ? _self.format : format // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [SchemaManifestNodeDto].
extension SchemaManifestNodeDtoPatterns on SchemaManifestNodeDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SchemaManifestNodeDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SchemaManifestNodeDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SchemaManifestNodeDto value)  $default,){
final _that = this;
switch (_that) {
case _SchemaManifestNodeDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SchemaManifestNodeDto value)?  $default,){
final _that = this;
switch (_that) {
case _SchemaManifestNodeDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? type,  String? title,  String? description,  Map<String, SchemaManifestNodeDto> properties,  List<String> required, @JsonKey(name: 'additionalProperties')  bool? additionalProperties,  String? format)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SchemaManifestNodeDto() when $default != null:
return $default(_that.type,_that.title,_that.description,_that.properties,_that.required,_that.additionalProperties,_that.format);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? type,  String? title,  String? description,  Map<String, SchemaManifestNodeDto> properties,  List<String> required, @JsonKey(name: 'additionalProperties')  bool? additionalProperties,  String? format)  $default,) {final _that = this;
switch (_that) {
case _SchemaManifestNodeDto():
return $default(_that.type,_that.title,_that.description,_that.properties,_that.required,_that.additionalProperties,_that.format);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? type,  String? title,  String? description,  Map<String, SchemaManifestNodeDto> properties,  List<String> required, @JsonKey(name: 'additionalProperties')  bool? additionalProperties,  String? format)?  $default,) {final _that = this;
switch (_that) {
case _SchemaManifestNodeDto() when $default != null:
return $default(_that.type,_that.title,_that.description,_that.properties,_that.required,_that.additionalProperties,_that.format);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _SchemaManifestNodeDto extends SchemaManifestNodeDto {
  const _SchemaManifestNodeDto({this.type, this.title, this.description, final  Map<String, SchemaManifestNodeDto> properties = const <String, SchemaManifestNodeDto>{}, final  List<String> required = const <String>[], @JsonKey(name: 'additionalProperties') this.additionalProperties, this.format}): _properties = properties,_required = required,super._();
  factory _SchemaManifestNodeDto.fromJson(Map<String, dynamic> json) => _$SchemaManifestNodeDtoFromJson(json);

@override final  String? type;
@override final  String? title;
@override final  String? description;
 final  Map<String, SchemaManifestNodeDto> _properties;
@override@JsonKey() Map<String, SchemaManifestNodeDto> get properties {
  if (_properties is EqualUnmodifiableMapView) return _properties;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_properties);
}

 final  List<String> _required;
@override@JsonKey() List<String> get required {
  if (_required is EqualUnmodifiableListView) return _required;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_required);
}

@override@JsonKey(name: 'additionalProperties') final  bool? additionalProperties;
@override final  String? format;

/// Create a copy of SchemaManifestNodeDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SchemaManifestNodeDtoCopyWith<_SchemaManifestNodeDto> get copyWith => __$SchemaManifestNodeDtoCopyWithImpl<_SchemaManifestNodeDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SchemaManifestNodeDtoToJson(this, );
}



@override
String toString() {
  return 'SchemaManifestNodeDto(type: $type, title: $title, description: $description, properties: $properties, required: $required, additionalProperties: $additionalProperties, format: $format)';
}


}

/// @nodoc
abstract mixin class _$SchemaManifestNodeDtoCopyWith<$Res> implements $SchemaManifestNodeDtoCopyWith<$Res> {
  factory _$SchemaManifestNodeDtoCopyWith(_SchemaManifestNodeDto value, $Res Function(_SchemaManifestNodeDto) _then) = __$SchemaManifestNodeDtoCopyWithImpl;
@override @useResult
$Res call({
 String? type, String? title, String? description, Map<String, SchemaManifestNodeDto> properties, List<String> required,@JsonKey(name: 'additionalProperties') bool? additionalProperties, String? format
});




}
/// @nodoc
class __$SchemaManifestNodeDtoCopyWithImpl<$Res>
    implements _$SchemaManifestNodeDtoCopyWith<$Res> {
  __$SchemaManifestNodeDtoCopyWithImpl(this._self, this._then);

  final _SchemaManifestNodeDto _self;
  final $Res Function(_SchemaManifestNodeDto) _then;

/// Create a copy of SchemaManifestNodeDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? type = freezed,Object? title = freezed,Object? description = freezed,Object? properties = null,Object? required = null,Object? additionalProperties = freezed,Object? format = freezed,}) {
  return _then(_SchemaManifestNodeDto(
type: freezed == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,properties: null == properties ? _self._properties : properties // ignore: cast_nullable_to_non_nullable
as Map<String, SchemaManifestNodeDto>,required: null == required ? _self._required : required // ignore: cast_nullable_to_non_nullable
as List<String>,additionalProperties: freezed == additionalProperties ? _self.additionalProperties : additionalProperties // ignore: cast_nullable_to_non_nullable
as bool?,format: freezed == format ? _self.format : format // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$GeneratedSchemaManifestDto {

 Map<String, SchemaManifestNodeDto> get schemas;
/// Create a copy of GeneratedSchemaManifestDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$GeneratedSchemaManifestDtoCopyWith<GeneratedSchemaManifestDto> get copyWith => _$GeneratedSchemaManifestDtoCopyWithImpl<GeneratedSchemaManifestDto>(this as GeneratedSchemaManifestDto, _$identity);

  /// Serializes this GeneratedSchemaManifestDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'GeneratedSchemaManifestDto(schemas: $schemas)';
}


}

/// @nodoc
abstract mixin class $GeneratedSchemaManifestDtoCopyWith<$Res>  {
  factory $GeneratedSchemaManifestDtoCopyWith(GeneratedSchemaManifestDto value, $Res Function(GeneratedSchemaManifestDto) _then) = _$GeneratedSchemaManifestDtoCopyWithImpl;
@useResult
$Res call({
 Map<String, SchemaManifestNodeDto> schemas
});




}
/// @nodoc
class _$GeneratedSchemaManifestDtoCopyWithImpl<$Res>
    implements $GeneratedSchemaManifestDtoCopyWith<$Res> {
  _$GeneratedSchemaManifestDtoCopyWithImpl(this._self, this._then);

  final GeneratedSchemaManifestDto _self;
  final $Res Function(GeneratedSchemaManifestDto) _then;

/// Create a copy of GeneratedSchemaManifestDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? schemas = null,}) {
  return _then(_self.copyWith(
schemas: null == schemas ? _self.schemas : schemas // ignore: cast_nullable_to_non_nullable
as Map<String, SchemaManifestNodeDto>,
  ));
}

}


/// Adds pattern-matching-related methods to [GeneratedSchemaManifestDto].
extension GeneratedSchemaManifestDtoPatterns on GeneratedSchemaManifestDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _GeneratedSchemaManifestDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _GeneratedSchemaManifestDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _GeneratedSchemaManifestDto value)  $default,){
final _that = this;
switch (_that) {
case _GeneratedSchemaManifestDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _GeneratedSchemaManifestDto value)?  $default,){
final _that = this;
switch (_that) {
case _GeneratedSchemaManifestDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( Map<String, SchemaManifestNodeDto> schemas)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _GeneratedSchemaManifestDto() when $default != null:
return $default(_that.schemas);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( Map<String, SchemaManifestNodeDto> schemas)  $default,) {final _that = this;
switch (_that) {
case _GeneratedSchemaManifestDto():
return $default(_that.schemas);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( Map<String, SchemaManifestNodeDto> schemas)?  $default,) {final _that = this;
switch (_that) {
case _GeneratedSchemaManifestDto() when $default != null:
return $default(_that.schemas);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _GeneratedSchemaManifestDto extends GeneratedSchemaManifestDto {
  const _GeneratedSchemaManifestDto({final  Map<String, SchemaManifestNodeDto> schemas = const <String, SchemaManifestNodeDto>{}}): _schemas = schemas,super._();
  factory _GeneratedSchemaManifestDto.fromJson(Map<String, dynamic> json) => _$GeneratedSchemaManifestDtoFromJson(json);

 final  Map<String, SchemaManifestNodeDto> _schemas;
@override@JsonKey() Map<String, SchemaManifestNodeDto> get schemas {
  if (_schemas is EqualUnmodifiableMapView) return _schemas;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_schemas);
}


/// Create a copy of GeneratedSchemaManifestDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$GeneratedSchemaManifestDtoCopyWith<_GeneratedSchemaManifestDto> get copyWith => __$GeneratedSchemaManifestDtoCopyWithImpl<_GeneratedSchemaManifestDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$GeneratedSchemaManifestDtoToJson(this, );
}



@override
String toString() {
  return 'GeneratedSchemaManifestDto(schemas: $schemas)';
}


}

/// @nodoc
abstract mixin class _$GeneratedSchemaManifestDtoCopyWith<$Res> implements $GeneratedSchemaManifestDtoCopyWith<$Res> {
  factory _$GeneratedSchemaManifestDtoCopyWith(_GeneratedSchemaManifestDto value, $Res Function(_GeneratedSchemaManifestDto) _then) = __$GeneratedSchemaManifestDtoCopyWithImpl;
@override @useResult
$Res call({
 Map<String, SchemaManifestNodeDto> schemas
});




}
/// @nodoc
class __$GeneratedSchemaManifestDtoCopyWithImpl<$Res>
    implements _$GeneratedSchemaManifestDtoCopyWith<$Res> {
  __$GeneratedSchemaManifestDtoCopyWithImpl(this._self, this._then);

  final _GeneratedSchemaManifestDto _self;
  final $Res Function(_GeneratedSchemaManifestDto) _then;

/// Create a copy of GeneratedSchemaManifestDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? schemas = null,}) {
  return _then(_GeneratedSchemaManifestDto(
schemas: null == schemas ? _self._schemas : schemas // ignore: cast_nullable_to_non_nullable
as Map<String, SchemaManifestNodeDto>,
  ));
}


}


/// @nodoc
mixin _$SystemConfigOptionDto {

 String get value; String? get label;
/// Create a copy of SystemConfigOptionDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SystemConfigOptionDtoCopyWith<SystemConfigOptionDto> get copyWith => _$SystemConfigOptionDtoCopyWithImpl<SystemConfigOptionDto>(this as SystemConfigOptionDto, _$identity);

  /// Serializes this SystemConfigOptionDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'SystemConfigOptionDto(value: $value, label: $label)';
}


}

/// @nodoc
abstract mixin class $SystemConfigOptionDtoCopyWith<$Res>  {
  factory $SystemConfigOptionDtoCopyWith(SystemConfigOptionDto value, $Res Function(SystemConfigOptionDto) _then) = _$SystemConfigOptionDtoCopyWithImpl;
@useResult
$Res call({
 String value, String? label
});




}
/// @nodoc
class _$SystemConfigOptionDtoCopyWithImpl<$Res>
    implements $SystemConfigOptionDtoCopyWith<$Res> {
  _$SystemConfigOptionDtoCopyWithImpl(this._self, this._then);

  final SystemConfigOptionDto _self;
  final $Res Function(SystemConfigOptionDto) _then;

/// Create a copy of SystemConfigOptionDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? value = null,Object? label = freezed,}) {
  return _then(_self.copyWith(
value: null == value ? _self.value : value // ignore: cast_nullable_to_non_nullable
as String,label: freezed == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [SystemConfigOptionDto].
extension SystemConfigOptionDtoPatterns on SystemConfigOptionDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SystemConfigOptionDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SystemConfigOptionDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SystemConfigOptionDto value)  $default,){
final _that = this;
switch (_that) {
case _SystemConfigOptionDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SystemConfigOptionDto value)?  $default,){
final _that = this;
switch (_that) {
case _SystemConfigOptionDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String value,  String? label)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SystemConfigOptionDto() when $default != null:
return $default(_that.value,_that.label);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String value,  String? label)  $default,) {final _that = this;
switch (_that) {
case _SystemConfigOptionDto():
return $default(_that.value,_that.label);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String value,  String? label)?  $default,) {final _that = this;
switch (_that) {
case _SystemConfigOptionDto() when $default != null:
return $default(_that.value,_that.label);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _SystemConfigOptionDto extends SystemConfigOptionDto {
  const _SystemConfigOptionDto({required this.value, this.label}): super._();
  factory _SystemConfigOptionDto.fromJson(Map<String, dynamic> json) => _$SystemConfigOptionDtoFromJson(json);

@override final  String value;
@override final  String? label;

/// Create a copy of SystemConfigOptionDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SystemConfigOptionDtoCopyWith<_SystemConfigOptionDto> get copyWith => __$SystemConfigOptionDtoCopyWithImpl<_SystemConfigOptionDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SystemConfigOptionDtoToJson(this, );
}



@override
String toString() {
  return 'SystemConfigOptionDto(value: $value, label: $label)';
}


}

/// @nodoc
abstract mixin class _$SystemConfigOptionDtoCopyWith<$Res> implements $SystemConfigOptionDtoCopyWith<$Res> {
  factory _$SystemConfigOptionDtoCopyWith(_SystemConfigOptionDto value, $Res Function(_SystemConfigOptionDto) _then) = __$SystemConfigOptionDtoCopyWithImpl;
@override @useResult
$Res call({
 String value, String? label
});




}
/// @nodoc
class __$SystemConfigOptionDtoCopyWithImpl<$Res>
    implements _$SystemConfigOptionDtoCopyWith<$Res> {
  __$SystemConfigOptionDtoCopyWithImpl(this._self, this._then);

  final _SystemConfigOptionDto _self;
  final $Res Function(_SystemConfigOptionDto) _then;

/// Create a copy of SystemConfigOptionDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? value = null,Object? label = freezed,}) {
  return _then(_SystemConfigOptionDto(
value: null == value ? _self.value : value // ignore: cast_nullable_to_non_nullable
as String,label: freezed == label ? _self.label : label // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$SystemValidationRulesDto {

 double? get min; double? get max; bool? get required; String? get pattern;
/// Create a copy of SystemValidationRulesDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SystemValidationRulesDtoCopyWith<SystemValidationRulesDto> get copyWith => _$SystemValidationRulesDtoCopyWithImpl<SystemValidationRulesDto>(this as SystemValidationRulesDto, _$identity);

  /// Serializes this SystemValidationRulesDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'SystemValidationRulesDto(min: $min, max: $max, required: $required, pattern: $pattern)';
}


}

/// @nodoc
abstract mixin class $SystemValidationRulesDtoCopyWith<$Res>  {
  factory $SystemValidationRulesDtoCopyWith(SystemValidationRulesDto value, $Res Function(SystemValidationRulesDto) _then) = _$SystemValidationRulesDtoCopyWithImpl;
@useResult
$Res call({
 double? min, double? max, bool? required, String? pattern
});




}
/// @nodoc
class _$SystemValidationRulesDtoCopyWithImpl<$Res>
    implements $SystemValidationRulesDtoCopyWith<$Res> {
  _$SystemValidationRulesDtoCopyWithImpl(this._self, this._then);

  final SystemValidationRulesDto _self;
  final $Res Function(SystemValidationRulesDto) _then;

/// Create a copy of SystemValidationRulesDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? min = freezed,Object? max = freezed,Object? required = freezed,Object? pattern = freezed,}) {
  return _then(_self.copyWith(
min: freezed == min ? _self.min : min // ignore: cast_nullable_to_non_nullable
as double?,max: freezed == max ? _self.max : max // ignore: cast_nullable_to_non_nullable
as double?,required: freezed == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool?,pattern: freezed == pattern ? _self.pattern : pattern // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [SystemValidationRulesDto].
extension SystemValidationRulesDtoPatterns on SystemValidationRulesDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SystemValidationRulesDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SystemValidationRulesDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SystemValidationRulesDto value)  $default,){
final _that = this;
switch (_that) {
case _SystemValidationRulesDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SystemValidationRulesDto value)?  $default,){
final _that = this;
switch (_that) {
case _SystemValidationRulesDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( double? min,  double? max,  bool? required,  String? pattern)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SystemValidationRulesDto() when $default != null:
return $default(_that.min,_that.max,_that.required,_that.pattern);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( double? min,  double? max,  bool? required,  String? pattern)  $default,) {final _that = this;
switch (_that) {
case _SystemValidationRulesDto():
return $default(_that.min,_that.max,_that.required,_that.pattern);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( double? min,  double? max,  bool? required,  String? pattern)?  $default,) {final _that = this;
switch (_that) {
case _SystemValidationRulesDto() when $default != null:
return $default(_that.min,_that.max,_that.required,_that.pattern);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _SystemValidationRulesDto extends SystemValidationRulesDto {
  const _SystemValidationRulesDto({this.min, this.max, this.required, this.pattern}): super._();
  factory _SystemValidationRulesDto.fromJson(Map<String, dynamic> json) => _$SystemValidationRulesDtoFromJson(json);

@override final  double? min;
@override final  double? max;
@override final  bool? required;
@override final  String? pattern;

/// Create a copy of SystemValidationRulesDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SystemValidationRulesDtoCopyWith<_SystemValidationRulesDto> get copyWith => __$SystemValidationRulesDtoCopyWithImpl<_SystemValidationRulesDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SystemValidationRulesDtoToJson(this, );
}



@override
String toString() {
  return 'SystemValidationRulesDto(min: $min, max: $max, required: $required, pattern: $pattern)';
}


}

/// @nodoc
abstract mixin class _$SystemValidationRulesDtoCopyWith<$Res> implements $SystemValidationRulesDtoCopyWith<$Res> {
  factory _$SystemValidationRulesDtoCopyWith(_SystemValidationRulesDto value, $Res Function(_SystemValidationRulesDto) _then) = __$SystemValidationRulesDtoCopyWithImpl;
@override @useResult
$Res call({
 double? min, double? max, bool? required, String? pattern
});




}
/// @nodoc
class __$SystemValidationRulesDtoCopyWithImpl<$Res>
    implements _$SystemValidationRulesDtoCopyWith<$Res> {
  __$SystemValidationRulesDtoCopyWithImpl(this._self, this._then);

  final _SystemValidationRulesDto _self;
  final $Res Function(_SystemValidationRulesDto) _then;

/// Create a copy of SystemValidationRulesDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? min = freezed,Object? max = freezed,Object? required = freezed,Object? pattern = freezed,}) {
  return _then(_SystemValidationRulesDto(
min: freezed == min ? _self.min : min // ignore: cast_nullable_to_non_nullable
as double?,max: freezed == max ? _self.max : max // ignore: cast_nullable_to_non_nullable
as double?,required: freezed == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as bool?,pattern: freezed == pattern ? _self.pattern : pattern // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$DataDictionaryField {

@JsonKey(name: 'field_id') String get fieldId;@JsonKey(name: 'component_type') String get componentType; List<SystemConfigOptionDto>? get options;@JsonKey(name: 'validation_rules') SystemValidationRulesDto? get validationRules;
/// Create a copy of DataDictionaryField
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$DataDictionaryFieldCopyWith<DataDictionaryField> get copyWith => _$DataDictionaryFieldCopyWithImpl<DataDictionaryField>(this as DataDictionaryField, _$identity);

  /// Serializes this DataDictionaryField to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'DataDictionaryField(fieldId: $fieldId, componentType: $componentType, options: $options, validationRules: $validationRules)';
}


}

/// @nodoc
abstract mixin class $DataDictionaryFieldCopyWith<$Res>  {
  factory $DataDictionaryFieldCopyWith(DataDictionaryField value, $Res Function(DataDictionaryField) _then) = _$DataDictionaryFieldCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'field_id') String fieldId,@JsonKey(name: 'component_type') String componentType, List<SystemConfigOptionDto>? options,@JsonKey(name: 'validation_rules') SystemValidationRulesDto? validationRules
});


$SystemValidationRulesDtoCopyWith<$Res>? get validationRules;

}
/// @nodoc
class _$DataDictionaryFieldCopyWithImpl<$Res>
    implements $DataDictionaryFieldCopyWith<$Res> {
  _$DataDictionaryFieldCopyWithImpl(this._self, this._then);

  final DataDictionaryField _self;
  final $Res Function(DataDictionaryField) _then;

/// Create a copy of DataDictionaryField
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? fieldId = null,Object? componentType = null,Object? options = freezed,Object? validationRules = freezed,}) {
  return _then(_self.copyWith(
fieldId: null == fieldId ? _self.fieldId : fieldId // ignore: cast_nullable_to_non_nullable
as String,componentType: null == componentType ? _self.componentType : componentType // ignore: cast_nullable_to_non_nullable
as String,options: freezed == options ? _self.options : options // ignore: cast_nullable_to_non_nullable
as List<SystemConfigOptionDto>?,validationRules: freezed == validationRules ? _self.validationRules : validationRules // ignore: cast_nullable_to_non_nullable
as SystemValidationRulesDto?,
  ));
}
/// Create a copy of DataDictionaryField
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SystemValidationRulesDtoCopyWith<$Res>? get validationRules {
    if (_self.validationRules == null) {
    return null;
  }

  return $SystemValidationRulesDtoCopyWith<$Res>(_self.validationRules!, (value) {
    return _then(_self.copyWith(validationRules: value));
  });
}
}


/// Adds pattern-matching-related methods to [DataDictionaryField].
extension DataDictionaryFieldPatterns on DataDictionaryField {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _DataDictionaryField value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _DataDictionaryField() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _DataDictionaryField value)  $default,){
final _that = this;
switch (_that) {
case _DataDictionaryField():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _DataDictionaryField value)?  $default,){
final _that = this;
switch (_that) {
case _DataDictionaryField() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'field_id')  String fieldId, @JsonKey(name: 'component_type')  String componentType,  List<SystemConfigOptionDto>? options, @JsonKey(name: 'validation_rules')  SystemValidationRulesDto? validationRules)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _DataDictionaryField() when $default != null:
return $default(_that.fieldId,_that.componentType,_that.options,_that.validationRules);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'field_id')  String fieldId, @JsonKey(name: 'component_type')  String componentType,  List<SystemConfigOptionDto>? options, @JsonKey(name: 'validation_rules')  SystemValidationRulesDto? validationRules)  $default,) {final _that = this;
switch (_that) {
case _DataDictionaryField():
return $default(_that.fieldId,_that.componentType,_that.options,_that.validationRules);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'field_id')  String fieldId, @JsonKey(name: 'component_type')  String componentType,  List<SystemConfigOptionDto>? options, @JsonKey(name: 'validation_rules')  SystemValidationRulesDto? validationRules)?  $default,) {final _that = this;
switch (_that) {
case _DataDictionaryField() when $default != null:
return $default(_that.fieldId,_that.componentType,_that.options,_that.validationRules);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _DataDictionaryField extends DataDictionaryField {
  const _DataDictionaryField({@JsonKey(name: 'field_id') required this.fieldId, @JsonKey(name: 'component_type') required this.componentType, final  List<SystemConfigOptionDto>? options, @JsonKey(name: 'validation_rules') this.validationRules}): _options = options,super._();
  factory _DataDictionaryField.fromJson(Map<String, dynamic> json) => _$DataDictionaryFieldFromJson(json);

@override@JsonKey(name: 'field_id') final  String fieldId;
@override@JsonKey(name: 'component_type') final  String componentType;
 final  List<SystemConfigOptionDto>? _options;
@override List<SystemConfigOptionDto>? get options {
  final value = _options;
  if (value == null) return null;
  if (_options is EqualUnmodifiableListView) return _options;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override@JsonKey(name: 'validation_rules') final  SystemValidationRulesDto? validationRules;

/// Create a copy of DataDictionaryField
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$DataDictionaryFieldCopyWith<_DataDictionaryField> get copyWith => __$DataDictionaryFieldCopyWithImpl<_DataDictionaryField>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$DataDictionaryFieldToJson(this, );
}



@override
String toString() {
  return 'DataDictionaryField(fieldId: $fieldId, componentType: $componentType, options: $options, validationRules: $validationRules)';
}


}

/// @nodoc
abstract mixin class _$DataDictionaryFieldCopyWith<$Res> implements $DataDictionaryFieldCopyWith<$Res> {
  factory _$DataDictionaryFieldCopyWith(_DataDictionaryField value, $Res Function(_DataDictionaryField) _then) = __$DataDictionaryFieldCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'field_id') String fieldId,@JsonKey(name: 'component_type') String componentType, List<SystemConfigOptionDto>? options,@JsonKey(name: 'validation_rules') SystemValidationRulesDto? validationRules
});


@override $SystemValidationRulesDtoCopyWith<$Res>? get validationRules;

}
/// @nodoc
class __$DataDictionaryFieldCopyWithImpl<$Res>
    implements _$DataDictionaryFieldCopyWith<$Res> {
  __$DataDictionaryFieldCopyWithImpl(this._self, this._then);

  final _DataDictionaryField _self;
  final $Res Function(_DataDictionaryField) _then;

/// Create a copy of DataDictionaryField
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? fieldId = null,Object? componentType = null,Object? options = freezed,Object? validationRules = freezed,}) {
  return _then(_DataDictionaryField(
fieldId: null == fieldId ? _self.fieldId : fieldId // ignore: cast_nullable_to_non_nullable
as String,componentType: null == componentType ? _self.componentType : componentType // ignore: cast_nullable_to_non_nullable
as String,options: freezed == options ? _self._options : options // ignore: cast_nullable_to_non_nullable
as List<SystemConfigOptionDto>?,validationRules: freezed == validationRules ? _self.validationRules : validationRules // ignore: cast_nullable_to_non_nullable
as SystemValidationRulesDto?,
  ));
}

/// Create a copy of DataDictionaryField
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SystemValidationRulesDtoCopyWith<$Res>? get validationRules {
    if (_self.validationRules == null) {
    return null;
  }

  return $SystemValidationRulesDtoCopyWith<$Res>(_self.validationRules!, (value) {
    return _then(_self.copyWith(validationRules: value));
  });
}
}


/// @nodoc
mixin _$FrozenContextSnapshot {

@JsonKey(name: 'version_id') String? get versionId;@JsonKey(name: 'workflow_id') String? get workflowId;@JsonKey(name: 'workflow_name') String? get workflowName;@JsonKey(name: 'organization_id') String? get organizationId;@JsonKey(name: 'user_id') String? get userId;@JsonKey(name: 'created_at') String? get createdAt;@JsonKey(name: 'compiled_prompts') Map<String, String> get compiledPrompts;@JsonKey(name: 'injected_theory') InjectedTheoryManifestDto get injectedTheory;@JsonKey(name: 'generated_schemas') GeneratedSchemaManifestDto get generatedSchemas;@JsonKey(name: 'ui_hints_snapshot') Map<String, DataDictionaryField> get uiHintsSnapshot;@JsonKey(name: 'mcp_tool_audit') List<McpAuditTraceDto> get mcpToolAudit;
/// Create a copy of FrozenContextSnapshot
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$FrozenContextSnapshotCopyWith<FrozenContextSnapshot> get copyWith => _$FrozenContextSnapshotCopyWithImpl<FrozenContextSnapshot>(this as FrozenContextSnapshot, _$identity);

  /// Serializes this FrozenContextSnapshot to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'FrozenContextSnapshot(versionId: $versionId, workflowId: $workflowId, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, createdAt: $createdAt, compiledPrompts: $compiledPrompts, injectedTheory: $injectedTheory, generatedSchemas: $generatedSchemas, uiHintsSnapshot: $uiHintsSnapshot, mcpToolAudit: $mcpToolAudit)';
}


}

/// @nodoc
abstract mixin class $FrozenContextSnapshotCopyWith<$Res>  {
  factory $FrozenContextSnapshotCopyWith(FrozenContextSnapshot value, $Res Function(FrozenContextSnapshot) _then) = _$FrozenContextSnapshotCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'version_id') String? versionId,@JsonKey(name: 'workflow_id') String? workflowId,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'compiled_prompts') Map<String, String> compiledPrompts,@JsonKey(name: 'injected_theory') InjectedTheoryManifestDto injectedTheory,@JsonKey(name: 'generated_schemas') GeneratedSchemaManifestDto generatedSchemas,@JsonKey(name: 'ui_hints_snapshot') Map<String, DataDictionaryField> uiHintsSnapshot,@JsonKey(name: 'mcp_tool_audit') List<McpAuditTraceDto> mcpToolAudit
});


$InjectedTheoryManifestDtoCopyWith<$Res> get injectedTheory;$GeneratedSchemaManifestDtoCopyWith<$Res> get generatedSchemas;

}
/// @nodoc
class _$FrozenContextSnapshotCopyWithImpl<$Res>
    implements $FrozenContextSnapshotCopyWith<$Res> {
  _$FrozenContextSnapshotCopyWithImpl(this._self, this._then);

  final FrozenContextSnapshot _self;
  final $Res Function(FrozenContextSnapshot) _then;

/// Create a copy of FrozenContextSnapshot
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? versionId = freezed,Object? workflowId = freezed,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? createdAt = freezed,Object? compiledPrompts = null,Object? injectedTheory = null,Object? generatedSchemas = null,Object? uiHintsSnapshot = null,Object? mcpToolAudit = null,}) {
  return _then(_self.copyWith(
versionId: freezed == versionId ? _self.versionId : versionId // ignore: cast_nullable_to_non_nullable
as String?,workflowId: freezed == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String?,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,compiledPrompts: null == compiledPrompts ? _self.compiledPrompts : compiledPrompts // ignore: cast_nullable_to_non_nullable
as Map<String, String>,injectedTheory: null == injectedTheory ? _self.injectedTheory : injectedTheory // ignore: cast_nullable_to_non_nullable
as InjectedTheoryManifestDto,generatedSchemas: null == generatedSchemas ? _self.generatedSchemas : generatedSchemas // ignore: cast_nullable_to_non_nullable
as GeneratedSchemaManifestDto,uiHintsSnapshot: null == uiHintsSnapshot ? _self.uiHintsSnapshot : uiHintsSnapshot // ignore: cast_nullable_to_non_nullable
as Map<String, DataDictionaryField>,mcpToolAudit: null == mcpToolAudit ? _self.mcpToolAudit : mcpToolAudit // ignore: cast_nullable_to_non_nullable
as List<McpAuditTraceDto>,
  ));
}
/// Create a copy of FrozenContextSnapshot
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$InjectedTheoryManifestDtoCopyWith<$Res> get injectedTheory {
  
  return $InjectedTheoryManifestDtoCopyWith<$Res>(_self.injectedTheory, (value) {
    return _then(_self.copyWith(injectedTheory: value));
  });
}/// Create a copy of FrozenContextSnapshot
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$GeneratedSchemaManifestDtoCopyWith<$Res> get generatedSchemas {
  
  return $GeneratedSchemaManifestDtoCopyWith<$Res>(_self.generatedSchemas, (value) {
    return _then(_self.copyWith(generatedSchemas: value));
  });
}
}


/// Adds pattern-matching-related methods to [FrozenContextSnapshot].
extension FrozenContextSnapshotPatterns on FrozenContextSnapshot {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _FrozenContextSnapshot value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _FrozenContextSnapshot() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _FrozenContextSnapshot value)  $default,){
final _that = this;
switch (_that) {
case _FrozenContextSnapshot():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _FrozenContextSnapshot value)?  $default,){
final _that = this;
switch (_that) {
case _FrozenContextSnapshot() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'version_id')  String? versionId, @JsonKey(name: 'workflow_id')  String? workflowId, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'compiled_prompts')  Map<String, String> compiledPrompts, @JsonKey(name: 'injected_theory')  InjectedTheoryManifestDto injectedTheory, @JsonKey(name: 'generated_schemas')  GeneratedSchemaManifestDto generatedSchemas, @JsonKey(name: 'ui_hints_snapshot')  Map<String, DataDictionaryField> uiHintsSnapshot, @JsonKey(name: 'mcp_tool_audit')  List<McpAuditTraceDto> mcpToolAudit)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _FrozenContextSnapshot() when $default != null:
return $default(_that.versionId,_that.workflowId,_that.workflowName,_that.organizationId,_that.userId,_that.createdAt,_that.compiledPrompts,_that.injectedTheory,_that.generatedSchemas,_that.uiHintsSnapshot,_that.mcpToolAudit);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'version_id')  String? versionId, @JsonKey(name: 'workflow_id')  String? workflowId, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'compiled_prompts')  Map<String, String> compiledPrompts, @JsonKey(name: 'injected_theory')  InjectedTheoryManifestDto injectedTheory, @JsonKey(name: 'generated_schemas')  GeneratedSchemaManifestDto generatedSchemas, @JsonKey(name: 'ui_hints_snapshot')  Map<String, DataDictionaryField> uiHintsSnapshot, @JsonKey(name: 'mcp_tool_audit')  List<McpAuditTraceDto> mcpToolAudit)  $default,) {final _that = this;
switch (_that) {
case _FrozenContextSnapshot():
return $default(_that.versionId,_that.workflowId,_that.workflowName,_that.organizationId,_that.userId,_that.createdAt,_that.compiledPrompts,_that.injectedTheory,_that.generatedSchemas,_that.uiHintsSnapshot,_that.mcpToolAudit);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'version_id')  String? versionId, @JsonKey(name: 'workflow_id')  String? workflowId, @JsonKey(name: 'workflow_name')  String? workflowName, @JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'compiled_prompts')  Map<String, String> compiledPrompts, @JsonKey(name: 'injected_theory')  InjectedTheoryManifestDto injectedTheory, @JsonKey(name: 'generated_schemas')  GeneratedSchemaManifestDto generatedSchemas, @JsonKey(name: 'ui_hints_snapshot')  Map<String, DataDictionaryField> uiHintsSnapshot, @JsonKey(name: 'mcp_tool_audit')  List<McpAuditTraceDto> mcpToolAudit)?  $default,) {final _that = this;
switch (_that) {
case _FrozenContextSnapshot() when $default != null:
return $default(_that.versionId,_that.workflowId,_that.workflowName,_that.organizationId,_that.userId,_that.createdAt,_that.compiledPrompts,_that.injectedTheory,_that.generatedSchemas,_that.uiHintsSnapshot,_that.mcpToolAudit);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _FrozenContextSnapshot extends FrozenContextSnapshot {
  const _FrozenContextSnapshot({@JsonKey(name: 'version_id') this.versionId, @JsonKey(name: 'workflow_id') this.workflowId, @JsonKey(name: 'workflow_name') this.workflowName, @JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'compiled_prompts') final  Map<String, String> compiledPrompts = const <String, String>{}, @JsonKey(name: 'injected_theory') this.injectedTheory = const InjectedTheoryManifestDto(), @JsonKey(name: 'generated_schemas') this.generatedSchemas = const GeneratedSchemaManifestDto(), @JsonKey(name: 'ui_hints_snapshot') final  Map<String, DataDictionaryField> uiHintsSnapshot = const <String, DataDictionaryField>{}, @JsonKey(name: 'mcp_tool_audit') final  List<McpAuditTraceDto> mcpToolAudit = const <McpAuditTraceDto>[]}): _compiledPrompts = compiledPrompts,_uiHintsSnapshot = uiHintsSnapshot,_mcpToolAudit = mcpToolAudit,super._();
  factory _FrozenContextSnapshot.fromJson(Map<String, dynamic> json) => _$FrozenContextSnapshotFromJson(json);

@override@JsonKey(name: 'version_id') final  String? versionId;
@override@JsonKey(name: 'workflow_id') final  String? workflowId;
@override@JsonKey(name: 'workflow_name') final  String? workflowName;
@override@JsonKey(name: 'organization_id') final  String? organizationId;
@override@JsonKey(name: 'user_id') final  String? userId;
@override@JsonKey(name: 'created_at') final  String? createdAt;
 final  Map<String, String> _compiledPrompts;
@override@JsonKey(name: 'compiled_prompts') Map<String, String> get compiledPrompts {
  if (_compiledPrompts is EqualUnmodifiableMapView) return _compiledPrompts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_compiledPrompts);
}

@override@JsonKey(name: 'injected_theory') final  InjectedTheoryManifestDto injectedTheory;
@override@JsonKey(name: 'generated_schemas') final  GeneratedSchemaManifestDto generatedSchemas;
 final  Map<String, DataDictionaryField> _uiHintsSnapshot;
@override@JsonKey(name: 'ui_hints_snapshot') Map<String, DataDictionaryField> get uiHintsSnapshot {
  if (_uiHintsSnapshot is EqualUnmodifiableMapView) return _uiHintsSnapshot;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_uiHintsSnapshot);
}

 final  List<McpAuditTraceDto> _mcpToolAudit;
@override@JsonKey(name: 'mcp_tool_audit') List<McpAuditTraceDto> get mcpToolAudit {
  if (_mcpToolAudit is EqualUnmodifiableListView) return _mcpToolAudit;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_mcpToolAudit);
}


/// Create a copy of FrozenContextSnapshot
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$FrozenContextSnapshotCopyWith<_FrozenContextSnapshot> get copyWith => __$FrozenContextSnapshotCopyWithImpl<_FrozenContextSnapshot>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$FrozenContextSnapshotToJson(this, );
}



@override
String toString() {
  return 'FrozenContextSnapshot(versionId: $versionId, workflowId: $workflowId, workflowName: $workflowName, organizationId: $organizationId, userId: $userId, createdAt: $createdAt, compiledPrompts: $compiledPrompts, injectedTheory: $injectedTheory, generatedSchemas: $generatedSchemas, uiHintsSnapshot: $uiHintsSnapshot, mcpToolAudit: $mcpToolAudit)';
}


}

/// @nodoc
abstract mixin class _$FrozenContextSnapshotCopyWith<$Res> implements $FrozenContextSnapshotCopyWith<$Res> {
  factory _$FrozenContextSnapshotCopyWith(_FrozenContextSnapshot value, $Res Function(_FrozenContextSnapshot) _then) = __$FrozenContextSnapshotCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'version_id') String? versionId,@JsonKey(name: 'workflow_id') String? workflowId,@JsonKey(name: 'workflow_name') String? workflowName,@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'compiled_prompts') Map<String, String> compiledPrompts,@JsonKey(name: 'injected_theory') InjectedTheoryManifestDto injectedTheory,@JsonKey(name: 'generated_schemas') GeneratedSchemaManifestDto generatedSchemas,@JsonKey(name: 'ui_hints_snapshot') Map<String, DataDictionaryField> uiHintsSnapshot,@JsonKey(name: 'mcp_tool_audit') List<McpAuditTraceDto> mcpToolAudit
});


@override $InjectedTheoryManifestDtoCopyWith<$Res> get injectedTheory;@override $GeneratedSchemaManifestDtoCopyWith<$Res> get generatedSchemas;

}
/// @nodoc
class __$FrozenContextSnapshotCopyWithImpl<$Res>
    implements _$FrozenContextSnapshotCopyWith<$Res> {
  __$FrozenContextSnapshotCopyWithImpl(this._self, this._then);

  final _FrozenContextSnapshot _self;
  final $Res Function(_FrozenContextSnapshot) _then;

/// Create a copy of FrozenContextSnapshot
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? versionId = freezed,Object? workflowId = freezed,Object? workflowName = freezed,Object? organizationId = freezed,Object? userId = freezed,Object? createdAt = freezed,Object? compiledPrompts = null,Object? injectedTheory = null,Object? generatedSchemas = null,Object? uiHintsSnapshot = null,Object? mcpToolAudit = null,}) {
  return _then(_FrozenContextSnapshot(
versionId: freezed == versionId ? _self.versionId : versionId // ignore: cast_nullable_to_non_nullable
as String?,workflowId: freezed == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String?,workflowName: freezed == workflowName ? _self.workflowName : workflowName // ignore: cast_nullable_to_non_nullable
as String?,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,compiledPrompts: null == compiledPrompts ? _self._compiledPrompts : compiledPrompts // ignore: cast_nullable_to_non_nullable
as Map<String, String>,injectedTheory: null == injectedTheory ? _self.injectedTheory : injectedTheory // ignore: cast_nullable_to_non_nullable
as InjectedTheoryManifestDto,generatedSchemas: null == generatedSchemas ? _self.generatedSchemas : generatedSchemas // ignore: cast_nullable_to_non_nullable
as GeneratedSchemaManifestDto,uiHintsSnapshot: null == uiHintsSnapshot ? _self._uiHintsSnapshot : uiHintsSnapshot // ignore: cast_nullable_to_non_nullable
as Map<String, DataDictionaryField>,mcpToolAudit: null == mcpToolAudit ? _self._mcpToolAudit : mcpToolAudit // ignore: cast_nullable_to_non_nullable
as List<McpAuditTraceDto>,
  ));
}

/// Create a copy of FrozenContextSnapshot
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$InjectedTheoryManifestDtoCopyWith<$Res> get injectedTheory {
  
  return $InjectedTheoryManifestDtoCopyWith<$Res>(_self.injectedTheory, (value) {
    return _then(_self.copyWith(injectedTheory: value));
  });
}/// Create a copy of FrozenContextSnapshot
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$GeneratedSchemaManifestDtoCopyWith<$Res> get generatedSchemas {
  
  return $GeneratedSchemaManifestDtoCopyWith<$Res>(_self.generatedSchemas, (value) {
    return _then(_self.copyWith(generatedSchemas: value));
  });
}
}

// dart format on
