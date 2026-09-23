// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'prompt_block_simulation.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$PromptBlockSimulationRequest {

 PromptBlock get block;@JsonKey(name: 'mock_inputs') Map<String, dynamic> get mockInputs;@JsonKey(name: 'target_scale_score') int? get targetScaleScore;@JsonKey(name: 'target_locale') String get targetLocale;@JsonKey(name: 'context_text') String get contextText;
/// Create a copy of PromptBlockSimulationRequest
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PromptBlockSimulationRequestCopyWith<PromptBlockSimulationRequest> get copyWith => _$PromptBlockSimulationRequestCopyWithImpl<PromptBlockSimulationRequest>(this as PromptBlockSimulationRequest, _$identity);

  /// Serializes this PromptBlockSimulationRequest to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'PromptBlockSimulationRequest(block: $block, mockInputs: $mockInputs, targetScaleScore: $targetScaleScore, targetLocale: $targetLocale, contextText: $contextText)';
}


}

/// @nodoc
abstract mixin class $PromptBlockSimulationRequestCopyWith<$Res>  {
  factory $PromptBlockSimulationRequestCopyWith(PromptBlockSimulationRequest value, $Res Function(PromptBlockSimulationRequest) _then) = _$PromptBlockSimulationRequestCopyWithImpl;
@useResult
$Res call({
 PromptBlock block,@JsonKey(name: 'mock_inputs') Map<String, dynamic> mockInputs,@JsonKey(name: 'target_scale_score') int? targetScaleScore,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'context_text') String contextText
});


$PromptBlockCopyWith<$Res> get block;

}
/// @nodoc
class _$PromptBlockSimulationRequestCopyWithImpl<$Res>
    implements $PromptBlockSimulationRequestCopyWith<$Res> {
  _$PromptBlockSimulationRequestCopyWithImpl(this._self, this._then);

  final PromptBlockSimulationRequest _self;
  final $Res Function(PromptBlockSimulationRequest) _then;

/// Create a copy of PromptBlockSimulationRequest
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? block = null,Object? mockInputs = null,Object? targetScaleScore = freezed,Object? targetLocale = null,Object? contextText = null,}) {
  return _then(_self.copyWith(
block: null == block ? _self.block : block // ignore: cast_nullable_to_non_nullable
as PromptBlock,mockInputs: null == mockInputs ? _self.mockInputs : mockInputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,targetScaleScore: freezed == targetScaleScore ? _self.targetScaleScore : targetScaleScore // ignore: cast_nullable_to_non_nullable
as int?,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,contextText: null == contextText ? _self.contextText : contextText // ignore: cast_nullable_to_non_nullable
as String,
  ));
}
/// Create a copy of PromptBlockSimulationRequest
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PromptBlockCopyWith<$Res> get block {
  
  return $PromptBlockCopyWith<$Res>(_self.block, (value) {
    return _then(_self.copyWith(block: value));
  });
}
}


