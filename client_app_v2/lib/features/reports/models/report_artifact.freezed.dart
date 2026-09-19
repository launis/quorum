// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'report_artifact.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ReportStoragePaths {

@JsonKey(name: 'pdf_path') String? get pdfPath;@JsonKey(name: 'sdui_json_path') String? get sduiJsonPath;@JsonKey(name: 'excel_path') String? get excelPath;@JsonKey(name: 'csv_path') String? get csvPath;
/// Create a copy of ReportStoragePaths
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportStoragePathsCopyWith<ReportStoragePaths> get copyWith => _$ReportStoragePathsCopyWithImpl<ReportStoragePaths>(this as ReportStoragePaths, _$identity);

  /// Serializes this ReportStoragePaths to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportStoragePaths(pdfPath: $pdfPath, sduiJsonPath: $sduiJsonPath, excelPath: $excelPath, csvPath: $csvPath)';
}


}

/// @nodoc
abstract mixin class $ReportStoragePathsCopyWith<$Res>  {
  factory $ReportStoragePathsCopyWith(ReportStoragePaths value, $Res Function(ReportStoragePaths) _then) = _$ReportStoragePathsCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'pdf_path') String? pdfPath,@JsonKey(name: 'sdui_json_path') String? sduiJsonPath,@JsonKey(name: 'excel_path') String? excelPath,@JsonKey(name: 'csv_path') String? csvPath
});




}
/// @nodoc
class _$ReportStoragePathsCopyWithImpl<$Res>
    implements $ReportStoragePathsCopyWith<$Res> {
  _$ReportStoragePathsCopyWithImpl(this._self, this._then);

  final ReportStoragePaths _self;
  final $Res Function(ReportStoragePaths) _then;

/// Create a copy of ReportStoragePaths
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? pdfPath = freezed,Object? sduiJsonPath = freezed,Object? excelPath = freezed,Object? csvPath = freezed,}) {
  return _then(_self.copyWith(
pdfPath: freezed == pdfPath ? _self.pdfPath : pdfPath // ignore: cast_nullable_to_non_nullable
as String?,sduiJsonPath: freezed == sduiJsonPath ? _self.sduiJsonPath : sduiJsonPath // ignore: cast_nullable_to_non_nullable
as String?,excelPath: freezed == excelPath ? _self.excelPath : excelPath // ignore: cast_nullable_to_non_nullable
as String?,csvPath: freezed == csvPath ? _self.csvPath : csvPath // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ReportStoragePaths].
extension ReportStoragePathsPatterns on ReportStoragePaths {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportStoragePaths value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportStoragePaths() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportStoragePaths value)  $default,){
final _that = this;
switch (_that) {
case _ReportStoragePaths():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportStoragePaths value)?  $default,){
final _that = this;
switch (_that) {
case _ReportStoragePaths() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'pdf_path')  String? pdfPath, @JsonKey(name: 'sdui_json_path')  String? sduiJsonPath, @JsonKey(name: 'excel_path')  String? excelPath, @JsonKey(name: 'csv_path')  String? csvPath)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportStoragePaths() when $default != null:
return $default(_that.pdfPath,_that.sduiJsonPath,_that.excelPath,_that.csvPath);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'pdf_path')  String? pdfPath, @JsonKey(name: 'sdui_json_path')  String? sduiJsonPath, @JsonKey(name: 'excel_path')  String? excelPath, @JsonKey(name: 'csv_path')  String? csvPath)  $default,) {final _that = this;
switch (_that) {
case _ReportStoragePaths():
return $default(_that.pdfPath,_that.sduiJsonPath,_that.excelPath,_that.csvPath);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'pdf_path')  String? pdfPath, @JsonKey(name: 'sdui_json_path')  String? sduiJsonPath, @JsonKey(name: 'excel_path')  String? excelPath, @JsonKey(name: 'csv_path')  String? csvPath)?  $default,) {final _that = this;
switch (_that) {
case _ReportStoragePaths() when $default != null:
return $default(_that.pdfPath,_that.sduiJsonPath,_that.excelPath,_that.csvPath);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportStoragePaths extends ReportStoragePaths {
  const _ReportStoragePaths({@JsonKey(name: 'pdf_path') this.pdfPath, @JsonKey(name: 'sdui_json_path') this.sduiJsonPath, @JsonKey(name: 'excel_path') this.excelPath, @JsonKey(name: 'csv_path') this.csvPath}): super._();
  factory _ReportStoragePaths.fromJson(Map<String, dynamic> json) => _$ReportStoragePathsFromJson(json);

@override@JsonKey(name: 'pdf_path') final  String? pdfPath;
@override@JsonKey(name: 'sdui_json_path') final  String? sduiJsonPath;
@override@JsonKey(name: 'excel_path') final  String? excelPath;
@override@JsonKey(name: 'csv_path') final  String? csvPath;

/// Create a copy of ReportStoragePaths
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportStoragePathsCopyWith<_ReportStoragePaths> get copyWith => __$ReportStoragePathsCopyWithImpl<_ReportStoragePaths>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportStoragePathsToJson(this, );
}



@override
String toString() {
  return 'ReportStoragePaths(pdfPath: $pdfPath, sduiJsonPath: $sduiJsonPath, excelPath: $excelPath, csvPath: $csvPath)';
}


}

/// @nodoc
abstract mixin class _$ReportStoragePathsCopyWith<$Res> implements $ReportStoragePathsCopyWith<$Res> {
  factory _$ReportStoragePathsCopyWith(_ReportStoragePaths value, $Res Function(_ReportStoragePaths) _then) = __$ReportStoragePathsCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'pdf_path') String? pdfPath,@JsonKey(name: 'sdui_json_path') String? sduiJsonPath,@JsonKey(name: 'excel_path') String? excelPath,@JsonKey(name: 'csv_path') String? csvPath
});




}
/// @nodoc
class __$ReportStoragePathsCopyWithImpl<$Res>
    implements _$ReportStoragePathsCopyWith<$Res> {
  __$ReportStoragePathsCopyWithImpl(this._self, this._then);

  final _ReportStoragePaths _self;
  final $Res Function(_ReportStoragePaths) _then;

/// Create a copy of ReportStoragePaths
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? pdfPath = freezed,Object? sduiJsonPath = freezed,Object? excelPath = freezed,Object? csvPath = freezed,}) {
  return _then(_ReportStoragePaths(
pdfPath: freezed == pdfPath ? _self.pdfPath : pdfPath // ignore: cast_nullable_to_non_nullable
as String?,sduiJsonPath: freezed == sduiJsonPath ? _self.sduiJsonPath : sduiJsonPath // ignore: cast_nullable_to_non_nullable
as String?,excelPath: freezed == excelPath ? _self.excelPath : excelPath // ignore: cast_nullable_to_non_nullable
as String?,csvPath: freezed == csvPath ? _self.csvPath : csvPath // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$ReportMetadata {

@JsonKey(name: 'cost_usd') double? get costUsd;@JsonKey(name: 'duration_ms') int? get durationMs;@JsonKey(name: 'tokens_used') int? get tokensUsed;@JsonKey(name: 'llm_model') String? get llmModel;@JsonKey(name: 'provider') String? get provider;@JsonKey(name: 'cognitive_tier') CognitiveTier? get cognitiveTier;@JsonKey(name: 'model_registry_id') String? get modelRegistryId;@JsonKey(name: 'thinking_tokens') int? get thinkingTokens;
/// Create a copy of ReportMetadata
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportMetadataCopyWith<ReportMetadata> get copyWith => _$ReportMetadataCopyWithImpl<ReportMetadata>(this as ReportMetadata, _$identity);

  /// Serializes this ReportMetadata to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportMetadata(costUsd: $costUsd, durationMs: $durationMs, tokensUsed: $tokensUsed, llmModel: $llmModel, provider: $provider, cognitiveTier: $cognitiveTier, modelRegistryId: $modelRegistryId, thinkingTokens: $thinkingTokens)';
}


}

/// @nodoc
abstract mixin class $ReportMetadataCopyWith<$Res>  {
  factory $ReportMetadataCopyWith(ReportMetadata value, $Res Function(ReportMetadata) _then) = _$ReportMetadataCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'cost_usd') double? costUsd,@JsonKey(name: 'duration_ms') int? durationMs,@JsonKey(name: 'tokens_used') int? tokensUsed,@JsonKey(name: 'llm_model') String? llmModel,@JsonKey(name: 'provider') String? provider,@JsonKey(name: 'cognitive_tier') CognitiveTier? cognitiveTier,@JsonKey(name: 'model_registry_id') String? modelRegistryId,@JsonKey(name: 'thinking_tokens') int? thinkingTokens
});




}
/// @nodoc
class _$ReportMetadataCopyWithImpl<$Res>
    implements $ReportMetadataCopyWith<$Res> {
  _$ReportMetadataCopyWithImpl(this._self, this._then);

  final ReportMetadata _self;
  final $Res Function(ReportMetadata) _then;

/// Create a copy of ReportMetadata
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? costUsd = freezed,Object? durationMs = freezed,Object? tokensUsed = freezed,Object? llmModel = freezed,Object? provider = freezed,Object? cognitiveTier = freezed,Object? modelRegistryId = freezed,Object? thinkingTokens = freezed,}) {
  return _then(_self.copyWith(
costUsd: freezed == costUsd ? _self.costUsd : costUsd // ignore: cast_nullable_to_non_nullable
as double?,durationMs: freezed == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int?,tokensUsed: freezed == tokensUsed ? _self.tokensUsed : tokensUsed // ignore: cast_nullable_to_non_nullable
as int?,llmModel: freezed == llmModel ? _self.llmModel : llmModel // ignore: cast_nullable_to_non_nullable
as String?,provider: freezed == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String?,cognitiveTier: freezed == cognitiveTier ? _self.cognitiveTier : cognitiveTier // ignore: cast_nullable_to_non_nullable
as CognitiveTier?,modelRegistryId: freezed == modelRegistryId ? _self.modelRegistryId : modelRegistryId // ignore: cast_nullable_to_non_nullable
as String?,thinkingTokens: freezed == thinkingTokens ? _self.thinkingTokens : thinkingTokens // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}

}


/// Adds pattern-matching-related methods to [ReportMetadata].
extension ReportMetadataPatterns on ReportMetadata {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportMetadata value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportMetadata() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportMetadata value)  $default,){
final _that = this;
switch (_that) {
case _ReportMetadata():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportMetadata value)?  $default,){
final _that = this;
switch (_that) {
case _ReportMetadata() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'cost_usd')  double? costUsd, @JsonKey(name: 'duration_ms')  int? durationMs, @JsonKey(name: 'tokens_used')  int? tokensUsed, @JsonKey(name: 'llm_model')  String? llmModel, @JsonKey(name: 'provider')  String? provider, @JsonKey(name: 'cognitive_tier')  CognitiveTier? cognitiveTier, @JsonKey(name: 'model_registry_id')  String? modelRegistryId, @JsonKey(name: 'thinking_tokens')  int? thinkingTokens)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportMetadata() when $default != null:
return $default(_that.costUsd,_that.durationMs,_that.tokensUsed,_that.llmModel,_that.provider,_that.cognitiveTier,_that.modelRegistryId,_that.thinkingTokens);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'cost_usd')  double? costUsd, @JsonKey(name: 'duration_ms')  int? durationMs, @JsonKey(name: 'tokens_used')  int? tokensUsed, @JsonKey(name: 'llm_model')  String? llmModel, @JsonKey(name: 'provider')  String? provider, @JsonKey(name: 'cognitive_tier')  CognitiveTier? cognitiveTier, @JsonKey(name: 'model_registry_id')  String? modelRegistryId, @JsonKey(name: 'thinking_tokens')  int? thinkingTokens)  $default,) {final _that = this;
switch (_that) {
case _ReportMetadata():
return $default(_that.costUsd,_that.durationMs,_that.tokensUsed,_that.llmModel,_that.provider,_that.cognitiveTier,_that.modelRegistryId,_that.thinkingTokens);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'cost_usd')  double? costUsd, @JsonKey(name: 'duration_ms')  int? durationMs, @JsonKey(name: 'tokens_used')  int? tokensUsed, @JsonKey(name: 'llm_model')  String? llmModel, @JsonKey(name: 'provider')  String? provider, @JsonKey(name: 'cognitive_tier')  CognitiveTier? cognitiveTier, @JsonKey(name: 'model_registry_id')  String? modelRegistryId, @JsonKey(name: 'thinking_tokens')  int? thinkingTokens)?  $default,) {final _that = this;
switch (_that) {
case _ReportMetadata() when $default != null:
return $default(_that.costUsd,_that.durationMs,_that.tokensUsed,_that.llmModel,_that.provider,_that.cognitiveTier,_that.modelRegistryId,_that.thinkingTokens);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportMetadata extends ReportMetadata {
  const _ReportMetadata({@JsonKey(name: 'cost_usd') this.costUsd, @JsonKey(name: 'duration_ms') this.durationMs, @JsonKey(name: 'tokens_used') this.tokensUsed, @JsonKey(name: 'llm_model') this.llmModel, @JsonKey(name: 'provider') this.provider, @JsonKey(name: 'cognitive_tier') this.cognitiveTier, @JsonKey(name: 'model_registry_id') this.modelRegistryId, @JsonKey(name: 'thinking_tokens') this.thinkingTokens}): super._();
  factory _ReportMetadata.fromJson(Map<String, dynamic> json) => _$ReportMetadataFromJson(json);

@override@JsonKey(name: 'cost_usd') final  double? costUsd;
@override@JsonKey(name: 'duration_ms') final  int? durationMs;
@override@JsonKey(name: 'tokens_used') final  int? tokensUsed;
@override@JsonKey(name: 'llm_model') final  String? llmModel;
@override@JsonKey(name: 'provider') final  String? provider;
@override@JsonKey(name: 'cognitive_tier') final  CognitiveTier? cognitiveTier;
@override@JsonKey(name: 'model_registry_id') final  String? modelRegistryId;
@override@JsonKey(name: 'thinking_tokens') final  int? thinkingTokens;

/// Create a copy of ReportMetadata
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportMetadataCopyWith<_ReportMetadata> get copyWith => __$ReportMetadataCopyWithImpl<_ReportMetadata>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportMetadataToJson(this, );
}



@override
String toString() {
  return 'ReportMetadata(costUsd: $costUsd, durationMs: $durationMs, tokensUsed: $tokensUsed, llmModel: $llmModel, provider: $provider, cognitiveTier: $cognitiveTier, modelRegistryId: $modelRegistryId, thinkingTokens: $thinkingTokens)';
}


}

/// @nodoc
abstract mixin class _$ReportMetadataCopyWith<$Res> implements $ReportMetadataCopyWith<$Res> {
  factory _$ReportMetadataCopyWith(_ReportMetadata value, $Res Function(_ReportMetadata) _then) = __$ReportMetadataCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'cost_usd') double? costUsd,@JsonKey(name: 'duration_ms') int? durationMs,@JsonKey(name: 'tokens_used') int? tokensUsed,@JsonKey(name: 'llm_model') String? llmModel,@JsonKey(name: 'provider') String? provider,@JsonKey(name: 'cognitive_tier') CognitiveTier? cognitiveTier,@JsonKey(name: 'model_registry_id') String? modelRegistryId,@JsonKey(name: 'thinking_tokens') int? thinkingTokens
});




}
/// @nodoc
class __$ReportMetadataCopyWithImpl<$Res>
    implements _$ReportMetadataCopyWith<$Res> {
  __$ReportMetadataCopyWithImpl(this._self, this._then);

  final _ReportMetadata _self;
  final $Res Function(_ReportMetadata) _then;

/// Create a copy of ReportMetadata
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? costUsd = freezed,Object? durationMs = freezed,Object? tokensUsed = freezed,Object? llmModel = freezed,Object? provider = freezed,Object? cognitiveTier = freezed,Object? modelRegistryId = freezed,Object? thinkingTokens = freezed,}) {
  return _then(_ReportMetadata(
costUsd: freezed == costUsd ? _self.costUsd : costUsd // ignore: cast_nullable_to_non_nullable
as double?,durationMs: freezed == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int?,tokensUsed: freezed == tokensUsed ? _self.tokensUsed : tokensUsed // ignore: cast_nullable_to_non_nullable
as int?,llmModel: freezed == llmModel ? _self.llmModel : llmModel // ignore: cast_nullable_to_non_nullable
as String?,provider: freezed == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String?,cognitiveTier: freezed == cognitiveTier ? _self.cognitiveTier : cognitiveTier // ignore: cast_nullable_to_non_nullable
as CognitiveTier?,modelRegistryId: freezed == modelRegistryId ? _self.modelRegistryId : modelRegistryId // ignore: cast_nullable_to_non_nullable
as String?,thinkingTokens: freezed == thinkingTokens ? _self.thinkingTokens : thinkingTokens // ignore: cast_nullable_to_non_nullable
as int?,
  ));
}


}


