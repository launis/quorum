// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'system_preview.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$SystemPreview {

@JsonKey(name: 'system_instruction') String get systemInstruction;@JsonKey(name: 'user_prompt') String get userPrompt;@JsonKey(name: 'agent_class') String get agentClass;
/// Create a copy of SystemPreview
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SystemPreviewCopyWith<SystemPreview> get copyWith => _$SystemPreviewCopyWithImpl<SystemPreview>(this as SystemPreview, _$identity);

  /// Serializes this SystemPreview to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is SystemPreview&&(identical(other.systemInstruction, systemInstruction) || other.systemInstruction == systemInstruction)&&(identical(other.userPrompt, userPrompt) || other.userPrompt == userPrompt)&&(identical(other.agentClass, agentClass) || other.agentClass == agentClass));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,systemInstruction,userPrompt,agentClass);

@override
String toString() {
  return 'SystemPreview(systemInstruction: $systemInstruction, userPrompt: $userPrompt, agentClass: $agentClass)';
}


}

/// @nodoc
abstract mixin class $SystemPreviewCopyWith<$Res>  {
  factory $SystemPreviewCopyWith(SystemPreview value, $Res Function(SystemPreview) _then) = _$SystemPreviewCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'system_instruction') String systemInstruction,@JsonKey(name: 'user_prompt') String userPrompt,@JsonKey(name: 'agent_class') String agentClass
});




}
/// @nodoc
class _$SystemPreviewCopyWithImpl<$Res>
    implements $SystemPreviewCopyWith<$Res> {
  _$SystemPreviewCopyWithImpl(this._self, this._then);

  final SystemPreview _self;
  final $Res Function(SystemPreview) _then;

/// Create a copy of SystemPreview
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? systemInstruction = null,Object? userPrompt = null,Object? agentClass = null,}) {
  return _then(_self.copyWith(
systemInstruction: null == systemInstruction ? _self.systemInstruction : systemInstruction // ignore: cast_nullable_to_non_nullable
as String,userPrompt: null == userPrompt ? _self.userPrompt : userPrompt // ignore: cast_nullable_to_non_nullable
as String,agentClass: null == agentClass ? _self.agentClass : agentClass // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [SystemPreview].
extension SystemPreviewPatterns on SystemPreview {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SystemPreview value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SystemPreview() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SystemPreview value)  $default,){
final _that = this;
switch (_that) {
case _SystemPreview():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SystemPreview value)?  $default,){
final _that = this;
switch (_that) {
case _SystemPreview() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'system_instruction')  String systemInstruction, @JsonKey(name: 'user_prompt')  String userPrompt, @JsonKey(name: 'agent_class')  String agentClass)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SystemPreview() when $default != null:
return $default(_that.systemInstruction,_that.userPrompt,_that.agentClass);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'system_instruction')  String systemInstruction, @JsonKey(name: 'user_prompt')  String userPrompt, @JsonKey(name: 'agent_class')  String agentClass)  $default,) {final _that = this;
switch (_that) {
case _SystemPreview():
return $default(_that.systemInstruction,_that.userPrompt,_that.agentClass);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'system_instruction')  String systemInstruction, @JsonKey(name: 'user_prompt')  String userPrompt, @JsonKey(name: 'agent_class')  String agentClass)?  $default,) {final _that = this;
switch (_that) {
case _SystemPreview() when $default != null:
return $default(_that.systemInstruction,_that.userPrompt,_that.agentClass);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _SystemPreview implements SystemPreview {
  const _SystemPreview({@JsonKey(name: 'system_instruction') required this.systemInstruction, @JsonKey(name: 'user_prompt') required this.userPrompt, @JsonKey(name: 'agent_class') required this.agentClass});
  factory _SystemPreview.fromJson(Map<String, dynamic> json) => _$SystemPreviewFromJson(json);

@override@JsonKey(name: 'system_instruction') final  String systemInstruction;
@override@JsonKey(name: 'user_prompt') final  String userPrompt;
@override@JsonKey(name: 'agent_class') final  String agentClass;

/// Create a copy of SystemPreview
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SystemPreviewCopyWith<_SystemPreview> get copyWith => __$SystemPreviewCopyWithImpl<_SystemPreview>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SystemPreviewToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _SystemPreview&&(identical(other.systemInstruction, systemInstruction) || other.systemInstruction == systemInstruction)&&(identical(other.userPrompt, userPrompt) || other.userPrompt == userPrompt)&&(identical(other.agentClass, agentClass) || other.agentClass == agentClass));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,systemInstruction,userPrompt,agentClass);

@override
String toString() {
  return 'SystemPreview(systemInstruction: $systemInstruction, userPrompt: $userPrompt, agentClass: $agentClass)';
}


}

