// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'json_schema.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$JsonSchema {

 String? get type; String? get title; String? get description;// Recursive definition for object properties
 Map<String, JsonSchema>? get properties;// For arrays
 JsonSchema? get items; List<String>? get required;// Mapped from 'enum' in JSON Schema
@JsonKey(name: 'enum') List<dynamic>? get enumValues; int? get minLength; int? get maxLength; double? get minimum; double? get maximum;// UI Hints
@JsonKey(name: 'x-ui-widget') String? get uiWidget;@JsonKey(name: 'x-ui-group') String? get uiGroup;
/// Create a copy of JsonSchema
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$JsonSchemaCopyWith<JsonSchema> get copyWith => _$JsonSchemaCopyWithImpl<JsonSchema>(this as JsonSchema, _$identity);

  /// Serializes this JsonSchema to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is JsonSchema&&(identical(other.type, type) || other.type == type)&&(identical(other.title, title) || other.title == title)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other.properties, properties)&&(identical(other.items, items) || other.items == items)&&const DeepCollectionEquality().equals(other.required, required)&&const DeepCollectionEquality().equals(other.enumValues, enumValues)&&(identical(other.minLength, minLength) || other.minLength == minLength)&&(identical(other.maxLength, maxLength) || other.maxLength == maxLength)&&(identical(other.minimum, minimum) || other.minimum == minimum)&&(identical(other.maximum, maximum) || other.maximum == maximum)&&(identical(other.uiWidget, uiWidget) || other.uiWidget == uiWidget)&&(identical(other.uiGroup, uiGroup) || other.uiGroup == uiGroup));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,type,title,description,const DeepCollectionEquality().hash(properties),items,const DeepCollectionEquality().hash(required),const DeepCollectionEquality().hash(enumValues),minLength,maxLength,minimum,maximum,uiWidget,uiGroup);

@override
String toString() {
  return 'JsonSchema(type: $type, title: $title, description: $description, properties: $properties, items: $items, required: $required, enumValues: $enumValues, minLength: $minLength, maxLength: $maxLength, minimum: $minimum, maximum: $maximum, uiWidget: $uiWidget, uiGroup: $uiGroup)';
}


}