/// Adds pattern-matching-related methods to [PromptBlockSimulationRequest].
extension PromptBlockSimulationRequestPatterns on PromptBlockSimulationRequest {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PromptBlockSimulationRequest value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PromptBlockSimulationRequest() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PromptBlockSimulationRequest value)  $default,){
final _that = this;
switch (_that) {
case _PromptBlockSimulationRequest():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PromptBlockSimulationRequest value)?  $default,){
final _that = this;
switch (_that) {
case _PromptBlockSimulationRequest() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( PromptBlock block, @JsonKey(name: 'mock_inputs')  Map<String, dynamic> mockInputs, @JsonKey(name: 'target_scale_score')  int? targetScaleScore, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'context_text')  String contextText)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PromptBlockSimulationRequest() when $default != null:
return $default(_that.block,_that.mockInputs,_that.targetScaleScore,_that.targetLocale,_that.contextText);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( PromptBlock block, @JsonKey(name: 'mock_inputs')  Map<String, dynamic> mockInputs, @JsonKey(name: 'target_scale_score')  int? targetScaleScore, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'context_text')  String contextText)  $default,) {final _that = this;
switch (_that) {
case _PromptBlockSimulationRequest():
return $default(_that.block,_that.mockInputs,_that.targetScaleScore,_that.targetLocale,_that.contextText);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( PromptBlock block, @JsonKey(name: 'mock_inputs')  Map<String, dynamic> mockInputs, @JsonKey(name: 'target_scale_score')  int? targetScaleScore, @JsonKey(name: 'target_locale')  String targetLocale, @JsonKey(name: 'context_text')  String contextText)?  $default,) {final _that = this;
switch (_that) {
case _PromptBlockSimulationRequest() when $default != null:
return $default(_that.block,_that.mockInputs,_that.targetScaleScore,_that.targetLocale,_that.contextText);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _PromptBlockSimulationRequest implements PromptBlockSimulationRequest {
  const _PromptBlockSimulationRequest({required this.block, @JsonKey(name: 'mock_inputs') final  Map<String, dynamic> mockInputs = const {}, @JsonKey(name: 'target_scale_score') this.targetScaleScore, @JsonKey(name: 'target_locale') this.targetLocale = 'en', @JsonKey(name: 'context_text') this.contextText = '[SIMULATED CONTEXT DOCUMENT]'}): _mockInputs = mockInputs;
  factory _PromptBlockSimulationRequest.fromJson(Map<String, dynamic> json) => _$PromptBlockSimulationRequestFromJson(json);

@override final  PromptBlock block;
 final  Map<String, dynamic> _mockInputs;
@override@JsonKey(name: 'mock_inputs') Map<String, dynamic> get mockInputs {
  if (_mockInputs is EqualUnmodifiableMapView) return _mockInputs;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_mockInputs);
}

@override@JsonKey(name: 'target_scale_score') final  int? targetScaleScore;
@override@JsonKey(name: 'target_locale') final  String targetLocale;
@override@JsonKey(name: 'context_text') final  String contextText;

/// Create a copy of PromptBlockSimulationRequest
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PromptBlockSimulationRequestCopyWith<_PromptBlockSimulationRequest> get copyWith => __$PromptBlockSimulationRequestCopyWithImpl<_PromptBlockSimulationRequest>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PromptBlockSimulationRequestToJson(this, );
}



@override
String toString() {
  return 'PromptBlockSimulationRequest(block: $block, mockInputs: $mockInputs, targetScaleScore: $targetScaleScore, targetLocale: $targetLocale, contextText: $contextText)';
}


}

/// @nodoc
abstract mixin class _$PromptBlockSimulationRequestCopyWith<$Res> implements $PromptBlockSimulationRequestCopyWith<$Res> {
  factory _$PromptBlockSimulationRequestCopyWith(_PromptBlockSimulationRequest value, $Res Function(_PromptBlockSimulationRequest) _then) = __$PromptBlockSimulationRequestCopyWithImpl;
@override @useResult
$Res call({
 PromptBlock block,@JsonKey(name: 'mock_inputs') Map<String, dynamic> mockInputs,@JsonKey(name: 'target_scale_score') int? targetScaleScore,@JsonKey(name: 'target_locale') String targetLocale,@JsonKey(name: 'context_text') String contextText
});


@override $PromptBlockCopyWith<$Res> get block;

}
/// @nodoc
class __$PromptBlockSimulationRequestCopyWithImpl<$Res>
    implements _$PromptBlockSimulationRequestCopyWith<$Res> {
  __$PromptBlockSimulationRequestCopyWithImpl(this._self, this._then);

  final _PromptBlockSimulationRequest _self;
  final $Res Function(_PromptBlockSimulationRequest) _then;

/// Create a copy of PromptBlockSimulationRequest
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? block = null,Object? mockInputs = null,Object? targetScaleScore = freezed,Object? targetLocale = null,Object? contextText = null,}) {
  return _then(_PromptBlockSimulationRequest(
block: null == block ? _self.block : block // ignore: cast_nullable_to_non_nullable
as PromptBlock,mockInputs: null == mockInputs ? _self._mockInputs : mockInputs // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,targetScaleScore: freezed == targetScaleScore ? _self.targetScaleScore : targetScaleScore // ignore: cast_nullable_to_non_nullable
as int?,targetLocale: null == targetLocale ? _self.targetLocale : targetLocale // ignore: cast_nullable_to_non_nullable
as String,contextText: null == contextText ? _self.contextText : contextText // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

/// Create a copy of PromptBlockSimulationRequest
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$PromptBlockCopyWith<$Res> get block {
  
  return $PromptBlockCopyWith<$Res>(_self.block, (value) {
    return _then(_self.copyWith(block: value));
  });
}
}


/// @nodoc
mixin _$PromptBlockSimulationResponse {

 bool get valid; List<String> get errors;@JsonKey(name: 'rendered_prompt') String get renderedPrompt; Map<String, dynamic> get trace;@JsonKey(name: 'prompt_context') PromptContextDto? get promptContext;
/// Create a copy of PromptBlockSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$PromptBlockSimulationResponseCopyWith<PromptBlockSimulationResponse> get copyWith => _$PromptBlockSimulationResponseCopyWithImpl<PromptBlockSimulationResponse>(this as PromptBlockSimulationResponse, _$identity);

  /// Serializes this PromptBlockSimulationResponse to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'PromptBlockSimulationResponse(valid: $valid, errors: $errors, renderedPrompt: $renderedPrompt, trace: $trace, promptContext: $promptContext)';
}


}

/// @nodoc
abstract mixin class $PromptBlockSimulationResponseCopyWith<$Res>  {
  factory $PromptBlockSimulationResponseCopyWith(PromptBlockSimulationResponse value, $Res Function(PromptBlockSimulationResponse) _then) = _$PromptBlockSimulationResponseCopyWithImpl;
@useResult
$Res call({
 bool valid, List<String> errors,@JsonKey(name: 'rendered_prompt') String renderedPrompt, Map<String, dynamic> trace,@JsonKey(name: 'prompt_context') PromptContextDto? promptContext
});


$PromptContextDtoCopyWith<$Res>? get promptContext;

}
/// @nodoc
class _$PromptBlockSimulationResponseCopyWithImpl<$Res>
    implements $PromptBlockSimulationResponseCopyWith<$Res> {
  _$PromptBlockSimulationResponseCopyWithImpl(this._self, this._then);

  final PromptBlockSimulationResponse _self;
  final $Res Function(PromptBlockSimulationResponse) _then;

/// Create a copy of PromptBlockSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? valid = null,Object? errors = null,Object? renderedPrompt = null,Object? trace = null,Object? promptContext = freezed,}) {
  return _then(_self.copyWith(
valid: null == valid ? _self.valid : valid // ignore: cast_nullable_to_non_nullable
as bool,errors: null == errors ? _self.errors : errors // ignore: cast_nullable_to_non_nullable
as List<String>,renderedPrompt: null == renderedPrompt ? _self.renderedPrompt : renderedPrompt // ignore: cast_nullable_to_non_nullable
as String,trace: null == trace ? _self.trace : trace // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,promptContext: freezed == promptContext ? _self.promptContext : promptContext // ignore: cast_nullable_to_non_nullable
as PromptContextDto?,
  ));
}
/// Create a copy of PromptBlockSimulationResponse
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


/// Adds pattern-matching-related methods to [PromptBlockSimulationResponse].
extension PromptBlockSimulationResponsePatterns on PromptBlockSimulationResponse {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _PromptBlockSimulationResponse value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _PromptBlockSimulationResponse() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _PromptBlockSimulationResponse value)  $default,){
final _that = this;
switch (_that) {
case _PromptBlockSimulationResponse():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _PromptBlockSimulationResponse value)?  $default,){
final _that = this;
switch (_that) {
case _PromptBlockSimulationResponse() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( bool valid,  List<String> errors, @JsonKey(name: 'rendered_prompt')  String renderedPrompt,  Map<String, dynamic> trace, @JsonKey(name: 'prompt_context')  PromptContextDto? promptContext)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _PromptBlockSimulationResponse() when $default != null:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( bool valid,  List<String> errors, @JsonKey(name: 'rendered_prompt')  String renderedPrompt,  Map<String, dynamic> trace, @JsonKey(name: 'prompt_context')  PromptContextDto? promptContext)  $default,) {final _that = this;
switch (_that) {
case _PromptBlockSimulationResponse():
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( bool valid,  List<String> errors, @JsonKey(name: 'rendered_prompt')  String renderedPrompt,  Map<String, dynamic> trace, @JsonKey(name: 'prompt_context')  PromptContextDto? promptContext)?  $default,) {final _that = this;
switch (_that) {
case _PromptBlockSimulationResponse() when $default != null:
return $default(_that.valid,_that.errors,_that.renderedPrompt,_that.trace,_that.promptContext);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _PromptBlockSimulationResponse implements PromptBlockSimulationResponse {
  const _PromptBlockSimulationResponse({this.valid = true, final  List<String> errors = const [], @JsonKey(name: 'rendered_prompt') this.renderedPrompt = '', final  Map<String, dynamic> trace = const {}, @JsonKey(name: 'prompt_context') this.promptContext}): _errors = errors,_trace = trace;
  factory _PromptBlockSimulationResponse.fromJson(Map<String, dynamic> json) => _$PromptBlockSimulationResponseFromJson(json);

@override@JsonKey() final  bool valid;
 final  List<String> _errors;
@override@JsonKey() List<String> get errors {
  if (_errors is EqualUnmodifiableListView) return _errors;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_errors);
}

@override@JsonKey(name: 'rendered_prompt') final  String renderedPrompt;
 final  Map<String, dynamic> _trace;
@override@JsonKey() Map<String, dynamic> get trace {
  if (_trace is EqualUnmodifiableMapView) return _trace;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_trace);
}

@override@JsonKey(name: 'prompt_context') final  PromptContextDto? promptContext;

/// Create a copy of PromptBlockSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$PromptBlockSimulationResponseCopyWith<_PromptBlockSimulationResponse> get copyWith => __$PromptBlockSimulationResponseCopyWithImpl<_PromptBlockSimulationResponse>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$PromptBlockSimulationResponseToJson(this, );
}



@override
String toString() {
  return 'PromptBlockSimulationResponse(valid: $valid, errors: $errors, renderedPrompt: $renderedPrompt, trace: $trace, promptContext: $promptContext)';
}


}

/// @nodoc
abstract mixin class _$PromptBlockSimulationResponseCopyWith<$Res> implements $PromptBlockSimulationResponseCopyWith<$Res> {
  factory _$PromptBlockSimulationResponseCopyWith(_PromptBlockSimulationResponse value, $Res Function(_PromptBlockSimulationResponse) _then) = __$PromptBlockSimulationResponseCopyWithImpl;
@override @useResult
$Res call({
 bool valid, List<String> errors,@JsonKey(name: 'rendered_prompt') String renderedPrompt, Map<String, dynamic> trace,@JsonKey(name: 'prompt_context') PromptContextDto? promptContext
});


@override $PromptContextDtoCopyWith<$Res>? get promptContext;

}
/// @nodoc
class __$PromptBlockSimulationResponseCopyWithImpl<$Res>
    implements _$PromptBlockSimulationResponseCopyWith<$Res> {
  __$PromptBlockSimulationResponseCopyWithImpl(this._self, this._then);

  final _PromptBlockSimulationResponse _self;
  final $Res Function(_PromptBlockSimulationResponse) _then;

/// Create a copy of PromptBlockSimulationResponse
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? valid = null,Object? errors = null,Object? renderedPrompt = null,Object? trace = null,Object? promptContext = freezed,}) {
  return _then(_PromptBlockSimulationResponse(
valid: null == valid ? _self.valid : valid // ignore: cast_nullable_to_non_nullable
as bool,errors: null == errors ? _self._errors : errors // ignore: cast_nullable_to_non_nullable
as List<String>,renderedPrompt: null == renderedPrompt ? _self.renderedPrompt : renderedPrompt // ignore: cast_nullable_to_non_nullable
as String,trace: null == trace ? _self._trace : trace // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>,promptContext: freezed == promptContext ? _self.promptContext : promptContext // ignore: cast_nullable_to_non_nullable
as PromptContextDto?,
  ));
}

/// Create a copy of PromptBlockSimulationResponse
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
