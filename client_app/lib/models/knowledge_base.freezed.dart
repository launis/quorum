// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'knowledge_base.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$IngestionStatus {

@JsonKey(name: 'job_id') String get jobId; String get status;// processing, completed, failed
 int get progress; String get stage; IngestionSummary? get result; String? get error;
/// Create a copy of IngestionStatus
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$IngestionStatusCopyWith<IngestionStatus> get copyWith => _$IngestionStatusCopyWithImpl<IngestionStatus>(this as IngestionStatus, _$identity);

  /// Serializes this IngestionStatus to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is IngestionStatus&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.status, status) || other.status == status)&&(identical(other.progress, progress) || other.progress == progress)&&(identical(other.stage, stage) || other.stage == stage)&&(identical(other.result, result) || other.result == result)&&(identical(other.error, error) || other.error == error));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,jobId,status,progress,stage,result,error);

@override
String toString() {
  return 'IngestionStatus(jobId: $jobId, status: $status, progress: $progress, stage: $stage, result: $result, error: $error)';
}


}

/// @nodoc
abstract mixin class $IngestionStatusCopyWith<$Res>  {
  factory $IngestionStatusCopyWith(IngestionStatus value, $Res Function(IngestionStatus) _then) = _$IngestionStatusCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'job_id') String jobId, String status, int progress, String stage, IngestionSummary? result, String? error
});


$IngestionSummaryCopyWith<$Res>? get result;

}
/// @nodoc
class _$IngestionStatusCopyWithImpl<$Res>
    implements $IngestionStatusCopyWith<$Res> {
  _$IngestionStatusCopyWithImpl(this._self, this._then);

  final IngestionStatus _self;
  final $Res Function(IngestionStatus) _then;

/// Create a copy of IngestionStatus
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? jobId = null,Object? status = null,Object? progress = null,Object? stage = null,Object? result = freezed,Object? error = freezed,}) {
  return _then(_self.copyWith(
jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,progress: null == progress ? _self.progress : progress // ignore: cast_nullable_to_non_nullable
as int,stage: null == stage ? _self.stage : stage // ignore: cast_nullable_to_non_nullable
as String,result: freezed == result ? _self.result : result // ignore: cast_nullable_to_non_nullable
as IngestionSummary?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of IngestionStatus
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$IngestionSummaryCopyWith<$Res>? get result {
    if (_self.result == null) {
    return null;
  }

  return $IngestionSummaryCopyWith<$Res>(_self.result!, (value) {
    return _then(_self.copyWith(result: value));
  });
}
}


/// Adds pattern-matching-related methods to [IngestionStatus].
extension IngestionStatusPatterns on IngestionStatus {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _IngestionStatus value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _IngestionStatus() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _IngestionStatus value)  $default,){
final _that = this;
switch (_that) {
case _IngestionStatus():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _IngestionStatus value)?  $default,){
final _that = this;
switch (_that) {
case _IngestionStatus() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'job_id')  String jobId,  String status,  int progress,  String stage,  IngestionSummary? result,  String? error)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _IngestionStatus() when $default != null:
return $default(_that.jobId,_that.status,_that.progress,_that.stage,_that.result,_that.error);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'job_id')  String jobId,  String status,  int progress,  String stage,  IngestionSummary? result,  String? error)  $default,) {final _that = this;
switch (_that) {
case _IngestionStatus():
return $default(_that.jobId,_that.status,_that.progress,_that.stage,_that.result,_that.error);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'job_id')  String jobId,  String status,  int progress,  String stage,  IngestionSummary? result,  String? error)?  $default,) {final _that = this;
switch (_that) {
case _IngestionStatus() when $default != null:
return $default(_that.jobId,_that.status,_that.progress,_that.stage,_that.result,_that.error);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _IngestionStatus implements IngestionStatus {
  const _IngestionStatus({@JsonKey(name: 'job_id') required this.jobId, required this.status, required this.progress, required this.stage, this.result, this.error});
  factory _IngestionStatus.fromJson(Map<String, dynamic> json) => _$IngestionStatusFromJson(json);

@override@JsonKey(name: 'job_id') final  String jobId;
@override final  String status;
// processing, completed, failed
@override final  int progress;
@override final  String stage;
@override final  IngestionSummary? result;
@override final  String? error;

/// Create a copy of IngestionStatus
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$IngestionStatusCopyWith<_IngestionStatus> get copyWith => __$IngestionStatusCopyWithImpl<_IngestionStatus>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$IngestionStatusToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _IngestionStatus&&(identical(other.jobId, jobId) || other.jobId == jobId)&&(identical(other.status, status) || other.status == status)&&(identical(other.progress, progress) || other.progress == progress)&&(identical(other.stage, stage) || other.stage == stage)&&(identical(other.result, result) || other.result == result)&&(identical(other.error, error) || other.error == error));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,jobId,status,progress,stage,result,error);

@override
String toString() {
  return 'IngestionStatus(jobId: $jobId, status: $status, progress: $progress, stage: $stage, result: $result, error: $error)';
}


}

