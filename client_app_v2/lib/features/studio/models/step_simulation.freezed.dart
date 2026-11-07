// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'step_simulation.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$PromptContextMetaValue {

@JsonKey(name: 'string_value') String? get stringValue;@JsonKey(name: 'number_value') double? get numberValue;@JsonKey(name: 'bool_value') bool? get boolValue;@JsonKey(name: 'string_list_value') List<String>? get stringListValue;
/// Create a copy of PromptContextMetaValue
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PromptContextMetaValueCopyWith<PromptContextMetaValue> get copyWith => _$PromptContextMetaValueCopyWithImpl<PromptContextMetaValue>(this as PromptContextMetaValue, _$identity);

  /// Serializes this PromptContextMetaValue to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is PromptContextMetaValue&&(identical(other.stringValue, stringValue) || other.stringValue == stringValue)&&(identical(other.numberValue, numberValue) || other.numberValue == numberValue)&&(identical(other.boolValue, boolValue) || other.boolValue == boolValue)&&const DeepCollectionEquality().equals(other.stringListValue, stringListValue));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,stringValue,numberValue,boolValue,const DeepCollectionEquality().hash(stringListValue));

@override
String toString() {
  return 'PromptContextMetaValue(stringValue: $stringValue, numberValue: $numberValue, boolValue: $boolValue, stringListValue: $stringListValue)';
}


}

/// @nodoc
abstract mixin class $PromptContextMetaValueCopyWith<$Res>  {
  factory $PromptContextMetaValueCopyWith(PromptContextMetaValue value, $Res Function(PromptContextMetaValue) _then) = _$PromptContextMetaValueCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'string_value') String? stringValue,@JsonKey(name: 'number_value') double? numberValue,@JsonKey(name: 'bool_value') bool? boolValue,@JsonKey(name: 'string_list_value') List<String>? stringListValue
});




}
/// @nodoc
class _$PromptContextMetaValueCopyWithImpl<$Res>
    implements $PromptContextMetaValueCopyWith<$Res> {
  _$PromptContextMetaValueCopyWithImpl(this._self, this._then);

  final PromptContextMetaValue _self;
  final $Res Function(PromptContextMetaValue) _then;

/// Create a copy of PromptContextMetaValue
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


/// Adds pattern-matching-related methods to [PromptContextMetaValue].
extension PromptContextMetaValuePatterns on PromptContextMetaValue {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PromptContextMetaValue value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PromptContextMetaValue() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PromptContextMetaValue value)  $default,){
final _that = this;
switch (_that) {
case _PromptContextMetaValue():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PromptContextMetaValue value)?  $default,){
final _that = this;
switch (_that) {
case _PromptContextMetaValue() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'string_value')  String? stringValue, @JsonKey(name: 'number_value')  double? numberValue, @JsonKey(name: 'bool_value')  bool? boolValue, @JsonKey(name: 'string_list_value')  List<String>? stringListValue)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PromptContextMetaValue() when $default != null:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'string_value')  String? stringValue, @JsonKey(name: 'number_value')  double? numberValue, @JsonKey(name: 'bool_value')  bool? boolValue, @JsonKey(name: 'string_list_value')  List<String>? stringListValue)  $default,) {final _that = this;
switch (_that) {
case _PromptContextMetaValue():
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'string_value')  String? stringValue, @JsonKey(name: 'number_value')  double? numberValue, @JsonKey(name: 'bool_value')  bool? boolValue, @JsonKey(name: 'string_list_value')  List<String>? stringListValue)?  $default,) {final _that = this;
switch (_that) {
case _PromptContextMetaValue() when $default != null:
return $default(_that.stringValue,_that.numberValue,_that.boolValue,_that.stringListValue);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _PromptContextMetaValue extends PromptContextMetaValue {
  const _PromptContextMetaValue({@JsonKey(name: 'string_value') this.stringValue, @JsonKey(name: 'number_value') this.numberValue, @JsonKey(name: 'bool_value') this.boolValue, @JsonKey(name: 'string_list_value') final  List<String>? stringListValue}): _stringListValue = stringListValue,super._();
  factory _PromptContextMetaValue.fromJson(Map<String, dynamic> json) => _$PromptContextMetaValueFromJson(json);

@override@JsonKey(name: 'string_value') final  String? stringValue;
@override@JsonKey(name: 'number_value') final  double? numberValue;
@override@JsonKey(name: 'bool_value') final  bool? boolValue;
 final  List<String>? _stringListValue;
@override@JsonKey(name: 'string_list_value') List<String>? get stringListValue {
  final value = _stringListValue;
  if (value == null) return null;
  if (_stringListValue is EqualUnmodifiableListView) return _stringListValue;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}


/// Create a copy of PromptContextMetaValue
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PromptContextMetaValueCopyWith<_PromptContextMetaValue> get copyWith => __$PromptContextMetaValueCopyWithImpl<_PromptContextMetaValue>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PromptContextMetaValueToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _PromptContextMetaValue&&(identical(other.stringValue, stringValue) || other.stringValue == stringValue)&&(identical(other.numberValue, numberValue) || other.numberValue == numberValue)&&(identical(other.boolValue, boolValue) || other.boolValue == boolValue)&&const DeepCollectionEquality().equals(other._stringListValue, _stringListValue));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,stringValue,numberValue,boolValue,const DeepCollectionEquality().hash(_stringListValue));

@override
String toString() {
  return 'PromptContextMetaValue(stringValue: $stringValue, numberValue: $numberValue, boolValue: $boolValue, stringListValue: $stringListValue)';
}


}

