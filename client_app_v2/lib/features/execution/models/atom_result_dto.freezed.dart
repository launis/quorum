// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'atom_result_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ExtractedValueDTO {

 dynamic get value; String? get unit;
/// Create a copy of ExtractedValueDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ExtractedValueDTOCopyWith<ExtractedValueDTO> get copyWith => _$ExtractedValueDTOCopyWithImpl<ExtractedValueDTO>(this as ExtractedValueDTO, _$identity);

  /// Serializes this ExtractedValueDTO to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ExtractedValueDTO&&const DeepCollectionEquality().equals(other.value, value)&&(identical(other.unit, unit) || other.unit == unit));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(value),unit);

@override
String toString() {
  return 'ExtractedValueDTO(value: $value, unit: $unit)';
}


}

/// @nodoc
abstract mixin class $ExtractedValueDTOCopyWith<$Res>  {
  factory $ExtractedValueDTOCopyWith(ExtractedValueDTO value, $Res Function(ExtractedValueDTO) _then) = _$ExtractedValueDTOCopyWithImpl;
@useResult
$Res call({
 dynamic value, String? unit
});




}
/// @nodoc
class _$ExtractedValueDTOCopyWithImpl<$Res>
    implements $ExtractedValueDTOCopyWith<$Res> {
  _$ExtractedValueDTOCopyWithImpl(this._self, this._then);

  final ExtractedValueDTO _self;
  final $Res Function(ExtractedValueDTO) _then;

/// Create a copy of ExtractedValueDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? value = freezed,Object? unit = freezed,}) {
  return _then(_self.copyWith(
value: freezed == value ? _self.value : value // ignore: cast_nullable_to_non_nullable
as dynamic,unit: freezed == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ExtractedValueDTO].
extension ExtractedValueDTOPatterns on ExtractedValueDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ExtractedValueDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ExtractedValueDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ExtractedValueDTO value)  $default,){
final _that = this;
switch (_that) {
case _ExtractedValueDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ExtractedValueDTO value)?  $default,){
final _that = this;
switch (_that) {
case _ExtractedValueDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( dynamic value,  String? unit)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ExtractedValueDTO() when $default != null:
return $default(_that.value,_that.unit);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( dynamic value,  String? unit)  $default,) {final _that = this;
switch (_that) {
case _ExtractedValueDTO():
return $default(_that.value,_that.unit);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( dynamic value,  String? unit)?  $default,) {final _that = this;
switch (_that) {
case _ExtractedValueDTO() when $default != null:
return $default(_that.value,_that.unit);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ExtractedValueDTO implements ExtractedValueDTO {
  const _ExtractedValueDTO({required this.value, this.unit});
  factory _ExtractedValueDTO.fromJson(Map<String, dynamic> json) => _$ExtractedValueDTOFromJson(json);

@override final  dynamic value;
@override final  String? unit;

/// Create a copy of ExtractedValueDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ExtractedValueDTOCopyWith<_ExtractedValueDTO> get copyWith => __$ExtractedValueDTOCopyWithImpl<_ExtractedValueDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ExtractedValueDTOToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ExtractedValueDTO&&const DeepCollectionEquality().equals(other.value, value)&&(identical(other.unit, unit) || other.unit == unit));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,const DeepCollectionEquality().hash(value),unit);

@override
String toString() {
  return 'ExtractedValueDTO(value: $value, unit: $unit)';
}


}

/// @nodoc
abstract mixin class _$ExtractedValueDTOCopyWith<$Res> implements $ExtractedValueDTOCopyWith<$Res> {
  factory _$ExtractedValueDTOCopyWith(_ExtractedValueDTO value, $Res Function(_ExtractedValueDTO) _then) = __$ExtractedValueDTOCopyWithImpl;
@override @useResult
$Res call({
 dynamic value, String? unit
});




}
/// @nodoc
class __$ExtractedValueDTOCopyWithImpl<$Res>
    implements _$ExtractedValueDTOCopyWith<$Res> {
  __$ExtractedValueDTOCopyWithImpl(this._self, this._then);

  final _ExtractedValueDTO _self;
  final $Res Function(_ExtractedValueDTO) _then;

/// Create a copy of ExtractedValueDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? value = freezed,Object? unit = freezed,}) {
  return _then(_ExtractedValueDTO(
value: freezed == value ? _self.value : value // ignore: cast_nullable_to_non_nullable
as dynamic,unit: freezed == unit ? _self.unit : unit // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$ErrorDetailsDTO {

@JsonKey(name: 'error_code') String get errorCode; String get message;
/// Create a copy of ErrorDetailsDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ErrorDetailsDTOCopyWith<ErrorDetailsDTO> get copyWith => _$ErrorDetailsDTOCopyWithImpl<ErrorDetailsDTO>(this as ErrorDetailsDTO, _$identity);

  /// Serializes this ErrorDetailsDTO to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ErrorDetailsDTO&&(identical(other.errorCode, errorCode) || other.errorCode == errorCode)&&(identical(other.message, message) || other.message == message));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,errorCode,message);

@override
String toString() {
  return 'ErrorDetailsDTO(errorCode: $errorCode, message: $message)';
}


}

/// @nodoc
abstract mixin class $ErrorDetailsDTOCopyWith<$Res>  {
  factory $ErrorDetailsDTOCopyWith(ErrorDetailsDTO value, $Res Function(ErrorDetailsDTO) _then) = _$ErrorDetailsDTOCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'error_code') String errorCode, String message
});




}
/// @nodoc
class _$ErrorDetailsDTOCopyWithImpl<$Res>
    implements $ErrorDetailsDTOCopyWith<$Res> {
  _$ErrorDetailsDTOCopyWithImpl(this._self, this._then);

  final ErrorDetailsDTO _self;
  final $Res Function(ErrorDetailsDTO) _then;

/// Create a copy of ErrorDetailsDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? errorCode = null,Object? message = null,}) {
  return _then(_self.copyWith(
errorCode: null == errorCode ? _self.errorCode : errorCode // ignore: cast_nullable_to_non_nullable
as String,message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [ErrorDetailsDTO].
extension ErrorDetailsDTOPatterns on ErrorDetailsDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ErrorDetailsDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ErrorDetailsDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ErrorDetailsDTO value)  $default,){
final _that = this;
switch (_that) {
case _ErrorDetailsDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ErrorDetailsDTO value)?  $default,){
final _that = this;
switch (_that) {
case _ErrorDetailsDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'error_code')  String errorCode,  String message)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ErrorDetailsDTO() when $default != null:
return $default(_that.errorCode,_that.message);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'error_code')  String errorCode,  String message)  $default,) {final _that = this;
switch (_that) {
case _ErrorDetailsDTO():
return $default(_that.errorCode,_that.message);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'error_code')  String errorCode,  String message)?  $default,) {final _that = this;
switch (_that) {
case _ErrorDetailsDTO() when $default != null:
return $default(_that.errorCode,_that.message);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ErrorDetailsDTO implements ErrorDetailsDTO {
  const _ErrorDetailsDTO({@JsonKey(name: 'error_code') required this.errorCode, required this.message});
  factory _ErrorDetailsDTO.fromJson(Map<String, dynamic> json) => _$ErrorDetailsDTOFromJson(json);

@override@JsonKey(name: 'error_code') final  String errorCode;
@override final  String message;

/// Create a copy of ErrorDetailsDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ErrorDetailsDTOCopyWith<_ErrorDetailsDTO> get copyWith => __$ErrorDetailsDTOCopyWithImpl<_ErrorDetailsDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ErrorDetailsDTOToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ErrorDetailsDTO&&(identical(other.errorCode, errorCode) || other.errorCode == errorCode)&&(identical(other.message, message) || other.message == message));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,errorCode,message);

@override
String toString() {
  return 'ErrorDetailsDTO(errorCode: $errorCode, message: $message)';
}


}

/// @nodoc
abstract mixin class _$ErrorDetailsDTOCopyWith<$Res> implements $ErrorDetailsDTOCopyWith<$Res> {
  factory _$ErrorDetailsDTOCopyWith(_ErrorDetailsDTO value, $Res Function(_ErrorDetailsDTO) _then) = __$ErrorDetailsDTOCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'error_code') String errorCode, String message
});




}
/// @nodoc
class __$ErrorDetailsDTOCopyWithImpl<$Res>
    implements _$ErrorDetailsDTOCopyWith<$Res> {
  __$ErrorDetailsDTOCopyWithImpl(this._self, this._then);

  final _ErrorDetailsDTO _self;
  final $Res Function(_ErrorDetailsDTO) _then;

/// Create a copy of ErrorDetailsDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? errorCode = null,Object? message = null,}) {
  return _then(_ErrorDetailsDTO(
errorCode: null == errorCode ? _self.errorCode : errorCode // ignore: cast_nullable_to_non_nullable
as String,message: null == message ? _self.message : message // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$AtomResultDTO {

@JsonKey(name: 'tda_id') String get tdaId;@JsonKey(name: 'matrix_id') String? get matrixId; ExecutionStatus get status;@JsonKey(name: 'extracted_data') ExtractedValueDTO? get extractedData;@JsonKey(name: 'source_quote') String? get sourceQuote;@JsonKey(name: 'contextual_override') bool get contextualOverride;@JsonKey(name: 'evaluation_reasoning') String? get evaluationReasoning;@JsonKey(name: 'error_details') ErrorDetailsDTO? get errorDetails;@JsonKey(name: 'extensions') Map<String, String> get extensions;@JsonKey(name: 'depends_on_tda_ids') List<String> get dependsOnTdaIds;@JsonKey(name: 'short_circuit_reason_tda_ids') List<String> get shortCircuitReasonTdaIds;
/// Create a copy of AtomResultDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AtomResultDTOCopyWith<AtomResultDTO> get copyWith => _$AtomResultDTOCopyWithImpl<AtomResultDTO>(this as AtomResultDTO, _$identity);

  /// Serializes this AtomResultDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'AtomResultDTO(tdaId: $tdaId, matrixId: $matrixId, status: $status, extractedData: $extractedData, sourceQuote: $sourceQuote, contextualOverride: $contextualOverride, evaluationReasoning: $evaluationReasoning, errorDetails: $errorDetails, extensions: $extensions, dependsOnTdaIds: $dependsOnTdaIds, shortCircuitReasonTdaIds: $shortCircuitReasonTdaIds)';
}


}

/// @nodoc
abstract mixin class $AtomResultDTOCopyWith<$Res>  {
  factory $AtomResultDTOCopyWith(AtomResultDTO value, $Res Function(AtomResultDTO) _then) = _$AtomResultDTOCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'tda_id') String tdaId,@JsonKey(name: 'matrix_id') String? matrixId, ExecutionStatus status,@JsonKey(name: 'extracted_data') ExtractedValueDTO? extractedData,@JsonKey(name: 'source_quote') String? sourceQuote,@JsonKey(name: 'contextual_override') bool contextualOverride,@JsonKey(name: 'evaluation_reasoning') String? evaluationReasoning,@JsonKey(name: 'error_details') ErrorDetailsDTO? errorDetails,@JsonKey(name: 'extensions') Map<String, String> extensions,@JsonKey(name: 'depends_on_tda_ids') List<String> dependsOnTdaIds,@JsonKey(name: 'short_circuit_reason_tda_ids') List<String> shortCircuitReasonTdaIds
});