/// @nodoc
mixin _$ReportRowItem {

@JsonKey(name: 'execution_id') String get executionId;@JsonKey(name: 'report_id') String get reportId;@JsonKey(name: 'metric_key') String get metricKey;@JsonKey(name: 'metric_label') String get metricLabel; double get score;@JsonKey(name: 'max_scale') double get maxScale; double get weight; String? get reasoning; String? get quote;
/// Create a copy of ReportRowItem
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportRowItemCopyWith<ReportRowItem> get copyWith => _$ReportRowItemCopyWithImpl<ReportRowItem>(this as ReportRowItem, _$identity);

  /// Serializes this ReportRowItem to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportRowItem(executionId: $executionId, reportId: $reportId, metricKey: $metricKey, metricLabel: $metricLabel, score: $score, maxScale: $maxScale, weight: $weight, reasoning: $reasoning, quote: $quote)';
}


}

/// @nodoc
abstract mixin class $ReportRowItemCopyWith<$Res>  {
  factory $ReportRowItemCopyWith(ReportRowItem value, $Res Function(ReportRowItem) _then) = _$ReportRowItemCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'execution_id') String executionId,@JsonKey(name: 'report_id') String reportId,@JsonKey(name: 'metric_key') String metricKey,@JsonKey(name: 'metric_label') String metricLabel, double score,@JsonKey(name: 'max_scale') double maxScale, double weight, String? reasoning, String? quote
});




}
/// @nodoc
class _$ReportRowItemCopyWithImpl<$Res>
    implements $ReportRowItemCopyWith<$Res> {
  _$ReportRowItemCopyWithImpl(this._self, this._then);

  final ReportRowItem _self;
  final $Res Function(ReportRowItem) _then;

/// Create a copy of ReportRowItem
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? executionId = null,Object? reportId = null,Object? metricKey = null,Object? metricLabel = null,Object? score = null,Object? maxScale = null,Object? weight = null,Object? reasoning = freezed,Object? quote = freezed,}) {
  return _then(_self.copyWith(
executionId: null == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String,reportId: null == reportId ? _self.reportId : reportId // ignore: cast_nullable_to_non_nullable
as String,metricKey: null == metricKey ? _self.metricKey : metricKey // ignore: cast_nullable_to_non_nullable
as String,metricLabel: null == metricLabel ? _self.metricLabel : metricLabel // ignore: cast_nullable_to_non_nullable
as String,score: null == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as double,maxScale: null == maxScale ? _self.maxScale : maxScale // ignore: cast_nullable_to_non_nullable
as double,weight: null == weight ? _self.weight : weight // ignore: cast_nullable_to_non_nullable
as double,reasoning: freezed == reasoning ? _self.reasoning : reasoning // ignore: cast_nullable_to_non_nullable
as String?,quote: freezed == quote ? _self.quote : quote // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [ReportRowItem].
extension ReportRowItemPatterns on ReportRowItem {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportRowItem value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportRowItem() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportRowItem value)  $default,){
final _that = this;
switch (_that) {
case _ReportRowItem():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportRowItem value)?  $default,){
final _that = this;
switch (_that) {
case _ReportRowItem() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'report_id')  String reportId, @JsonKey(name: 'metric_key')  String metricKey, @JsonKey(name: 'metric_label')  String metricLabel,  double score, @JsonKey(name: 'max_scale')  double maxScale,  double weight,  String? reasoning,  String? quote)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportRowItem() when $default != null:
return $default(_that.executionId,_that.reportId,_that.metricKey,_that.metricLabel,_that.score,_that.maxScale,_that.weight,_that.reasoning,_that.quote);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'report_id')  String reportId, @JsonKey(name: 'metric_key')  String metricKey, @JsonKey(name: 'metric_label')  String metricLabel,  double score, @JsonKey(name: 'max_scale')  double maxScale,  double weight,  String? reasoning,  String? quote)  $default,) {final _that = this;
switch (_that) {
case _ReportRowItem():
return $default(_that.executionId,_that.reportId,_that.metricKey,_that.metricLabel,_that.score,_that.maxScale,_that.weight,_that.reasoning,_that.quote);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'report_id')  String reportId, @JsonKey(name: 'metric_key')  String metricKey, @JsonKey(name: 'metric_label')  String metricLabel,  double score, @JsonKey(name: 'max_scale')  double maxScale,  double weight,  String? reasoning,  String? quote)?  $default,) {final _that = this;
switch (_that) {
case _ReportRowItem() when $default != null:
return $default(_that.executionId,_that.reportId,_that.metricKey,_that.metricLabel,_that.score,_that.maxScale,_that.weight,_that.reasoning,_that.quote);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportRowItem extends ReportRowItem {
  const _ReportRowItem({@JsonKey(name: 'execution_id') required this.executionId, @JsonKey(name: 'report_id') required this.reportId, @JsonKey(name: 'metric_key') required this.metricKey, @JsonKey(name: 'metric_label') required this.metricLabel, required this.score, @JsonKey(name: 'max_scale') required this.maxScale, required this.weight, this.reasoning, this.quote}): super._();
  factory _ReportRowItem.fromJson(Map<String, dynamic> json) => _$ReportRowItemFromJson(json);

@override@JsonKey(name: 'execution_id') final  String executionId;
@override@JsonKey(name: 'report_id') final  String reportId;
@override@JsonKey(name: 'metric_key') final  String metricKey;
@override@JsonKey(name: 'metric_label') final  String metricLabel;
@override final  double score;
@override@JsonKey(name: 'max_scale') final  double maxScale;
@override final  double weight;
@override final  String? reasoning;
@override final  String? quote;

/// Create a copy of ReportRowItem
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportRowItemCopyWith<_ReportRowItem> get copyWith => __$ReportRowItemCopyWithImpl<_ReportRowItem>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportRowItemToJson(this, );
}



@override
String toString() {
  return 'ReportRowItem(executionId: $executionId, reportId: $reportId, metricKey: $metricKey, metricLabel: $metricLabel, score: $score, maxScale: $maxScale, weight: $weight, reasoning: $reasoning, quote: $quote)';
}


}

/// @nodoc
abstract mixin class _$ReportRowItemCopyWith<$Res> implements $ReportRowItemCopyWith<$Res> {
  factory _$ReportRowItemCopyWith(_ReportRowItem value, $Res Function(_ReportRowItem) _then) = __$ReportRowItemCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'execution_id') String executionId,@JsonKey(name: 'report_id') String reportId,@JsonKey(name: 'metric_key') String metricKey,@JsonKey(name: 'metric_label') String metricLabel, double score,@JsonKey(name: 'max_scale') double maxScale, double weight, String? reasoning, String? quote
});




}
/// @nodoc
class __$ReportRowItemCopyWithImpl<$Res>
    implements _$ReportRowItemCopyWith<$Res> {
  __$ReportRowItemCopyWithImpl(this._self, this._then);

  final _ReportRowItem _self;
  final $Res Function(_ReportRowItem) _then;

/// Create a copy of ReportRowItem
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? executionId = null,Object? reportId = null,Object? metricKey = null,Object? metricLabel = null,Object? score = null,Object? maxScale = null,Object? weight = null,Object? reasoning = freezed,Object? quote = freezed,}) {
  return _then(_ReportRowItem(
executionId: null == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String,reportId: null == reportId ? _self.reportId : reportId // ignore: cast_nullable_to_non_nullable
as String,metricKey: null == metricKey ? _self.metricKey : metricKey // ignore: cast_nullable_to_non_nullable
as String,metricLabel: null == metricLabel ? _self.metricLabel : metricLabel // ignore: cast_nullable_to_non_nullable
as String,score: null == score ? _self.score : score // ignore: cast_nullable_to_non_nullable
as double,maxScale: null == maxScale ? _self.maxScale : maxScale // ignore: cast_nullable_to_non_nullable
as double,weight: null == weight ? _self.weight : weight // ignore: cast_nullable_to_non_nullable
as double,reasoning: freezed == reasoning ? _self.reasoning : reasoning // ignore: cast_nullable_to_non_nullable
as String?,quote: freezed == quote ? _self.quote : quote // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}


/// @nodoc
mixin _$ReportArtifact {

 String get id;@JsonKey(name: 'execution_id') String get executionId;@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'profile_id') String get profileId; String get locale; String get title; ReportStatus get status;@JsonKey(name: 'storage_paths') ReportStoragePaths get storagePaths;@JsonKey(name: 'metadata') ReportMetadata get metadata;@JsonKey(name: 'custom_preface_md') String? get customPrefaceMd;@JsonKey(name: 'error_message') String? get errorMessage;@JsonKey(name: 'created_at') DateTime get createdAt;@JsonKey(name: 'updated_at') DateTime get updatedAt;
/// Create a copy of ReportArtifact
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportArtifactCopyWith<ReportArtifact> get copyWith => _$ReportArtifactCopyWithImpl<ReportArtifact>(this as ReportArtifact, _$identity);

  /// Serializes this ReportArtifact to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportArtifact(id: $id, executionId: $executionId, workflowId: $workflowId, profileId: $profileId, locale: $locale, title: $title, status: $status, storagePaths: $storagePaths, metadata: $metadata, customPrefaceMd: $customPrefaceMd, errorMessage: $errorMessage, createdAt: $createdAt, updatedAt: $updatedAt)';
}


}

/// @nodoc
abstract mixin class $ReportArtifactCopyWith<$Res>  {
  factory $ReportArtifactCopyWith(ReportArtifact value, $Res Function(ReportArtifact) _then) = _$ReportArtifactCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'execution_id') String executionId,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'profile_id') String profileId, String locale, String title, ReportStatus status,@JsonKey(name: 'storage_paths') ReportStoragePaths storagePaths,@JsonKey(name: 'metadata') ReportMetadata metadata,@JsonKey(name: 'custom_preface_md') String? customPrefaceMd,@JsonKey(name: 'error_message') String? errorMessage,@JsonKey(name: 'created_at') DateTime createdAt,@JsonKey(name: 'updated_at') DateTime updatedAt
});


