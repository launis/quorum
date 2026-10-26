// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'mcp_gateway.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$McpToolSchemaPropertyDto {

 JsonSchemaPropertyType? get type; String? get title; String get description;@JsonKey(name: 'enum_values') List<String>? get enumValues; McpToolSchemaPropertyDto? get items; Map<String, McpToolSchemaPropertyDto>? get properties;@JsonKey(name: 'required') List<String>? get requiredFields;@JsonKey(name: 'additional_properties') bool? get additionalProperties;@JsonKey(name: 'default') Object? get defaultValue; num? get minimum; num? get maximum;@JsonKey(name: 'min_length') int? get minLength;@JsonKey(name: 'max_length') int? get maxLength;@JsonKey(name: 'any_of') List<McpToolSchemaPropertyDto>? get anyOf;
/// Create a copy of McpToolSchemaPropertyDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$McpToolSchemaPropertyDtoCopyWith<McpToolSchemaPropertyDto> get copyWith => _$McpToolSchemaPropertyDtoCopyWithImpl<McpToolSchemaPropertyDto>(this as McpToolSchemaPropertyDto, _$identity);

  /// Serializes this McpToolSchemaPropertyDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'McpToolSchemaPropertyDto(type: $type, title: $title, description: $description, enumValues: $enumValues, items: $items, properties: $properties, requiredFields: $requiredFields, additionalProperties: $additionalProperties, defaultValue: $defaultValue, minimum: $minimum, maximum: $maximum, minLength: $minLength, maxLength: $maxLength, anyOf: $anyOf)';
}


}

/// @nodoc
abstract mixin class $McpToolSchemaPropertyDtoCopyWith<$Res>  {
  factory $McpToolSchemaPropertyDtoCopyWith(McpToolSchemaPropertyDto value, $Res Function(McpToolSchemaPropertyDto) _then) = _$McpToolSchemaPropertyDtoCopyWithImpl;
@useResult
$Res call({
 JsonSchemaPropertyType? type, String? title, String description,@JsonKey(name: 'enum_values') List<String>? enumValues, McpToolSchemaPropertyDto? items, Map<String, McpToolSchemaPropertyDto>? properties,@JsonKey(name: 'required') List<String>? requiredFields,@JsonKey(name: 'additional_properties') bool? additionalProperties,@JsonKey(name: 'default') Object? defaultValue, num? minimum, num? maximum,@JsonKey(name: 'min_length') int? minLength,@JsonKey(name: 'max_length') int? maxLength,@JsonKey(name: 'any_of') List<McpToolSchemaPropertyDto>? anyOf
});


$McpToolSchemaPropertyDtoCopyWith<$Res>? get items;

}
/// @nodoc
class _$McpToolSchemaPropertyDtoCopyWithImpl<$Res>
    implements $McpToolSchemaPropertyDtoCopyWith<$Res> {
  _$McpToolSchemaPropertyDtoCopyWithImpl(this._self, this._then);

  final McpToolSchemaPropertyDto _self;
  final $Res Function(McpToolSchemaPropertyDto) _then;

/// Create a copy of McpToolSchemaPropertyDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? type = freezed,Object? title = freezed,Object? description = null,Object? enumValues = freezed,Object? items = freezed,Object? properties = freezed,Object? requiredFields = freezed,Object? additionalProperties = freezed,Object? defaultValue = freezed,Object? minimum = freezed,Object? maximum = freezed,Object? minLength = freezed,Object? maxLength = freezed,Object? anyOf = freezed,}) {
  return _then(_self.copyWith(
type: freezed == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as JsonSchemaPropertyType?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String?,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,enumValues: freezed == enumValues ? _self.enumValues : enumValues // ignore: cast_nullable_to_non_nullable
as List<String>?,items: freezed == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as McpToolSchemaPropertyDto?,properties: freezed == properties ? _self.properties : properties // ignore: cast_nullable_to_non_nullable
as Map<String, McpToolSchemaPropertyDto>?,requiredFields: freezed == requiredFields ? _self.requiredFields : requiredFields // ignore: cast_nullable_to_non_nullable
as List<String>?,additionalProperties: freezed == additionalProperties ? _self.additionalProperties : additionalProperties // ignore: cast_nullable_to_non_nullable
as bool?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue ,minimum: freezed == minimum ? _self.minimum : minimum // ignore: cast_nullable_to_non_nullable
as num?,maximum: freezed == maximum ? _self.maximum : maximum // ignore: cast_nullable_to_non_nullable
as num?,minLength: freezed == minLength ? _self.minLength : minLength // ignore: cast_nullable_to_non_nullable
as int?,maxLength: freezed == maxLength ? _self.maxLength : maxLength // ignore: cast_nullable_to_non_nullable
as int?,anyOf: freezed == anyOf ? _self.anyOf : anyOf // ignore: cast_nullable_to_non_nullable
as List<McpToolSchemaPropertyDto>?,
  ));
}
/// Create a copy of McpToolSchemaPropertyDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$McpToolSchemaPropertyDtoCopyWith<$Res>? get items {
    if (_self.items == null) {
    return null;
  }

  return $McpToolSchemaPropertyDtoCopyWith<$Res>(_self.items!, (value) {
    return _then(_self.copyWith(items: value));
  });
}
}


