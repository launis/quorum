// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'model_config.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ModelConfig {

@StrictOpaqueIdConverter() String get id; String? get slug; String get type; Map<String, LlmModelConfig> get models;
/// Create a copy of ModelConfig
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ModelConfigCopyWith<ModelConfig> get copyWith => _$ModelConfigCopyWithImpl<ModelConfig>(this as ModelConfig, _$identity);

  /// Serializes this ModelConfig to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ModelConfig&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.type, type) || other.type == type)&&const DeepCollectionEquality().equals(other.models, models));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slug,type,const DeepCollectionEquality().hash(models));

@override
String toString() {
  return 'ModelConfig(id: $id, slug: $slug, type: $type, models: $models)';
}


}

/// @nodoc
abstract mixin class $ModelConfigCopyWith<$Res>  {
  factory $ModelConfigCopyWith(ModelConfig value, $Res Function(ModelConfig) _then) = _$ModelConfigCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String? slug, String type, Map<String, LlmModelConfig> models
});




}
/// @nodoc
class _$ModelConfigCopyWithImpl<$Res>
    implements $ModelConfigCopyWith<$Res> {
  _$ModelConfigCopyWithImpl(this._self, this._then);

  final ModelConfig _self;
  final $Res Function(ModelConfig) _then;

/// Create a copy of ModelConfig
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = freezed,Object? type = null,Object? models = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,models: null == models ? _self.models : models // ignore: cast_nullable_to_non_nullable
as Map<String, LlmModelConfig>,
  ));
}

}


/// Adds pattern-matching-related methods to [ModelConfig].
extension ModelConfigPatterns on ModelConfig {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ModelConfig value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ModelConfig() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ModelConfig value)  $default,){
final _that = this;
switch (_that) {
case _ModelConfig():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ModelConfig value)?  $default,){
final _that = this;
switch (_that) {
case _ModelConfig() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String? slug,  String type,  Map<String, LlmModelConfig> models)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ModelConfig() when $default != null:
return $default(_that.id,_that.slug,_that.type,_that.models);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String? slug,  String type,  Map<String, LlmModelConfig> models)  $default,) {final _that = this;
switch (_that) {
case _ModelConfig():
return $default(_that.id,_that.slug,_that.type,_that.models);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String? slug,  String type,  Map<String, LlmModelConfig> models)?  $default,) {final _that = this;
switch (_that) {
case _ModelConfig() when $default != null:
return $default(_that.id,_that.slug,_that.type,_that.models);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ModelConfig implements ModelConfig {
  const _ModelConfig({@StrictOpaqueIdConverter() required this.id, this.slug, this.type = 'model_registry', final  Map<String, LlmModelConfig> models = const {}}): _models = models;
  factory _ModelConfig.fromJson(Map<String, dynamic> json) => _$ModelConfigFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override final  String? slug;
@override@JsonKey() final  String type;
 final  Map<String, LlmModelConfig> _models;
@override@JsonKey() Map<String, LlmModelConfig> get models {
  if (_models is EqualUnmodifiableMapView) return _models;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_models);
}


/// Create a copy of ModelConfig
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ModelConfigCopyWith<_ModelConfig> get copyWith => __$ModelConfigCopyWithImpl<_ModelConfig>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ModelConfigToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ModelConfig&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.type, type) || other.type == type)&&const DeepCollectionEquality().equals(other._models, _models));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slug,type,const DeepCollectionEquality().hash(_models));

@override
String toString() {
  return 'ModelConfig(id: $id, slug: $slug, type: $type, models: $models)';
}


}

/// @nodoc
abstract mixin class _$ModelConfigCopyWith<$Res> implements $ModelConfigCopyWith<$Res> {
  factory _$ModelConfigCopyWith(_ModelConfig value, $Res Function(_ModelConfig) _then) = __$ModelConfigCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String? slug, String type, Map<String, LlmModelConfig> models
});




}
/// @nodoc
class __$ModelConfigCopyWithImpl<$Res>
    implements _$ModelConfigCopyWith<$Res> {
  __$ModelConfigCopyWithImpl(this._self, this._then);

  final _ModelConfig _self;
  final $Res Function(_ModelConfig) _then;

/// Create a copy of ModelConfig
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = freezed,Object? type = null,Object? models = null,}) {
  return _then(_ModelConfig(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,type: null == type ? _self.type : type // ignore: cast_nullable_to_non_nullable
as String,models: null == models ? _self._models : models // ignore: cast_nullable_to_non_nullable
as Map<String, LlmModelConfig>,
  ));
}


}