/// @nodoc
abstract mixin class _$IngestionStatusCopyWith<$Res> implements $IngestionStatusCopyWith<$Res> {
  factory _$IngestionStatusCopyWith(_IngestionStatus value, $Res Function(_IngestionStatus) _then) = __$IngestionStatusCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'job_id') String jobId, String status, int progress, String stage, IngestionSummary? result, String? error
});


@override $IngestionSummaryCopyWith<$Res>? get result;

}
/// @nodoc
class __$IngestionStatusCopyWithImpl<$Res>
    implements _$IngestionStatusCopyWith<$Res> {
  __$IngestionStatusCopyWithImpl(this._self, this._then);

  final _IngestionStatus _self;
  final $Res Function(_IngestionStatus) _then;

/// Create a copy of IngestionStatus
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? jobId = null,Object? status = null,Object? progress = null,Object? stage = null,Object? result = freezed,Object? error = freezed,}) {
  return _then(_IngestionStatus(
jobId: null == jobId ? _self.jobId : jobId // ignore: cast_nullable_to_non_nullable
as String,status: null == status ? _self.status : status // ignore: cast_nullable_to_non_nullable
as String,progress: null == progress ? _self.progress : progress // ignore: cast_nullable_to_non_nullable
as int,stage: null == stage ? _self.stage : stage // ignore: cast_nullable_to_non_nullable
as String,result: freezed == result ? _self.result : result // ignore: cast_nullable_to_non_nullable
as IngestionSummary?,error: freezed == error ? _self.error : error // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of IngestionStatus
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$IngestionSummaryCopyWith<$Res>? get result {
    if (_self.result == null) {
    return null;
  }

  return $IngestionSummaryCopyWith<$Res>(_self.result!, (value) {
    return _then(_self.copyWith(result: value));
  });
}
}


/// @nodoc
mixin _$IngestionSummary {

@JsonKey(name: 'concepts_count') int get conceptsCount;@JsonKey(name: 'references_count') int get referencesCount;@JsonKey(name: 'claims_count') int get claimsCount;@JsonKey(name: 'file_size') int get fileSize; String get filename;
/// Create a copy of IngestionSummary
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$IngestionSummaryCopyWith<IngestionSummary> get copyWith => _$IngestionSummaryCopyWithImpl<IngestionSummary>(this as IngestionSummary, _$identity);

  /// Serializes this IngestionSummary to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is IngestionSummary&&(identical(other.conceptsCount, conceptsCount) || other.conceptsCount == conceptsCount)&&(identical(other.referencesCount, referencesCount) || other.referencesCount == referencesCount)&&(identical(other.claimsCount, claimsCount) || other.claimsCount == claimsCount)&&(identical(other.fileSize, fileSize) || other.fileSize == fileSize)&&(identical(other.filename, filename) || other.filename == filename));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,conceptsCount,referencesCount,claimsCount,fileSize,filename);

@override
String toString() {
  return 'IngestionSummary(conceptsCount: $conceptsCount, referencesCount: $referencesCount, claimsCount: $claimsCount, fileSize: $fileSize, filename: $filename)';
}


}

/// @nodoc
abstract mixin class $IngestionSummaryCopyWith<$Res>  {
  factory $IngestionSummaryCopyWith(IngestionSummary value, $Res Function(IngestionSummary) _then) = _$IngestionSummaryCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'concepts_count') int conceptsCount,@JsonKey(name: 'references_count') int referencesCount,@JsonKey(name: 'claims_count') int claimsCount,@JsonKey(name: 'file_size') int fileSize, String filename
});




}
/// @nodoc
class _$IngestionSummaryCopyWithImpl<$Res>
    implements $IngestionSummaryCopyWith<$Res> {
  _$IngestionSummaryCopyWithImpl(this._self, this._then);

  final IngestionSummary _self;
  final $Res Function(IngestionSummary) _then;

/// Create a copy of IngestionSummary
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? conceptsCount = null,Object? referencesCount = null,Object? claimsCount = null,Object? fileSize = null,Object? filename = null,}) {
  return _then(_self.copyWith(
conceptsCount: null == conceptsCount ? _self.conceptsCount : conceptsCount // ignore: cast_nullable_to_non_nullable
as int,referencesCount: null == referencesCount ? _self.referencesCount : referencesCount // ignore: cast_nullable_to_non_nullable
as int,claimsCount: null == claimsCount ? _self.claimsCount : claimsCount // ignore: cast_nullable_to_non_nullable
as int,fileSize: null == fileSize ? _self.fileSize : fileSize // ignore: cast_nullable_to_non_nullable
as int,filename: null == filename ? _self.filename : filename // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [IngestionSummary].
extension IngestionSummaryPatterns on IngestionSummary {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _IngestionSummary value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _IngestionSummary() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _IngestionSummary value)  $default,){
final _that = this;
switch (_that) {
case _IngestionSummary():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _IngestionSummary value)?  $default,){
final _that = this;
switch (_that) {
case _IngestionSummary() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'concepts_count')  int conceptsCount, @JsonKey(name: 'references_count')  int referencesCount, @JsonKey(name: 'claims_count')  int claimsCount, @JsonKey(name: 'file_size')  int fileSize,  String filename)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _IngestionSummary() when $default != null:
return $default(_that.conceptsCount,_that.referencesCount,_that.claimsCount,_that.fileSize,_that.filename);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'concepts_count')  int conceptsCount, @JsonKey(name: 'references_count')  int referencesCount, @JsonKey(name: 'claims_count')  int claimsCount, @JsonKey(name: 'file_size')  int fileSize,  String filename)  $default,) {final _that = this;
switch (_that) {
case _IngestionSummary():
return $default(_that.conceptsCount,_that.referencesCount,_that.claimsCount,_that.fileSize,_that.filename);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'concepts_count')  int conceptsCount, @JsonKey(name: 'references_count')  int referencesCount, @JsonKey(name: 'claims_count')  int claimsCount, @JsonKey(name: 'file_size')  int fileSize,  String filename)?  $default,) {final _that = this;
switch (_that) {
case _IngestionSummary() when $default != null:
return $default(_that.conceptsCount,_that.referencesCount,_that.claimsCount,_that.fileSize,_that.filename);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _IngestionSummary implements IngestionSummary {
  const _IngestionSummary({@JsonKey(name: 'concepts_count') this.conceptsCount = 0, @JsonKey(name: 'references_count') this.referencesCount = 0, @JsonKey(name: 'claims_count') this.claimsCount = 0, @JsonKey(name: 'file_size') this.fileSize = 0, required this.filename});
  factory _IngestionSummary.fromJson(Map<String, dynamic> json) => _$IngestionSummaryFromJson(json);

@override@JsonKey(name: 'concepts_count') final  int conceptsCount;
@override@JsonKey(name: 'references_count') final  int referencesCount;
@override@JsonKey(name: 'claims_count') final  int claimsCount;
@override@JsonKey(name: 'file_size') final  int fileSize;
@override final  String filename;

/// Create a copy of IngestionSummary
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$IngestionSummaryCopyWith<_IngestionSummary> get copyWith => __$IngestionSummaryCopyWithImpl<_IngestionSummary>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$IngestionSummaryToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _IngestionSummary&&(identical(other.conceptsCount, conceptsCount) || other.conceptsCount == conceptsCount)&&(identical(other.referencesCount, referencesCount) || other.referencesCount == referencesCount)&&(identical(other.claimsCount, claimsCount) || other.claimsCount == claimsCount)&&(identical(other.fileSize, fileSize) || other.fileSize == fileSize)&&(identical(other.filename, filename) || other.filename == filename));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,conceptsCount,referencesCount,claimsCount,fileSize,filename);

@override
String toString() {
  return 'IngestionSummary(conceptsCount: $conceptsCount, referencesCount: $referencesCount, claimsCount: $claimsCount, fileSize: $fileSize, filename: $filename)';
}


}

