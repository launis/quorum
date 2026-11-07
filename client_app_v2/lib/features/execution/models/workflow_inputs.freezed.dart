// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'workflow_inputs.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$RawFileInputDto {

 String get filename;@JsonKey(name: 'content_type') String get contentType;@JsonKey(name: 'data_base64') String? get dataBase64;@JsonKey(name: 'content_base64') String? get contentBase64;
/// Create a copy of RawFileInputDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$RawFileInputDtoCopyWith<RawFileInputDto> get copyWith => _$RawFileInputDtoCopyWithImpl<RawFileInputDto>(this as RawFileInputDto, _$identity);

  /// Serializes this RawFileInputDto to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is RawFileInputDto&&(identical(other.filename, filename) || other.filename == filename)&&(identical(other.contentType, contentType) || other.contentType == contentType)&&(identical(other.dataBase64, dataBase64) || other.dataBase64 == dataBase64)&&(identical(other.contentBase64, contentBase64) || other.contentBase64 == contentBase64));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,filename,contentType,dataBase64,contentBase64);

@override
String toString() {
  return 'RawFileInputDto(filename: $filename, contentType: $contentType, dataBase64: $dataBase64, contentBase64: $contentBase64)';
}


}

/// @nodoc
abstract mixin class $RawFileInputDtoCopyWith<$Res>  {
  factory $RawFileInputDtoCopyWith(RawFileInputDto value, $Res Function(RawFileInputDto) _then) = _$RawFileInputDtoCopyWithImpl;
@useResult
$Res call({
 String filename,@JsonKey(name: 'content_type') String contentType,@JsonKey(name: 'data_base64') String? dataBase64,@JsonKey(name: 'content_base64') String? contentBase64
});




}
/// @nodoc
class _$RawFileInputDtoCopyWithImpl<$Res>
    implements $RawFileInputDtoCopyWith<$Res> {
  _$RawFileInputDtoCopyWithImpl(this._self, this._then);

  final RawFileInputDto _self;
  final $Res Function(RawFileInputDto) _then;

/// Create a copy of RawFileInputDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? filename = null,Object? contentType = null,Object? dataBase64 = freezed,Object? contentBase64 = freezed,}) {
  return _then(_self.copyWith(
filename: null == filename ? _self.filename : filename // ignore: cast_nullable_to_non_nullable
as String,contentType: null == contentType ? _self.contentType : contentType // ignore: cast_nullable_to_non_nullable
as String,dataBase64: freezed == dataBase64 ? _self.dataBase64 : dataBase64 // ignore: cast_nullable_to_non_nullable
as String?,contentBase64: freezed == contentBase64 ? _self.contentBase64 : contentBase64 // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [RawFileInputDto].
extension RawFileInputDtoPatterns on RawFileInputDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _RawFileInputDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _RawFileInputDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _RawFileInputDto value)  $default,){
final _that = this;
switch (_that) {
case _RawFileInputDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _RawFileInputDto value)?  $default,){
final _that = this;
switch (_that) {
case _RawFileInputDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String filename, @JsonKey(name: 'content_type')  String contentType, @JsonKey(name: 'data_base64')  String? dataBase64, @JsonKey(name: 'content_base64')  String? contentBase64)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _RawFileInputDto() when $default != null:
return $default(_that.filename,_that.contentType,_that.dataBase64,_that.contentBase64);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String filename, @JsonKey(name: 'content_type')  String contentType, @JsonKey(name: 'data_base64')  String? dataBase64, @JsonKey(name: 'content_base64')  String? contentBase64)  $default,) {final _that = this;
switch (_that) {
case _RawFileInputDto():
return $default(_that.filename,_that.contentType,_that.dataBase64,_that.contentBase64);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String filename, @JsonKey(name: 'content_type')  String contentType, @JsonKey(name: 'data_base64')  String? dataBase64, @JsonKey(name: 'content_base64')  String? contentBase64)?  $default,) {final _that = this;
switch (_that) {
case _RawFileInputDto() when $default != null:
return $default(_that.filename,_that.contentType,_that.dataBase64,_that.contentBase64);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _RawFileInputDto extends RawFileInputDto {
  const _RawFileInputDto({required this.filename, @JsonKey(name: 'content_type') this.contentType = 'application/octet-stream', @JsonKey(name: 'data_base64') this.dataBase64, @JsonKey(name: 'content_base64') this.contentBase64}): super._();
  factory _RawFileInputDto.fromJson(Map<String, dynamic> json) => _$RawFileInputDtoFromJson(json);

@override final  String filename;
@override@JsonKey(name: 'content_type') final  String contentType;
@override@JsonKey(name: 'data_base64') final  String? dataBase64;
@override@JsonKey(name: 'content_base64') final  String? contentBase64;

/// Create a copy of RawFileInputDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$RawFileInputDtoCopyWith<_RawFileInputDto> get copyWith => __$RawFileInputDtoCopyWithImpl<_RawFileInputDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$RawFileInputDtoToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _RawFileInputDto&&(identical(other.filename, filename) || other.filename == filename)&&(identical(other.contentType, contentType) || other.contentType == contentType)&&(identical(other.dataBase64, dataBase64) || other.dataBase64 == dataBase64)&&(identical(other.contentBase64, contentBase64) || other.contentBase64 == contentBase64));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,filename,contentType,dataBase64,contentBase64);

@override
String toString() {
  return 'RawFileInputDto(filename: $filename, contentType: $contentType, dataBase64: $dataBase64, contentBase64: $contentBase64)';
}


}

/// @nodoc
abstract mixin class _$RawFileInputDtoCopyWith<$Res> implements $RawFileInputDtoCopyWith<$Res> {
  factory _$RawFileInputDtoCopyWith(_RawFileInputDto value, $Res Function(_RawFileInputDto) _then) = __$RawFileInputDtoCopyWithImpl;
@override @useResult
$Res call({
 String filename,@JsonKey(name: 'content_type') String contentType,@JsonKey(name: 'data_base64') String? dataBase64,@JsonKey(name: 'content_base64') String? contentBase64
});




}
/// @nodoc
class __$RawFileInputDtoCopyWithImpl<$Res>
    implements _$RawFileInputDtoCopyWith<$Res> {
  __$RawFileInputDtoCopyWithImpl(this._self, this._then);

  final _RawFileInputDto _self;
  final $Res Function(_RawFileInputDto) _then;

/// Create a copy of RawFileInputDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? filename = null,Object? contentType = null,Object? dataBase64 = freezed,Object? contentBase64 = freezed,}) {
  return _then(_RawFileInputDto(
filename: null == filename ? _self.filename : filename // ignore: cast_nullable_to_non_nullable
as String,contentType: null == contentType ? _self.contentType : contentType // ignore: cast_nullable_to_non_nullable
as String,dataBase64: freezed == dataBase64 ? _self.dataBase64 : dataBase64 // ignore: cast_nullable_to_non_nullable
as String?,contentBase64: freezed == contentBase64 ? _self.contentBase64 : contentBase64 // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$WorkflowInputValue {

@JsonKey(name: 'text_value') String? get textValue;@JsonKey(name: 'file_value') RawFileInputDto? get fileValue;@JsonKey(name: 'questionnaire_value') Map<String, String>? get questionnaireValue;
/// Create a copy of WorkflowInputValue
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowInputValueCopyWith<WorkflowInputValue> get copyWith => _$WorkflowInputValueCopyWithImpl<WorkflowInputValue>(this as WorkflowInputValue, _$identity);

  /// Serializes this WorkflowInputValue to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is WorkflowInputValue&&(identical(other.textValue, textValue) || other.textValue == textValue)&&(identical(other.fileValue, fileValue) || other.fileValue == fileValue)&&const DeepCollectionEquality().equals(other.questionnaireValue, questionnaireValue));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,textValue,fileValue,const DeepCollectionEquality().hash(questionnaireValue));

@override
String toString() {
  return 'WorkflowInputValue(textValue: $textValue, fileValue: $fileValue, questionnaireValue: $questionnaireValue)';
}


}

/// @nodoc
abstract mixin class $WorkflowInputValueCopyWith<$Res>  {
  factory $WorkflowInputValueCopyWith(WorkflowInputValue value, $Res Function(WorkflowInputValue) _then) = _$WorkflowInputValueCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'text_value') String? textValue,@JsonKey(name: 'file_value') RawFileInputDto? fileValue,@JsonKey(name: 'questionnaire_value') Map<String, String>? questionnaireValue
});


$RawFileInputDtoCopyWith<$Res>? get fileValue;

}
/// @nodoc
class _$WorkflowInputValueCopyWithImpl<$Res>
    implements $WorkflowInputValueCopyWith<$Res> {
  _$WorkflowInputValueCopyWithImpl(this._self, this._then);

  final WorkflowInputValue _self;
  final $Res Function(WorkflowInputValue) _then;

/// Create a copy of WorkflowInputValue
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? textValue = freezed,Object? fileValue = freezed,Object? questionnaireValue = freezed,}) {
  return _then(_self.copyWith(
textValue: freezed == textValue ? _self.textValue : textValue // ignore: cast_nullable_to_non_nullable
as String?,fileValue: freezed == fileValue ? _self.fileValue : fileValue // ignore: cast_nullable_to_non_nullable
as RawFileInputDto?,questionnaireValue: freezed == questionnaireValue ? _self.questionnaireValue : questionnaireValue // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,
  ));
}
/// Create a copy of WorkflowInputValue
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RawFileInputDtoCopyWith<$Res>? get fileValue {
    if (_self.fileValue == null) {
    return null;
  }

  return $RawFileInputDtoCopyWith<$Res>(_self.fileValue!, (value) {
    return _then(_self.copyWith(fileValue: value));
  });
}
}