/// @nodoc
abstract mixin class $JsonSchemaCopyWith<$Res>  {
  factory $JsonSchemaCopyWith(JsonSchema value, $Res Function(JsonSchema) _then) = _$JsonSchemaCopyWithImpl;
@useResult
$Res call({
 String? type, String? title, String? description, Map<String, JsonSchema>? properties, JsonSchema? items, List<String>? required,@JsonKey(name: 'enum') List<dynamic>? enumValues, int? minLength, int? maxLength, double? minimum, double? maximum,@JsonKey(name: 'x-ui-widget') String? uiWidget,@JsonKey(name: 'x-ui-group') String? uiGroup
});


$JsonSchemaCopyWith<$Res>? get items;

}
/// @nodoc
class _$JsonSchemaCopyWithImpl<$Res>
    implements $JsonSchemaCopyWith<$Res> {
  _$JsonSchemaCopyWithImpl(this._self, this._then);

  final JsonSchema _self;
  final $Res Function(JsonSchema) _then;

/// Create a copy of JsonSchema
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? type = freezed,Object? title = freezed,Object? description = freezed,Object? properties = freezed,Object? items = freezed,Object? required = freezed,Object? enumValues = freezed,Object? minLength = freezed,Object? maxLength = freezed,Object? minimum = freezed,Object? maximum = freezed,Object? uiWidget = freezed,Object? uiGroup = freezed,}) {
  return _then(_self.copyWith(
type: freezed == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,properties: freezed == properties ? _self.properties : properties // ignore: cast_nullable_to_non_nullable
as Map<String, JsonSchema>?,items: freezed == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as JsonSchema?,required: freezed == required ? _self.required : required // ignore: cast_nullable_to_non_nullable
as List<String>?,enumValues: freezed == enumValues ? _self.enumValues : enumValues // ignore: cast_nullable_to_non_nullable
as List<dynamic>?,minLength: freezed == minLength ? _self.minLength : minLength // ignore: cast_nullable_to_non_nullable
as int?,maxLength: freezed == maxLength ? _self.maxLength : maxLength // ignore: cast_nullable_to_non_nullable
as int?,minimum: freezed == minimum ? _self.minimum : minimum // ignore: cast_nullable_to_non_nullable
as double?,maximum: freezed == maximum ? _self.maximum : maximum // ignore: cast_nullable_to_non_nullable
as double?,uiWidget: freezed == uiWidget ? _self.uiWidget : uiWidget // ignore: cast_nullable_to_non_nullable
as String?,uiGroup: freezed == uiGroup ? _self.uiGroup : uiGroup // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of JsonSchema
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$JsonSchemaCopyWith<$Res>? get items {
    if (_self.items == null) {
    return null;
  }

  return $JsonSchemaCopyWith<$Res>(_self.items!, (value) {
    return _then(_self.copyWith(items: value));
  });
}
}


/// Adds pattern-matching-related methods to [JsonSchema].
extension JsonSchemaPatterns on JsonSchema {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _JsonSchema value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _JsonSchema() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _JsonSchema value)  $default,){
final _that = this;
switch (_that) {
case _JsonSchema():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _JsonSchema value)?  $default,){
final _that = this;
switch (_that) {
case _JsonSchema() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? type,  String? title,  String? description,  Map<String, JsonSchema>? properties,  JsonSchema? items,  List<String>? required, @JsonKey(name: 'enum')  List<dynamic>? enumValues,  int? minLength,  int? maxLength,  double? minimum,  double? maximum, @JsonKey(name: 'x-ui-widget')  String? uiWidget, @JsonKey(name: 'x-ui-group')  String? uiGroup)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _JsonSchema() when $default != null:
return $default(_that.type,_that.title,_that.description,_that.properties,_that.items,_that.required,_that.enumValues,_that.minLength,_that.maxLength,_that.minimum,_that.maximum,_that.uiWidget,_that.uiGroup);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? type,  String? title,  String? description,  Map<String, JsonSchema>? properties,  JsonSchema? items,  List<String>? required, @JsonKey(name: 'enum')  List<dynamic>? enumValues,  int? minLength,  int? maxLength,  double? minimum,  double? maximum, @JsonKey(name: 'x-ui-widget')  String? uiWidget, @JsonKey(name: 'x-ui-group')  String? uiGroup)  $default,) {final _that = this;
switch (_that) {
case _JsonSchema():
return $default(_that.type,_that.title,_that.description,_that.properties,_that.items,_that.required,_that.enumValues,_that.minLength,_that.maxLength,_that.minimum,_that.maximum,_that.uiWidget,_that.uiGroup);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? type,  String? title,  String? description,  Map<String, JsonSchema>? properties,  JsonSchema? items,  List<String>? required, @JsonKey(name: 'enum')  List<dynamic>? enumValues,  int? minLength,  int? maxLength,  double? minimum,  double? maximum, @JsonKey(name: 'x-ui-widget')  String? uiWidget, @JsonKey(name: 'x-ui-group')  String? uiGroup)?  $default,) {final _that = this;
switch (_that) {
case _JsonSchema() when $default != null:
return $default(_that.type,_that.title,_that.description,_that.properties,_that.items,_that.required,_that.enumValues,_that.minLength,_that.maxLength,_that.minimum,_that.maximum,_that.uiWidget,_that.uiGroup);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _JsonSchema implements JsonSchema {
  const _JsonSchema({this.type, this.title, this.description, final  Map<String, JsonSchema>? properties, this.items, final  List<String>? required, @JsonKey(name: 'enum') final  List<dynamic>? enumValues, this.minLength, this.maxLength, this.minimum, this.maximum, @JsonKey(name: 'x-ui-widget') this.uiWidget, @JsonKey(name: 'x-ui-group') this.uiGroup}): _properties = properties,_required = required,_enumValues = enumValues;
  factory _JsonSchema.fromJson(Map<String, dynamic> json) => _$JsonSchemaFromJson(json);

@override final  String? type;
@override final  String? title;
@override final  String? description;
// Recursive definition for object properties
 final  Map<String, JsonSchema>? _properties;
// Recursive definition for object properties
@override Map<String, JsonSchema>? get properties {
  final value = _properties;
  if (value == null) return null;
  if (_properties is EqualUnmodifiableMapView) return _properties;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

// For arrays
@override final  JsonSchema? items;
 final  List<String>? _required;
@override List<String>? get required {
  final value = _required;
  if (value == null) return null;
  if (_required is EqualUnmodifiableListView) return _required;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

// Mapped from 'enum' in JSON Schema
 final  List<dynamic>? _enumValues;
// Mapped from 'enum' in JSON Schema
@override@JsonKey(name: 'enum') List<dynamic>? get enumValues {
  final value = _enumValues;
  if (value == null) return null;
  if (_enumValues is EqualUnmodifiableListView) return _enumValues;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override final  int? minLength;
@override final  int? maxLength;
@override final  double? minimum;
@override final  double? maximum;
// UI Hints
@override@JsonKey(name: 'x-ui-widget') final  String? uiWidget;
@override@JsonKey(name: 'x-ui-group') final  String? uiGroup;

/// Create a copy of JsonSchema
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$JsonSchemaCopyWith<_JsonSchema> get copyWith => __$JsonSchemaCopyWithImpl<_JsonSchema>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$JsonSchemaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _JsonSchema&&(identical(other.type, type) || other.type == type)&&(identical(other.title, title) || other.title == title)&&(identical(other.description, description) || other.description == description)&&const DeepCollectionEquality().equals(other._properties, _properties)&&(identical(other.items, items) || other.items == items)&&const DeepCollectionEquality().equals(other._required, _required)&&const DeepCollectionEquality().equals(other._enumValues, _enumValues)&&(identical(other.minLength, minLength) || other.minLength == minLength)&&(identical(other.maxLength, maxLength) || other.maxLength == maxLength)&&(identical(other.minimum, minimum) || other.minimum == minimum)&&(identical(other.maximum, maximum) || other.maximum == maximum)&&(identical(other.uiWidget, uiWidget) || other.uiWidget == uiWidget)&&(identical(other.uiGroup, uiGroup) || other.uiGroup == uiGroup));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,type,title,description,const DeepCollectionEquality().hash(_properties),items,const DeepCollectionEquality().hash(_required),const DeepCollectionEquality().hash(_enumValues),minLength,maxLength,minimum,maximum,uiWidget,uiGroup);

@override
String toString() {
  return 'JsonSchema(type: $type, title: $title, description: $description, properties: $properties, items: $items, required: $required, enumValues: $enumValues, minLength: $minLength, maxLength: $maxLength, minimum: $minimum, maximum: $maximum, uiWidget: $uiWidget, uiGroup: $uiGroup)';
}


}

/// @nodoc
abstract mixin class _$JsonSchemaCopyWith<$Res> implements $JsonSchemaCopyWith<$Res> {
  factory _$JsonSchemaCopyWith(_JsonSchema value, $Res Function(_JsonSchema) _then) = __$JsonSchemaCopyWithImpl;
@override @useResult
$Res call({
 String? type, String? title, String? description, Map<String, JsonSchema>? properties, JsonSchema? items, List<String>? required,@JsonKey(name: 'enum') List<dynamic>? enumValues, int? minLength, int? maxLength, double? minimum, double? maximum,@JsonKey(name: 'x-ui-widget') String? uiWidget,@JsonKey(name: 'x-ui-group') String? uiGroup
});


@override $JsonSchemaCopyWith<$Res>? get items;

}
/// @nodoc
class __$JsonSchemaCopyWithImpl<$Res>
    implements _$JsonSchemaCopyWith<$Res> {
  __$JsonSchemaCopyWithImpl(this._self, this._then);

  final _JsonSchema _self;
  final $Res Function(_JsonSchema) _then;

/// Create a copy of JsonSchema
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? type = freezed,Object? title = freezed,Object? description = freezed,Object? properties = freezed,Object? items = freezed,Object? required = freezed,Object? enumValues = freezed,Object? minLength = freezed,Object? maxLength = freezed,Object? minimum = freezed,Object? maximum = freezed,Object? uiWidget = freezed,Object? uiGroup = freezed,}) {
  return _then(_JsonSchema(
type: freezed == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String?,properties: freezed == properties ? _self._properties : properties // ignore: cast_nullable_to_non_nullable
as Map<String, JsonSchema>?,items: freezed == items ? _self.items : items // ignore: cast_nullable_to_non_nullable
as JsonSchema?,required: freezed == required ? _self._required : required // ignore: cast_nullable_to_non_nullable
as List<String>?,enumValues: freezed == enumValues ? _self._enumValues : enumValues // ignore: cast_nullable_to_non_nullable
as List<dynamic>?,minLength: freezed == minLength ? _self.minLength : minLength // ignore: cast_nullable_to_non_nullable
as int?,maxLength: freezed == maxLength ? _self.maxLength : maxLength // ignore: cast_nullable_to_non_nullable
as int?,minimum: freezed == minimum ? _self.minimum : minimum // ignore: cast_nullable_to_non_nullable
as double?,maximum: freezed == maximum ? _self.maximum : maximum // ignore: cast_nullable_to_non_nullable
as double?,uiWidget: freezed == uiWidget ? _self.uiWidget : uiWidget // ignore: cast_nullable_to_non_nullable
as String?,uiGroup: freezed == uiGroup ? _self.uiGroup : uiGroup // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of JsonSchema
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$JsonSchemaCopyWith<$Res>? get items {
    if (_self.items == null) {
    return null;
  }

  return $JsonSchemaCopyWith<$Res>(_self.items!, (value) {
    return _then(_self.copyWith(items: value));
  });
}
}

// dart format on