/// Adds pattern-matching-related methods to [McpToolSchemaPropertyDto].
extension McpToolSchemaPropertyDtoPatterns on McpToolSchemaPropertyDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _McpToolSchemaPropertyDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _McpToolSchemaPropertyDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _McpToolSchemaPropertyDto value)  $default,){
final _that = this;
switch (_that) {
case _McpToolSchemaPropertyDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _McpToolSchemaPropertyDto value)?  $default,){
final _that = this;
switch (_that) {
case _McpToolSchemaPropertyDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( JsonSchemaPropertyType? type,  String? title,  String description, @JsonKey(name: 'enum_values')  List<String>? enumValues,  McpToolSchemaPropertyDto? items,  Map<String, McpToolSchemaPropertyDto>? properties, @JsonKey(name: 'required')  List<String>? requiredFields, @JsonKey(name: 'additional_properties')  bool? additionalProperties, @JsonKey(name: 'default')  Object? defaultValue,  num? minimum,  num? maximum, @JsonKey(name: 'min_length')  int? minLength, @JsonKey(name: 'max_length')  int? maxLength, @JsonKey(name: 'any_of')  List<McpToolSchemaPropertyDto>? anyOf)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _McpToolSchemaPropertyDto() when $default != null:
return $default(_that.type,_that.title,_that.description,_that.enumValues,_that.items,_that.properties,_that.requiredFields,_that.additionalProperties,_that.defaultValue,_that.minimum,_that.maximum,_that.minLength,_that.maxLength,_that.anyOf);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( JsonSchemaPropertyType? type,  String? title,  String description, @JsonKey(name: 'enum_values')  List<String>? enumValues,  McpToolSchemaPropertyDto? items,  Map<String, McpToolSchemaPropertyDto>? properties, @JsonKey(name: 'required')  List<String>? requiredFields, @JsonKey(name: 'additional_properties')  bool? additionalProperties, @JsonKey(name: 'default')  Object? defaultValue,  num? minimum,  num? maximum, @JsonKey(name: 'min_length')  int? minLength, @JsonKey(name: 'max_length')  int? maxLength, @JsonKey(name: 'any_of')  List<McpToolSchemaPropertyDto>? anyOf)  $default,) {final _that = this;
switch (_that) {
case _McpToolSchemaPropertyDto():
return $default(_that.type,_that.title,_that.description,_that.enumValues,_that.items,_that.properties,_that.requiredFields,_that.additionalProperties,_that.defaultValue,_that.minimum,_that.maximum,_that.minLength,_that.maxLength,_that.anyOf);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( JsonSchemaPropertyType? type,  String? title,  String description, @JsonKey(name: 'enum_values')  List<String>? enumValues,  McpToolSchemaPropertyDto? items,  Map<String, McpToolSchemaPropertyDto>? properties, @JsonKey(name: 'required')  List<String>? requiredFields, @JsonKey(name: 'additional_properties')  bool? additionalProperties, @JsonKey(name: 'default')  Object? defaultValue,  num? minimum,  num? maximum, @JsonKey(name: 'min_length')  int? minLength, @JsonKey(name: 'max_length')  int? maxLength, @JsonKey(name: 'any_of')  List<McpToolSchemaPropertyDto>? anyOf)?  $default,) {final _that = this;
switch (_that) {
case _McpToolSchemaPropertyDto() when $default != null:
return $default(_that.type,_that.title,_that.description,_that.enumValues,_that.items,_that.properties,_that.requiredFields,_that.additionalProperties,_that.defaultValue,_that.minimum,_that.maximum,_that.minLength,_that.maxLength,_that.anyOf);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _McpToolSchemaPropertyDto implements McpToolSchemaPropertyDto {
  const _McpToolSchemaPropertyDto({this.type, this.title, this.description = '', @JsonKey(name: 'enum_values') final  List<String>? enumValues, this.items, final  Map<String, McpToolSchemaPropertyDto>? properties, @JsonKey(name: 'required') final  List<String>? requiredFields, @JsonKey(name: 'additional_properties') this.additionalProperties, @JsonKey(name: 'default') this.defaultValue, this.minimum, this.maximum, @JsonKey(name: 'min_length') this.minLength, @JsonKey(name: 'max_length') this.maxLength, @JsonKey(name: 'any_of') final  List<McpToolSchemaPropertyDto>? anyOf}): _enumValues = enumValues,_properties = properties,_requiredFields = requiredFields,_anyOf = anyOf;
  factory _McpToolSchemaPropertyDto.fromJson(Map<String, dynamic> json) => _$McpToolSchemaPropertyDtoFromJson(json);

@override final  JsonSchemaPropertyType? type;
@override final  String? title;
@override@JsonKey() final  String description;
 final  List<String>? _enumValues;
@override@JsonKey(name: 'enum_values') List<String>? get enumValues {
  final value = _enumValues;
  if (value == null) return null;
  if (_enumValues is EqualUnmodifiableListView) return _enumValues;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override final  McpToolSchemaPropertyDto? items;
 final  Map<String, McpToolSchemaPropertyDto>? _properties;
@override Map<String, McpToolSchemaPropertyDto>? get properties {
  final value = _properties;
  if (value == null) return null;
  if (_properties is EqualUnmodifiableMapView) return _properties;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

 final  List<String>? _requiredFields;
@override@JsonKey(name: 'required') List<String>? get requiredFields {
  final value = _requiredFields;
  if (value == null) return null;
  if (_requiredFields is EqualUnmodifiableListView) return _requiredFields;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override@JsonKey(name: 'additional_properties') final  bool? additionalProperties;
@override@JsonKey(name: 'default') final  Object? defaultValue;
@override final  num? minimum;
@override final  num? maximum;
@override@JsonKey(name: 'min_length') final  int? minLength;
@override@JsonKey(name: 'max_length') final  int? maxLength;
 final  List<McpToolSchemaPropertyDto>? _anyOf;
@override@JsonKey(name: 'any_of') List<McpToolSchemaPropertyDto>? get anyOf {
  final value = _anyOf;
  if (value == null) return null;
  if (_anyOf is EqualUnmodifiableListView) return _anyOf;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}


/// Create a copy of McpToolSchemaPropertyDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$McpToolSchemaPropertyDtoCopyWith<_McpToolSchemaPropertyDto> get copyWith => __$McpToolSchemaPropertyDtoCopyWithImpl<_McpToolSchemaPropertyDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$McpToolSchemaPropertyDtoToJson(this, );
}



@override
String toString() {
  return 'McpToolSchemaPropertyDto(type: $type, title: $title, description: $description, enumValues: $enumValues, items: $items, properties: $properties, requiredFields: $requiredFields, additionalProperties: $additionalProperties, defaultValue: $defaultValue, minimum: $minimum, maximum: $maximum, minLength: $minLength, maxLength: $maxLength, anyOf: $anyOf)';
}


}

/// @nodoc
abstract mixin class _$McpToolSchemaPropertyDtoCopyWith<$Res> implements $McpToolSchemaPropertyDtoCopyWith<$Res> {
  factory _$McpToolSchemaPropertyDtoCopyWith(_McpToolSchemaPropertyDto value, $Res Function(_McpToolSchemaPropertyDto) _then) = __$McpToolSchemaPropertyDtoCopyWithImpl;
@override @useResult
$Res call({
 JsonSchemaPropertyType? type, String? title, String description,@JsonKey(name: 'enum_values') List<String>? enumValues, McpToolSchemaPropertyDto? items, Map<String, McpToolSchemaPropertyDto>? properties,@JsonKey(name: 'required') List<String>? requiredFields,@JsonKey(name: 'additional_properties') bool? additionalProperties,@JsonKey(name: 'default') Object? defaultValue, num? minimum, num? maximum,@JsonKey(name: 'min_length') int? minLength,@JsonKey(name: 'max_length') int? maxLength,@JsonKey(name: 'any_of') List<McpToolSchemaPropertyDto>? anyOf
});


@override $McpToolSchemaPropertyDtoCopyWith<$Res>? get items;

}
/// @nodoc
class __$McpToolSchemaPropertyDtoCopyWithImpl<$Res>
    implements _$McpToolSchemaPropertyDtoCopyWith<$Res> {
  __$McpToolSchemaPropertyDtoCopyWithImpl(this._self, this._then);

  final _McpToolSchemaPropertyDto _self;
  final $Res Function(_McpToolSchemaPropertyDto) _then;

/// Create a copy of McpToolSchemaPropertyDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? type = freezed,Object? title = freezed,Object? description = null,Object? enumValues = freezed,Object? items = freezed,Object? properties = freezed,Object? requiredFields = freezed,Object? additionalProperties = freezed,Object? defaultValue = freezed,Object? minimum = freezed,Object? maximum = freezed,Object? minLength = freezed,Object? maxLength = freezed,Object? anyOf = freezed,}) {
  return _then(_McpToolSchemaPropertyDto(
type: freezed == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as JsonSchemaPropertyType?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String?,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,enumValues: freezed == enumValues ? _self._enumValues : enumValues // ignore: cast_nullable_to_non_nullable
as List<String>?,items: freezed == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as McpToolSchemaPropertyDto?,properties: freezed == properties ? _self._properties : properties // ignore: cast_nullable_to_non_nullable
as Map<String, McpToolSchemaPropertyDto>?,requiredFields: freezed == requiredFields ? _self._requiredFields : requiredFields // ignore: cast_nullable_to_non_nullable
as List<String>?,additionalProperties: freezed == additionalProperties ? _self.additionalProperties : additionalProperties // ignore: cast_nullable_to_non_nullable
as bool?,defaultValue: freezed == defaultValue ? _self.defaultValue : defaultValue ,minimum: freezed == minimum ? _self.minimum : minimum // ignore: cast_nullable_to_non_nullable
as num?,maximum: freezed == maximum ? _self.maximum : maximum // ignore: cast_nullable_to_non_nullable
as num?,minLength: freezed == minLength ? _self.minLength : minLength // ignore: cast_nullable_to_non_nullable
as int?,maxLength: freezed == maxLength ? _self.maxLength : maxLength // ignore: cast_nullable_to_non_nullable
as int?,anyOf: freezed == anyOf ? _self._anyOf : anyOf // ignore: cast_nullable_to_non_nullable
as List<McpToolSchemaPropertyDto>?,
  ));
}

/// Create a copy of McpToolSchemaPropertyDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$McpToolSchemaPropertyDtoCopyWith<$Res>? get items {
    if (_self.items == null) {
    return null;
  }

  return $McpToolSchemaPropertyDtoCopyWith<$Res>(_self.items!, (value) {
    return _then(_self.copyWith(items: value));
  });
}
}


/// @nodoc
mixin _$McpToolInputSchemaDto {

 String get type; String? get title; String get description; Map<String, McpToolSchemaPropertyDto> get properties;@JsonKey(name: 'required') List<String> get requiredFields;@JsonKey(name: 'additional_properties') bool? get additionalProperties;@JsonKey(name: 'schema_uri') String? get schemaUri;
/// Create a copy of McpToolInputSchemaDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$McpToolInputSchemaDtoCopyWith<McpToolInputSchemaDto> get copyWith => _$McpToolInputSchemaDtoCopyWithImpl<McpToolInputSchemaDto>(this as McpToolInputSchemaDto, _$identity);

  /// Serializes this McpToolInputSchemaDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'McpToolInputSchemaDto(type: $type, title: $title, description: $description, properties: $properties, requiredFields: $requiredFields, additionalProperties: $additionalProperties, schemaUri: $schemaUri)';
}


}

/// @nodoc
abstract mixin class $McpToolInputSchemaDtoCopyWith<$Res>  {
  factory $McpToolInputSchemaDtoCopyWith(McpToolInputSchemaDto value, $Res Function(McpToolInputSchemaDto) _then) = _$McpToolInputSchemaDtoCopyWithImpl;
@useResult
$Res call({
 String type, String? title, String description, Map<String, McpToolSchemaPropertyDto> properties,@JsonKey(name: 'required') List<String> requiredFields,@JsonKey(name: 'additional_properties') bool? additionalProperties,@JsonKey(name: 'schema_uri') String? schemaUri
});




}
/// @nodoc
class _$McpToolInputSchemaDtoCopyWithImpl<$Res>
    implements $McpToolInputSchemaDtoCopyWith<$Res> {
  _$McpToolInputSchemaDtoCopyWithImpl(this._self, this._then);

  final McpToolInputSchemaDto _self;
  final $Res Function(McpToolInputSchemaDto) _then;

/// Create a copy of McpToolInputSchemaDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? type = null,Object? title = freezed,Object? description = null,Object? properties = null,Object? requiredFields = null,Object? additionalProperties = freezed,Object? schemaUri = freezed,}) {
  return _then(_self.copyWith(
type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String?,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,properties: null == properties ? _self.properties : properties // ignore: cast_nullable_to_non_nullable
as Map<String, McpToolSchemaPropertyDto>,requiredFields: null == requiredFields ? _self.requiredFields : requiredFields // ignore: cast_nullable_to_non_nullable
as List<String>,additionalProperties: freezed == additionalProperties ? _self.additionalProperties : additionalProperties // ignore: cast_nullable_to_non_nullable
as bool?,schemaUri: freezed == schemaUri ? _self.schemaUri : schemaUri // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [McpToolInputSchemaDto].
extension McpToolInputSchemaDtoPatterns on McpToolInputSchemaDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _McpToolInputSchemaDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _McpToolInputSchemaDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _McpToolInputSchemaDto value)  $default,){
final _that = this;
switch (_that) {
case _McpToolInputSchemaDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _McpToolInputSchemaDto value)?  $default,){
final _that = this;
switch (_that) {
case _McpToolInputSchemaDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String type,  String? title,  String description,  Map<String, McpToolSchemaPropertyDto> properties, @JsonKey(name: 'required')  List<String> requiredFields, @JsonKey(name: 'additional_properties')  bool? additionalProperties, @JsonKey(name: 'schema_uri')  String? schemaUri)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _McpToolInputSchemaDto() when $default != null:
return $default(_that.type,_that.title,_that.description,_that.properties,_that.requiredFields,_that.additionalProperties,_that.schemaUri);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String type,  String? title,  String description,  Map<String, McpToolSchemaPropertyDto> properties, @JsonKey(name: 'required')  List<String> requiredFields, @JsonKey(name: 'additional_properties')  bool? additionalProperties, @JsonKey(name: 'schema_uri')  String? schemaUri)  $default,) {final _that = this;
switch (_that) {
case _McpToolInputSchemaDto():
return $default(_that.type,_that.title,_that.description,_that.properties,_that.requiredFields,_that.additionalProperties,_that.schemaUri);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String type,  String? title,  String description,  Map<String, McpToolSchemaPropertyDto> properties, @JsonKey(name: 'required')  List<String> requiredFields, @JsonKey(name: 'additional_properties')  bool? additionalProperties, @JsonKey(name: 'schema_uri')  String? schemaUri)?  $default,) {final _that = this;
switch (_that) {
case _McpToolInputSchemaDto() when $default != null:
return $default(_that.type,_that.title,_that.description,_that.properties,_that.requiredFields,_that.additionalProperties,_that.schemaUri);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _McpToolInputSchemaDto implements McpToolInputSchemaDto {
  const _McpToolInputSchemaDto({this.type = 'object', this.title, this.description = '', final  Map<String, McpToolSchemaPropertyDto> properties = const <String, McpToolSchemaPropertyDto>{}, @JsonKey(name: 'required') final  List<String> requiredFields = const <String>[], @JsonKey(name: 'additional_properties') this.additionalProperties, @JsonKey(name: 'schema_uri') this.schemaUri}): _properties = properties,_requiredFields = requiredFields;
  factory _McpToolInputSchemaDto.fromJson(Map<String, dynamic> json) => _$McpToolInputSchemaDtoFromJson(json);

@override@JsonKey() final  String type;
@override final  String? title;
@override@JsonKey() final  String description;
 final  Map<String, McpToolSchemaPropertyDto> _properties;
@override@JsonKey() Map<String, McpToolSchemaPropertyDto> get properties {
  if (_properties is EqualUnmodifiableMapView) return _properties;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_properties);
}

 final  List<String> _requiredFields;
@override@JsonKey(name: 'required') List<String> get requiredFields {
  if (_requiredFields is EqualUnmodifiableListView) return _requiredFields;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_requiredFields);
}

@override@JsonKey(name: 'additional_properties') final  bool? additionalProperties;
@override@JsonKey(name: 'schema_uri') final  String? schemaUri;

/// Create a copy of McpToolInputSchemaDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$McpToolInputSchemaDtoCopyWith<_McpToolInputSchemaDto> get copyWith => __$McpToolInputSchemaDtoCopyWithImpl<_McpToolInputSchemaDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$McpToolInputSchemaDtoToJson(this, );
}



@override
String toString() {
  return 'McpToolInputSchemaDto(type: $type, title: $title, description: $description, properties: $properties, requiredFields: $requiredFields, additionalProperties: $additionalProperties, schemaUri: $schemaUri)';
}


}

/// @nodoc
abstract mixin class _$McpToolInputSchemaDtoCopyWith<$Res> implements $McpToolInputSchemaDtoCopyWith<$Res> {
  factory _$McpToolInputSchemaDtoCopyWith(_McpToolInputSchemaDto value, $Res Function(_McpToolInputSchemaDto) _then) = __$McpToolInputSchemaDtoCopyWithImpl;
@override @useResult
$Res call({
 String type, String? title, String description, Map<String, McpToolSchemaPropertyDto> properties,@JsonKey(name: 'required') List<String> requiredFields,@JsonKey(name: 'additional_properties') bool? additionalProperties,@JsonKey(name: 'schema_uri') String? schemaUri
});




}
/// @nodoc
class __$McpToolInputSchemaDtoCopyWithImpl<$Res>
    implements _$McpToolInputSchemaDtoCopyWith<$Res> {
  __$McpToolInputSchemaDtoCopyWithImpl(this._self, this._then);

  final _McpToolInputSchemaDto _self;
  final $Res Function(_McpToolInputSchemaDto) _then;

/// Create a copy of McpToolInputSchemaDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? type = null,Object? title = freezed,Object? description = null,Object? properties = null,Object? requiredFields = null,Object? additionalProperties = freezed,Object? schemaUri = freezed,}) {
  return _then(_McpToolInputSchemaDto(
type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String?,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,properties: null == properties ? _self._properties : properties // ignore: cast_nullable_to_non_nullable
as Map<String, McpToolSchemaPropertyDto>,requiredFields: null == requiredFields ? _self._requiredFields : requiredFields // ignore: cast_nullable_to_non_nullable
as List<String>,additionalProperties: freezed == additionalProperties ? _self.additionalProperties : additionalProperties // ignore: cast_nullable_to_non_nullable
as bool?,schemaUri: freezed == schemaUri ? _self.schemaUri : schemaUri // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$McpToolExecutionDto {

@JsonKey(name: 'task_support') String? get taskSupport;
/// Create a copy of McpToolExecutionDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$McpToolExecutionDtoCopyWith<McpToolExecutionDto> get copyWith => _$McpToolExecutionDtoCopyWithImpl<McpToolExecutionDto>(this as McpToolExecutionDto, _$identity);

  /// Serializes this McpToolExecutionDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'McpToolExecutionDto(taskSupport: $taskSupport)';
}


}

/// @nodoc
abstract mixin class $McpToolExecutionDtoCopyWith<$Res>  {
  factory $McpToolExecutionDtoCopyWith(McpToolExecutionDto value, $Res Function(McpToolExecutionDto) _then) = _$McpToolExecutionDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'task_support') String? taskSupport
});




}
/// @nodoc
class _$McpToolExecutionDtoCopyWithImpl<$Res>
    implements $McpToolExecutionDtoCopyWith<$Res> {
  _$McpToolExecutionDtoCopyWithImpl(this._self, this._then);

  final McpToolExecutionDto _self;
  final $Res Function(McpToolExecutionDto) _then;

/// Create a copy of McpToolExecutionDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? taskSupport = freezed,}) {
  return _then(_self.copyWith(
taskSupport: freezed == taskSupport ? _self.taskSupport : taskSupport // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [McpToolExecutionDto].
extension McpToolExecutionDtoPatterns on McpToolExecutionDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _McpToolExecutionDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _McpToolExecutionDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _McpToolExecutionDto value)  $default,){
final _that = this;
switch (_that) {
case _McpToolExecutionDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _McpToolExecutionDto value)?  $default,){
final _that = this;
switch (_that) {
case _McpToolExecutionDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'task_support')  String? taskSupport)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _McpToolExecutionDto() when $default != null:
return $default(_that.taskSupport);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'task_support')  String? taskSupport)  $default,) {final _that = this;
switch (_that) {
case _McpToolExecutionDto():
return $default(_that.taskSupport);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'task_support')  String? taskSupport)?  $default,) {final _that = this;
switch (_that) {
case _McpToolExecutionDto() when $default != null:
return $default(_that.taskSupport);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _McpToolExecutionDto implements McpToolExecutionDto {
  const _McpToolExecutionDto({@JsonKey(name: 'task_support') this.taskSupport});
  factory _McpToolExecutionDto.fromJson(Map<String, dynamic> json) => _$McpToolExecutionDtoFromJson(json);

@override@JsonKey(name: 'task_support') final  String? taskSupport;

/// Create a copy of McpToolExecutionDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$McpToolExecutionDtoCopyWith<_McpToolExecutionDto> get copyWith => __$McpToolExecutionDtoCopyWithImpl<_McpToolExecutionDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$McpToolExecutionDtoToJson(this, );
}



@override
String toString() {
  return 'McpToolExecutionDto(taskSupport: $taskSupport)';
}


}

/// @nodoc
abstract mixin class _$McpToolExecutionDtoCopyWith<$Res> implements $McpToolExecutionDtoCopyWith<$Res> {
  factory _$McpToolExecutionDtoCopyWith(_McpToolExecutionDto value, $Res Function(_McpToolExecutionDto) _then) = __$McpToolExecutionDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'task_support') String? taskSupport
});




}
/// @nodoc
class __$McpToolExecutionDtoCopyWithImpl<$Res>
    implements _$McpToolExecutionDtoCopyWith<$Res> {
  __$McpToolExecutionDtoCopyWithImpl(this._self, this._then);

  final _McpToolExecutionDto _self;
  final $Res Function(_McpToolExecutionDto) _then;

/// Create a copy of McpToolExecutionDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? taskSupport = freezed,}) {
  return _then(_McpToolExecutionDto(
taskSupport: freezed == taskSupport ? _self.taskSupport : taskSupport // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$AllowedMcpTool {

@JsonKey(name: 'tool_id') String get toolId; ToolCapability get capability; I18nText get name; String get description;@JsonKey(name: 'input_schema') McpToolInputSchemaDto get inputSchema; McpToolExecutionDto? get execution; bool get enabled;
/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AllowedMcpToolCopyWith<AllowedMcpTool> get copyWith => _$AllowedMcpToolCopyWithImpl<AllowedMcpTool>(this as AllowedMcpTool, _$identity);

  /// Serializes this AllowedMcpTool to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'AllowedMcpTool(toolId: $toolId, capability: $capability, name: $name, description: $description, inputSchema: $inputSchema, execution: $execution, enabled: $enabled)';
}


}

/// @nodoc
abstract mixin class $AllowedMcpToolCopyWith<$Res>  {
  factory $AllowedMcpToolCopyWith(AllowedMcpTool value, $Res Function(AllowedMcpTool) _then) = _$AllowedMcpToolCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'tool_id') String toolId, ToolCapability capability, I18nText name, String description,@JsonKey(name: 'input_schema') McpToolInputSchemaDto inputSchema, McpToolExecutionDto? execution, bool enabled
});