/// @nodoc
abstract mixin class _$SystemPreviewCopyWith<$Res> implements $SystemPreviewCopyWith<$Res> {
  factory _$SystemPreviewCopyWith(_SystemPreview value, $Res Function(_SystemPreview) _then) = __$SystemPreviewCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'system_instruction') String systemInstruction,@JsonKey(name: 'user_prompt') String userPrompt,@JsonKey(name: 'agent_class') String agentClass
});




}
/// @nodoc
class __$SystemPreviewCopyWithImpl<$Res>
    implements _$SystemPreviewCopyWith<$Res> {
  __$SystemPreviewCopyWithImpl(this._self, this._then);

  final _SystemPreview _self;
  final $Res Function(_SystemPreview) _then;

/// Create a copy of SystemPreview
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? systemInstruction = null,Object? userPrompt = null,Object? agentClass = null,}) {
  return _then(_SystemPreview(
systemInstruction: null == systemInstruction ? _self.systemInstruction : systemInstruction // ignore: cast_nullable_to_non_nullable
as String,userPrompt: null == userPrompt ? _self.userPrompt : userPrompt // ignore: cast_nullable_to_non_nullable
as String,agentClass: null == agentClass ? _self.agentClass : agentClass // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$ChainPreview {

@JsonKey(name: 'markdown_content') String get markdownContent;
/// Create a copy of ChainPreview
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ChainPreviewCopyWith<ChainPreview> get copyWith => _$ChainPreviewCopyWithImpl<ChainPreview>(this as ChainPreview, _$identity);

  /// Serializes this ChainPreview to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ChainPreview&&(identical(other.markdownContent, markdownContent) || other.markdownContent == markdownContent));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,markdownContent);

@override
String toString() {
  return 'ChainPreview(markdownContent: $markdownContent)';
}


}

/// @nodoc
abstract mixin class $ChainPreviewCopyWith<$Res>  {
  factory $ChainPreviewCopyWith(ChainPreview value, $Res Function(ChainPreview) _then) = _$ChainPreviewCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'markdown_content') String markdownContent
});




}
/// @nodoc
class _$ChainPreviewCopyWithImpl<$Res>
    implements $ChainPreviewCopyWith<$Res> {
  _$ChainPreviewCopyWithImpl(this._self, this._then);

  final ChainPreview _self;
  final $Res Function(ChainPreview) _then;

/// Create a copy of ChainPreview
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? markdownContent = null,}) {
  return _then(_self.copyWith(
markdownContent: null == markdownContent ? _self.markdownContent : markdownContent // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [ChainPreview].
extension ChainPreviewPatterns on ChainPreview {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ChainPreview value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ChainPreview() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ChainPreview value)  $default,){
final _that = this;
switch (_that) {
case _ChainPreview():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ChainPreview value)?  $default,){
final _that = this;
switch (_that) {
case _ChainPreview() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'markdown_content')  String markdownContent)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ChainPreview() when $default != null:
return $default(_that.markdownContent);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'markdown_content')  String markdownContent)  $default,) {final _that = this;
switch (_that) {
case _ChainPreview():
return $default(_that.markdownContent);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'markdown_content')  String markdownContent)?  $default,) {final _that = this;
switch (_that) {
case _ChainPreview() when $default != null:
return $default(_that.markdownContent);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ChainPreview implements ChainPreview {
  const _ChainPreview({@JsonKey(name: 'markdown_content') required this.markdownContent});
  factory _ChainPreview.fromJson(Map<String, dynamic> json) => _$ChainPreviewFromJson(json);

@override@JsonKey(name: 'markdown_content') final  String markdownContent;

/// Create a copy of ChainPreview
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ChainPreviewCopyWith<_ChainPreview> get copyWith => __$ChainPreviewCopyWithImpl<_ChainPreview>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ChainPreviewToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ChainPreview&&(identical(other.markdownContent, markdownContent) || other.markdownContent == markdownContent));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,markdownContent);

@override
String toString() {
  return 'ChainPreview(markdownContent: $markdownContent)';
}


}

/// @nodoc
abstract mixin class _$ChainPreviewCopyWith<$Res> implements $ChainPreviewCopyWith<$Res> {
  factory _$ChainPreviewCopyWith(_ChainPreview value, $Res Function(_ChainPreview) _then) = __$ChainPreviewCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'markdown_content') String markdownContent
});




}
/// @nodoc
class __$ChainPreviewCopyWithImpl<$Res>
    implements _$ChainPreviewCopyWith<$Res> {
  __$ChainPreviewCopyWithImpl(this._self, this._then);

  final _ChainPreview _self;
  final $Res Function(_ChainPreview) _then;

/// Create a copy of ChainPreview
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? markdownContent = null,}) {
  return _then(_ChainPreview(
markdownContent: null == markdownContent ? _self.markdownContent : markdownContent // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