/// Adds pattern-matching-related methods to [WorkflowInputValue].
extension WorkflowInputValuePatterns on WorkflowInputValue {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WorkflowInputValue value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WorkflowInputValue() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WorkflowInputValue value)  $default,){
final _that = this;
switch (_that) {
case _WorkflowInputValue():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WorkflowInputValue value)?  $default,){
final _that = this;
switch (_that) {
case _WorkflowInputValue() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'text_value')  String? textValue, @JsonKey(name: 'file_value')  RawFileInputDto? fileValue, @JsonKey(name: 'questionnaire_value')  Map<String, String>? questionnaireValue)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WorkflowInputValue() when $default != null:
return $default(_that.textValue,_that.fileValue,_that.questionnaireValue);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'text_value')  String? textValue, @JsonKey(name: 'file_value')  RawFileInputDto? fileValue, @JsonKey(name: 'questionnaire_value')  Map<String, String>? questionnaireValue)  $default,) {final _that = this;
switch (_that) {
case _WorkflowInputValue():
return $default(_that.textValue,_that.fileValue,_that.questionnaireValue);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'text_value')  String? textValue, @JsonKey(name: 'file_value')  RawFileInputDto? fileValue, @JsonKey(name: 'questionnaire_value')  Map<String, String>? questionnaireValue)?  $default,) {final _that = this;
switch (_that) {
case _WorkflowInputValue() when $default != null:
return $default(_that.textValue,_that.fileValue,_that.questionnaireValue);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _WorkflowInputValue extends WorkflowInputValue {
  const _WorkflowInputValue({@JsonKey(name: 'text_value') this.textValue, @JsonKey(name: 'file_value') this.fileValue, @JsonKey(name: 'questionnaire_value') final  Map<String, String>? questionnaireValue}): _questionnaireValue = questionnaireValue,super._();
  factory _WorkflowInputValue.fromJson(Map<String, dynamic> json) => _$WorkflowInputValueFromJson(json);

@override@JsonKey(name: 'text_value') final  String? textValue;
@override@JsonKey(name: 'file_value') final  RawFileInputDto? fileValue;
 final  Map<String, String>? _questionnaireValue;
@override@JsonKey(name: 'questionnaire_value') Map<String, String>? get questionnaireValue {
  final value = _questionnaireValue;
  if (value == null) return null;
  if (_questionnaireValue is EqualUnmodifiableMapView) return _questionnaireValue;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}


/// Create a copy of WorkflowInputValue
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WorkflowInputValueCopyWith<_WorkflowInputValue> get copyWith => __$WorkflowInputValueCopyWithImpl<_WorkflowInputValue>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$WorkflowInputValueToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _WorkflowInputValue&&(identical(other.textValue, textValue) || other.textValue == textValue)&&(identical(other.fileValue, fileValue) || other.fileValue == fileValue)&&const DeepCollectionEquality().equals(other._questionnaireValue, _questionnaireValue));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,textValue,fileValue,const DeepCollectionEquality().hash(_questionnaireValue));

@override
String toString() {
  return 'WorkflowInputValue(textValue: $textValue, fileValue: $fileValue, questionnaireValue: $questionnaireValue)';
}


}