/// @nodoc
abstract mixin class _$PromptContextMetaValueCopyWith<$Res> implements $PromptContextMetaValueCopyWith<$Res> {
  factory _$PromptContextMetaValueCopyWith(_PromptContextMetaValue value, $Res Function(_PromptContextMetaValue) _then) = __$PromptContextMetaValueCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'string_value') String? stringValue,@JsonKey(name: 'number_value') double? numberValue,@JsonKey(name: 'bool_value') bool? boolValue,@JsonKey(name: 'string_list_value') List<String>? stringListValue
});




}
/// @nodoc
class __$PromptContextMetaValueCopyWithImpl<$Res>
    implements _$PromptContextMetaValueCopyWith<$Res> {
  __$PromptContextMetaValueCopyWithImpl(this._self, this._then);

  final _PromptContextMetaValue _self;
  final $Res Function(_PromptContextMetaValue) _then;

/// Create a copy of PromptContextMetaValue
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? stringValue = freezed,Object? numberValue = freezed,Object? boolValue = freezed,Object? stringListValue = freezed,}) {
  return _then(_PromptContextMetaValue(
stringValue: freezed == stringValue ? _self.stringValue : stringValue // ignore: cast_nullable_to_non_nullable
as String?,numberValue: freezed == numberValue ? _self.numberValue : numberValue // ignore: cast_nullable_to_non_nullable
as double?,boolValue: freezed == boolValue ? _self.boolValue : boolValue // ignore: cast_nullable_to_non_nullable
as bool?,stringListValue: freezed == stringListValue ? _self._stringListValue : stringListValue // ignore: cast_nullable_to_non_nullable
as List<String>?,
  ));
}


}


/// @nodoc
mixin _$StepSimulationTraceDto {

@JsonKey(name: 'execution_time_ms') double get executionTimeMs;@JsonKey(name: 'estimated_tokens') int get estimatedTokens;
/// Create a copy of StepSimulationTraceDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StepSimulationTraceDtoCopyWith<StepSimulationTraceDto> get copyWith => _$StepSimulationTraceDtoCopyWithImpl<StepSimulationTraceDto>(this as StepSimulationTraceDto, _$identity);

  /// Serializes this StepSimulationTraceDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'StepSimulationTraceDto(executionTimeMs: $executionTimeMs, estimatedTokens: $estimatedTokens)';
}


}