/// @nodoc
mixin _$LlmModelConfig {

 String get provider;@JsonKey(name: 'model_name') String get modelName; double get temperature;@JsonKey(name: 'max_tokens') int? get maxTokens;@JsonKey(name: 'parsing_mode') String? get parsingMode;@JsonKey(name: 'top_p') double? get topP;@JsonKey(name: 'top_k') int? get topK;@JsonKey(name: 'frequency_penalty') double? get frequencyPenalty;@JsonKey(name: 'presence_penalty') double? get presencePenalty;@JsonKey(name: 'tpm_limit') int? get tpmLimit;@JsonKey(name: 'rpm_limit') int? get rpmLimit;@JsonKey(name: 'supports_grounding') bool get supportsGrounding;@JsonKey(name: 'is_active') bool get isActive;@JsonKey(name: 'allowed_tools') List<String> get allowedTools;@JsonKey(name: 'api_key') String? get apiKey;@JsonKey(name: 'caching_strategy') String? get cachingStrategy;@JsonKey(name: 'additional_params') Map<String, dynamic> get additionalParams;
/// Create a copy of LlmModelConfig
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$LlmModelConfigCopyWith<LlmModelConfig> get copyWith => _$LlmModelConfigCopyWithImpl<LlmModelConfig>(this as LlmModelConfig, _$identity);

  /// Serializes this LlmModelConfig to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is LlmModelConfig&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.modelName, modelName) || other.modelName == modelName)&&(identical(other.temperature, temperature) || other.temperature == temperature)&&(identical(other.maxTokens, maxTokens) || other.maxTokens == maxTokens)&&(identical(other.parsingMode, parsingMode) || other.parsingMode == parsingMode)&&(identical(other.topP, topP) || other.topP == topP)&&(identical(other.topK, topK) || other.topK == topK)&&(identical(other.frequencyPenalty, frequencyPenalty) || other.frequencyPenalty == frequencyPenalty)&&(identical(other.presencePenalty, presencePenalty) || other.presencePenalty == presencePenalty)&&(identical(other.tpmLimit, tpmLimit) || other.tpmLimit == tpmLimit)&&(identical(other.rpmLimit, rpmLimit) || other.rpmLimit == rpmLimit)&&(identical(other.supportsGrounding, supportsGrounding) || other.supportsGrounding == supportsGrounding)&&(identical(other.isActive, isActive) || other.isActive == isActive)&&const DeepCollectionEquality().equals(other.allowedTools, allowedTools)&&(identical(other.apiKey, apiKey) || other.apiKey == apiKey)&&(identical(other.cachingStrategy, cachingStrategy) || other.cachingStrategy == cachingStrategy)&&const DeepCollectionEquality().equals(other.additionalParams, additionalParams));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,provider,modelName,temperature,maxTokens,parsingMode,topP,topK,frequencyPenalty,presencePenalty,tpmLimit,rpmLimit,supportsGrounding,isActive,const DeepCollectionEquality().hash(allowedTools),apiKey,cachingStrategy,const DeepCollectionEquality().hash(additionalParams));

@override
String toString() {
  return 'LlmModelConfig(provider: $provider, modelName: $modelName, temperature: $temperature, maxTokens: $maxTokens, parsingMode: $parsingMode, topP: $topP, topK: $topK, frequencyPenalty: $frequencyPenalty, presencePenalty: $presencePenalty, tpmLimit: $tpmLimit, rpmLimit: $rpmLimit, supportsGrounding: $supportsGrounding, isActive: $isActive, allowedTools: $allowedTools, apiKey: $apiKey, cachingStrategy: $cachingStrategy, additionalParams: $additionalParams)';
}


}