$ReportStoragePathsCopyWith<$Res> get storagePaths;$ReportMetadataCopyWith<$Res> get metadata;

}
/// @nodoc
class _$ReportArtifactCopyWithImpl<$Res>
    implements $ReportArtifactCopyWith<$Res> {
  _$ReportArtifactCopyWithImpl(this._self, this._then);

  final ReportArtifact _self;
  final $Res Function(ReportArtifact) _then;

/// Create a copy of ReportArtifact
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? executionId = null,Object? workflowId = null,Object? profileId = null,Object? locale = null,Object? title = null,Object? status = null,Object? storagePaths = null,Object? metadata = null,Object? customPrefaceMd = freezed,Object? errorMessage = freezed,Object? createdAt = null,Object? updatedAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,executionId: null == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,profileId: null == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String,locale: null == locale ? _self.locale : locale // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ReportStatus,storagePaths: null == storagePaths ? _self.storagePaths : storagePaths // ignore: cast_nullable_to_non_nullable
as ReportStoragePaths,metadata: null == metadata ? _self.metadata : metadata // ignore: cast_nullable_to_non_nullable
as ReportMetadata,customPrefaceMd: freezed == customPrefaceMd ? _self.customPrefaceMd : customPrefaceMd // ignore: cast_nullable_to_non_nullable
as String?,errorMessage: freezed == errorMessage ? _self.errorMessage : errorMessage // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}
/// Create a copy of ReportArtifact
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReportStoragePathsCopyWith<$Res> get storagePaths {
  
  return $ReportStoragePathsCopyWith<$Res>(_self.storagePaths, (value) {
    return _then(_self.copyWith(storagePaths: value));
  });
}/// Create a copy of ReportArtifact
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReportMetadataCopyWith<$Res> get metadata {
  
  return $ReportMetadataCopyWith<$Res>(_self.metadata, (value) {
    return _then(_self.copyWith(metadata: value));
  });
}
}