/// @nodoc
abstract mixin class $StepSimulationTraceDtoCopyWith<$Res>  {
  factory $StepSimulationTraceDtoCopyWith(StepSimulationTraceDto value, $Res Function(StepSimulationTraceDto) _then) = _$StepSimulationTraceDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'execution_time_ms') double executionTimeMs,@JsonKey(name: 'estimated_tokens') int estimatedTokens
});




}
/// @nodoc
class _$StepSimulationTraceDtoCopyWithImpl<$Res>
    implements $StepSimulationTraceDtoCopyWith<$Res> {
  _$StepSimulationTraceDtoCopyWithImpl(this._self, this._then);

  final StepSimulationTraceDto _self;
  final $Res Function(StepSimulationTraceDto) _then;

/// Create a copy of StepSimulationTraceDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? executionTimeMs = null,Object? estimatedTokens = null,}) {
  return _then(_self.copyWith(
executionTimeMs: null == executionTimeMs ? _self.executionTimeMs : executionTimeMs // ignore: cast_nullable_to_non_nullable
as double,estimatedTokens: null == estimatedTokens ? _self.estimatedTokens : estimatedTokens // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [StepSimulationTraceDto].
extension StepSimulationTraceDtoPatterns on StepSimulationTraceDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StepSimulationTraceDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StepSimulationTraceDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StepSimulationTraceDto value)  $default,){
final _that = this;
switch (_that) {
case _StepSimulationTraceDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StepSimulationTraceDto value)?  $default,){
final _that = this;
switch (_that) {
case _StepSimulationTraceDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'execution_time_ms')  double executionTimeMs, @JsonKey(name: 'estimated_tokens')  int estimatedTokens)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StepSimulationTraceDto() when $default != null:
return $default(_that.executionTimeMs,_that.estimatedTokens);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'execution_time_ms')  double executionTimeMs, @JsonKey(name: 'estimated_tokens')  int estimatedTokens)  $default,) {final _that = this;
switch (_that) {
case _StepSimulationTraceDto():
return $default(_that.executionTimeMs,_that.estimatedTokens);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'execution_time_ms')  double executionTimeMs, @JsonKey(name: 'estimated_tokens')  int estimatedTokens)?  $default,) {final _that = this;
switch (_that) {
case _StepSimulationTraceDto() when $default != null:
return $default(_that.executionTimeMs,_that.estimatedTokens);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _StepSimulationTraceDto extends StepSimulationTraceDto {
  const _StepSimulationTraceDto({@JsonKey(name: 'execution_time_ms') this.executionTimeMs = 0.0, @JsonKey(name: 'estimated_tokens') this.estimatedTokens = 0}): super._();
  factory _StepSimulationTraceDto.fromJson(Map<String, dynamic> json) => _$StepSimulationTraceDtoFromJson(json);

@override@JsonKey(name: 'execution_time_ms') final  double executionTimeMs;
@override@JsonKey(name: 'estimated_tokens') final  int estimatedTokens;

/// Create a copy of StepSimulationTraceDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StepSimulationTraceDtoCopyWith<_StepSimulationTraceDto> get copyWith => __$StepSimulationTraceDtoCopyWithImpl<_StepSimulationTraceDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StepSimulationTraceDtoToJson(this, );
}



@override
String toString() {
  return 'StepSimulationTraceDto(executionTimeMs: $executionTimeMs, estimatedTokens: $estimatedTokens)';
}


}

/// @nodoc
abstract mixin class _$StepSimulationTraceDtoCopyWith<$Res> implements $StepSimulationTraceDtoCopyWith<$Res> {
  factory _$StepSimulationTraceDtoCopyWith(_StepSimulationTraceDto value, $Res Function(_StepSimulationTraceDto) _then) = __$StepSimulationTraceDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'execution_time_ms') double executionTimeMs,@JsonKey(name: 'estimated_tokens') int estimatedTokens
});




}
/// @nodoc
class __$StepSimulationTraceDtoCopyWithImpl<$Res>
    implements _$StepSimulationTraceDtoCopyWith<$Res> {
  __$StepSimulationTraceDtoCopyWithImpl(this._self, this._then);

  final _StepSimulationTraceDto _self;
  final $Res Function(_StepSimulationTraceDto) _then;

/// Create a copy of StepSimulationTraceDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? executionTimeMs = null,Object? estimatedTokens = null,}) {
  return _then(_StepSimulationTraceDto(
executionTimeMs: null == executionTimeMs ? _self.executionTimeMs : executionTimeMs // ignore: cast_nullable_to_non_nullable
as double,estimatedTokens: null == estimatedTokens ? _self.estimatedTokens : estimatedTokens // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$LlmMessageDto {

 String get role; String get content;@JsonKey(name: 'tool_calls') Object? get toolCalls;@JsonKey(name: 'tool_call_id') String? get toolCallId; String? get name;
/// Create a copy of LlmMessageDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LlmMessageDtoCopyWith<LlmMessageDto> get copyWith => _$LlmMessageDtoCopyWithImpl<LlmMessageDto>(this as LlmMessageDto, _$identity);

  /// Serializes this LlmMessageDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'LlmMessageDto(role: $role, content: $content, toolCalls: $toolCalls, toolCallId: $toolCallId, name: $name)';
}


}

/// @nodoc
abstract mixin class $LlmMessageDtoCopyWith<$Res>  {
  factory $LlmMessageDtoCopyWith(LlmMessageDto value, $Res Function(LlmMessageDto) _then) = _$LlmMessageDtoCopyWithImpl;
@useResult
$Res call({
 String role, String content,@JsonKey(name: 'tool_calls') Object? toolCalls,@JsonKey(name: 'tool_call_id') String? toolCallId, String? name
});




}
/// @nodoc
class _$LlmMessageDtoCopyWithImpl<$Res>
    implements $LlmMessageDtoCopyWith<$Res> {
  _$LlmMessageDtoCopyWithImpl(this._self, this._then);

  final LlmMessageDto _self;
  final $Res Function(LlmMessageDto) _then;

/// Create a copy of LlmMessageDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? role = null,Object? content = null,Object? toolCalls = freezed,Object? toolCallId = freezed,Object? name = freezed,}) {
  return _then(_self.copyWith(
role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as String,content: null == content ? _self.content : content // ignore: cast_nullable_to_non_nullable
as String,toolCalls: freezed == toolCalls ? _self.toolCalls : toolCalls ,toolCallId: freezed == toolCallId ? _self.toolCallId : toolCallId // ignore: cast_nullable_to_non_nullable
as String?,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [LlmMessageDto].
extension LlmMessageDtoPatterns on LlmMessageDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LlmMessageDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LlmMessageDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LlmMessageDto value)  $default,){
final _that = this;
switch (_that) {
case _LlmMessageDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LlmMessageDto value)?  $default,){
final _that = this;
switch (_that) {
case _LlmMessageDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String role,  String content, @JsonKey(name: 'tool_calls')  Object? toolCalls, @JsonKey(name: 'tool_call_id')  String? toolCallId,  String? name)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LlmMessageDto() when $default != null:
return $default(_that.role,_that.content,_that.toolCalls,_that.toolCallId,_that.name);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String role,  String content, @JsonKey(name: 'tool_calls')  Object? toolCalls, @JsonKey(name: 'tool_call_id')  String? toolCallId,  String? name)  $default,) {final _that = this;
switch (_that) {
case _LlmMessageDto():
return $default(_that.role,_that.content,_that.toolCalls,_that.toolCallId,_that.name);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String role,  String content, @JsonKey(name: 'tool_calls')  Object? toolCalls, @JsonKey(name: 'tool_call_id')  String? toolCallId,  String? name)?  $default,) {final _that = this;
switch (_that) {
case _LlmMessageDto() when $default != null:
return $default(_that.role,_that.content,_that.toolCalls,_that.toolCallId,_that.name);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _LlmMessageDto extends LlmMessageDto {
  const _LlmMessageDto({required this.role, required this.content, @JsonKey(name: 'tool_calls') this.toolCalls, @JsonKey(name: 'tool_call_id') this.toolCallId, this.name}): super._();
  factory _LlmMessageDto.fromJson(Map<String, dynamic> json) => _$LlmMessageDtoFromJson(json);

@override final  String role;
@override final  String content;
@override@JsonKey(name: 'tool_calls') final  Object? toolCalls;
@override@JsonKey(name: 'tool_call_id') final  String? toolCallId;
@override final  String? name;

/// Create a copy of LlmMessageDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LlmMessageDtoCopyWith<_LlmMessageDto> get copyWith => __$LlmMessageDtoCopyWithImpl<_LlmMessageDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LlmMessageDtoToJson(this, );
}



@override
String toString() {
  return 'LlmMessageDto(role: $role, content: $content, toolCalls: $toolCalls, toolCallId: $toolCallId, name: $name)';
}


}

/// @nodoc
abstract mixin class _$LlmMessageDtoCopyWith<$Res> implements $LlmMessageDtoCopyWith<$Res> {
  factory _$LlmMessageDtoCopyWith(_LlmMessageDto value, $Res Function(_LlmMessageDto) _then) = __$LlmMessageDtoCopyWithImpl;
@override @useResult
$Res call({
 String role, String content,@JsonKey(name: 'tool_calls') Object? toolCalls,@JsonKey(name: 'tool_call_id') String? toolCallId, String? name
});




}
/// @nodoc
class __$LlmMessageDtoCopyWithImpl<$Res>
    implements _$LlmMessageDtoCopyWith<$Res> {
  __$LlmMessageDtoCopyWithImpl(this._self, this._then);

  final _LlmMessageDto _self;
  final $Res Function(_LlmMessageDto) _then;

/// Create a copy of LlmMessageDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? role = null,Object? content = null,Object? toolCalls = freezed,Object? toolCallId = freezed,Object? name = freezed,}) {
  return _then(_LlmMessageDto(
role: null == role ? _self.role : role // ignore: cast_nullable_to_non_nullable
as String,content: null == content ? _self.content : content // ignore: cast_nullable_to_non_nullable
as String,toolCalls: freezed == toolCalls ? _self.toolCalls : toolCalls ,toolCallId: freezed == toolCallId ? _self.toolCallId : toolCallId // ignore: cast_nullable_to_non_nullable
as String?,name: freezed == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$PromptContextDto {

@JsonKey(name: 'static_messages') List<LlmMessageDto> get staticMessages;@JsonKey(name: 'dynamic_messages') List<LlmMessageDto> get dynamicMessages;@PromptContextMetaValueConverter() Map<String, PromptContextMetaValue> get metadata;
/// Create a copy of PromptContextDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PromptContextDtoCopyWith<PromptContextDto> get copyWith => _$PromptContextDtoCopyWithImpl<PromptContextDto>(this as PromptContextDto, _$identity);

  /// Serializes this PromptContextDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'PromptContextDto(staticMessages: $staticMessages, dynamicMessages: $dynamicMessages, metadata: $metadata)';
}


}

/// @nodoc
abstract mixin class $PromptContextDtoCopyWith<$Res>  {
  factory $PromptContextDtoCopyWith(PromptContextDto value, $Res Function(PromptContextDto) _then) = _$PromptContextDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'static_messages') List<LlmMessageDto> staticMessages,@JsonKey(name: 'dynamic_messages') List<LlmMessageDto> dynamicMessages,@PromptContextMetaValueConverter() Map<String, PromptContextMetaValue> metadata
});




}
/// @nodoc
class _$PromptContextDtoCopyWithImpl<$Res>
    implements $PromptContextDtoCopyWith<$Res> {
  _$PromptContextDtoCopyWithImpl(this._self, this._then);

  final PromptContextDto _self;
  final $Res Function(PromptContextDto) _then;

/// Create a copy of PromptContextDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? staticMessages = null,Object? dynamicMessages = null,Object? metadata = null,}) {
  return _then(_self.copyWith(
staticMessages: null == staticMessages ? _self.staticMessages : staticMessages // ignore: cast_nullable_to_non_nullable
as List<LlmMessageDto>,dynamicMessages: null == dynamicMessages ? _self.dynamicMessages : dynamicMessages // ignore: cast_nullable_to_non_nullable
as List<LlmMessageDto>,metadata: null == metadata ? _self.metadata : metadata // ignore: cast_nullable_to_non_nullable
as Map<String, PromptContextMetaValue>,
  ));
}

}