/// @nodoc
abstract mixin class $LlmModelConfigCopyWith<$Res>  {
  factory $LlmModelConfigCopyWith(LlmModelConfig value, $Res Function(LlmModelConfig) _then) = _$LlmModelConfigCopyWithImpl;
@useResult
$Res call({
 String provider,@JsonKey(name: 'model_name') String modelName, double temperature,@JsonKey(name: 'max_tokens') int? maxTokens,@JsonKey(name: 'parsing_mode') String? parsingMode,@JsonKey(name: 'top_p') double? topP,@JsonKey(name: 'top_k') int? topK,@JsonKey(name: 'frequency_penalty') double? frequencyPenalty,@JsonKey(name: 'presence_penalty') double? presencePenalty,@JsonKey(name: 'tpm_limit') int? tpmLimit,@JsonKey(name: 'rpm_limit') int? rpmLimit,@JsonKey(name: 'supports_grounding') bool supportsGrounding,@JsonKey(name: 'is_active') bool isActive,@JsonKey(name: 'allowed_tools') List<String> allowedTools,@JsonKey(name: 'api_key') String? apiKey,@JsonKey(name: 'caching_strategy') String? cachingStrategy,@JsonKey(name: 'additional_params') Map<String, dynamic> additionalParams
});




}
/// @nodoc
class _$LlmModelConfigCopyWithImpl<$Res>
    implements $LlmModelConfigCopyWith<$Res> {
  _$LlmModelConfigCopyWithImpl(this._self, this._then);

  final LlmModelConfig _self;
  final $Res Function(LlmModelConfig) _then;

/// Create a copy of LlmModelConfig
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? provider = null,Object? modelName = null,Object? temperature = null,Object? maxTokens = freezed,Object? parsingMode = freezed,Object? topP = freezed,Object? topK = freezed,Object? frequencyPenalty = freezed,Object? presencePenalty = freezed,Object? tpmLimit = freezed,Object? rpmLimit = freezed,Object? supportsGrounding = null,Object? isActive = null,Object? allowedTools = null,Object? apiKey = freezed,Object? cachingStrategy = freezed,Object? additionalParams = null,}) {
  return _then(_self.copyWith(
provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,modelName: null == modelName ? _self.modelName : modelName // ignore: cast_nullable_to_non_nullable
as String,temperature: null == temperature ? _self.temperature : temperature // ignore: cast_nullable_to_non_nullable
as double,maxTokens: freezed == maxTokens ? _self.maxTokens : maxTokens // ignore: cast_nullable_to_non_nullable
as int?,parsingMode: freezed == parsingMode ? _self.parsingMode : parsingMode // ignore: cast_nullable_to_non_nullable
as String?,topP: freezed == topP ? _self.topP : topP // ignore: cast_nullable_to_non_nullable
as double?,topK: freezed == topK ? _self.topK : topK // ignore: cast_nullable_to_non_nullable
as int?,frequencyPenalty: freezed == frequencyPenalty ? _self.frequencyPenalty : frequencyPenalty // ignore: cast_nullable_to_non_nullable
as double?,presencePenalty: freezed == presencePenalty ? _self.presencePenalty : presencePenalty // ignore: cast_nullable_to_non_nullable
as double?,tpmLimit: freezed == tpmLimit ? _self.tpmLimit : tpmLimit // ignore: cast_nullable_to_non_nullable
as int?,rpmLimit: freezed == rpmLimit ? _self.rpmLimit : rpmLimit // ignore: cast_nullable_to_non_nullable
as int?,supportsGrounding: null == supportsGrounding ? _self.supportsGrounding : supportsGrounding // ignore: cast_nullable_to_non_nullable
as bool,isActive: null == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool,allowedTools: null == allowedTools ? _self.allowedTools : allowedTools // ignore: cast_nullable_to_non_nullable
as List<String>,apiKey: freezed == apiKey ? _self.apiKey : apiKey // ignore: cast_nullable_to_non_nullable
as String?,cachingStrategy: freezed == cachingStrategy ? _self.cachingStrategy : cachingStrategy // ignore: cast_nullable_to_non_nullable
as String?,additionalParams: null == additionalParams ? _self.additionalParams : additionalParams // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}

}


/// Adds pattern-matching-related methods to [LlmModelConfig].
extension LlmModelConfigPatterns on LlmModelConfig {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _LlmModelConfig value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _LlmModelConfig() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _LlmModelConfig value)  $default,){
final _that = this;
switch (_that) {
case _LlmModelConfig():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _LlmModelConfig value)?  $default,){
final _that = this;
switch (_that) {
case _LlmModelConfig() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String provider, @JsonKey(name: 'model_name')  String modelName,  double temperature, @JsonKey(name: 'max_tokens')  int? maxTokens, @JsonKey(name: 'parsing_mode')  String? parsingMode, @JsonKey(name: 'top_p')  double? topP, @JsonKey(name: 'top_k')  int? topK, @JsonKey(name: 'frequency_penalty')  double? frequencyPenalty, @JsonKey(name: 'presence_penalty')  double? presencePenalty, @JsonKey(name: 'tpm_limit')  int? tpmLimit, @JsonKey(name: 'rpm_limit')  int? rpmLimit, @JsonKey(name: 'supports_grounding')  bool supportsGrounding, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'allowed_tools')  List<String> allowedTools, @JsonKey(name: 'api_key')  String? apiKey, @JsonKey(name: 'caching_strategy')  String? cachingStrategy, @JsonKey(name: 'additional_params')  Map<String, dynamic> additionalParams)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _LlmModelConfig() when $default != null:
return $default(_that.provider,_that.modelName,_that.temperature,_that.maxTokens,_that.parsingMode,_that.topP,_that.topK,_that.frequencyPenalty,_that.presencePenalty,_that.tpmLimit,_that.rpmLimit,_that.supportsGrounding,_that.isActive,_that.allowedTools,_that.apiKey,_that.cachingStrategy,_that.additionalParams);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String provider, @JsonKey(name: 'model_name')  String modelName,  double temperature, @JsonKey(name: 'max_tokens')  int? maxTokens, @JsonKey(name: 'parsing_mode')  String? parsingMode, @JsonKey(name: 'top_p')  double? topP, @JsonKey(name: 'top_k')  int? topK, @JsonKey(name: 'frequency_penalty')  double? frequencyPenalty, @JsonKey(name: 'presence_penalty')  double? presencePenalty, @JsonKey(name: 'tpm_limit')  int? tpmLimit, @JsonKey(name: 'rpm_limit')  int? rpmLimit, @JsonKey(name: 'supports_grounding')  bool supportsGrounding, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'allowed_tools')  List<String> allowedTools, @JsonKey(name: 'api_key')  String? apiKey, @JsonKey(name: 'caching_strategy')  String? cachingStrategy, @JsonKey(name: 'additional_params')  Map<String, dynamic> additionalParams)  $default,) {final _that = this;
switch (_that) {
case _LlmModelConfig():
return $default(_that.provider,_that.modelName,_that.temperature,_that.maxTokens,_that.parsingMode,_that.topP,_that.topK,_that.frequencyPenalty,_that.presencePenalty,_that.tpmLimit,_that.rpmLimit,_that.supportsGrounding,_that.isActive,_that.allowedTools,_that.apiKey,_that.cachingStrategy,_that.additionalParams);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String provider, @JsonKey(name: 'model_name')  String modelName,  double temperature, @JsonKey(name: 'max_tokens')  int? maxTokens, @JsonKey(name: 'parsing_mode')  String? parsingMode, @JsonKey(name: 'top_p')  double? topP, @JsonKey(name: 'top_k')  int? topK, @JsonKey(name: 'frequency_penalty')  double? frequencyPenalty, @JsonKey(name: 'presence_penalty')  double? presencePenalty, @JsonKey(name: 'tpm_limit')  int? tpmLimit, @JsonKey(name: 'rpm_limit')  int? rpmLimit, @JsonKey(name: 'supports_grounding')  bool supportsGrounding, @JsonKey(name: 'is_active')  bool isActive, @JsonKey(name: 'allowed_tools')  List<String> allowedTools, @JsonKey(name: 'api_key')  String? apiKey, @JsonKey(name: 'caching_strategy')  String? cachingStrategy, @JsonKey(name: 'additional_params')  Map<String, dynamic> additionalParams)?  $default,) {final _that = this;
switch (_that) {
case _LlmModelConfig() when $default != null:
return $default(_that.provider,_that.modelName,_that.temperature,_that.maxTokens,_that.parsingMode,_that.topP,_that.topK,_that.frequencyPenalty,_that.presencePenalty,_that.tpmLimit,_that.rpmLimit,_that.supportsGrounding,_that.isActive,_that.allowedTools,_that.apiKey,_that.cachingStrategy,_that.additionalParams);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _LlmModelConfig implements LlmModelConfig {
  const _LlmModelConfig({this.provider = 'unknown', @JsonKey(name: 'model_name') this.modelName = '', this.temperature = 0.0, @JsonKey(name: 'max_tokens') this.maxTokens, @JsonKey(name: 'parsing_mode') this.parsingMode, @JsonKey(name: 'top_p') this.topP, @JsonKey(name: 'top_k') this.topK, @JsonKey(name: 'frequency_penalty') this.frequencyPenalty, @JsonKey(name: 'presence_penalty') this.presencePenalty, @JsonKey(name: 'tpm_limit') this.tpmLimit, @JsonKey(name: 'rpm_limit') this.rpmLimit, @JsonKey(name: 'supports_grounding') this.supportsGrounding = false, @JsonKey(name: 'is_active') this.isActive = false, @JsonKey(name: 'allowed_tools') final  List<String> allowedTools = const [], @JsonKey(name: 'api_key') this.apiKey, @JsonKey(name: 'caching_strategy') this.cachingStrategy, @JsonKey(name: 'additional_params') final  Map<String, dynamic> additionalParams = const {}}): _allowedTools = allowedTools,_additionalParams = additionalParams;
  factory _LlmModelConfig.fromJson(Map<String, dynamic> json) => _$LlmModelConfigFromJson(json);

@override@JsonKey() final  String provider;
@override@JsonKey(name: 'model_name') final  String modelName;
@override@JsonKey() final  double temperature;
@override@JsonKey(name: 'max_tokens') final  int? maxTokens;
@override@JsonKey(name: 'parsing_mode') final  String? parsingMode;
@override@JsonKey(name: 'top_p') final  double? topP;
@override@JsonKey(name: 'top_k') final  int? topK;
@override@JsonKey(name: 'frequency_penalty') final  double? frequencyPenalty;
@override@JsonKey(name: 'presence_penalty') final  double? presencePenalty;
@override@JsonKey(name: 'tpm_limit') final  int? tpmLimit;
@override@JsonKey(name: 'rpm_limit') final  int? rpmLimit;
@override@JsonKey(name: 'supports_grounding') final  bool supportsGrounding;
@override@JsonKey(name: 'is_active') final  bool isActive;
 final  List<String> _allowedTools;
@override@JsonKey(name: 'allowed_tools') List<String> get allowedTools {
  if (_allowedTools is EqualUnmodifiableListView) return _allowedTools;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_allowedTools);
}

@override@JsonKey(name: 'api_key') final  String? apiKey;
@override@JsonKey(name: 'caching_strategy') final  String? cachingStrategy;
 final  Map<String, dynamic> _additionalParams;
@override@JsonKey(name: 'additional_params') Map<String, dynamic> get additionalParams {
  if (_additionalParams is EqualUnmodifiableMapView) return _additionalParams;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_additionalParams);
}


/// Create a copy of LlmModelConfig
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$LlmModelConfigCopyWith<_LlmModelConfig> get copyWith => __$LlmModelConfigCopyWithImpl<_LlmModelConfig>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$LlmModelConfigToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _LlmModelConfig&&(identical(other.provider, provider) || other.provider == provider)&&(identical(other.modelName, modelName) || other.modelName == modelName)&&(identical(other.temperature, temperature) || other.temperature == temperature)&&(identical(other.maxTokens, maxTokens) || other.maxTokens == maxTokens)&&(identical(other.parsingMode, parsingMode) || other.parsingMode == parsingMode)&&(identical(other.topP, topP) || other.topP == topP)&&(identical(other.topK, topK) || other.topK == topK)&&(identical(other.frequencyPenalty, frequencyPenalty) || other.frequencyPenalty == frequencyPenalty)&&(identical(other.presencePenalty, presencePenalty) || other.presencePenalty == presencePenalty)&&(identical(other.tpmLimit, tpmLimit) || other.tpmLimit == tpmLimit)&&(identical(other.rpmLimit, rpmLimit) || other.rpmLimit == rpmLimit)&&(identical(other.supportsGrounding, supportsGrounding) || other.supportsGrounding == supportsGrounding)&&(identical(other.isActive, isActive) || other.isActive == isActive)&&const DeepCollectionEquality().equals(other._allowedTools, _allowedTools)&&(identical(other.apiKey, apiKey) || other.apiKey == apiKey)&&(identical(other.cachingStrategy, cachingStrategy) || other.cachingStrategy == cachingStrategy)&&const DeepCollectionEquality().equals(other._additionalParams, _additionalParams));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,provider,modelName,temperature,maxTokens,parsingMode,topP,topK,frequencyPenalty,presencePenalty,tpmLimit,rpmLimit,supportsGrounding,isActive,const DeepCollectionEquality().hash(_allowedTools),apiKey,cachingStrategy,const DeepCollectionEquality().hash(_additionalParams));