$I18nTextCopyWith<$Res> get name;$McpToolInputSchemaDtoCopyWith<$Res> get inputSchema;$McpToolExecutionDtoCopyWith<$Res>? get execution;

}
/// @nodoc
class _$AllowedMcpToolCopyWithImpl<$Res>
    implements $AllowedMcpToolCopyWith<$Res> {
  _$AllowedMcpToolCopyWithImpl(this._self, this._then);

  final AllowedMcpTool _self;
  final $Res Function(AllowedMcpTool) _then;

/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? toolId = null,Object? capability = null,Object? name = null,Object? description = null,Object? inputSchema = null,Object? execution = freezed,Object? enabled = null,}) {
  return _then(_self.copyWith(
toolId: null == toolId ? _self.toolId : toolId // ignore: cast_nullable_to_non_nullable
as String,capability: null == capability ? _self.capability : capability // ignore: cast_nullable_to_non_nullable
as ToolCapability,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,inputSchema: null == inputSchema ? _self.inputSchema : inputSchema // ignore: cast_nullable_to_non_nullable
as McpToolInputSchemaDto,execution: freezed == execution ? _self.execution : execution // ignore: cast_nullable_to_non_nullable
as McpToolExecutionDto?,enabled: null == enabled ? _self.enabled : enabled // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}
/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$McpToolInputSchemaDtoCopyWith<$Res> get inputSchema {
  
  return $McpToolInputSchemaDtoCopyWith<$Res>(_self.inputSchema, (value) {
    return _then(_self.copyWith(inputSchema: value));
  });
}/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$McpToolExecutionDtoCopyWith<$Res>? get execution {
    if (_self.execution == null) {
    return null;
  }

  return $McpToolExecutionDtoCopyWith<$Res>(_self.execution!, (value) {
    return _then(_self.copyWith(execution: value));
  });
}
}


/// Adds pattern-matching-related methods to [AllowedMcpTool].
extension AllowedMcpToolPatterns on AllowedMcpTool {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AllowedMcpTool value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AllowedMcpTool() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AllowedMcpTool value)  $default,){
final _that = this;
switch (_that) {
case _AllowedMcpTool():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AllowedMcpTool value)?  $default,){
final _that = this;
switch (_that) {
case _AllowedMcpTool() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'tool_id')  String toolId,  ToolCapability capability,  I18nText name,  String description, @JsonKey(name: 'input_schema')  McpToolInputSchemaDto inputSchema,  McpToolExecutionDto? execution,  bool enabled)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AllowedMcpTool() when $default != null:
return $default(_that.toolId,_that.capability,_that.name,_that.description,_that.inputSchema,_that.execution,_that.enabled);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'tool_id')  String toolId,  ToolCapability capability,  I18nText name,  String description, @JsonKey(name: 'input_schema')  McpToolInputSchemaDto inputSchema,  McpToolExecutionDto? execution,  bool enabled)  $default,) {final _that = this;
switch (_that) {
case _AllowedMcpTool():
return $default(_that.toolId,_that.capability,_that.name,_that.description,_that.inputSchema,_that.execution,_that.enabled);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'tool_id')  String toolId,  ToolCapability capability,  I18nText name,  String description, @JsonKey(name: 'input_schema')  McpToolInputSchemaDto inputSchema,  McpToolExecutionDto? execution,  bool enabled)?  $default,) {final _that = this;
switch (_that) {
case _AllowedMcpTool() when $default != null:
return $default(_that.toolId,_that.capability,_that.name,_that.description,_that.inputSchema,_that.execution,_that.enabled);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _AllowedMcpTool implements AllowedMcpTool {
  const _AllowedMcpTool({@JsonKey(name: 'tool_id') required this.toolId, this.capability = ToolCapability.search, required this.name, required this.description, @JsonKey(name: 'input_schema') this.inputSchema = const McpToolInputSchemaDto(), this.execution, this.enabled = true});
  factory _AllowedMcpTool.fromJson(Map<String, dynamic> json) => _$AllowedMcpToolFromJson(json);

@override@JsonKey(name: 'tool_id') final  String toolId;
@override@JsonKey() final  ToolCapability capability;
@override final  I18nText name;
@override final  String description;
@override@JsonKey(name: 'input_schema') final  McpToolInputSchemaDto inputSchema;
@override final  McpToolExecutionDto? execution;
@override@JsonKey() final  bool enabled;

/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AllowedMcpToolCopyWith<_AllowedMcpTool> get copyWith => __$AllowedMcpToolCopyWithImpl<_AllowedMcpTool>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AllowedMcpToolToJson(this, );
}



@override
String toString() {
  return 'AllowedMcpTool(toolId: $toolId, capability: $capability, name: $name, description: $description, inputSchema: $inputSchema, execution: $execution, enabled: $enabled)';
}


}

/// @nodoc
abstract mixin class _$AllowedMcpToolCopyWith<$Res> implements $AllowedMcpToolCopyWith<$Res> {
  factory _$AllowedMcpToolCopyWith(_AllowedMcpTool value, $Res Function(_AllowedMcpTool) _then) = __$AllowedMcpToolCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'tool_id') String toolId, ToolCapability capability, I18nText name, String description,@JsonKey(name: 'input_schema') McpToolInputSchemaDto inputSchema, McpToolExecutionDto? execution, bool enabled
});


