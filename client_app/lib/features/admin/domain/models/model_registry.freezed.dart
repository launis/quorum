// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'model_registry.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$LLMProviderConfig {

 String get id; String get provider;@JsonKey(name: 'model_name') String get modelName;@JsonKey(name: 'api_key') String? get apiKey;@JsonKey(name: 'base_url') String? get baseUrl; double get temperature;@JsonKey(name: 'additional_params') Map<String, dynamic> get additionalParams;
/// Create a copy of LLMProviderConfig
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LLMProviderConfigCopyWith<LLMProviderConfig> get copyWith => _$LLMProviderConfigCopyWithImpl<LLMProviderConfig>(this as LLMProviderConfig, _$identity);

  /// Serializes this LLMProviderConfig to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LLMProviderConfig&&(identical(other.id, id) || other.id == id)&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.modelName, modelName) || other.modelName == modelName)&&(identical(other.apiKey, apiKey) || other.apiKey == apiKey)&&(identical(other.baseUrl, baseUrl) || other.baseUrl == baseUrl)&&(identical(other.temperature, temperature) || other.temperature == temperature)&&const DeepCollectionEquality().equals(other.additionalParams, additionalParams));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,provider,modelName,apiKey,baseUrl,temperature,const DeepCollectionEquality().hash(additionalParams));

@override
String toString() {
  return 'LLMProviderConfig(id: $id, provider: $provider, modelName: $modelName, apiKey: $apiKey, baseUrl: $baseUrl, temperature: $temperature, additionalParams: $additionalParams)';
}


}

/// @nodoc
abstract mixin class $LLMProviderConfigCopyWith<$Res>  {
  factory $LLMProviderConfigCopyWith(LLMProviderConfig value, $Res Function(LLMProviderConfig) _then) = _$LLMProviderConfigCopyWithImpl;
@useResult
$Res call({
 String id, String provider,@JsonKey(name: 'model_name') String modelName,@JsonKey(name: 'api_key') String? apiKey,@JsonKey(name: 'base_url') String? baseUrl, double temperature,@JsonKey(name: 'additional_params') Map<String, dynamic> additionalParams
});




}
/// @nodoc
class _$LLMProviderConfigCopyWithImpl<$Res>
    implements $LLMProviderConfigCopyWith<$Res> {
  _$LLMProviderConfigCopyWithImpl(this._self, this._then);

  final LLMProviderConfig _self;
  final $Res Function(LLMProviderConfig) _then;

/// Create a copy of LLMProviderConfig
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? provider = null,Object? modelName = null,Object? apiKey = freezed,Object? baseUrl = freezed,Object? temperature = null,Object? additionalParams = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,modelName: null == modelName ? _self.modelName : modelName // ignore: cast_nullable_to_non_nullable
as String,apiKey: freezed == apiKey ? _self.apiKey : apiKey // ignore: cast_nullable_to_non_nullable
as String?,baseUrl: freezed == baseUrl ? _self.baseUrl : baseUrl // ignore: cast_nullable_to_non_nullable
as String?,temperature: null == temperature ? _self.temperature : temperature // ignore: cast_nullable_to_non_nullable
as double,additionalParams: null == additionalParams ? _self.additionalParams : additionalParams // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [LLMProviderConfig].
extension LLMProviderConfigPatterns on LLMProviderConfig {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LLMProviderConfig value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LLMProviderConfig() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LLMProviderConfig value)  $default,){
final _that = this;
switch (_that) {
case _LLMProviderConfig():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LLMProviderConfig value)?  $default,){
final _that = this;
switch (_that) {
case _LLMProviderConfig() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String provider, @JsonKey(name: 'model_name')  String modelName, @JsonKey(name: 'api_key')  String? apiKey, @JsonKey(name: 'base_url')  String? baseUrl,  double temperature, @JsonKey(name: 'additional_params')  Map<String, dynamic> additionalParams)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LLMProviderConfig() when $default != null:
return $default(_that.id,_that.provider,_that.modelName,_that.apiKey,_that.baseUrl,_that.temperature,_that.additionalParams);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String provider, @JsonKey(name: 'model_name')  String modelName, @JsonKey(name: 'api_key')  String? apiKey, @JsonKey(name: 'base_url')  String? baseUrl,  double temperature, @JsonKey(name: 'additional_params')  Map<String, dynamic> additionalParams)  $default,) {final _that = this;
switch (_that) {
case _LLMProviderConfig():
return $default(_that.id,_that.provider,_that.modelName,_that.apiKey,_that.baseUrl,_that.temperature,_that.additionalParams);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String provider, @JsonKey(name: 'model_name')  String modelName, @JsonKey(name: 'api_key')  String? apiKey, @JsonKey(name: 'base_url')  String? baseUrl,  double temperature, @JsonKey(name: 'additional_params')  Map<String, dynamic> additionalParams)?  $default,) {final _that = this;
switch (_that) {
case _LLMProviderConfig() when $default != null:
return $default(_that.id,_that.provider,_that.modelName,_that.apiKey,_that.baseUrl,_that.temperature,_that.additionalParams);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LLMProviderConfig implements LLMProviderConfig {
  const _LLMProviderConfig({required this.id, required this.provider, @JsonKey(name: 'model_name') required this.modelName, @JsonKey(name: 'api_key') this.apiKey, @JsonKey(name: 'base_url') this.baseUrl, this.temperature = 0.7, @JsonKey(name: 'additional_params') final  Map<String, dynamic> additionalParams = const {}}): _additionalParams = additionalParams;
  factory _LLMProviderConfig.fromJson(Map<String, dynamic> json) => _$LLMProviderConfigFromJson(json);

@override final  String id;
@override final  String provider;
@override@JsonKey(name: 'model_name') final  String modelName;
@override@JsonKey(name: 'api_key') final  String? apiKey;
@override@JsonKey(name: 'base_url') final  String? baseUrl;
@override@JsonKey() final  double temperature;
 final  Map<String, dynamic> _additionalParams;
@override@JsonKey(name: 'additional_params') Map<String, dynamic> get additionalParams {
  if (_additionalParams is EqualUnmodifiableMapView) return _additionalParams;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_additionalParams);
}


/// Create a copy of LLMProviderConfig
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LLMProviderConfigCopyWith<_LLMProviderConfig> get copyWith => __$LLMProviderConfigCopyWithImpl<_LLMProviderConfig>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LLMProviderConfigToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _LLMProviderConfig&&(identical(other.id, id) || other.id == id)&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.modelName, modelName) || other.modelName == modelName)&&(identical(other.apiKey, apiKey) || other.apiKey == apiKey)&&(identical(other.baseUrl, baseUrl) || other.baseUrl == baseUrl)&&(identical(other.temperature, temperature) || other.temperature == temperature)&&const DeepCollectionEquality().equals(other._additionalParams, _additionalParams));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,provider,modelName,apiKey,baseUrl,temperature,const DeepCollectionEquality().hash(_additionalParams));