/// Adds pattern-matching-related methods to [ReportArtifact].
extension ReportArtifactPatterns on ReportArtifact {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportArtifact value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportArtifact() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportArtifact value)  $default,){
final _that = this;
switch (_that) {
case _ReportArtifact():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportArtifact value)?  $default,){
final _that = this;
switch (_that) {
case _ReportArtifact() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'profile_id')  String profileId,  String locale,  String title,  ReportStatus status, @JsonKey(name: 'storage_paths')  ReportStoragePaths storagePaths, @JsonKey(name: 'metadata')  ReportMetadata metadata, @JsonKey(name: 'custom_preface_md')  String? customPrefaceMd, @JsonKey(name: 'error_message')  String? errorMessage, @JsonKey(name: 'created_at')  DateTime createdAt, @JsonKey(name: 'updated_at')  DateTime updatedAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportArtifact() when $default != null:
return $default(_that.id,_that.executionId,_that.workflowId,_that.profileId,_that.locale,_that.title,_that.status,_that.storagePaths,_that.metadata,_that.customPrefaceMd,_that.errorMessage,_that.createdAt,_that.updatedAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'profile_id')  String profileId,  String locale,  String title,  ReportStatus status, @JsonKey(name: 'storage_paths')  ReportStoragePaths storagePaths, @JsonKey(name: 'metadata')  ReportMetadata metadata, @JsonKey(name: 'custom_preface_md')  String? customPrefaceMd, @JsonKey(name: 'error_message')  String? errorMessage, @JsonKey(name: 'created_at')  DateTime createdAt, @JsonKey(name: 'updated_at')  DateTime updatedAt)  $default,) {final _that = this;
switch (_that) {
case _ReportArtifact():
return $default(_that.id,_that.executionId,_that.workflowId,_that.profileId,_that.locale,_that.title,_that.status,_that.storagePaths,_that.metadata,_that.customPrefaceMd,_that.errorMessage,_that.createdAt,_that.updatedAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'profile_id')  String profileId,  String locale,  String title,  ReportStatus status, @JsonKey(name: 'storage_paths')  ReportStoragePaths storagePaths, @JsonKey(name: 'metadata')  ReportMetadata metadata, @JsonKey(name: 'custom_preface_md')  String? customPrefaceMd, @JsonKey(name: 'error_message')  String? errorMessage, @JsonKey(name: 'created_at')  DateTime createdAt, @JsonKey(name: 'updated_at')  DateTime updatedAt)?  $default,) {final _that = this;
switch (_that) {
case _ReportArtifact() when $default != null:
return $default(_that.id,_that.executionId,_that.workflowId,_that.profileId,_that.locale,_that.title,_that.status,_that.storagePaths,_that.metadata,_that.customPrefaceMd,_that.errorMessage,_that.createdAt,_that.updatedAt);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportArtifact extends ReportArtifact {
  const _ReportArtifact({required this.id, @JsonKey(name: 'execution_id') required this.executionId, @JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'profile_id') required this.profileId, required this.locale, required this.title, required this.status, @JsonKey(name: 'storage_paths') this.storagePaths = const ReportStoragePaths(), @JsonKey(name: 'metadata') this.metadata = const ReportMetadata(), @JsonKey(name: 'custom_preface_md') this.customPrefaceMd, @JsonKey(name: 'error_message') this.errorMessage, @JsonKey(name: 'created_at') required this.createdAt, @JsonKey(name: 'updated_at') required this.updatedAt}): super._();
  factory _ReportArtifact.fromJson(Map<String, dynamic> json) => _$ReportArtifactFromJson(json);

@override final  String id;
@override@JsonKey(name: 'execution_id') final  String executionId;
@override@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'profile_id') final  String profileId;
@override final  String locale;
@override final  String title;
@override final  ReportStatus status;
@override@JsonKey(name: 'storage_paths') final  ReportStoragePaths storagePaths;
@override@JsonKey(name: 'metadata') final  ReportMetadata metadata;
@override@JsonKey(name: 'custom_preface_md') final  String? customPrefaceMd;
@override@JsonKey(name: 'error_message') final  String? errorMessage;
@override@JsonKey(name: 'created_at') final  DateTime createdAt;
@override@JsonKey(name: 'updated_at') final  DateTime updatedAt;

/// Create a copy of ReportArtifact
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportArtifactCopyWith<_ReportArtifact> get copyWith => __$ReportArtifactCopyWithImpl<_ReportArtifact>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportArtifactToJson(this, );
}