@override $I18nTextCopyWith<$Res> get name;@override $McpToolInputSchemaDtoCopyWith<$Res> get inputSchema;@override $McpToolExecutionDtoCopyWith<$Res>? get execution;

}
/// @nodoc
class __$AllowedMcpToolCopyWithImpl<$Res>
    implements _$AllowedMcpToolCopyWith<$Res> {
  __$AllowedMcpToolCopyWithImpl(this._self, this._then);

  final _AllowedMcpTool _self;
  final $Res Function(_AllowedMcpTool) _then;

/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? toolId = null,Object? capability = null,Object? name = null,Object? description = null,Object? inputSchema = null,Object? execution = freezed,Object? enabled = null,}) {
  return _then(_AllowedMcpTool(
toolId: null == toolId ? _self.toolId : toolId // ignore: cast_nullable_to_non_nullable
as String,capability: null == capability ? _self.capability : capability // ignore: cast_nullable_to_non_nullable
as ToolCapability,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,inputSchema: null == inputSchema ? _self.inputSchema : inputSchema // ignore: cast_nullable_to_non_nullable
as McpToolInputSchemaDto,execution: freezed == execution ? _self.execution : execution // ignore: cast_nullable_to_non_nullable
as McpToolExecutionDto?,enabled: null == enabled ? _self.enabled : enabled // ignore: cast_nullable_to_non_nullable
as bool,
  ));
}