/// Adds pattern-matching-related methods to [PromptContextDto].
extension PromptContextDtoPatterns on PromptContextDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PromptContextDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PromptContextDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PromptContextDto value)  $default,){
final _that = this;
switch (_that) {
case _PromptContextDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PromptContextDto value)?  $default,){
final _that = this;
switch (_that) {
case _PromptContextDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'static_messages')  List<LlmMessageDto> staticMessages, @JsonKey(name: 'dynamic_messages')  List<LlmMessageDto> dynamicMessages, @PromptContextMetaValueConverter()  Map<String, PromptContextMetaValue> metadata)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PromptContextDto() when $default != null:
return $default(_that.staticMessages,_that.dynamicMessages,_that.metadata);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'static_messages')  List<LlmMessageDto> staticMessages, @JsonKey(name: 'dynamic_messages')  List<LlmMessageDto> dynamicMessages, @PromptContextMetaValueConverter()  Map<String, PromptContextMetaValue> metadata)  $default,) {final _that = this;
switch (_that) {
case _PromptContextDto():
return $default(_that.staticMessages,_that.dynamicMessages,_that.metadata);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'static_messages')  List<LlmMessageDto> staticMessages, @JsonKey(name: 'dynamic_messages')  List<LlmMessageDto> dynamicMessages, @PromptContextMetaValueConverter()  Map<String, PromptContextMetaValue> metadata)?  $default,) {final _that = this;
switch (_that) {
case _PromptContextDto() when $default != null:
return $default(_that.staticMessages,_that.dynamicMessages,_that.metadata);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _PromptContextDto extends PromptContextDto {
  const _PromptContextDto({@JsonKey(name: 'static_messages') final  List<LlmMessageDto> staticMessages = const <LlmMessageDto>[], @JsonKey(name: 'dynamic_messages') final  List<LlmMessageDto> dynamicMessages = const <LlmMessageDto>[], @PromptContextMetaValueConverter() final  Map<String, PromptContextMetaValue> metadata = const <String, PromptContextMetaValue>{}}): _staticMessages = staticMessages,_dynamicMessages = dynamicMessages,_metadata = metadata,super._();
  factory _PromptContextDto.fromJson(Map<String, dynamic> json) => _$PromptContextDtoFromJson(json);

 final  List<LlmMessageDto> _staticMessages;
@override@JsonKey(name: 'static_messages') List<LlmMessageDto> get staticMessages {
  if (_staticMessages is EqualUnmodifiableListView) return _staticMessages;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_staticMessages);
}

 final  List<LlmMessageDto> _dynamicMessages;
@override@JsonKey(name: 'dynamic_messages') List<LlmMessageDto> get dynamicMessages {
  if (_dynamicMessages is EqualUnmodifiableListView) return _dynamicMessages;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_dynamicMessages);
}

 final  Map<String, PromptContextMetaValue> _metadata;
@override@JsonKey()@PromptContextMetaValueConverter() Map<String, PromptContextMetaValue> get metadata {
  if (_metadata is EqualUnmodifiableMapView) return _metadata;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_metadata);
}