@override
String toString() {
  return 'LLMProviderConfig(id: $id, provider: $provider, modelName: $modelName, apiKey: $apiKey, baseUrl: $baseUrl, temperature: $temperature, additionalParams: $additionalParams)';
}


}

/// @nodoc
abstract mixin class _$LLMProviderConfigCopyWith<$Res> implements $LLMProviderConfigCopyWith<$Res> {
  factory _$LLMProviderConfigCopyWith(_LLMProviderConfig value, $Res Function(_LLMProviderConfig) _then) = __$LLMProviderConfigCopyWithImpl;
@override @useResult
$Res call({
 String id, String provider,@JsonKey(name: 'model_name') String modelName,@JsonKey(name: 'api_key') String? apiKey,@JsonKey(name: 'base_url') String? baseUrl, double temperature,@JsonKey(name: 'additional_params') Map<String, dynamic> additionalParams
});




}
/// @nodoc
class __$LLMProviderConfigCopyWithImpl<$Res>
    implements _$LLMProviderConfigCopyWith<$Res> {
  __$LLMProviderConfigCopyWithImpl(this._self, this._then);

  final _LLMProviderConfig _self;
  final $Res Function(_LLMProviderConfig) _then;

/// Create a copy of LLMProviderConfig
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? provider = null,Object? modelName = null,Object? apiKey = freezed,Object? baseUrl = freezed,Object? temperature = null,Object? additionalParams = null,}) {
  return _then(_LLMProviderConfig(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,modelName: null == modelName ? _self.modelName : modelName // ignore: cast_nullable_to_non_nullable
as String,apiKey: freezed == apiKey ? _self.apiKey : apiKey // ignore: cast_nullable_to_non_nullable
as String?,baseUrl: freezed == baseUrl ? _self.baseUrl : baseUrl // ignore: cast_nullable_to_non_nullable
as String?,temperature: null == temperature ? _self.temperature : temperature // ignore: cast_nullable_to_non_nullable
as double,additionalParams: null == additionalParams ? _self._additionalParams : additionalParams // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}


/// @nodoc
mixin _$AdHocTestRequest {

 String get provider;@JsonKey(name: 'api_key') String? get apiKey;@JsonKey(name: 'system_instruction') String get systemInstruction;@JsonKey(name: 'user_prompt') String get userPrompt;@JsonKey(name: 'model_params') Map<String, dynamic> get modelParams;
/// Create a copy of AdHocTestRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AdHocTestRequestCopyWith<AdHocTestRequest> get copyWith => _$AdHocTestRequestCopyWithImpl<AdHocTestRequest>(this as AdHocTestRequest, _$identity);

  /// Serializes this AdHocTestRequest to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AdHocTestRequest&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.apiKey, apiKey) || other.apiKey == apiKey)&&(identical(other.systemInstruction, systemInstruction) || other.systemInstruction == systemInstruction)&&(identical(other.userPrompt, userPrompt) || other.userPrompt == userPrompt)&&const DeepCollectionEquality().equals(other.modelParams, modelParams));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,provider,apiKey,systemInstruction,userPrompt,const DeepCollectionEquality().hash(modelParams));

@override
String toString() {
  return 'AdHocTestRequest(provider: $provider, apiKey: $apiKey, systemInstruction: $systemInstruction, userPrompt: $userPrompt, modelParams: $modelParams)';
}


}

/// @nodoc
abstract mixin class $AdHocTestRequestCopyWith<$Res>  {
  factory $AdHocTestRequestCopyWith(AdHocTestRequest value, $Res Function(AdHocTestRequest) _then) = _$AdHocTestRequestCopyWithImpl;
@useResult
$Res call({
 String provider,@JsonKey(name: 'api_key') String? apiKey,@JsonKey(name: 'system_instruction') String systemInstruction,@JsonKey(name: 'user_prompt') String userPrompt,@JsonKey(name: 'model_params') Map<String, dynamic> modelParams
});




}
/// @nodoc
class _$AdHocTestRequestCopyWithImpl<$Res>
    implements $AdHocTestRequestCopyWith<$Res> {
  _$AdHocTestRequestCopyWithImpl(this._self, this._then);

  final AdHocTestRequest _self;
  final $Res Function(AdHocTestRequest) _then;

/// Create a copy of AdHocTestRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? provider = null,Object? apiKey = freezed,Object? systemInstruction = null,Object? userPrompt = null,Object? modelParams = null,}) {
  return _then(_self.copyWith(
provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,apiKey: freezed == apiKey ? _self.apiKey : apiKey // ignore: cast_nullable_to_non_nullable
as String?,systemInstruction: null == systemInstruction ? _self.systemInstruction : systemInstruction // ignore: cast_nullable_to_non_nullable
as String,userPrompt: null == userPrompt ? _self.userPrompt : userPrompt // ignore: cast_nullable_to_non_nullable
as String,modelParams: null == modelParams ? _self.modelParams : modelParams // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [AdHocTestRequest].
extension AdHocTestRequestPatterns on AdHocTestRequest {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AdHocTestRequest value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AdHocTestRequest() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AdHocTestRequest value)  $default,){
final _that = this;
switch (_that) {
case _AdHocTestRequest():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AdHocTestRequest value)?  $default,){
final _that = this;
switch (_that) {
case _AdHocTestRequest() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String provider, @JsonKey(name: 'api_key')  String? apiKey, @JsonKey(name: 'system_instruction')  String systemInstruction, @JsonKey(name: 'user_prompt')  String userPrompt, @JsonKey(name: 'model_params')  Map<String, dynamic> modelParams)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AdHocTestRequest() when $default != null:
return $default(_that.provider,_that.apiKey,_that.systemInstruction,_that.userPrompt,_that.modelParams);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String provider, @JsonKey(name: 'api_key')  String? apiKey, @JsonKey(name: 'system_instruction')  String systemInstruction, @JsonKey(name: 'user_prompt')  String userPrompt, @JsonKey(name: 'model_params')  Map<String, dynamic> modelParams)  $default,) {final _that = this;
switch (_that) {
case _AdHocTestRequest():
return $default(_that.provider,_that.apiKey,_that.systemInstruction,_that.userPrompt,_that.modelParams);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String provider, @JsonKey(name: 'api_key')  String? apiKey, @JsonKey(name: 'system_instruction')  String systemInstruction, @JsonKey(name: 'user_prompt')  String userPrompt, @JsonKey(name: 'model_params')  Map<String, dynamic> modelParams)?  $default,) {final _that = this;
switch (_that) {
case _AdHocTestRequest() when $default != null:
return $default(_that.provider,_that.apiKey,_that.systemInstruction,_that.userPrompt,_that.modelParams);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AdHocTestRequest implements AdHocTestRequest {
  const _AdHocTestRequest({required this.provider, @JsonKey(name: 'api_key') this.apiKey, @JsonKey(name: 'system_instruction') required this.systemInstruction, @JsonKey(name: 'user_prompt') required this.userPrompt, @JsonKey(name: 'model_params') final  Map<String, dynamic> modelParams = const {}}): _modelParams = modelParams;
  factory _AdHocTestRequest.fromJson(Map<String, dynamic> json) => _$AdHocTestRequestFromJson(json);

@override final  String provider;
@override@JsonKey(name: 'api_key') final  String? apiKey;
@override@JsonKey(name: 'system_instruction') final  String systemInstruction;
@override@JsonKey(name: 'user_prompt') final  String userPrompt;
 final  Map<String, dynamic> _modelParams;
@override@JsonKey(name: 'model_params') Map<String, dynamic> get modelParams {
  if (_modelParams is EqualUnmodifiableMapView) return _modelParams;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_modelParams);
}


/// Create a copy of AdHocTestRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AdHocTestRequestCopyWith<_AdHocTestRequest> get copyWith => __$AdHocTestRequestCopyWithImpl<_AdHocTestRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AdHocTestRequestToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _AdHocTestRequest&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.apiKey, apiKey) || other.apiKey == apiKey)&&(identical(other.systemInstruction, systemInstruction) || other.systemInstruction == systemInstruction)&&(identical(other.userPrompt, userPrompt) || other.userPrompt == userPrompt)&&const DeepCollectionEquality().equals(other._modelParams, _modelParams));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,provider,apiKey,systemInstruction,userPrompt,const DeepCollectionEquality().hash(_modelParams));

@override
String toString() {
  return 'AdHocTestRequest(provider: $provider, apiKey: $apiKey, systemInstruction: $systemInstruction, userPrompt: $userPrompt, modelParams: $modelParams)';
}


}

/// @nodoc
abstract mixin class _$AdHocTestRequestCopyWith<$Res> implements $AdHocTestRequestCopyWith<$Res> {
  factory _$AdHocTestRequestCopyWith(_AdHocTestRequest value, $Res Function(_AdHocTestRequest) _then) = __$AdHocTestRequestCopyWithImpl;
@override @useResult
$Res call({
 String provider,@JsonKey(name: 'api_key') String? apiKey,@JsonKey(name: 'system_instruction') String systemInstruction,@JsonKey(name: 'user_prompt') String userPrompt,@JsonKey(name: 'model_params') Map<String, dynamic> modelParams
});




}
/// @nodoc
class __$AdHocTestRequestCopyWithImpl<$Res>
    implements _$AdHocTestRequestCopyWith<$Res> {
  __$AdHocTestRequestCopyWithImpl(this._self, this._then);

  final _AdHocTestRequest _self;
  final $Res Function(_AdHocTestRequest) _then;

/// Create a copy of AdHocTestRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? provider = null,Object? apiKey = freezed,Object? systemInstruction = null,Object? userPrompt = null,Object? modelParams = null,}) {
  return _then(_AdHocTestRequest(
provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,apiKey: freezed == apiKey ? _self.apiKey : apiKey // ignore: cast_nullable_to_non_nullable
as String?,systemInstruction: null == systemInstruction ? _self.systemInstruction : systemInstruction // ignore: cast_nullable_to_non_nullable
as String,userPrompt: null == userPrompt ? _self.userPrompt : userPrompt // ignore: cast_nullable_to_non_nullable
as String,modelParams: null == modelParams ? _self._modelParams : modelParams // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}


/// @nodoc
mixin _$AdHocTestResult {

 String get content;@JsonKey(name: 'latency_ms') double get latencyMs; String get status;
/// Create a copy of AdHocTestResult
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$AdHocTestResultCopyWith<AdHocTestResult> get copyWith => _$AdHocTestResultCopyWithImpl<AdHocTestResult>(this as AdHocTestResult, _$identity);

  /// Serializes this AdHocTestResult to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is AdHocTestResult&&(identical(other.content, content) || other.content == content)&&(identical(other.latencyMs, latencyMs) || other.latencyMs == latencyMs)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,content,latencyMs,status);

@override
String toString() {
  return 'AdHocTestResult(content: $content, latencyMs: $latencyMs, status: $status)';
}


}

/// @nodoc
abstract mixin class $AdHocTestResultCopyWith<$Res>  {
  factory $AdHocTestResultCopyWith(AdHocTestResult value, $Res Function(AdHocTestResult) _then) = _$AdHocTestResultCopyWithImpl;
@useResult
$Res call({
 String content,@JsonKey(name: 'latency_ms') double latencyMs, String status
});




}
/// @nodoc
class _$AdHocTestResultCopyWithImpl<$Res>
    implements $AdHocTestResultCopyWith<$Res> {
  _$AdHocTestResultCopyWithImpl(this._self, this._then);

  final AdHocTestResult _self;
  final $Res Function(AdHocTestResult) _then;

/// Create a copy of AdHocTestResult
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? content = null,Object? latencyMs = null,Object? status = null,}) {
  return _then(_self.copyWith(
content: null == content ? _self.content : content // ignore: cast_nullable_to_non_nullable
as String,latencyMs: null == latencyMs ? _self.latencyMs : latencyMs // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [AdHocTestResult].
extension AdHocTestResultPatterns on AdHocTestResult {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _AdHocTestResult value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _AdHocTestResult() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _AdHocTestResult value)  $default,){
final _that = this;
switch (_that) {
case _AdHocTestResult():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _AdHocTestResult value)?  $default,){
final _that = this;
switch (_that) {
case _AdHocTestResult() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String content, @JsonKey(name: 'latency_ms')  double latencyMs,  String status)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _AdHocTestResult() when $default != null:
return $default(_that.content,_that.latencyMs,_that.status);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String content, @JsonKey(name: 'latency_ms')  double latencyMs,  String status)  $default,) {final _that = this;
switch (_that) {
case _AdHocTestResult():
return $default(_that.content,_that.latencyMs,_that.status);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String content, @JsonKey(name: 'latency_ms')  double latencyMs,  String status)?  $default,) {final _that = this;
switch (_that) {
case _AdHocTestResult() when $default != null:
return $default(_that.content,_that.latencyMs,_that.status);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _AdHocTestResult implements AdHocTestResult {
  const _AdHocTestResult({required this.content, @JsonKey(name: 'latency_ms') required this.latencyMs, required this.status});
  factory _AdHocTestResult.fromJson(Map<String, dynamic> json) => _$AdHocTestResultFromJson(json);

@override final  String content;
@override@JsonKey(name: 'latency_ms') final  double latencyMs;
@override final  String status;

/// Create a copy of AdHocTestResult
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$AdHocTestResultCopyWith<_AdHocTestResult> get copyWith => __$AdHocTestResultCopyWithImpl<_AdHocTestResult>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$AdHocTestResultToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _AdHocTestResult&&(identical(other.content, content) || other.content == content)&&(identical(other.latencyMs, latencyMs) || other.latencyMs == latencyMs)&&(identical(other.status, status) || other.status == status));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,content,latencyMs,status);

@override
String toString() {
  return 'AdHocTestResult(content: $content, latencyMs: $latencyMs, status: $status)';
}


}

/// @nodoc
abstract mixin class _$AdHocTestResultCopyWith<$Res> implements $AdHocTestResultCopyWith<$Res> {
  factory _$AdHocTestResultCopyWith(_AdHocTestResult value, $Res Function(_AdHocTestResult) _then) = __$AdHocTestResultCopyWithImpl;
@override @useResult
$Res call({
 String content,@JsonKey(name: 'latency_ms') double latencyMs, String status
});




}
/// @nodoc
class __$AdHocTestResultCopyWithImpl<$Res>
    implements _$AdHocTestResultCopyWith<$Res> {
  __$AdHocTestResultCopyWithImpl(this._self, this._then);

  final _AdHocTestResult _self;
  final $Res Function(_AdHocTestResult) _then;

/// Create a copy of AdHocTestResult
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? content = null,Object? latencyMs = null,Object? status = null,}) {
  return _then(_AdHocTestResult(
content: null == content ? _self.content : content // ignore: cast_nullable_to_non_nullable
as String,latencyMs: null == latencyMs ? _self.latencyMs : latencyMs // ignore: cast_nullable_to_non_nullable
as double,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