/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$McpToolInputSchemaDtoCopyWith<$Res> get inputSchema {
  
  return $McpToolInputSchemaDtoCopyWith<$Res>(_self.inputSchema, (value) {
    return _then(_self.copyWith(inputSchema: value));
  });
}/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$McpToolExecutionDtoCopyWith<$Res>? get execution {
    if (_self.execution == null) {
    return null;
  }

  return $McpToolExecutionDtoCopyWith<$Res>(_self.execution!, (value) {
    return _then(_self.copyWith(execution: value));
  });
}
}


/// @nodoc
mixin _$McpGateway {

@StrictOpaqueIdConverter() String get id; String get type; String get slug;@JsonKey(name: 'endpoint_url') String get endpointUrl;@JsonKey(name: 'transport_type') McpTransportType get transportType;@JsonKey(name: 'auth_type') McpAuthType get authType;@JsonKey(name: 'auth_header_name') String? get authHeaderName;@JsonKey(name: 'auth_env_var') String? get authEnvVar;@JsonKey(name: 'timeout_seconds') int get timeoutSeconds; List<AllowedMcpTool> get tools;
/// Create a copy of McpGateway
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$McpGatewayCopyWith<McpGateway> get copyWith => _$McpGatewayCopyWithImpl<McpGateway>(this as McpGateway, _$identity);

  /// Serializes this McpGateway to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'McpGateway(id: $id, type: $type, slug: $slug, endpointUrl: $endpointUrl, transportType: $transportType, authType: $authType, authHeaderName: $authHeaderName, authEnvVar: $authEnvVar, timeoutSeconds: $timeoutSeconds, tools: $tools)';
}


}