/// Create a copy of PromptContextDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PromptContextDtoCopyWith<_PromptContextDto> get copyWith => __$PromptContextDtoCopyWithImpl<_PromptContextDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PromptContextDtoToJson(this, );
}



@override
String toString() {
  return 'PromptContextDto(staticMessages: $staticMessages, dynamicMessages: $dynamicMessages, metadata: $metadata)';
}


}

/// @nodoc
abstract mixin class _$PromptContextDtoCopyWith<$Res> implements $PromptContextDtoCopyWith<$Res> {
  factory _$PromptContextDtoCopyWith(_PromptContextDto value, $Res Function(_PromptContextDto) _then) = __$PromptContextDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'static_messages') List<LlmMessageDto> staticMessages,@JsonKey(name: 'dynamic_messages') List<LlmMessageDto> dynamicMessages,@PromptContextMetaValueConverter() Map<String, PromptContextMetaValue> metadata
});




}
/// @nodoc
class __$PromptContextDtoCopyWithImpl<$Res>
    implements _$PromptContextDtoCopyWith<$Res> {
  __$PromptContextDtoCopyWithImpl(this._self, this._then);

  final _PromptContextDto _self;
  final $Res Function(_PromptContextDto) _then;

/// Create a copy of PromptContextDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? staticMessages = null,Object? dynamicMessages = null,Object? metadata = null,}) {
  return _then(_PromptContextDto(
staticMessages: null == staticMessages ? _self._staticMessages : staticMessages // ignore: cast_nullable_to_non_nullable
as List<LlmMessageDto>,dynamicMessages: null == dynamicMessages ? _self._dynamicMessages : dynamicMessages // ignore: cast_nullable_to_non_nullable
as List<LlmMessageDto>,metadata: null == metadata ? _self._metadata : metadata // ignore: cast_nullable_to_non_nullable
as Map<String, PromptContextMetaValue>,
  ));
}


}