/// @nodoc
abstract mixin class _$WorkflowInputValueCopyWith<$Res> implements $WorkflowInputValueCopyWith<$Res> {
  factory _$WorkflowInputValueCopyWith(_WorkflowInputValue value, $Res Function(_WorkflowInputValue) _then) = __$WorkflowInputValueCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'text_value') String? textValue,@JsonKey(name: 'file_value') RawFileInputDto? fileValue,@JsonKey(name: 'questionnaire_value') Map<String, String>? questionnaireValue
});


@override $RawFileInputDtoCopyWith<$Res>? get fileValue;

}
/// @nodoc
class __$WorkflowInputValueCopyWithImpl<$Res>
    implements _$WorkflowInputValueCopyWith<$Res> {
  __$WorkflowInputValueCopyWithImpl(this._self, this._then);

  final _WorkflowInputValue _self;
  final $Res Function(_WorkflowInputValue) _then;

/// Create a copy of WorkflowInputValue
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? textValue = freezed,Object? fileValue = freezed,Object? questionnaireValue = freezed,}) {
  return _then(_WorkflowInputValue(
textValue: freezed == textValue ? _self.textValue : textValue // ignore: cast_nullable_to_non_nullable
as String?,fileValue: freezed == fileValue ? _self.fileValue : fileValue // ignore: cast_nullable_to_non_nullable
as RawFileInputDto?,questionnaireValue: freezed == questionnaireValue ? _self._questionnaireValue : questionnaireValue // ignore: cast_nullable_to_non_nullable
as Map<String, String>?,
  ));
}