$ExtractedValueDTOCopyWith<$Res>? get extractedData;$ErrorDetailsDTOCopyWith<$Res>? get errorDetails;

}
/// @nodoc
class _$AtomResultDTOCopyWithImpl<$Res>
    implements $AtomResultDTOCopyWith<$Res> {
  _$AtomResultDTOCopyWithImpl(this._self, this._then);

  final AtomResultDTO _self;
  final $Res Function(AtomResultDTO) _then;

/// Create a copy of AtomResultDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? tdaId = null,Object? matrixId = freezed,Object? status = null,Object? extractedData = freezed,Object? sourceQuote = freezed,Object? contextualOverride = null,Object? evaluationReasoning = freezed,Object? errorDetails = freezed,Object? extensions = null,Object? dependsOnTdaIds = null,Object? shortCircuitReasonTdaIds = null,}) {
  return _then(_self.copyWith(
tdaId: null == tdaId ? _self.tdaId : tdaId // ignore: cast_nullable_to_non_nullable
as String,matrixId: freezed == matrixId ? _self.matrixId : matrixId // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,extractedData: freezed == extractedData ? _self.extractedData : extractedData // ignore: cast_nullable_to_non_nullable
as ExtractedValueDTO?,sourceQuote: freezed == sourceQuote ? _self.sourceQuote : sourceQuote // ignore: cast_nullable_to_non_nullable
as String?,contextualOverride: null == contextualOverride ? _self.contextualOverride : contextualOverride // ignore: cast_nullable_to_non_nullable
as bool,evaluationReasoning: freezed == evaluationReasoning ? _self.evaluationReasoning : evaluationReasoning // ignore: cast_nullable_to_non_nullable
as String?,errorDetails: freezed == errorDetails ? _self.errorDetails : errorDetails // ignore: cast_nullable_to_non_nullable
as ErrorDetailsDTO?,extensions: null == extensions ? _self.extensions : extensions // ignore: cast_nullable_to_non_nullable
as Map<String, String>,dependsOnTdaIds: null == dependsOnTdaIds ? _self.dependsOnTdaIds : dependsOnTdaIds // ignore: cast_nullable_to_non_nullable
as List<String>,shortCircuitReasonTdaIds: null == shortCircuitReasonTdaIds ? _self.shortCircuitReasonTdaIds : shortCircuitReasonTdaIds // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}
/// Create a copy of AtomResultDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ExtractedValueDTOCopyWith<$Res>? get extractedData {
    if (_self.extractedData == null) {
    return null;
  }

  return $ExtractedValueDTOCopyWith<$Res>(_self.extractedData!, (value) {
    return _then(_self.copyWith(extractedData: value));
  });
}/// Create a copy of AtomResultDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ErrorDetailsDTOCopyWith<$Res>? get errorDetails {
    if (_self.errorDetails == null) {
    return null;
  }

  return $ErrorDetailsDTOCopyWith<$Res>(_self.errorDetails!, (value) {
    return _then(_self.copyWith(errorDetails: value));
  });
}
}