/// @nodoc
mixin _$StepSimulationRequest {

 NodeStrategy get step;@JsonKey(name: 'mock_inputs') Map<String, String> get mockInputs;@JsonKey(name: 'target_locale') String get targetLocale;@JsonKey(name: 'context_text') String get contextText;
/// Create a copy of StepSimulationRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StepSimulationRequestCopyWith<StepSimulationRequest> get copyWith => _$StepSimulationRequestCopyWithImpl<StepSimulationRequest>(this as StepSimulationRequest, _$identity);

  /// Serializes this StepSimulationRequest to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'StepSimulationRequest(step: $step, mockInputs: $mockInputs, targetLocale: $targetLocale, contextText: $contextText)';
}


}

/// @nodoc
abstract mixin class $StepSimulationRequestCopyWith<$Res>  {
  factory $StepSimulationRequestCopyWith(StepSimulationRequest value, $Res Function(StepSimulationRequest) _then) = _$StepSimulationRequestCopyWithImpl;
@useResult
$Res call({
 NodeStrategy step,@JsonKey(name: 'mock_inputs') Map<String, String> mockInputs,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'context_text') String contextText
});


$NodeStrategyCopyWith<$Res> get step;

}
/// @nodoc
class _$StepSimulationRequestCopyWithImpl<$Res>
    implements $StepSimulationRequestCopyWith<$Res> {
  _$StepSimulationRequestCopyWithImpl(this._self, this._then);

  final StepSimulationRequest _self;
  final $Res Function(StepSimulationRequest) _then;

/// Create a copy of StepSimulationRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? step = null,Object? mockInputs = null,Object? targetLocale = null,Object? contextText = null,}) {
  return _then(_self.copyWith(
step: null == step ? _self.step : step // ignore: cast_nullable_to_non_nullable
as NodeStrategy,mockInputs: null == mockInputs ? _self.mockInputs : mockInputs // ignore: cast_nullable_to_non_nullable
as Map<String, String>,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,contextText: null == contextText ? _self.contextText : contextText // ignore: cast_nullable_to_non_nullable
as String,
  ));
}
/// Create a copy of StepSimulationRequest
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$NodeStrategyCopyWith<$Res> get step {
  
  return $NodeStrategyCopyWith<$Res>(_self.step, (value) {
    return _then(_self.copyWith(step: value));
  });
}
}


/// Adds pattern-matching-related methods to [StepSimulationRequest].
extension StepSimulationRequestPatterns on StepSimulationRequest {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StepSimulationRequest value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StepSimulationRequest() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StepSimulationRequest value)  $default,){
final _that = this;
switch (_that) {
case _StepSimulationRequest():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StepSimulationRequest value)?  $default,){
final _that = this;
switch (_that) {
case _StepSimulationRequest() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( NodeStrategy step, @JsonKey(name: 'mock_inputs')  Map<String, String> mockInputs, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'context_text')  String contextText)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StepSimulationRequest() when $default != null:
return $default(_that.step,_that.mockInputs,_that.targetLocale,_that.contextText);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( NodeStrategy step, @JsonKey(name: 'mock_inputs')  Map<String, String> mockInputs, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'context_text')  String contextText)  $default,) {final _that = this;
switch (_that) {
case _StepSimulationRequest():
return $default(_that.step,_that.mockInputs,_that.targetLocale,_that.contextText);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( NodeStrategy step, @JsonKey(name: 'mock_inputs')  Map<String, String> mockInputs, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'context_text')  String contextText)?  $default,) {final _that = this;
switch (_that) {
case _StepSimulationRequest() when $default != null:
return $default(_that.step,_that.mockInputs,_that.targetLocale,_that.contextText);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _StepSimulationRequest extends StepSimulationRequest {
  const _StepSimulationRequest({required this.step, @JsonKey(name: 'mock_inputs') final  Map<String, String> mockInputs = const <String, String>{}, @JsonKey(name: 'target_locale') this.targetLocale = 'en', @JsonKey(name: 'context_text') this.contextText = '[SIMULATED CONTEXT DOCUMENT]'}): _mockInputs = mockInputs,super._();
  factory _StepSimulationRequest.fromJson(Map<String, dynamic> json) => _$StepSimulationRequestFromJson(json);

@override final  NodeStrategy step;
 final  Map<String, String> _mockInputs;
@override@JsonKey(name: 'mock_inputs') Map<String, String> get mockInputs {
  if (_mockInputs is EqualUnmodifiableMapView) return _mockInputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_mockInputs);
}

@override@JsonKey(name: 'target_locale') final  String targetLocale;
@override@JsonKey(name: 'context_text') final  String contextText;

/// Create a copy of StepSimulationRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StepSimulationRequestCopyWith<_StepSimulationRequest> get copyWith => __$StepSimulationRequestCopyWithImpl<_StepSimulationRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StepSimulationRequestToJson(this, );
}



@override
String toString() {
  return 'StepSimulationRequest(step: $step, mockInputs: $mockInputs, targetLocale: $targetLocale, contextText: $contextText)';
}


}