/// Create a copy of WorkflowInputValue
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$RawFileInputDtoCopyWith<$Res>? get fileValue {
    if (_self.fileValue == null) {
    return null;
  }

  return $RawFileInputDtoCopyWith<$Res>(_self.fileValue!, (value) {
    return _then(_self.copyWith(fileValue: value));
  });
}
}


/// @nodoc
mixin _$WorkflowInputs {

@JsonKey(name: 'organization_id') String? get organizationId;@JsonKey(name: 'user_id') String? get userId;@JsonKey(name: 'simulation_mode') bool get simulationMode; String get language;@JsonKey(name: 'dynamic_inputs')@WorkflowInputValueConverter() Map<String, WorkflowInputValue> get dynamicInputs;
/// Create a copy of WorkflowInputs
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$WorkflowInputsCopyWith<WorkflowInputs> get copyWith => _$WorkflowInputsCopyWithImpl<WorkflowInputs>(this as WorkflowInputs, _$identity);

  /// Serializes this WorkflowInputs to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'WorkflowInputs(organizationId: $organizationId, userId: $userId, simulationMode: $simulationMode, language: $language, dynamicInputs: $dynamicInputs)';
}


}

/// @nodoc
abstract mixin class $WorkflowInputsCopyWith<$Res>  {
  factory $WorkflowInputsCopyWith(WorkflowInputs value, $Res Function(WorkflowInputs) _then) = _$WorkflowInputsCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId,@JsonKey(name: 'simulation_mode') bool simulationMode, String language,@JsonKey(name: 'dynamic_inputs')@WorkflowInputValueConverter() Map<String, WorkflowInputValue> dynamicInputs
});




}
/// @nodoc
class _$WorkflowInputsCopyWithImpl<$Res>
    implements $WorkflowInputsCopyWith<$Res> {
  _$WorkflowInputsCopyWithImpl(this._self, this._then);

  final WorkflowInputs _self;
  final $Res Function(WorkflowInputs) _then;

/// Create a copy of WorkflowInputs
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? organizationId = freezed,Object? userId = freezed,Object? simulationMode = null,Object? language = null,Object? dynamicInputs = null,}) {
  return _then(_self.copyWith(
organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,simulationMode: null == simulationMode ? _self.simulationMode : simulationMode // ignore: cast_nullable_to_non_nullable
as bool,language: null == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String,dynamicInputs: null == dynamicInputs ? _self.dynamicInputs : dynamicInputs // ignore: cast_nullable_to_non_nullable
as Map<String, WorkflowInputValue>,
  ));
}

}