/// @nodoc
abstract mixin class $McpGatewayCopyWith<$Res>  {
  factory $McpGatewayCopyWith(McpGateway value, $Res Function(McpGateway) _then) = _$McpGatewayCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String type, String slug,@JsonKey(name: 'endpoint_url') String endpointUrl,@JsonKey(name: 'transport_type') McpTransportType transportType,@JsonKey(name: 'auth_type') McpAuthType authType,@JsonKey(name: 'auth_header_name') String? authHeaderName,@JsonKey(name: 'auth_env_var') String? authEnvVar,@JsonKey(name: 'timeout_seconds') int timeoutSeconds, List<AllowedMcpTool> tools
});




}
/// @nodoc
class _$McpGatewayCopyWithImpl<$Res>
    implements $McpGatewayCopyWith<$Res> {
  _$McpGatewayCopyWithImpl(this._self, this._then);

  final McpGateway _self;
  final $Res Function(McpGateway) _then;

/// Create a copy of McpGateway
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? type = null,Object? slug = null,Object? endpointUrl = null,Object? transportType = null,Object? authType = null,Object? authHeaderName = freezed,Object? authEnvVar = freezed,Object? timeoutSeconds = null,Object? tools = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,endpointUrl: null == endpointUrl ? _self.endpointUrl : endpointUrl // ignore: cast_nullable_to_non_nullable
as String,transportType: null == transportType ? _self.transportType : transportType // ignore: cast_nullable_to_non_nullable
as McpTransportType,authType: null == authType ? _self.authType : authType // ignore: cast_nullable_to_non_nullable
as McpAuthType,authHeaderName: freezed == authHeaderName ? _self.authHeaderName : authHeaderName // ignore: cast_nullable_to_non_nullable
as String?,authEnvVar: freezed == authEnvVar ? _self.authEnvVar : authEnvVar // ignore: cast_nullable_to_non_nullable
as String?,timeoutSeconds: null == timeoutSeconds ? _self.timeoutSeconds : timeoutSeconds // ignore: cast_nullable_to_non_nullable
as int,tools: null == tools ? _self.tools : tools // ignore: cast_nullable_to_non_nullable
as List<AllowedMcpTool>,
  ));
}

}