/// @nodoc
abstract mixin class _$StepSimulationRequestCopyWith<$Res> implements $StepSimulationRequestCopyWith<$Res> {
  factory _$StepSimulationRequestCopyWith(_StepSimulationRequest value, $Res Function(_StepSimulationRequest) _then) = __$StepSimulationRequestCopyWithImpl;
@override @useResult
$Res call({
 NodeStrategy step,@JsonKey(name: 'mock_inputs') Map<String, String> mockInputs,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'context_text') String contextText
});


@override $NodeStrategyCopyWith<$Res> get step;

}
/// @nodoc
class __$StepSimulationRequestCopyWithImpl<$Res>
    implements _$StepSimulationRequestCopyWith<$Res> {
  __$StepSimulationRequestCopyWithImpl(this._self, this._then);

  final _StepSimulationRequest _self;
  final $Res Function(_StepSimulationRequest) _then;

/// Create a copy of StepSimulationRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? step = null,Object? mockInputs = null,Object? targetLocale = null,Object? contextText = null,}) {
  return _then(_StepSimulationRequest(
step: null == step ? _self.step : step // ignore: cast_nullable_to_non_nullable
as NodeStrategy,mockInputs: null == mockInputs ? _self._mockInputs : mockInputs // ignore: cast_nullable_to_non_nullable
as Map<String, String>,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,contextText: null == contextText ? _self.contextText : contextText // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

/// Create a copy of StepSimulationRequest
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$NodeStrategyCopyWith<$Res> get step {
  
  return $NodeStrategyCopyWith<$Res>(_self.step, (value) {
    return _then(_self.copyWith(step: value));
  });
}
}


/// @nodoc
mixin _$StepSimulationResponse {

 bool get valid; List<String> get errors;@JsonKey(name: 'rendered_prompt') String get renderedPrompt; StepSimulationTraceDto get trace;@JsonKey(name: 'prompt_context') PromptContextDto? get promptContext;
/// Create a copy of StepSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$StepSimulationResponseCopyWith<StepSimulationResponse> get copyWith => _$StepSimulationResponseCopyWithImpl<StepSimulationResponse>(this as StepSimulationResponse, _$identity);

  /// Serializes this StepSimulationResponse to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'StepSimulationResponse(valid: $valid, errors: $errors, renderedPrompt: $renderedPrompt, trace: $trace, promptContext: $promptContext)';
}


}

/// @nodoc
abstract mixin class $StepSimulationResponseCopyWith<$Res>  {
  factory $StepSimulationResponseCopyWith(StepSimulationResponse value, $Res Function(StepSimulationResponse) _then) = _$StepSimulationResponseCopyWithImpl;
@useResult
$Res call({
 bool valid, List<String> errors,@JsonKey(name: 'rendered_prompt') String renderedPrompt, StepSimulationTraceDto trace,@JsonKey(name: 'prompt_context') PromptContextDto? promptContext
});


$StepSimulationTraceDtoCopyWith<$Res> get trace;$PromptContextDtoCopyWith<$Res>? get promptContext;

}
/// @nodoc
class _$StepSimulationResponseCopyWithImpl<$Res>
    implements $StepSimulationResponseCopyWith<$Res> {
  _$StepSimulationResponseCopyWithImpl(this._self, this._then);

  final StepSimulationResponse _self;
  final $Res Function(StepSimulationResponse) _then;

/// Create a copy of StepSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? valid = null,Object? errors = null,Object? renderedPrompt = null,Object? trace = null,Object? promptContext = freezed,}) {
  return _then(_self.copyWith(
valid: null == valid ? _self.valid : valid // ignore: cast_nullable_to_non_nullable
as bool,errors: null == errors ? _self.errors : errors // ignore: cast_nullable_to_non_nullable
as List<String>,renderedPrompt: null == renderedPrompt ? _self.renderedPrompt : renderedPrompt // ignore: cast_nullable_to_non_nullable
as String,trace: null == trace ? _self.trace : trace // ignore: cast_nullable_to_non_nullable
as StepSimulationTraceDto,promptContext: freezed == promptContext ? _self.promptContext : promptContext // ignore: cast_nullable_to_non_nullable
as PromptContextDto?,
  ));
}
/// Create a copy of StepSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StepSimulationTraceDtoCopyWith<$Res> get trace {
  
  return $StepSimulationTraceDtoCopyWith<$Res>(_self.trace, (value) {
    return _then(_self.copyWith(trace: value));
  });
}/// Create a copy of StepSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PromptContextDtoCopyWith<$Res>? get promptContext {
    if (_self.promptContext == null) {
    return null;
  }

  return $PromptContextDtoCopyWith<$Res>(_self.promptContext!, (value) {
    return _then(_self.copyWith(promptContext: value));
  });
}
}