/// @nodoc
abstract mixin class _$IngestionSummaryCopyWith<$Res> implements $IngestionSummaryCopyWith<$Res> {
  factory _$IngestionSummaryCopyWith(_IngestionSummary value, $Res Function(_IngestionSummary) _then) = __$IngestionSummaryCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'concepts_count') int conceptsCount,@JsonKey(name: 'references_count') int referencesCount,@JsonKey(name: 'claims_count') int claimsCount,@JsonKey(name: 'file_size') int fileSize, String filename
});




}
/// @nodoc
class __$IngestionSummaryCopyWithImpl<$Res>
    implements _$IngestionSummaryCopyWith<$Res> {
  __$IngestionSummaryCopyWithImpl(this._self, this._then);

  final _IngestionSummary _self;
  final $Res Function(_IngestionSummary) _then;

/// Create a copy of IngestionSummary
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? conceptsCount = null,Object? referencesCount = null,Object? claimsCount = null,Object? fileSize = null,Object? filename = null,}) {
  return _then(_IngestionSummary(
conceptsCount: null == conceptsCount ? _self.conceptsCount : conceptsCount // ignore: cast_nullable_to_non_nullable
as int,referencesCount: null == referencesCount ? _self.referencesCount : referencesCount // ignore: cast_nullable_to_non_nullable
as int,claimsCount: null == claimsCount ? _self.claimsCount : claimsCount // ignore: cast_nullable_to_non_nullable
as int,fileSize: null == fileSize ? _self.fileSize : fileSize // ignore: cast_nullable_to_non_nullable
as int,filename: null == filename ? _self.filename : filename // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}


/// @nodoc
mixin _$KnowledgeModelStrategy {

 String get id; String? get slug;@JsonKey(name: 'model_name') String get modelName; String? get provider;
/// Create a copy of KnowledgeModelStrategy
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$KnowledgeModelStrategyCopyWith<KnowledgeModelStrategy> get copyWith => _$KnowledgeModelStrategyCopyWithImpl<KnowledgeModelStrategy>(this as KnowledgeModelStrategy, _$identity);

  /// Serializes this KnowledgeModelStrategy to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is KnowledgeModelStrategy&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.modelName, modelName) || other.modelName == modelName)&&(identical(other.provider, provider) || other.provider == provider));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slug,modelName,provider);

@override
String toString() {
  return 'KnowledgeModelStrategy(id: $id, slug: $slug, modelName: $modelName, provider: $provider)';
}


}

/// @nodoc
abstract mixin class $KnowledgeModelStrategyCopyWith<$Res>  {
  factory $KnowledgeModelStrategyCopyWith(KnowledgeModelStrategy value, $Res Function(KnowledgeModelStrategy) _then) = _$KnowledgeModelStrategyCopyWithImpl;
@useResult
$Res call({
 String id, String? slug,@JsonKey(name: 'model_name') String modelName, String? provider
});




}
/// @nodoc
class _$KnowledgeModelStrategyCopyWithImpl<$Res>
    implements $KnowledgeModelStrategyCopyWith<$Res> {
  _$KnowledgeModelStrategyCopyWithImpl(this._self, this._then);

  final KnowledgeModelStrategy _self;
  final $Res Function(KnowledgeModelStrategy) _then;

/// Create a copy of KnowledgeModelStrategy
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = freezed,Object? modelName = null,Object? provider = freezed,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,modelName: null == modelName ? _self.modelName : modelName // ignore: cast_nullable_to_non_nullable
as String,provider: freezed == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

}


/// Adds pattern-matching-related methods to [KnowledgeModelStrategy].
extension KnowledgeModelStrategyPatterns on KnowledgeModelStrategy {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _KnowledgeModelStrategy value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _KnowledgeModelStrategy() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _KnowledgeModelStrategy value)  $default,){
final _that = this;
switch (_that) {
case _KnowledgeModelStrategy():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _KnowledgeModelStrategy value)?  $default,){
final _that = this;
switch (_that) {
case _KnowledgeModelStrategy() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  String? slug, @JsonKey(name: 'model_name')  String modelName,  String? provider)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _KnowledgeModelStrategy() when $default != null:
return $default(_that.id,_that.slug,_that.modelName,_that.provider);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  String? slug, @JsonKey(name: 'model_name')  String modelName,  String? provider)  $default,) {final _that = this;
switch (_that) {
case _KnowledgeModelStrategy():
return $default(_that.id,_that.slug,_that.modelName,_that.provider);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  String? slug, @JsonKey(name: 'model_name')  String modelName,  String? provider)?  $default,) {final _that = this;
switch (_that) {
case _KnowledgeModelStrategy() when $default != null:
return $default(_that.id,_that.slug,_that.modelName,_that.provider);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _KnowledgeModelStrategy implements KnowledgeModelStrategy {
  const _KnowledgeModelStrategy({required this.id, this.slug, @JsonKey(name: 'model_name') required this.modelName, this.provider});
  factory _KnowledgeModelStrategy.fromJson(Map<String, dynamic> json) => _$KnowledgeModelStrategyFromJson(json);

@override final  String id;
@override final  String? slug;
@override@JsonKey(name: 'model_name') final  String modelName;
@override final  String? provider;

/// Create a copy of KnowledgeModelStrategy
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$KnowledgeModelStrategyCopyWith<_KnowledgeModelStrategy> get copyWith => __$KnowledgeModelStrategyCopyWithImpl<_KnowledgeModelStrategy>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$KnowledgeModelStrategyToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _KnowledgeModelStrategy&&(identical(other.id, id) || other.id == id)&&(identical(other.slug, slug) || other.slug == slug)&&(identical(other.modelName, modelName) || other.modelName == modelName)&&(identical(other.provider, provider) || other.provider == provider));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,slug,modelName,provider);

@override
String toString() {
  return 'KnowledgeModelStrategy(id: $id, slug: $slug, modelName: $modelName, provider: $provider)';
}


}

/// @nodoc
abstract mixin class _$KnowledgeModelStrategyCopyWith<$Res> implements $KnowledgeModelStrategyCopyWith<$Res> {
  factory _$KnowledgeModelStrategyCopyWith(_KnowledgeModelStrategy value, $Res Function(_KnowledgeModelStrategy) _then) = __$KnowledgeModelStrategyCopyWithImpl;
@override @useResult
$Res call({
 String id, String? slug,@JsonKey(name: 'model_name') String modelName, String? provider
});




}
/// @nodoc
class __$KnowledgeModelStrategyCopyWithImpl<$Res>
    implements _$KnowledgeModelStrategyCopyWith<$Res> {
  __$KnowledgeModelStrategyCopyWithImpl(this._self, this._then);

  final _KnowledgeModelStrategy _self;
  final $Res Function(_KnowledgeModelStrategy) _then;

/// Create a copy of KnowledgeModelStrategy
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = freezed,Object? modelName = null,Object? provider = freezed,}) {
  return _then(_KnowledgeModelStrategy(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: freezed == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String?,modelName: null == modelName ? _self.modelName : modelName // ignore: cast_nullable_to_non_nullable
as String,provider: freezed == provider ? _self.provider : provider // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}


}

// dart format on