/// Adds pattern-matching-related methods to [McpGateway].
extension McpGatewayPatterns on McpGateway {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _McpGateway value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _McpGateway() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _McpGateway value)  $default,){
final _that = this;
switch (_that) {
case _McpGateway():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _McpGateway value)?  $default,){
final _that = this;
switch (_that) {
case _McpGateway() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String type,  String slug, @JsonKey(name: 'endpoint_url')  String endpointUrl, @JsonKey(name: 'transport_type')  McpTransportType transportType, @JsonKey(name: 'auth_type')  McpAuthType authType, @JsonKey(name: 'auth_header_name')  String? authHeaderName, @JsonKey(name: 'auth_env_var')  String? authEnvVar, @JsonKey(name: 'timeout_seconds')  int timeoutSeconds,  List<AllowedMcpTool> tools)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _McpGateway() when $default != null:
return $default(_that.id,_that.type,_that.slug,_that.endpointUrl,_that.transportType,_that.authType,_that.authHeaderName,_that.authEnvVar,_that.timeoutSeconds,_that.tools);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String type,  String slug, @JsonKey(name: 'endpoint_url')  String endpointUrl, @JsonKey(name: 'transport_type')  McpTransportType transportType, @JsonKey(name: 'auth_type')  McpAuthType authType, @JsonKey(name: 'auth_header_name')  String? authHeaderName, @JsonKey(name: 'auth_env_var')  String? authEnvVar, @JsonKey(name: 'timeout_seconds')  int timeoutSeconds,  List<AllowedMcpTool> tools)  $default,) {final _that = this;
switch (_that) {
case _McpGateway():
return $default(_that.id,_that.type,_that.slug,_that.endpointUrl,_that.transportType,_that.authType,_that.authHeaderName,_that.authEnvVar,_that.timeoutSeconds,_that.tools);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String type,  String slug, @JsonKey(name: 'endpoint_url')  String endpointUrl, @JsonKey(name: 'transport_type')  McpTransportType transportType, @JsonKey(name: 'auth_type')  McpAuthType authType, @JsonKey(name: 'auth_header_name')  String? authHeaderName, @JsonKey(name: 'auth_env_var')  String? authEnvVar, @JsonKey(name: 'timeout_seconds')  int timeoutSeconds,  List<AllowedMcpTool> tools)?  $default,) {final _that = this;
switch (_that) {
case _McpGateway() when $default != null:
return $default(_that.id,_that.type,_that.slug,_that.endpointUrl,_that.transportType,_that.authType,_that.authHeaderName,_that.authEnvVar,_that.timeoutSeconds,_that.tools);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _McpGateway implements McpGateway {
  const _McpGateway({@StrictOpaqueIdConverter() required this.id, this.type = 'mcp_gateways', this.slug = 'default_mcp_gateway', @JsonKey(name: 'endpoint_url') this.endpointUrl = '', @JsonKey(name: 'transport_type') this.transportType = McpTransportType.streamableHttp, @JsonKey(name: 'auth_type') this.authType = McpAuthType.none, @JsonKey(name: 'auth_header_name') this.authHeaderName, @JsonKey(name: 'auth_env_var') this.authEnvVar, @JsonKey(name: 'timeout_seconds') this.timeoutSeconds = 30, final  List<AllowedMcpTool> tools = const []}): _tools = tools;
  factory _McpGateway.fromJson(Map<String, dynamic> json) => _$McpGatewayFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override@JsonKey() final  String type;
@override@JsonKey() final  String slug;
@override@JsonKey(name: 'endpoint_url') final  String endpointUrl;
@override@JsonKey(name: 'transport_type') final  McpTransportType transportType;
@override@JsonKey(name: 'auth_type') final  McpAuthType authType;
@override@JsonKey(name: 'auth_header_name') final  String? authHeaderName;
@override@JsonKey(name: 'auth_env_var') final  String? authEnvVar;
@override@JsonKey(name: 'timeout_seconds') final  int timeoutSeconds;
 final  List<AllowedMcpTool> _tools;
@override@JsonKey() List<AllowedMcpTool> get tools {
  if (_tools is EqualUnmodifiableListView) return _tools;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_tools);
}


/// Create a copy of McpGateway
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$McpGatewayCopyWith<_McpGateway> get copyWith => __$McpGatewayCopyWithImpl<_McpGateway>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$McpGatewayToJson(this, );
}



@override
String toString() {
  return 'McpGateway(id: $id, type: $type, slug: $slug, endpointUrl: $endpointUrl, transportType: $transportType, authType: $authType, authHeaderName: $authHeaderName, authEnvVar: $authEnvVar, timeoutSeconds: $timeoutSeconds, tools: $tools)';
}


}