/// Adds pattern-matching-related methods to [StepSimulationResponse].
extension StepSimulationResponsePatterns on StepSimulationResponse {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _StepSimulationResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _StepSimulationResponse() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _StepSimulationResponse value)  $default,){
final _that = this;
switch (_that) {
case _StepSimulationResponse():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _StepSimulationResponse value)?  $default,){
final _that = this;
switch (_that) {
case _StepSimulationResponse() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( bool valid,  List<String> errors, @JsonKey(name: 'rendered_prompt')  String renderedPrompt,  StepSimulationTraceDto trace, @JsonKey(name: 'prompt_context')  PromptContextDto? promptContext)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _StepSimulationResponse() when $default != null:
return $default(_that.valid,_that.errors,_that.renderedPrompt,_that.trace,_that.promptContext);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( bool valid,  List<String> errors, @JsonKey(name: 'rendered_prompt')  String renderedPrompt,  StepSimulationTraceDto trace, @JsonKey(name: 'prompt_context')  PromptContextDto? promptContext)  $default,) {final _that = this;
switch (_that) {
case _StepSimulationResponse():
return $default(_that.valid,_that.errors,_that.renderedPrompt,_that.trace,_that.promptContext);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( bool valid,  List<String> errors, @JsonKey(name: 'rendered_prompt')  String renderedPrompt,  StepSimulationTraceDto trace, @JsonKey(name: 'prompt_context')  PromptContextDto? promptContext)?  $default,) {final _that = this;
switch (_that) {
case _StepSimulationResponse() when $default != null:
return $default(_that.valid,_that.errors,_that.renderedPrompt,_that.trace,_that.promptContext);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _StepSimulationResponse extends StepSimulationResponse {
  const _StepSimulationResponse({this.valid = true, final  List<String> errors = const <String>[], @JsonKey(name: 'rendered_prompt') this.renderedPrompt = '', this.trace = const StepSimulationTraceDto(), @JsonKey(name: 'prompt_context') this.promptContext}): _errors = errors,super._();
  factory _StepSimulationResponse.fromJson(Map<String, dynamic> json) => _$StepSimulationResponseFromJson(json);

@override@JsonKey() final  bool valid;
 final  List<String> _errors;
@override@JsonKey() List<String> get errors {
  if (_errors is EqualUnmodifiableListView) return _errors;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_errors);
}

@override@JsonKey(name: 'rendered_prompt') final  String renderedPrompt;
@override@JsonKey() final  StepSimulationTraceDto trace;
@override@JsonKey(name: 'prompt_context') final  PromptContextDto? promptContext;

/// Create a copy of StepSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$StepSimulationResponseCopyWith<_StepSimulationResponse> get copyWith => __$StepSimulationResponseCopyWithImpl<_StepSimulationResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$StepSimulationResponseToJson(this, );
}



@override
String toString() {
  return 'StepSimulationResponse(valid: $valid, errors: $errors, renderedPrompt: $renderedPrompt, trace: $trace, promptContext: $promptContext)';
}


}

/// @nodoc
abstract mixin class _$StepSimulationResponseCopyWith<$Res> implements $StepSimulationResponseCopyWith<$Res> {
  factory _$StepSimulationResponseCopyWith(_StepSimulationResponse value, $Res Function(_StepSimulationResponse) _then) = __$StepSimulationResponseCopyWithImpl;
@override @useResult
$Res call({
 bool valid, List<String> errors,@JsonKey(name: 'rendered_prompt') String renderedPrompt, StepSimulationTraceDto trace,@JsonKey(name: 'prompt_context') PromptContextDto? promptContext
});


@override $StepSimulationTraceDtoCopyWith<$Res> get trace;@override $PromptContextDtoCopyWith<$Res>? get promptContext;

}
/// @nodoc
class __$StepSimulationResponseCopyWithImpl<$Res>
    implements _$StepSimulationResponseCopyWith<$Res> {
  __$StepSimulationResponseCopyWithImpl(this._self, this._then);

  final _StepSimulationResponse _self;
  final $Res Function(_StepSimulationResponse) _then;

/// Create a copy of StepSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? valid = null,Object? errors = null,Object? renderedPrompt = null,Object? trace = null,Object? promptContext = freezed,}) {
  return _then(_StepSimulationResponse(
valid: null == valid ? _self.valid : valid // ignore: cast_nullable_to_non_nullable
as bool,errors: null == errors ? _self._errors : errors // ignore: cast_nullable_to_non_nullable
as List<String>,renderedPrompt: null == renderedPrompt ? _self.renderedPrompt : renderedPrompt // ignore: cast_nullable_to_non_nullable
as String,trace: null == trace ? _self.trace : trace // ignore: cast_nullable_to_non_nullable
as StepSimulationTraceDto,promptContext: freezed == promptContext ? _self.promptContext : promptContext // ignore: cast_nullable_to_non_nullable
as PromptContextDto?,
  ));
}

/// Create a copy of StepSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$StepSimulationTraceDtoCopyWith<$Res> get trace {
  
  return $StepSimulationTraceDtoCopyWith<$Res>(_self.trace, (value) {
    return _then(_self.copyWith(trace: value));
  });
}/// Create a copy of StepSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PromptContextDtoCopyWith<$Res>? get promptContext {
    if (_self.promptContext == null) {
    return null;
  }

  return $PromptContextDtoCopyWith<$Res>(_self.promptContext!, (value) {
    return _then(_self.copyWith(promptContext: value));
  });
}
}

// dart format on