/// Adds pattern-matching-related methods to [AtomResultDTO].
extension AtomResultDTOPatterns on AtomResultDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AtomResultDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AtomResultDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AtomResultDTO value)  $default,){
final _that = this;
switch (_that) {
case _AtomResultDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AtomResultDTO value)?  $default,){
final _that = this;
switch (_that) {
case _AtomResultDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'tda_id')  String tdaId, @JsonKey(name: 'matrix_id')  String? matrixId,  ExecutionStatus status, @JsonKey(name: 'extracted_data')  ExtractedValueDTO? extractedData, @JsonKey(name: 'source_quote')  String? sourceQuote, @JsonKey(name: 'contextual_override')  bool contextualOverride, @JsonKey(name: 'evaluation_reasoning')  String? evaluationReasoning, @JsonKey(name: 'error_details')  ErrorDetailsDTO? errorDetails, @JsonKey(name: 'extensions')  Map<String, String> extensions, @JsonKey(name: 'depends_on_tda_ids')  List<String> dependsOnTdaIds, @JsonKey(name: 'short_circuit_reason_tda_ids')  List<String> shortCircuitReasonTdaIds)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AtomResultDTO() when $default != null:
return $default(_that.tdaId,_that.matrixId,_that.status,_that.extractedData,_that.sourceQuote,_that.contextualOverride,_that.evaluationReasoning,_that.errorDetails,_that.extensions,_that.dependsOnTdaIds,_that.shortCircuitReasonTdaIds);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'tda_id')  String tdaId, @JsonKey(name: 'matrix_id')  String? matrixId,  ExecutionStatus status, @JsonKey(name: 'extracted_data')  ExtractedValueDTO? extractedData, @JsonKey(name: 'source_quote')  String? sourceQuote, @JsonKey(name: 'contextual_override')  bool contextualOverride, @JsonKey(name: 'evaluation_reasoning')  String? evaluationReasoning, @JsonKey(name: 'error_details')  ErrorDetailsDTO? errorDetails, @JsonKey(name: 'extensions')  Map<String, String> extensions, @JsonKey(name: 'depends_on_tda_ids')  List<String> dependsOnTdaIds, @JsonKey(name: 'short_circuit_reason_tda_ids')  List<String> shortCircuitReasonTdaIds)  $default,) {final _that = this;
switch (_that) {
case _AtomResultDTO():
return $default(_that.tdaId,_that.matrixId,_that.status,_that.extractedData,_that.sourceQuote,_that.contextualOverride,_that.evaluationReasoning,_that.errorDetails,_that.extensions,_that.dependsOnTdaIds,_that.shortCircuitReasonTdaIds);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'tda_id')  String tdaId, @JsonKey(name: 'matrix_id')  String? matrixId,  ExecutionStatus status, @JsonKey(name: 'extracted_data')  ExtractedValueDTO? extractedData, @JsonKey(name: 'source_quote')  String? sourceQuote, @JsonKey(name: 'contextual_override')  bool contextualOverride, @JsonKey(name: 'evaluation_reasoning')  String? evaluationReasoning, @JsonKey(name: 'error_details')  ErrorDetailsDTO? errorDetails, @JsonKey(name: 'extensions')  Map<String, String> extensions, @JsonKey(name: 'depends_on_tda_ids')  List<String> dependsOnTdaIds, @JsonKey(name: 'short_circuit_reason_tda_ids')  List<String> shortCircuitReasonTdaIds)?  $default,) {final _that = this;
switch (_that) {
case _AtomResultDTO() when $default != null:
return $default(_that.tdaId,_that.matrixId,_that.status,_that.extractedData,_that.sourceQuote,_that.contextualOverride,_that.evaluationReasoning,_that.errorDetails,_that.extensions,_that.dependsOnTdaIds,_that.shortCircuitReasonTdaIds);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _AtomResultDTO implements AtomResultDTO {
  const _AtomResultDTO({@JsonKey(name: 'tda_id') required this.tdaId, @JsonKey(name: 'matrix_id') this.matrixId, required this.status, @JsonKey(name: 'extracted_data') this.extractedData, @JsonKey(name: 'source_quote') this.sourceQuote, @JsonKey(name: 'contextual_override') this.contextualOverride = false, @JsonKey(name: 'evaluation_reasoning') this.evaluationReasoning, @JsonKey(name: 'error_details') this.errorDetails, @JsonKey(name: 'extensions') final  Map<String, String> extensions = const {}, @JsonKey(name: 'depends_on_tda_ids') final  List<String> dependsOnTdaIds = const [], @JsonKey(name: 'short_circuit_reason_tda_ids') final  List<String> shortCircuitReasonTdaIds = const []}): _extensions = extensions,_dependsOnTdaIds = dependsOnTdaIds,_shortCircuitReasonTdaIds = shortCircuitReasonTdaIds;
  factory _AtomResultDTO.fromJson(Map<String, dynamic> json) => _$AtomResultDTOFromJson(json);

@override@JsonKey(name: 'tda_id') final  String tdaId;
@override@JsonKey(name: 'matrix_id') final  String? matrixId;
@override final  ExecutionStatus status;
@override@JsonKey(name: 'extracted_data') final  ExtractedValueDTO? extractedData;
@override@JsonKey(name: 'source_quote') final  String? sourceQuote;
@override@JsonKey(name: 'contextual_override') final  bool contextualOverride;
@override@JsonKey(name: 'evaluation_reasoning') final  String? evaluationReasoning;
@override@JsonKey(name: 'error_details') final  ErrorDetailsDTO? errorDetails;
 final  Map<String, String> _extensions;
@override@JsonKey(name: 'extensions') Map<String, String> get extensions {
  if (_extensions is EqualUnmodifiableMapView) return _extensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_extensions);
}

 final  List<String> _dependsOnTdaIds;
@override@JsonKey(name: 'depends_on_tda_ids') List<String> get dependsOnTdaIds {
  if (_dependsOnTdaIds is EqualUnmodifiableListView) return _dependsOnTdaIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_dependsOnTdaIds);
}

 final  List<String> _shortCircuitReasonTdaIds;
@override@JsonKey(name: 'short_circuit_reason_tda_ids') List<String> get shortCircuitReasonTdaIds {
  if (_shortCircuitReasonTdaIds is EqualUnmodifiableListView) return _shortCircuitReasonTdaIds;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_shortCircuitReasonTdaIds);
}