/// Adds pattern-matching-related methods to [WorkflowInputs].
extension WorkflowInputsPatterns on WorkflowInputs {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _WorkflowInputs value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _WorkflowInputs() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _WorkflowInputs value)  $default,){
final _that = this;
switch (_that) {
case _WorkflowInputs():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _WorkflowInputs value)?  $default,){
final _that = this;
switch (_that) {
case _WorkflowInputs() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'simulation_mode')  bool simulationMode,  String language, @JsonKey(name: 'dynamic_inputs')@WorkflowInputValueConverter()  Map<String, WorkflowInputValue> dynamicInputs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _WorkflowInputs() when $default != null:
return $default(_that.organizationId,_that.userId,_that.simulationMode,_that.language,_that.dynamicInputs);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'simulation_mode')  bool simulationMode,  String language, @JsonKey(name: 'dynamic_inputs')@WorkflowInputValueConverter()  Map<String, WorkflowInputValue> dynamicInputs)  $default,) {final _that = this;
switch (_that) {
case _WorkflowInputs():
return $default(_that.organizationId,_that.userId,_that.simulationMode,_that.language,_that.dynamicInputs);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'organization_id')  String? organizationId, @JsonKey(name: 'user_id')  String? userId, @JsonKey(name: 'simulation_mode')  bool simulationMode,  String language, @JsonKey(name: 'dynamic_inputs')@WorkflowInputValueConverter()  Map<String, WorkflowInputValue> dynamicInputs)?  $default,) {final _that = this;
switch (_that) {
case _WorkflowInputs() when $default != null:
return $default(_that.organizationId,_that.userId,_that.simulationMode,_that.language,_that.dynamicInputs);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
class _WorkflowInputs extends WorkflowInputs {
  const _WorkflowInputs({@JsonKey(name: 'organization_id') this.organizationId, @JsonKey(name: 'user_id') this.userId, @JsonKey(name: 'simulation_mode') this.simulationMode = false, this.language = 'en', @JsonKey(name: 'dynamic_inputs')@WorkflowInputValueConverter() final  Map<String, WorkflowInputValue> dynamicInputs = const <String, WorkflowInputValue>{}}): _dynamicInputs = dynamicInputs,super._();
  factory _WorkflowInputs.fromJson(Map<String, dynamic> json) => _$WorkflowInputsFromJson(json);

@override@JsonKey(name: 'organization_id') final  String? organizationId;
@override@JsonKey(name: 'user_id') final  String? userId;
@override@JsonKey(name: 'simulation_mode') final  bool simulationMode;
@override@JsonKey() final  String language;
 final  Map<String, WorkflowInputValue> _dynamicInputs;
@override@JsonKey(name: 'dynamic_inputs')@WorkflowInputValueConverter() Map<String, WorkflowInputValue> get dynamicInputs {
  if (_dynamicInputs is EqualUnmodifiableMapView) return _dynamicInputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_dynamicInputs);
}


/// Create a copy of WorkflowInputs
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$WorkflowInputsCopyWith<_WorkflowInputs> get copyWith => __$WorkflowInputsCopyWithImpl<_WorkflowInputs>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$WorkflowInputsToJson(this, );
}



@override
String toString() {
  return 'WorkflowInputs(organizationId: $organizationId, userId: $userId, simulationMode: $simulationMode, language: $language, dynamicInputs: $dynamicInputs)';
}


}

/// @nodoc
abstract mixin class _$WorkflowInputsCopyWith<$Res> implements $WorkflowInputsCopyWith<$Res> {
  factory _$WorkflowInputsCopyWith(_WorkflowInputs value, $Res Function(_WorkflowInputs) _then) = __$WorkflowInputsCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'organization_id') String? organizationId,@JsonKey(name: 'user_id') String? userId,@JsonKey(name: 'simulation_mode') bool simulationMode, String language,@JsonKey(name: 'dynamic_inputs')@WorkflowInputValueConverter() Map<String, WorkflowInputValue> dynamicInputs
});




}
/// @nodoc
class __$WorkflowInputsCopyWithImpl<$Res>
    implements _$WorkflowInputsCopyWith<$Res> {
  __$WorkflowInputsCopyWithImpl(this._self, this._then);

  final _WorkflowInputs _self;
  final $Res Function(_WorkflowInputs) _then;

/// Create a copy of WorkflowInputs
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? organizationId = freezed,Object? userId = freezed,Object? simulationMode = null,Object? language = null,Object? dynamicInputs = null,}) {
  return _then(_WorkflowInputs(
organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,userId: freezed == userId ? _self.userId : userId // ignore: cast_nullable_to_non_nullable
as String?,simulationMode: null == simulationMode ? _self.simulationMode : simulationMode // ignore: cast_nullable_to_non_nullable
as bool,language: null == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String,dynamicInputs: null == dynamicInputs ? _self._dynamicInputs : dynamicInputs // ignore: cast_nullable_to_non_nullable
as Map<String, WorkflowInputValue>,
  ));
}


}

// dart format on