@override
String toString() {
  return 'ReportArtifact(id: $id, executionId: $executionId, workflowId: $workflowId, profileId: $profileId, locale: $locale, title: $title, status: $status, storagePaths: $storagePaths, metadata: $metadata, customPrefaceMd: $customPrefaceMd, errorMessage: $errorMessage, createdAt: $createdAt, updatedAt: $updatedAt)';
}


}

/// @nodoc
abstract mixin class _$ReportArtifactCopyWith<$Res> implements $ReportArtifactCopyWith<$Res> {
  factory _$ReportArtifactCopyWith(_ReportArtifact value, $Res Function(_ReportArtifact) _then) = __$ReportArtifactCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'execution_id') String executionId,@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'profile_id') String profileId, String locale, String title, ReportStatus status,@JsonKey(name: 'storage_paths') ReportStoragePaths storagePaths,@JsonKey(name: 'metadata') ReportMetadata metadata,@JsonKey(name: 'custom_preface_md') String? customPrefaceMd,@JsonKey(name: 'error_message') String? errorMessage,@JsonKey(name: 'created_at') DateTime createdAt,@JsonKey(name: 'updated_at') DateTime updatedAt
});


@override $ReportStoragePathsCopyWith<$Res> get storagePaths;@override $ReportMetadataCopyWith<$Res> get metadata;

}
/// @nodoc
class __$ReportArtifactCopyWithImpl<$Res>
    implements _$ReportArtifactCopyWith<$Res> {
  __$ReportArtifactCopyWithImpl(this._self, this._then);

  final _ReportArtifact _self;
  final $Res Function(_ReportArtifact) _then;

/// Create a copy of ReportArtifact
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? executionId = null,Object? workflowId = null,Object? profileId = null,Object? locale = null,Object? title = null,Object? status = null,Object? storagePaths = null,Object? metadata = null,Object? customPrefaceMd = freezed,Object? errorMessage = freezed,Object? createdAt = null,Object? updatedAt = null,}) {
  return _then(_ReportArtifact(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,executionId: null == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,profileId: null == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String,locale: null == locale ? _self.locale : locale // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ReportStatus,storagePaths: null == storagePaths ? _self.storagePaths : storagePaths // ignore: cast_nullable_to_non_nullable
as ReportStoragePaths,metadata: null == metadata ? _self.metadata : metadata // ignore: cast_nullable_to_non_nullable
as ReportMetadata,customPrefaceMd: freezed == customPrefaceMd ? _self.customPrefaceMd : customPrefaceMd // ignore: cast_nullable_to_non_nullable
as String?,errorMessage: freezed == errorMessage ? _self.errorMessage : errorMessage // ignore: cast_nullable_to_non_nullable
as String?,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

/// Create a copy of ReportArtifact
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReportStoragePathsCopyWith<$Res> get storagePaths {
  
  return $ReportStoragePathsCopyWith<$Res>(_self.storagePaths, (value) {
    return _then(_self.copyWith(storagePaths: value));
  });
}/// Create a copy of ReportArtifact
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$ReportMetadataCopyWith<$Res> get metadata {
  
  return $ReportMetadataCopyWith<$Res>(_self.metadata, (value) {
    return _then(_self.copyWith(metadata: value));
  });
}
}


/// @nodoc
mixin _$ReportArtifactSummary {

 String get id;@JsonKey(name: 'execution_id') String get executionId;@JsonKey(name: 'profile_id') String get profileId; String get locale; String get title; ReportStatus get status;@JsonKey(name: 'created_at') DateTime get createdAt;@JsonKey(name: 'updated_at') DateTime get updatedAt;
/// Create a copy of ReportArtifactSummary
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportArtifactSummaryCopyWith<ReportArtifactSummary> get copyWith => _$ReportArtifactSummaryCopyWithImpl<ReportArtifactSummary>(this as ReportArtifactSummary, _$identity);

  /// Serializes this ReportArtifactSummary to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportArtifactSummary(id: $id, executionId: $executionId, profileId: $profileId, locale: $locale, title: $title, status: $status, createdAt: $createdAt, updatedAt: $updatedAt)';
}


}

/// @nodoc
abstract mixin class $ReportArtifactSummaryCopyWith<$Res>  {
  factory $ReportArtifactSummaryCopyWith(ReportArtifactSummary value, $Res Function(ReportArtifactSummary) _then) = _$ReportArtifactSummaryCopyWithImpl;
@useResult
$Res call({
 String id,@JsonKey(name: 'execution_id') String executionId,@JsonKey(name: 'profile_id') String profileId, String locale, String title, ReportStatus status,@JsonKey(name: 'created_at') DateTime createdAt,@JsonKey(name: 'updated_at') DateTime updatedAt
});




}
/// @nodoc
class _$ReportArtifactSummaryCopyWithImpl<$Res>
    implements $ReportArtifactSummaryCopyWith<$Res> {
  _$ReportArtifactSummaryCopyWithImpl(this._self, this._then);

  final ReportArtifactSummary _self;
  final $Res Function(ReportArtifactSummary) _then;

/// Create a copy of ReportArtifactSummary
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? executionId = null,Object? profileId = null,Object? locale = null,Object? title = null,Object? status = null,Object? createdAt = null,Object? updatedAt = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,executionId: null == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String,profileId: null == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String,locale: null == locale ? _self.locale : locale // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ReportStatus,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}

}


/// Adds pattern-matching-related methods to [ReportArtifactSummary].
extension ReportArtifactSummaryPatterns on ReportArtifactSummary {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportArtifactSummary value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportArtifactSummary() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportArtifactSummary value)  $default,){
final _that = this;
switch (_that) {
case _ReportArtifactSummary():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportArtifactSummary value)?  $default,){
final _that = this;
switch (_that) {
case _ReportArtifactSummary() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'profile_id')  String profileId,  String locale,  String title,  ReportStatus status, @JsonKey(name: 'created_at')  DateTime createdAt, @JsonKey(name: 'updated_at')  DateTime updatedAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportArtifactSummary() when $default != null:
return $default(_that.id,_that.executionId,_that.profileId,_that.locale,_that.title,_that.status,_that.createdAt,_that.updatedAt);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id, @JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'profile_id')  String profileId,  String locale,  String title,  ReportStatus status, @JsonKey(name: 'created_at')  DateTime createdAt, @JsonKey(name: 'updated_at')  DateTime updatedAt)  $default,) {final _that = this;
switch (_that) {
case _ReportArtifactSummary():
return $default(_that.id,_that.executionId,_that.profileId,_that.locale,_that.title,_that.status,_that.createdAt,_that.updatedAt);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id, @JsonKey(name: 'execution_id')  String executionId, @JsonKey(name: 'profile_id')  String profileId,  String locale,  String title,  ReportStatus status, @JsonKey(name: 'created_at')  DateTime createdAt, @JsonKey(name: 'updated_at')  DateTime updatedAt)?  $default,) {final _that = this;
switch (_that) {
case _ReportArtifactSummary() when $default != null:
return $default(_that.id,_that.executionId,_that.profileId,_that.locale,_that.title,_that.status,_that.createdAt,_that.updatedAt);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportArtifactSummary extends ReportArtifactSummary {
  const _ReportArtifactSummary({required this.id, @JsonKey(name: 'execution_id') required this.executionId, @JsonKey(name: 'profile_id') required this.profileId, required this.locale, required this.title, required this.status, @JsonKey(name: 'created_at') required this.createdAt, @JsonKey(name: 'updated_at') required this.updatedAt}): super._();
  factory _ReportArtifactSummary.fromJson(Map<String, dynamic> json) => _$ReportArtifactSummaryFromJson(json);

@override final  String id;
@override@JsonKey(name: 'execution_id') final  String executionId;
@override@JsonKey(name: 'profile_id') final  String profileId;
@override final  String locale;
@override final  String title;
@override final  ReportStatus status;
@override@JsonKey(name: 'created_at') final  DateTime createdAt;
@override@JsonKey(name: 'updated_at') final  DateTime updatedAt;

/// Create a copy of ReportArtifactSummary
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportArtifactSummaryCopyWith<_ReportArtifactSummary> get copyWith => __$ReportArtifactSummaryCopyWithImpl<_ReportArtifactSummary>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportArtifactSummaryToJson(this, );
}



@override
String toString() {
  return 'ReportArtifactSummary(id: $id, executionId: $executionId, profileId: $profileId, locale: $locale, title: $title, status: $status, createdAt: $createdAt, updatedAt: $updatedAt)';
}


}

/// @nodoc
abstract mixin class _$ReportArtifactSummaryCopyWith<$Res> implements $ReportArtifactSummaryCopyWith<$Res> {
  factory _$ReportArtifactSummaryCopyWith(_ReportArtifactSummary value, $Res Function(_ReportArtifactSummary) _then) = __$ReportArtifactSummaryCopyWithImpl;
@override @useResult
$Res call({
 String id,@JsonKey(name: 'execution_id') String executionId,@JsonKey(name: 'profile_id') String profileId, String locale, String title, ReportStatus status,@JsonKey(name: 'created_at') DateTime createdAt,@JsonKey(name: 'updated_at') DateTime updatedAt
});




}
/// @nodoc
class __$ReportArtifactSummaryCopyWithImpl<$Res>
    implements _$ReportArtifactSummaryCopyWith<$Res> {
  __$ReportArtifactSummaryCopyWithImpl(this._self, this._then);

  final _ReportArtifactSummary _self;
  final $Res Function(_ReportArtifactSummary) _then;

/// Create a copy of ReportArtifactSummary
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? executionId = null,Object? profileId = null,Object? locale = null,Object? title = null,Object? status = null,Object? createdAt = null,Object? updatedAt = null,}) {
  return _then(_ReportArtifactSummary(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,executionId: null == executionId ? _self.executionId : executionId // ignore: cast_nullable_to_non_nullable
as String,profileId: null == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String,locale: null == locale ? _self.locale : locale // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as ReportStatus,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as DateTime,updatedAt: null == updatedAt ? _self.updatedAt : updatedAt // ignore: cast_nullable_to_non_nullable
as DateTime,
  ));
}


}

// dart format on