/// Create a copy of AtomResultDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AtomResultDTOCopyWith<_AtomResultDTO> get copyWith => __$AtomResultDTOCopyWithImpl<_AtomResultDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AtomResultDTOToJson(this, );
}



@override
String toString() {
  return 'AtomResultDTO(tdaId: $tdaId, matrixId: $matrixId, status: $status, extractedData: $extractedData, sourceQuote: $sourceQuote, contextualOverride: $contextualOverride, evaluationReasoning: $evaluationReasoning, errorDetails: $errorDetails, extensions: $extensions, dependsOnTdaIds: $dependsOnTdaIds, shortCircuitReasonTdaIds: $shortCircuitReasonTdaIds)';
}


}

/// @nodoc
abstract mixin class _$AtomResultDTOCopyWith<$Res> implements $AtomResultDTOCopyWith<$Res> {
  factory _$AtomResultDTOCopyWith(_AtomResultDTO value, $Res Function(_AtomResultDTO) _then) = __$AtomResultDTOCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'tda_id') String tdaId,@JsonKey(name: 'matrix_id') String? matrixId, ExecutionStatus status,@JsonKey(name: 'extracted_data') ExtractedValueDTO? extractedData,@JsonKey(name: 'source_quote') String? sourceQuote,@JsonKey(name: 'contextual_override') bool contextualOverride,@JsonKey(name: 'evaluation_reasoning') String? evaluationReasoning,@JsonKey(name: 'error_details') ErrorDetailsDTO? errorDetails,@JsonKey(name: 'extensions') Map<String, String> extensions,@JsonKey(name: 'depends_on_tda_ids') List<String> dependsOnTdaIds,@JsonKey(name: 'short_circuit_reason_tda_ids') List<String> shortCircuitReasonTdaIds
});