/// @nodoc
abstract mixin class _$McpGatewayCopyWith<$Res> implements $McpGatewayCopyWith<$Res> {
  factory _$McpGatewayCopyWith(_McpGateway value, $Res Function(_McpGateway) _then) = __$McpGatewayCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String type, String slug,@JsonKey(name: 'endpoint_url') String endpointUrl,@JsonKey(name: 'transport_type') McpTransportType transportType,@JsonKey(name: 'auth_type') McpAuthType authType,@JsonKey(name: 'auth_header_name') String? authHeaderName,@JsonKey(name: 'auth_env_var') String? authEnvVar,@JsonKey(name: 'timeout_seconds') int timeoutSeconds, List<AllowedMcpTool> tools
});




}
/// @nodoc
class __$McpGatewayCopyWithImpl<$Res>
    implements _$McpGatewayCopyWith<$Res> {
  __$McpGatewayCopyWithImpl(this._self, this._then);

  final _McpGateway _self;
  final $Res Function(_McpGateway) _then;

/// Create a copy of McpGateway
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? type = null,Object? slug = null,Object? endpointUrl = null,Object? transportType = null,Object? authType = null,Object? authHeaderName = freezed,Object? authEnvVar = freezed,Object? timeoutSeconds = null,Object? tools = null,}) {
  return _then(_McpGateway(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,endpointUrl: null == endpointUrl ? _self.endpointUrl : endpointUrl // ignore: cast_nullable_to_non_nullable
as String,transportType: null == transportType ? _self.transportType : transportType // ignore: cast_nullable_to_non_nullable
as McpTransportType,authType: null == authType ? _self.authType : authType // ignore: cast_nullable_to_non_nullable
as McpAuthType,authHeaderName: freezed == authHeaderName ? _self.authHeaderName : authHeaderName // ignore: cast_nullable_to_non_nullable
as String?,authEnvVar: freezed == authEnvVar ? _self.authEnvVar : authEnvVar // ignore: cast_nullable_to_non_nullable
as String?,timeoutSeconds: null == timeoutSeconds ? _self.timeoutSeconds : timeoutSeconds // ignore: cast_nullable_to_non_nullable
as int,tools: null == tools ? _self._tools : tools // ignore: cast_nullable_to_non_nullable
as List<AllowedMcpTool>,
  ));
}


}

// dart format on
