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
mixin _$AllowedMcpTool {

@JsonKey(name: 'tool_id') String get toolId; I18nText get name; String get description;@JsonKey(name: 'input_schema') Map<String, dynamic> get inputSchema;
/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AllowedMcpToolCopyWith<AllowedMcpTool> get copyWith => _$AllowedMcpToolCopyWithImpl<AllowedMcpTool>(this as AllowedMcpTool, _$identity);

  /// Serializes this AllowedMcpTool to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'AllowedMcpTool(toolId: $toolId, name: $name, description: $description, inputSchema: $inputSchema)';
}


}

/// @nodoc
abstract mixin class $AllowedMcpToolCopyWith<$Res>  {
  factory $AllowedMcpToolCopyWith(AllowedMcpTool value, $Res Function(AllowedMcpTool) _then) = _$AllowedMcpToolCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'tool_id') String toolId, I18nText name, String description,@JsonKey(name: 'input_schema') Map<String, dynamic> inputSchema
});


$I18nTextCopyWith<$Res> get name;

}
/// @nodoc
class _$AllowedMcpToolCopyWithImpl<$Res>
    implements $AllowedMcpToolCopyWith<$Res> {
  _$AllowedMcpToolCopyWithImpl(this._self, this._then);

  final AllowedMcpTool _self;
  final $Res Function(AllowedMcpTool) _then;

/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? toolId = null,Object? name = null,Object? description = null,Object? inputSchema = null,}) {
  return _then(_self.copyWith(
toolId: null == toolId ? _self.toolId : toolId // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,inputSchema: null == inputSchema ? _self.inputSchema : inputSchema // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'tool_id')  String toolId,  I18nText name,  String description, @JsonKey(name: 'input_schema')  Map<String, dynamic> inputSchema)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AllowedMcpTool() when $default != null:
return $default(_that.toolId,_that.name,_that.description,_that.inputSchema);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'tool_id')  String toolId,  I18nText name,  String description, @JsonKey(name: 'input_schema')  Map<String, dynamic> inputSchema)  $default,) {final _that = this;
switch (_that) {
case _AllowedMcpTool():
return $default(_that.toolId,_that.name,_that.description,_that.inputSchema);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'tool_id')  String toolId,  I18nText name,  String description, @JsonKey(name: 'input_schema')  Map<String, dynamic> inputSchema)?  $default,) {final _that = this;
switch (_that) {
case _AllowedMcpTool() when $default != null:
return $default(_that.toolId,_that.name,_that.description,_that.inputSchema);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _AllowedMcpTool implements AllowedMcpTool {
  const _AllowedMcpTool({@JsonKey(name: 'tool_id') required this.toolId, required this.name, required this.description, @JsonKey(name: 'input_schema') final  Map<String, dynamic> inputSchema = const {}}): _inputSchema = inputSchema;
  factory _AllowedMcpTool.fromJson(Map<String, dynamic> json) => _$AllowedMcpToolFromJson(json);

@override@JsonKey(name: 'tool_id') final  String toolId;
@override final  I18nText name;
@override final  String description;
 final  Map<String, dynamic> _inputSchema;
@override@JsonKey(name: 'input_schema') Map<String, dynamic> get inputSchema {
  if (_inputSchema is EqualUnmodifiableMapView) return _inputSchema;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_inputSchema);
}


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
  return 'AllowedMcpTool(toolId: $toolId, name: $name, description: $description, inputSchema: $inputSchema)';
}


}

/// @nodoc
abstract mixin class _$AllowedMcpToolCopyWith<$Res> implements $AllowedMcpToolCopyWith<$Res> {
  factory _$AllowedMcpToolCopyWith(_AllowedMcpTool value, $Res Function(_AllowedMcpTool) _then) = __$AllowedMcpToolCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'tool_id') String toolId, I18nText name, String description,@JsonKey(name: 'input_schema') Map<String, dynamic> inputSchema
});


@override $I18nTextCopyWith<$Res> get name;

}
/// @nodoc
class __$AllowedMcpToolCopyWithImpl<$Res>
    implements _$AllowedMcpToolCopyWith<$Res> {
  __$AllowedMcpToolCopyWithImpl(this._self, this._then);

  final _AllowedMcpTool _self;
  final $Res Function(_AllowedMcpTool) _then;

/// Create a copy of AllowedMcpTool
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? toolId = null,Object? name = null,Object? description = null,Object? inputSchema = null,}) {
  return _then(_AllowedMcpTool(
toolId: null == toolId ? _self.toolId : toolId // ignore: cast_nullable_to_non_nullable
as String,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: null == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as String,inputSchema: null == inputSchema ? _self._inputSchema : inputSchema // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
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
}
}


/// @nodoc
mixin _$McpGateway {

@StrictOpaqueIdConverter() String get id; String get type; String? get slug; List<AllowedMcpTool> get tools;
/// Create a copy of McpGateway
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$McpGatewayCopyWith<McpGateway> get copyWith => _$McpGatewayCopyWithImpl<McpGateway>(this as McpGateway, _$identity);

  /// Serializes this McpGateway to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'McpGateway(id: $id, type: $type, slug: $slug, tools: $tools)';
}


}

/// @nodoc
abstract mixin class $McpGatewayCopyWith<$Res>  {
  factory $McpGatewayCopyWith(McpGateway value, $Res Function(McpGateway) _then) = _$McpGatewayCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String type, String? slug, List<AllowedMcpTool> tools
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
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? type = null,Object? slug = freezed,Object? tools = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,tools: null == tools ? _self.tools : tools // ignore: cast_nullable_to_non_nullable
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String type,  String? slug,  List<AllowedMcpTool> tools)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _McpGateway() when $default != null:
return $default(_that.id,_that.type,_that.slug,_that.tools);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String type,  String? slug,  List<AllowedMcpTool> tools)  $default,) {final _that = this;
switch (_that) {
case _McpGateway():
return $default(_that.id,_that.type,_that.slug,_that.tools);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String type,  String? slug,  List<AllowedMcpTool> tools)?  $default,) {final _that = this;
switch (_that) {
case _McpGateway() when $default != null:
return $default(_that.id,_that.type,_that.slug,_that.tools);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _McpGateway implements McpGateway {
  const _McpGateway({@StrictOpaqueIdConverter() required this.id, this.type = 'mcp_gateways', this.slug, final  List<AllowedMcpTool> tools = const []}): _tools = tools;
  factory _McpGateway.fromJson(Map<String, dynamic> json) => _$McpGatewayFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override@JsonKey() final  String type;
@override final  String? slug;
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
  return 'McpGateway(id: $id, type: $type, slug: $slug, tools: $tools)';
}


}

/// @nodoc
abstract mixin class _$McpGatewayCopyWith<$Res> implements $McpGatewayCopyWith<$Res> {
  factory _$McpGatewayCopyWith(_McpGateway value, $Res Function(_McpGateway) _then) = __$McpGatewayCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String type, String? slug, List<AllowedMcpTool> tools
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
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? type = null,Object? slug = freezed,Object? tools = null,}) {
  return _then(_McpGateway(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,tools: null == tools ? _self._tools : tools // ignore: cast_nullable_to_non_nullable
as List<AllowedMcpTool>,
  ));
}


}

// dart format on