@override $ExtractedValueDTOCopyWith<$Res>? get extractedData;@override $ErrorDetailsDTOCopyWith<$Res>? get errorDetails;

}
/// @nodoc
class __$AtomResultDTOCopyWithImpl<$Res>
    implements _$AtomResultDTOCopyWith<$Res> {
  __$AtomResultDTOCopyWithImpl(this._self, this._then);

  final _AtomResultDTO _self;
  final $Res Function(_AtomResultDTO) _then;

/// Create a copy of AtomResultDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? tdaId = null,Object? matrixId = freezed,Object? status = null,Object? extractedData = freezed,Object? sourceQuote = freezed,Object? contextualOverride = null,Object? evaluationReasoning = freezed,Object? errorDetails = freezed,Object? extensions = null,Object? dependsOnTdaIds = null,Object? shortCircuitReasonTdaIds = null,}) {
  return _then(_AtomResultDTO(
tdaId: null == tdaId ? _self.tdaId : tdaId // ignore: cast_nullable_to_non_nullable
as String,matrixId: freezed == matrixId ? _self.matrixId : matrixId // ignore: cast_nullable_to_non_nullable
as String?,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ExecutionStatus,extractedData: freezed == extractedData ? _self.extractedData : extractedData // ignore: cast_nullable_to_non_nullable
as ExtractedValueDTO?,sourceQuote: freezed == sourceQuote ? _self.sourceQuote : sourceQuote // ignore: cast_nullable_to_non_nullable
as String?,contextualOverride: null == contextualOverride ? _self.contextualOverride : contextualOverride // ignore: cast_nullable_to_non_nullable
as bool,evaluationReasoning: freezed == evaluationReasoning ? _self.evaluationReasoning : evaluationReasoning // ignore: cast_nullable_to_non_nullable
as String?,errorDetails: freezed == errorDetails ? _self.errorDetails : errorDetails // ignore: cast_nullable_to_non_nullable
as ErrorDetailsDTO?,extensions: null == extensions ? _self._extensions : extensions // ignore: cast_nullable_to_non_nullable
as Map<String, String>,dependsOnTdaIds: null == dependsOnTdaIds ? _self._dependsOnTdaIds : dependsOnTdaIds // ignore: cast_nullable_to_non_nullable
as List<String>,shortCircuitReasonTdaIds: null == shortCircuitReasonTdaIds ? _self._shortCircuitReasonTdaIds : shortCircuitReasonTdaIds // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

/// Create a copy of AtomResultDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ExtractedValueDTOCopyWith<$Res>? get extractedData {
    if (_self.extractedData == null) {
    return null;
  }

  return $ExtractedValueDTOCopyWith<$Res>(_self.extractedData!, (value) {
    return _then(_self.copyWith(extractedData: value));
  });
}/// Create a copy of AtomResultDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ErrorDetailsDTOCopyWith<$Res>? get errorDetails {
    if (_self.errorDetails == null) {
    return null;
  }

  return $ErrorDetailsDTOCopyWith<$Res>(_self.errorDetails!, (value) {
    return _then(_self.copyWith(errorDetails: value));
  });
}
}

// dart format on