@override
String toString() {
  return 'LlmModelConfig(provider: $provider, modelName: $modelName, temperature: $temperature, maxTokens: $maxTokens, parsingMode: $parsingMode, topP: $topP, topK: $topK, frequencyPenalty: $frequencyPenalty, presencePenalty: $presencePenalty, tpmLimit: $tpmLimit, rpmLimit: $rpmLimit, supportsGrounding: $supportsGrounding, isActive: $isActive, allowedTools: $allowedTools, apiKey: $apiKey, cachingStrategy: $cachingStrategy, additionalParams: $additionalParams)';
}


}

/// @nodoc
abstract mixin class _$LlmModelConfigCopyWith<$Res> implements $LlmModelConfigCopyWith<$Res> {
  factory _$LlmModelConfigCopyWith(_LlmModelConfig value, $Res Function(_LlmModelConfig) _then) = __$LlmModelConfigCopyWithImpl;
@override @useResult
$Res call({
 String provider,@JsonKey(name: 'model_name') String modelName, double temperature,@JsonKey(name: 'max_tokens') int? maxTokens,@JsonKey(name: 'parsing_mode') String? parsingMode,@JsonKey(name: 'top_p') double? topP,@JsonKey(name: 'top_k') int? topK,@JsonKey(name: 'frequency_penalty') double? frequencyPenalty,@JsonKey(name: 'presence_penalty') double? presencePenalty,@JsonKey(name: 'tpm_limit') int? tpmLimit,@JsonKey(name: 'rpm_limit') int? rpmLimit,@JsonKey(name: 'supports_grounding') bool supportsGrounding,@JsonKey(name: 'is_active') bool isActive,@JsonKey(name: 'allowed_tools') List<String> allowedTools,@JsonKey(name: 'api_key') String? apiKey,@JsonKey(name: 'caching_strategy') String? cachingStrategy,@JsonKey(name: 'additional_params') Map<String, dynamic> additionalParams
});




}
/// @nodoc
class __$LlmModelConfigCopyWithImpl<$Res>
    implements _$LlmModelConfigCopyWith<$Res> {
  __$LlmModelConfigCopyWithImpl(this._self, this._then);

  final _LlmModelConfig _self;
  final $Res Function(_LlmModelConfig) _then;

/// Create a copy of LlmModelConfig
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? provider = null,Object? modelName = null,Object? temperature = null,Object? maxTokens = freezed,Object? parsingMode = freezed,Object? topP = freezed,Object? topK = freezed,Object? frequencyPenalty = freezed,Object? presencePenalty = freezed,Object? tpmLimit = freezed,Object? rpmLimit = freezed,Object? supportsGrounding = null,Object? isActive = null,Object? allowedTools = null,Object? apiKey = freezed,Object? cachingStrategy = freezed,Object? additionalParams = null,}) {
  return _then(_LlmModelConfig(
provider: null == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String,modelName: null == modelName ? _self.modelName : modelName // ignore: cast_nullable_to_non_nullable
as String,temperature: null == temperature ? _self.temperature : temperature // ignore: cast_nullable_to_non_nullable
as double,maxTokens: freezed == maxTokens ? _self.maxTokens : maxTokens // ignore: cast_nullable_to_non_nullable
as int?,parsingMode: freezed == parsingMode ? _self.parsingMode : parsingMode // ignore: cast_nullable_to_non_nullable
as String?,topP: freezed == topP ? _self.topP : topP // ignore: cast_nullable_to_non_nullable
as double?,topK: freezed == topK ? _self.topK : topK // ignore: cast_nullable_to_non_nullable
as int?,frequencyPenalty: freezed == frequencyPenalty ? _self.frequencyPenalty : frequencyPenalty // ignore: cast_nullable_to_non_nullable
as double?,presencePenalty: freezed == presencePenalty ? _self.presencePenalty : presencePenalty // ignore: cast_nullable_to_non_nullable
as double?,tpmLimit: freezed == tpmLimit ? _self.tpmLimit : tpmLimit // ignore: cast_nullable_to_non_nullable
as int?,rpmLimit: freezed == rpmLimit ? _self.rpmLimit : rpmLimit // ignore: cast_nullable_to_non_nullable
as int?,supportsGrounding: null == supportsGrounding ? _self.supportsGrounding : supportsGrounding // ignore: cast_nullable_to_non_nullable
as bool,isActive: null == isActive ? _self.isActive : isActive // ignore: cast_nullable_to_non_nullable
as bool,allowedTools: null == allowedTools ? _self._allowedTools : allowedTools // ignore: cast_nullable_to_non_nullable
as List<String>,apiKey: freezed == apiKey ? _self.apiKey : apiKey // ignore: cast_nullable_to_non_nullable
as String?,cachingStrategy: freezed == cachingStrategy ? _self.cachingStrategy : cachingStrategy // ignore: cast_nullable_to_non_nullable
as String?,additionalParams: null == additionalParams ? _self._additionalParams : additionalParams // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,
  ));
}


}

// dart format on
