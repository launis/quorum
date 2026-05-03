// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'report_data_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ReportLayoutDTO {

@JsonKey(name: 'preset_view') PresetView get presetView;@JsonKey(name: 'matrix_type') String? get matrixType; I18nText? get title; I18nText? get description; List<MatrixScorecardRowDto> get axes;@JsonKey(name: 'text_delivery_mode') String get textDeliveryMode; Map<String, dynamic>? get synthesis;@JsonKey(name: 'synthesis_md') String? get synthesisMd;
/// Create a copy of ReportLayoutDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportLayoutDTOCopyWith<ReportLayoutDTO> get copyWith => _$ReportLayoutDTOCopyWithImpl<ReportLayoutDTO>(this as ReportLayoutDTO, _$identity);

  /// Serializes this ReportLayoutDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportLayoutDTO(presetView: $presetView, matrixType: $matrixType, title: $title, description: $description, axes: $axes, textDeliveryMode: $textDeliveryMode, synthesis: $synthesis, synthesisMd: $synthesisMd)';
}


}

/// @nodoc
abstract mixin class $ReportLayoutDTOCopyWith<$Res>  {
  factory $ReportLayoutDTOCopyWith(ReportLayoutDTO value, $Res Function(ReportLayoutDTO) _then) = _$ReportLayoutDTOCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'preset_view') PresetView presetView,@JsonKey(name: 'matrix_type') String? matrixType, I18nText? title, I18nText? description, List<MatrixScorecardRowDto> axes,@JsonKey(name: 'text_delivery_mode') String textDeliveryMode, Map<String, dynamic>? synthesis,@JsonKey(name: 'synthesis_md') String? synthesisMd
});


$I18nTextCopyWith<$Res>? get title;$I18nTextCopyWith<$Res>? get description;

}
/// @nodoc
class _$ReportLayoutDTOCopyWithImpl<$Res>
    implements $ReportLayoutDTOCopyWith<$Res> {
  _$ReportLayoutDTOCopyWithImpl(this._self, this._then);

  final ReportLayoutDTO _self;
  final $Res Function(ReportLayoutDTO) _then;

/// Create a copy of ReportLayoutDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? presetView = null,Object? matrixType = freezed,Object? title = freezed,Object? description = freezed,Object? axes = null,Object? textDeliveryMode = null,Object? synthesis = freezed,Object? synthesisMd = freezed,}) {
  return _then(_self.copyWith(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as PresetView,matrixType: freezed == matrixType ? _self.matrixType : matrixType // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self.axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,textDeliveryMode: null == textDeliveryMode ? _self.textDeliveryMode : textDeliveryMode // ignore: cast_nullable_to_non_nullable
as String,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,synthesisMd: freezed == synthesisMd ? _self.synthesisMd : synthesisMd // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of ReportLayoutDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get title {
    if (_self.title == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.title!, (value) {
    return _then(_self.copyWith(title: value));
  });
}/// Create a copy of ReportLayoutDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get description {
    if (_self.description == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.description!, (value) {
    return _then(_self.copyWith(description: value));
  });
}
}


/// Adds pattern-matching-related methods to [ReportLayoutDTO].
extension ReportLayoutDTOPatterns on ReportLayoutDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportLayoutDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportLayoutDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportLayoutDTO value)  $default,){
final _that = this;
switch (_that) {
case _ReportLayoutDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportLayoutDTO value)?  $default,){
final _that = this;
switch (_that) {
case _ReportLayoutDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'preset_view')  PresetView presetView, @JsonKey(name: 'matrix_type')  String? matrixType,  I18nText? title,  I18nText? description,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'text_delivery_mode')  String textDeliveryMode,  Map<String, dynamic>? synthesis, @JsonKey(name: 'synthesis_md')  String? synthesisMd)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportLayoutDTO() when $default != null:
return $default(_that.presetView,_that.matrixType,_that.title,_that.description,_that.axes,_that.textDeliveryMode,_that.synthesis,_that.synthesisMd);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'preset_view')  PresetView presetView, @JsonKey(name: 'matrix_type')  String? matrixType,  I18nText? title,  I18nText? description,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'text_delivery_mode')  String textDeliveryMode,  Map<String, dynamic>? synthesis, @JsonKey(name: 'synthesis_md')  String? synthesisMd)  $default,) {final _that = this;
switch (_that) {
case _ReportLayoutDTO():
return $default(_that.presetView,_that.matrixType,_that.title,_that.description,_that.axes,_that.textDeliveryMode,_that.synthesis,_that.synthesisMd);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'preset_view')  PresetView presetView, @JsonKey(name: 'matrix_type')  String? matrixType,  I18nText? title,  I18nText? description,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'text_delivery_mode')  String textDeliveryMode,  Map<String, dynamic>? synthesis, @JsonKey(name: 'synthesis_md')  String? synthesisMd)?  $default,) {final _that = this;
switch (_that) {
case _ReportLayoutDTO() when $default != null:
return $default(_that.presetView,_that.matrixType,_that.title,_that.description,_that.axes,_that.textDeliveryMode,_that.synthesis,_that.synthesisMd);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportLayoutDTO implements ReportLayoutDTO {
  const _ReportLayoutDTO({@JsonKey(name: 'preset_view') required this.presetView, @JsonKey(name: 'matrix_type') this.matrixType, this.title, this.description, final  List<MatrixScorecardRowDto> axes = const [], @JsonKey(name: 'text_delivery_mode') required this.textDeliveryMode, final  Map<String, dynamic>? synthesis, @JsonKey(name: 'synthesis_md') this.synthesisMd}): _axes = axes,_synthesis = synthesis;
  factory _ReportLayoutDTO.fromJson(Map<String, dynamic> json) => _$ReportLayoutDTOFromJson(json);

@override@JsonKey(name: 'preset_view') final  PresetView presetView;
@override@JsonKey(name: 'matrix_type') final  String? matrixType;
@override final  I18nText? title;
@override final  I18nText? description;
 final  List<MatrixScorecardRowDto> _axes;
@override@JsonKey() List<MatrixScorecardRowDto> get axes {
  if (_axes is EqualUnmodifiableListView) return _axes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_axes);
}

@override@JsonKey(name: 'text_delivery_mode') final  String textDeliveryMode;
 final  Map<String, dynamic>? _synthesis;
@override Map<String, dynamic>? get synthesis {
  final value = _synthesis;
  if (value == null) return null;
  if (_synthesis is EqualUnmodifiableMapView) return _synthesis;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(value);
}

@override@JsonKey(name: 'synthesis_md') final  String? synthesisMd;

/// Create a copy of ReportLayoutDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportLayoutDTOCopyWith<_ReportLayoutDTO> get copyWith => __$ReportLayoutDTOCopyWithImpl<_ReportLayoutDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportLayoutDTOToJson(this, );
}



@override
String toString() {
  return 'ReportLayoutDTO(presetView: $presetView, matrixType: $matrixType, title: $title, description: $description, axes: $axes, textDeliveryMode: $textDeliveryMode, synthesis: $synthesis, synthesisMd: $synthesisMd)';
}


}

/// @nodoc
abstract mixin class _$ReportLayoutDTOCopyWith<$Res> implements $ReportLayoutDTOCopyWith<$Res> {
  factory _$ReportLayoutDTOCopyWith(_ReportLayoutDTO value, $Res Function(_ReportLayoutDTO) _then) = __$ReportLayoutDTOCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'preset_view') PresetView presetView,@JsonKey(name: 'matrix_type') String? matrixType, I18nText? title, I18nText? description, List<MatrixScorecardRowDto> axes,@JsonKey(name: 'text_delivery_mode') String textDeliveryMode, Map<String, dynamic>? synthesis,@JsonKey(name: 'synthesis_md') String? synthesisMd
});


@override $I18nTextCopyWith<$Res>? get title;@override $I18nTextCopyWith<$Res>? get description;

}
/// @nodoc
class __$ReportLayoutDTOCopyWithImpl<$Res>
    implements _$ReportLayoutDTOCopyWith<$Res> {
  __$ReportLayoutDTOCopyWithImpl(this._self, this._then);

  final _ReportLayoutDTO _self;
  final $Res Function(_ReportLayoutDTO) _then;

/// Create a copy of ReportLayoutDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? presetView = null,Object? matrixType = freezed,Object? title = freezed,Object? description = freezed,Object? axes = null,Object? textDeliveryMode = null,Object? synthesis = freezed,Object? synthesisMd = freezed,}) {
  return _then(_ReportLayoutDTO(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as PresetView,matrixType: freezed == matrixType ? _self.matrixType : matrixType // ignore: cast_nullable_to_non_nullable
as String?,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self._axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,textDeliveryMode: null == textDeliveryMode ? _self.textDeliveryMode : textDeliveryMode // ignore: cast_nullable_to_non_nullable
as String,synthesis: freezed == synthesis ? _self._synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as Map<String, dynamic>?,synthesisMd: freezed == synthesisMd ? _self.synthesisMd : synthesisMd // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of ReportLayoutDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get title {
    if (_self.title == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.title!, (value) {
    return _then(_self.copyWith(title: value));
  });
}/// Create a copy of ReportLayoutDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get description {
    if (_self.description == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.description!, (value) {
    return _then(_self.copyWith(description: value));
  });
}
}


/// @nodoc
mixin _$MCPToolAuditDTO {

 String? get id;@JsonKey(name: 'tool_id') String get toolId;@JsonKey(name: 'step_name') String get stepName; String get query;@JsonKey(name: 'response_summary') String get responseSummary;@JsonKey(name: 'source_urls') List<String> get sourceUrls; String? get timestamp;@JsonKey(name: 'duration_ms') int get durationMs;
/// Create a copy of MCPToolAuditDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MCPToolAuditDTOCopyWith<MCPToolAuditDTO> get copyWith => _$MCPToolAuditDTOCopyWithImpl<MCPToolAuditDTO>(this as MCPToolAuditDTO, _$identity);

  /// Serializes this MCPToolAuditDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'MCPToolAuditDTO(id: $id, toolId: $toolId, stepName: $stepName, query: $query, responseSummary: $responseSummary, sourceUrls: $sourceUrls, timestamp: $timestamp, durationMs: $durationMs)';
}


}

/// @nodoc
abstract mixin class $MCPToolAuditDTOCopyWith<$Res>  {
  factory $MCPToolAuditDTOCopyWith(MCPToolAuditDTO value, $Res Function(MCPToolAuditDTO) _then) = _$MCPToolAuditDTOCopyWithImpl;
@useResult
$Res call({
 String? id,@JsonKey(name: 'tool_id') String toolId,@JsonKey(name: 'step_name') String stepName, String query,@JsonKey(name: 'response_summary') String responseSummary,@JsonKey(name: 'source_urls') List<String> sourceUrls, String? timestamp,@JsonKey(name: 'duration_ms') int durationMs
});




}
/// @nodoc
class _$MCPToolAuditDTOCopyWithImpl<$Res>
    implements $MCPToolAuditDTOCopyWith<$Res> {
  _$MCPToolAuditDTOCopyWithImpl(this._self, this._then);

  final MCPToolAuditDTO _self;
  final $Res Function(MCPToolAuditDTO) _then;

/// Create a copy of MCPToolAuditDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = freezed,Object? toolId = null,Object? stepName = null,Object? query = null,Object? responseSummary = null,Object? sourceUrls = null,Object? timestamp = freezed,Object? durationMs = null,}) {
  return _then(_self.copyWith(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,toolId: null == toolId ? _self.toolId : toolId // ignore: cast_nullable_to_non_nullable
as String,stepName: null == stepName ? _self.stepName : stepName // ignore: cast_nullable_to_non_nullable
as String,query: null == query ? _self.query : query // ignore: cast_nullable_to_non_nullable
as String,responseSummary: null == responseSummary ? _self.responseSummary : responseSummary // ignore: cast_nullable_to_non_nullable
as String,sourceUrls: null == sourceUrls ? _self.sourceUrls : sourceUrls // ignore: cast_nullable_to_non_nullable
as List<String>,timestamp: freezed == timestamp ? _self.timestamp : timestamp // ignore: cast_nullable_to_non_nullable
as String?,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,
  ));
}

}


/// Adds pattern-matching-related methods to [MCPToolAuditDTO].
extension MCPToolAuditDTOPatterns on MCPToolAuditDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MCPToolAuditDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MCPToolAuditDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MCPToolAuditDTO value)  $default,){
final _that = this;
switch (_that) {
case _MCPToolAuditDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MCPToolAuditDTO value)?  $default,){
final _that = this;
switch (_that) {
case _MCPToolAuditDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? id, @JsonKey(name: 'tool_id')  String toolId, @JsonKey(name: 'step_name')  String stepName,  String query, @JsonKey(name: 'response_summary')  String responseSummary, @JsonKey(name: 'source_urls')  List<String> sourceUrls,  String? timestamp, @JsonKey(name: 'duration_ms')  int durationMs)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MCPToolAuditDTO() when $default != null:
return $default(_that.id,_that.toolId,_that.stepName,_that.query,_that.responseSummary,_that.sourceUrls,_that.timestamp,_that.durationMs);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? id, @JsonKey(name: 'tool_id')  String toolId, @JsonKey(name: 'step_name')  String stepName,  String query, @JsonKey(name: 'response_summary')  String responseSummary, @JsonKey(name: 'source_urls')  List<String> sourceUrls,  String? timestamp, @JsonKey(name: 'duration_ms')  int durationMs)  $default,) {final _that = this;
switch (_that) {
case _MCPToolAuditDTO():
return $default(_that.id,_that.toolId,_that.stepName,_that.query,_that.responseSummary,_that.sourceUrls,_that.timestamp,_that.durationMs);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? id, @JsonKey(name: 'tool_id')  String toolId, @JsonKey(name: 'step_name')  String stepName,  String query, @JsonKey(name: 'response_summary')  String responseSummary, @JsonKey(name: 'source_urls')  List<String> sourceUrls,  String? timestamp, @JsonKey(name: 'duration_ms')  int durationMs)?  $default,) {final _that = this;
switch (_that) {
case _MCPToolAuditDTO() when $default != null:
return $default(_that.id,_that.toolId,_that.stepName,_that.query,_that.responseSummary,_that.sourceUrls,_that.timestamp,_that.durationMs);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _MCPToolAuditDTO implements MCPToolAuditDTO {
  const _MCPToolAuditDTO({this.id, @JsonKey(name: 'tool_id') required this.toolId, @JsonKey(name: 'step_name') required this.stepName, required this.query, @JsonKey(name: 'response_summary') this.responseSummary = '', @JsonKey(name: 'source_urls') final  List<String> sourceUrls = const [], this.timestamp, @JsonKey(name: 'duration_ms') this.durationMs = 0}): _sourceUrls = sourceUrls;
  factory _MCPToolAuditDTO.fromJson(Map<String, dynamic> json) => _$MCPToolAuditDTOFromJson(json);

@override final  String? id;
@override@JsonKey(name: 'tool_id') final  String toolId;
@override@JsonKey(name: 'step_name') final  String stepName;
@override final  String query;
@override@JsonKey(name: 'response_summary') final  String responseSummary;
 final  List<String> _sourceUrls;
@override@JsonKey(name: 'source_urls') List<String> get sourceUrls {
  if (_sourceUrls is EqualUnmodifiableListView) return _sourceUrls;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_sourceUrls);
}

@override final  String? timestamp;
@override@JsonKey(name: 'duration_ms') final  int durationMs;

/// Create a copy of MCPToolAuditDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MCPToolAuditDTOCopyWith<_MCPToolAuditDTO> get copyWith => __$MCPToolAuditDTOCopyWithImpl<_MCPToolAuditDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MCPToolAuditDTOToJson(this, );
}



@override
String toString() {
  return 'MCPToolAuditDTO(id: $id, toolId: $toolId, stepName: $stepName, query: $query, responseSummary: $responseSummary, sourceUrls: $sourceUrls, timestamp: $timestamp, durationMs: $durationMs)';
}


}

/// @nodoc
abstract mixin class _$MCPToolAuditDTOCopyWith<$Res> implements $MCPToolAuditDTOCopyWith<$Res> {
  factory _$MCPToolAuditDTOCopyWith(_MCPToolAuditDTO value, $Res Function(_MCPToolAuditDTO) _then) = __$MCPToolAuditDTOCopyWithImpl;
@override @useResult
$Res call({
 String? id,@JsonKey(name: 'tool_id') String toolId,@JsonKey(name: 'step_name') String stepName, String query,@JsonKey(name: 'response_summary') String responseSummary,@JsonKey(name: 'source_urls') List<String> sourceUrls, String? timestamp,@JsonKey(name: 'duration_ms') int durationMs
});




}
/// @nodoc
class __$MCPToolAuditDTOCopyWithImpl<$Res>
    implements _$MCPToolAuditDTOCopyWith<$Res> {
  __$MCPToolAuditDTOCopyWithImpl(this._self, this._then);

  final _MCPToolAuditDTO _self;
  final $Res Function(_MCPToolAuditDTO) _then;

/// Create a copy of MCPToolAuditDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = freezed,Object? toolId = null,Object? stepName = null,Object? query = null,Object? responseSummary = null,Object? sourceUrls = null,Object? timestamp = freezed,Object? durationMs = null,}) {
  return _then(_MCPToolAuditDTO(
id: freezed == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String?,toolId: null == toolId ? _self.toolId : toolId // ignore: cast_nullable_to_non_nullable
as String,stepName: null == stepName ? _self.stepName : stepName // ignore: cast_nullable_to_non_nullable
as String,query: null == query ? _self.query : query // ignore: cast_nullable_to_non_nullable
as String,responseSummary: null == responseSummary ? _self.responseSummary : responseSummary // ignore: cast_nullable_to_non_nullable
as String,sourceUrls: null == sourceUrls ? _self._sourceUrls : sourceUrls // ignore: cast_nullable_to_non_nullable
as List<String>,timestamp: freezed == timestamp ? _self.timestamp : timestamp // ignore: cast_nullable_to_non_nullable
as String?,durationMs: null == durationMs ? _self.durationMs : durationMs // ignore: cast_nullable_to_non_nullable
as int,
  ));
}


}


/// @nodoc
mixin _$ReportDataDTO {

@JsonKey(name: 'workflow_id') String get workflowId;@JsonKey(name: 'profile_id') String get profileId;@JsonKey(name: 'profile_name') I18nText? get profileName;@JsonKey(name: 'available_profiles') Map<String, I18nText> get availableProfiles;@JsonKey(name: 'global_score') double? get globalScore; List<ReportLayoutDTO> get layouts;@JsonKey(name: 'created_at') String? get createdAt;@JsonKey(name: 'org_name') String? get orgName;@JsonKey(name: 'strictness_level') int? get strictnessLevel;@JsonKey(name: 'scoring_strategy') String? get scoringStrategy;@JsonKey(name: 'cost_estimate') double? get costEstimate;@JsonKey(name: 'total_tokens') int? get totalTokens;@JsonKey(name: 'prompt_tokens') int? get promptTokens;@JsonKey(name: 'completion_tokens') int? get completionTokens;@JsonKey(name: 'reasoning_tokens') int? get reasoningTokens;@JsonKey(name: 'mcp_tool_audit') List<MCPToolAuditDTO> get mcpToolAudit;@JsonKey(name: 'has_warning') bool get hasWarning;@JsonKey(name: 'synthesized_markdown') String? get synthesizedMarkdown;@JsonKey(name: 'visible_metadata') List<String> get visibleMetadata;@JsonKey(name: 'grouped_extensions') Map<String, List<dynamic>> get groupedExtensions;@JsonKey(name: 'penalties_applied') List<String> get penaltiesApplied;@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto> get evaluativeMatrices;@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto> get informationalMatrices;
/// Create a copy of ReportDataDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportDataDTOCopyWith<ReportDataDTO> get copyWith => _$ReportDataDTOCopyWithImpl<ReportDataDTO>(this as ReportDataDTO, _$identity);

  /// Serializes this ReportDataDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportDataDTO(workflowId: $workflowId, profileId: $profileId, profileName: $profileName, availableProfiles: $availableProfiles, globalScore: $globalScore, layouts: $layouts, createdAt: $createdAt, orgName: $orgName, strictnessLevel: $strictnessLevel, scoringStrategy: $scoringStrategy, costEstimate: $costEstimate, totalTokens: $totalTokens, promptTokens: $promptTokens, completionTokens: $completionTokens, reasoningTokens: $reasoningTokens, mcpToolAudit: $mcpToolAudit, hasWarning: $hasWarning, synthesizedMarkdown: $synthesizedMarkdown, visibleMetadata: $visibleMetadata, groupedExtensions: $groupedExtensions, penaltiesApplied: $penaltiesApplied, evaluativeMatrices: $evaluativeMatrices, informationalMatrices: $informationalMatrices)';
}


}

/// @nodoc
abstract mixin class $ReportDataDTOCopyWith<$Res>  {
  factory $ReportDataDTOCopyWith(ReportDataDTO value, $Res Function(ReportDataDTO) _then) = _$ReportDataDTOCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'profile_id') String profileId,@JsonKey(name: 'profile_name') I18nText? profileName,@JsonKey(name: 'available_profiles') Map<String, I18nText> availableProfiles,@JsonKey(name: 'global_score') double? globalScore, List<ReportLayoutDTO> layouts,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'org_name') String? orgName,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'scoring_strategy') String? scoringStrategy,@JsonKey(name: 'cost_estimate') double? costEstimate,@JsonKey(name: 'total_tokens') int? totalTokens,@JsonKey(name: 'prompt_tokens') int? promptTokens,@JsonKey(name: 'completion_tokens') int? completionTokens,@JsonKey(name: 'reasoning_tokens') int? reasoningTokens,@JsonKey(name: 'mcp_tool_audit') List<MCPToolAuditDTO> mcpToolAudit,@JsonKey(name: 'has_warning') bool hasWarning,@JsonKey(name: 'synthesized_markdown') String? synthesizedMarkdown,@JsonKey(name: 'visible_metadata') List<String> visibleMetadata,@JsonKey(name: 'grouped_extensions') Map<String, List<dynamic>> groupedExtensions,@JsonKey(name: 'penalties_applied') List<String> penaltiesApplied,@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto> evaluativeMatrices,@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto> informationalMatrices
});


$I18nTextCopyWith<$Res>? get profileName;

}
/// @nodoc
class _$ReportDataDTOCopyWithImpl<$Res>
    implements $ReportDataDTOCopyWith<$Res> {
  _$ReportDataDTOCopyWithImpl(this._self, this._then);

  final ReportDataDTO _self;
  final $Res Function(ReportDataDTO) _then;

/// Create a copy of ReportDataDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? workflowId = null,Object? profileId = null,Object? profileName = freezed,Object? availableProfiles = null,Object? globalScore = freezed,Object? layouts = null,Object? createdAt = freezed,Object? orgName = freezed,Object? strictnessLevel = freezed,Object? scoringStrategy = freezed,Object? costEstimate = freezed,Object? totalTokens = freezed,Object? promptTokens = freezed,Object? completionTokens = freezed,Object? reasoningTokens = freezed,Object? mcpToolAudit = null,Object? hasWarning = null,Object? synthesizedMarkdown = freezed,Object? visibleMetadata = null,Object? groupedExtensions = null,Object? penaltiesApplied = null,Object? evaluativeMatrices = null,Object? informationalMatrices = null,}) {
  return _then(_self.copyWith(
workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,profileId: null == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String,profileName: freezed == profileName ? _self.profileName : profileName // ignore: cast_nullable_to_non_nullable
as I18nText?,availableProfiles: null == availableProfiles ? _self.availableProfiles : availableProfiles // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,globalScore: freezed == globalScore ? _self.globalScore : globalScore // ignore: cast_nullable_to_non_nullable
as double?,layouts: null == layouts ? _self.layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<ReportLayoutDTO>,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,orgName: freezed == orgName ? _self.orgName : orgName // ignore: cast_nullable_to_non_nullable
as String?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as String?,costEstimate: freezed == costEstimate ? _self.costEstimate : costEstimate // ignore: cast_nullable_to_non_nullable
as double?,totalTokens: freezed == totalTokens ? _self.totalTokens : totalTokens // ignore: cast_nullable_to_non_nullable
as int?,promptTokens: freezed == promptTokens ? _self.promptTokens : promptTokens // ignore: cast_nullable_to_non_nullable
as int?,completionTokens: freezed == completionTokens ? _self.completionTokens : completionTokens // ignore: cast_nullable_to_non_nullable
as int?,reasoningTokens: freezed == reasoningTokens ? _self.reasoningTokens : reasoningTokens // ignore: cast_nullable_to_non_nullable
as int?,mcpToolAudit: null == mcpToolAudit ? _self.mcpToolAudit : mcpToolAudit // ignore: cast_nullable_to_non_nullable
as List<MCPToolAuditDTO>,hasWarning: null == hasWarning ? _self.hasWarning : hasWarning // ignore: cast_nullable_to_non_nullable
as bool,synthesizedMarkdown: freezed == synthesizedMarkdown ? _self.synthesizedMarkdown : synthesizedMarkdown // ignore: cast_nullable_to_non_nullable
as String?,visibleMetadata: null == visibleMetadata ? _self.visibleMetadata : visibleMetadata // ignore: cast_nullable_to_non_nullable
as List<String>,groupedExtensions: null == groupedExtensions ? _self.groupedExtensions : groupedExtensions // ignore: cast_nullable_to_non_nullable
as Map<String, List<dynamic>>,penaltiesApplied: null == penaltiesApplied ? _self.penaltiesApplied : penaltiesApplied // ignore: cast_nullable_to_non_nullable
as List<String>,evaluativeMatrices: null == evaluativeMatrices ? _self.evaluativeMatrices : evaluativeMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,informationalMatrices: null == informationalMatrices ? _self.informationalMatrices : informationalMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,
  ));
}
/// Create a copy of ReportDataDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get profileName {
    if (_self.profileName == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.profileName!, (value) {
    return _then(_self.copyWith(profileName: value));
  });
}
}


/// Adds pattern-matching-related methods to [ReportDataDTO].
extension ReportDataDTOPatterns on ReportDataDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportDataDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportDataDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportDataDTO value)  $default,){
final _that = this;
switch (_that) {
case _ReportDataDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportDataDTO value)?  $default,){
final _that = this;
switch (_that) {
case _ReportDataDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'profile_id')  String profileId, @JsonKey(name: 'profile_name')  I18nText? profileName, @JsonKey(name: 'available_profiles')  Map<String, I18nText> availableProfiles, @JsonKey(name: 'global_score')  double? globalScore,  List<ReportLayoutDTO> layouts, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'org_name')  String? orgName, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  String? scoringStrategy, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'total_tokens')  int? totalTokens, @JsonKey(name: 'prompt_tokens')  int? promptTokens, @JsonKey(name: 'completion_tokens')  int? completionTokens, @JsonKey(name: 'reasoning_tokens')  int? reasoningTokens, @JsonKey(name: 'mcp_tool_audit')  List<MCPToolAuditDTO> mcpToolAudit, @JsonKey(name: 'has_warning')  bool hasWarning, @JsonKey(name: 'synthesized_markdown')  String? synthesizedMarkdown, @JsonKey(name: 'visible_metadata')  List<String> visibleMetadata, @JsonKey(name: 'grouped_extensions')  Map<String, List<dynamic>> groupedExtensions, @JsonKey(name: 'penalties_applied')  List<String> penaltiesApplied, @JsonKey(name: 'evaluative_matrices')  List<MatrixScorecardRowDto> evaluativeMatrices, @JsonKey(name: 'informational_matrices')  List<MatrixScorecardRowDto> informationalMatrices)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportDataDTO() when $default != null:
return $default(_that.workflowId,_that.profileId,_that.profileName,_that.availableProfiles,_that.globalScore,_that.layouts,_that.createdAt,_that.orgName,_that.strictnessLevel,_that.scoringStrategy,_that.costEstimate,_that.totalTokens,_that.promptTokens,_that.completionTokens,_that.reasoningTokens,_that.mcpToolAudit,_that.hasWarning,_that.synthesizedMarkdown,_that.visibleMetadata,_that.groupedExtensions,_that.penaltiesApplied,_that.evaluativeMatrices,_that.informationalMatrices);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'profile_id')  String profileId, @JsonKey(name: 'profile_name')  I18nText? profileName, @JsonKey(name: 'available_profiles')  Map<String, I18nText> availableProfiles, @JsonKey(name: 'global_score')  double? globalScore,  List<ReportLayoutDTO> layouts, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'org_name')  String? orgName, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  String? scoringStrategy, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'total_tokens')  int? totalTokens, @JsonKey(name: 'prompt_tokens')  int? promptTokens, @JsonKey(name: 'completion_tokens')  int? completionTokens, @JsonKey(name: 'reasoning_tokens')  int? reasoningTokens, @JsonKey(name: 'mcp_tool_audit')  List<MCPToolAuditDTO> mcpToolAudit, @JsonKey(name: 'has_warning')  bool hasWarning, @JsonKey(name: 'synthesized_markdown')  String? synthesizedMarkdown, @JsonKey(name: 'visible_metadata')  List<String> visibleMetadata, @JsonKey(name: 'grouped_extensions')  Map<String, List<dynamic>> groupedExtensions, @JsonKey(name: 'penalties_applied')  List<String> penaltiesApplied, @JsonKey(name: 'evaluative_matrices')  List<MatrixScorecardRowDto> evaluativeMatrices, @JsonKey(name: 'informational_matrices')  List<MatrixScorecardRowDto> informationalMatrices)  $default,) {final _that = this;
switch (_that) {
case _ReportDataDTO():
return $default(_that.workflowId,_that.profileId,_that.profileName,_that.availableProfiles,_that.globalScore,_that.layouts,_that.createdAt,_that.orgName,_that.strictnessLevel,_that.scoringStrategy,_that.costEstimate,_that.totalTokens,_that.promptTokens,_that.completionTokens,_that.reasoningTokens,_that.mcpToolAudit,_that.hasWarning,_that.synthesizedMarkdown,_that.visibleMetadata,_that.groupedExtensions,_that.penaltiesApplied,_that.evaluativeMatrices,_that.informationalMatrices);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'workflow_id')  String workflowId, @JsonKey(name: 'profile_id')  String profileId, @JsonKey(name: 'profile_name')  I18nText? profileName, @JsonKey(name: 'available_profiles')  Map<String, I18nText> availableProfiles, @JsonKey(name: 'global_score')  double? globalScore,  List<ReportLayoutDTO> layouts, @JsonKey(name: 'created_at')  String? createdAt, @JsonKey(name: 'org_name')  String? orgName, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  String? scoringStrategy, @JsonKey(name: 'cost_estimate')  double? costEstimate, @JsonKey(name: 'total_tokens')  int? totalTokens, @JsonKey(name: 'prompt_tokens')  int? promptTokens, @JsonKey(name: 'completion_tokens')  int? completionTokens, @JsonKey(name: 'reasoning_tokens')  int? reasoningTokens, @JsonKey(name: 'mcp_tool_audit')  List<MCPToolAuditDTO> mcpToolAudit, @JsonKey(name: 'has_warning')  bool hasWarning, @JsonKey(name: 'synthesized_markdown')  String? synthesizedMarkdown, @JsonKey(name: 'visible_metadata')  List<String> visibleMetadata, @JsonKey(name: 'grouped_extensions')  Map<String, List<dynamic>> groupedExtensions, @JsonKey(name: 'penalties_applied')  List<String> penaltiesApplied, @JsonKey(name: 'evaluative_matrices')  List<MatrixScorecardRowDto> evaluativeMatrices, @JsonKey(name: 'informational_matrices')  List<MatrixScorecardRowDto> informationalMatrices)?  $default,) {final _that = this;
switch (_that) {
case _ReportDataDTO() when $default != null:
return $default(_that.workflowId,_that.profileId,_that.profileName,_that.availableProfiles,_that.globalScore,_that.layouts,_that.createdAt,_that.orgName,_that.strictnessLevel,_that.scoringStrategy,_that.costEstimate,_that.totalTokens,_that.promptTokens,_that.completionTokens,_that.reasoningTokens,_that.mcpToolAudit,_that.hasWarning,_that.synthesizedMarkdown,_that.visibleMetadata,_that.groupedExtensions,_that.penaltiesApplied,_that.evaluativeMatrices,_that.informationalMatrices);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportDataDTO extends ReportDataDTO {
  const _ReportDataDTO({@JsonKey(name: 'workflow_id') required this.workflowId, @JsonKey(name: 'profile_id') required this.profileId, @JsonKey(name: 'profile_name') this.profileName, @JsonKey(name: 'available_profiles') final  Map<String, I18nText> availableProfiles = const {}, @JsonKey(name: 'global_score') this.globalScore, final  List<ReportLayoutDTO> layouts = const [], @JsonKey(name: 'created_at') this.createdAt, @JsonKey(name: 'org_name') this.orgName, @JsonKey(name: 'strictness_level') this.strictnessLevel, @JsonKey(name: 'scoring_strategy') this.scoringStrategy, @JsonKey(name: 'cost_estimate') this.costEstimate, @JsonKey(name: 'total_tokens') this.totalTokens, @JsonKey(name: 'prompt_tokens') this.promptTokens, @JsonKey(name: 'completion_tokens') this.completionTokens, @JsonKey(name: 'reasoning_tokens') this.reasoningTokens, @JsonKey(name: 'mcp_tool_audit') final  List<MCPToolAuditDTO> mcpToolAudit = const [], @JsonKey(name: 'has_warning') this.hasWarning = false, @JsonKey(name: 'synthesized_markdown') this.synthesizedMarkdown, @JsonKey(name: 'visible_metadata') final  List<String> visibleMetadata = const [], @JsonKey(name: 'grouped_extensions') final  Map<String, List<dynamic>> groupedExtensions = const {}, @JsonKey(name: 'penalties_applied') final  List<String> penaltiesApplied = const [], @JsonKey(name: 'evaluative_matrices') final  List<MatrixScorecardRowDto> evaluativeMatrices = const [], @JsonKey(name: 'informational_matrices') final  List<MatrixScorecardRowDto> informationalMatrices = const []}): _availableProfiles = availableProfiles,_layouts = layouts,_mcpToolAudit = mcpToolAudit,_visibleMetadata = visibleMetadata,_groupedExtensions = groupedExtensions,_penaltiesApplied = penaltiesApplied,_evaluativeMatrices = evaluativeMatrices,_informationalMatrices = informationalMatrices,super._();
  factory _ReportDataDTO.fromJson(Map<String, dynamic> json) => _$ReportDataDTOFromJson(json);

@override@JsonKey(name: 'workflow_id') final  String workflowId;
@override@JsonKey(name: 'profile_id') final  String profileId;
@override@JsonKey(name: 'profile_name') final  I18nText? profileName;
 final  Map<String, I18nText> _availableProfiles;
@override@JsonKey(name: 'available_profiles') Map<String, I18nText> get availableProfiles {
  if (_availableProfiles is EqualUnmodifiableMapView) return _availableProfiles;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_availableProfiles);
}

@override@JsonKey(name: 'global_score') final  double? globalScore;
 final  List<ReportLayoutDTO> _layouts;
@override@JsonKey() List<ReportLayoutDTO> get layouts {
  if (_layouts is EqualUnmodifiableListView) return _layouts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_layouts);
}

@override@JsonKey(name: 'created_at') final  String? createdAt;
@override@JsonKey(name: 'org_name') final  String? orgName;
@override@JsonKey(name: 'strictness_level') final  int? strictnessLevel;
@override@JsonKey(name: 'scoring_strategy') final  String? scoringStrategy;
@override@JsonKey(name: 'cost_estimate') final  double? costEstimate;
@override@JsonKey(name: 'total_tokens') final  int? totalTokens;
@override@JsonKey(name: 'prompt_tokens') final  int? promptTokens;
@override@JsonKey(name: 'completion_tokens') final  int? completionTokens;
@override@JsonKey(name: 'reasoning_tokens') final  int? reasoningTokens;
 final  List<MCPToolAuditDTO> _mcpToolAudit;
@override@JsonKey(name: 'mcp_tool_audit') List<MCPToolAuditDTO> get mcpToolAudit {
  if (_mcpToolAudit is EqualUnmodifiableListView) return _mcpToolAudit;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_mcpToolAudit);
}

@override@JsonKey(name: 'has_warning') final  bool hasWarning;
@override@JsonKey(name: 'synthesized_markdown') final  String? synthesizedMarkdown;
 final  List<String> _visibleMetadata;
@override@JsonKey(name: 'visible_metadata') List<String> get visibleMetadata {
  if (_visibleMetadata is EqualUnmodifiableListView) return _visibleMetadata;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleMetadata);
}

 final  Map<String, List<dynamic>> _groupedExtensions;
@override@JsonKey(name: 'grouped_extensions') Map<String, List<dynamic>> get groupedExtensions {
  if (_groupedExtensions is EqualUnmodifiableMapView) return _groupedExtensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_groupedExtensions);
}

 final  List<String> _penaltiesApplied;
@override@JsonKey(name: 'penalties_applied') List<String> get penaltiesApplied {
  if (_penaltiesApplied is EqualUnmodifiableListView) return _penaltiesApplied;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_penaltiesApplied);
}

 final  List<MatrixScorecardRowDto> _evaluativeMatrices;
@override@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto> get evaluativeMatrices {
  if (_evaluativeMatrices is EqualUnmodifiableListView) return _evaluativeMatrices;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_evaluativeMatrices);
}

 final  List<MatrixScorecardRowDto> _informationalMatrices;
@override@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto> get informationalMatrices {
  if (_informationalMatrices is EqualUnmodifiableListView) return _informationalMatrices;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_informationalMatrices);
}


/// Create a copy of ReportDataDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportDataDTOCopyWith<_ReportDataDTO> get copyWith => __$ReportDataDTOCopyWithImpl<_ReportDataDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportDataDTOToJson(this, );
}



@override
String toString() {
  return 'ReportDataDTO(workflowId: $workflowId, profileId: $profileId, profileName: $profileName, availableProfiles: $availableProfiles, globalScore: $globalScore, layouts: $layouts, createdAt: $createdAt, orgName: $orgName, strictnessLevel: $strictnessLevel, scoringStrategy: $scoringStrategy, costEstimate: $costEstimate, totalTokens: $totalTokens, promptTokens: $promptTokens, completionTokens: $completionTokens, reasoningTokens: $reasoningTokens, mcpToolAudit: $mcpToolAudit, hasWarning: $hasWarning, synthesizedMarkdown: $synthesizedMarkdown, visibleMetadata: $visibleMetadata, groupedExtensions: $groupedExtensions, penaltiesApplied: $penaltiesApplied, evaluativeMatrices: $evaluativeMatrices, informationalMatrices: $informationalMatrices)';
}


}

/// @nodoc
abstract mixin class _$ReportDataDTOCopyWith<$Res> implements $ReportDataDTOCopyWith<$Res> {
  factory _$ReportDataDTOCopyWith(_ReportDataDTO value, $Res Function(_ReportDataDTO) _then) = __$ReportDataDTOCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'workflow_id') String workflowId,@JsonKey(name: 'profile_id') String profileId,@JsonKey(name: 'profile_name') I18nText? profileName,@JsonKey(name: 'available_profiles') Map<String, I18nText> availableProfiles,@JsonKey(name: 'global_score') double? globalScore, List<ReportLayoutDTO> layouts,@JsonKey(name: 'created_at') String? createdAt,@JsonKey(name: 'org_name') String? orgName,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'scoring_strategy') String? scoringStrategy,@JsonKey(name: 'cost_estimate') double? costEstimate,@JsonKey(name: 'total_tokens') int? totalTokens,@JsonKey(name: 'prompt_tokens') int? promptTokens,@JsonKey(name: 'completion_tokens') int? completionTokens,@JsonKey(name: 'reasoning_tokens') int? reasoningTokens,@JsonKey(name: 'mcp_tool_audit') List<MCPToolAuditDTO> mcpToolAudit,@JsonKey(name: 'has_warning') bool hasWarning,@JsonKey(name: 'synthesized_markdown') String? synthesizedMarkdown,@JsonKey(name: 'visible_metadata') List<String> visibleMetadata,@JsonKey(name: 'grouped_extensions') Map<String, List<dynamic>> groupedExtensions,@JsonKey(name: 'penalties_applied') List<String> penaltiesApplied,@JsonKey(name: 'evaluative_matrices') List<MatrixScorecardRowDto> evaluativeMatrices,@JsonKey(name: 'informational_matrices') List<MatrixScorecardRowDto> informationalMatrices
});


@override $I18nTextCopyWith<$Res>? get profileName;

}
/// @nodoc
class __$ReportDataDTOCopyWithImpl<$Res>
    implements _$ReportDataDTOCopyWith<$Res> {
  __$ReportDataDTOCopyWithImpl(this._self, this._then);

  final _ReportDataDTO _self;
  final $Res Function(_ReportDataDTO) _then;

/// Create a copy of ReportDataDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? workflowId = null,Object? profileId = null,Object? profileName = freezed,Object? availableProfiles = null,Object? globalScore = freezed,Object? layouts = null,Object? createdAt = freezed,Object? orgName = freezed,Object? strictnessLevel = freezed,Object? scoringStrategy = freezed,Object? costEstimate = freezed,Object? totalTokens = freezed,Object? promptTokens = freezed,Object? completionTokens = freezed,Object? reasoningTokens = freezed,Object? mcpToolAudit = null,Object? hasWarning = null,Object? synthesizedMarkdown = freezed,Object? visibleMetadata = null,Object? groupedExtensions = null,Object? penaltiesApplied = null,Object? evaluativeMatrices = null,Object? informationalMatrices = null,}) {
  return _then(_ReportDataDTO(
workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,profileId: null == profileId ? _self.profileId : profileId // ignore: cast_nullable_to_non_nullable
as String,profileName: freezed == profileName ? _self.profileName : profileName // ignore: cast_nullable_to_non_nullable
as I18nText?,availableProfiles: null == availableProfiles ? _self._availableProfiles : availableProfiles // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,globalScore: freezed == globalScore ? _self.globalScore : globalScore // ignore: cast_nullable_to_non_nullable
as double?,layouts: null == layouts ? _self._layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<ReportLayoutDTO>,createdAt: freezed == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String?,orgName: freezed == orgName ? _self.orgName : orgName // ignore: cast_nullable_to_non_nullable
as String?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as String?,costEstimate: freezed == costEstimate ? _self.costEstimate : costEstimate // ignore: cast_nullable_to_non_nullable
as double?,totalTokens: freezed == totalTokens ? _self.totalTokens : totalTokens // ignore: cast_nullable_to_non_nullable
as int?,promptTokens: freezed == promptTokens ? _self.promptTokens : promptTokens // ignore: cast_nullable_to_non_nullable
as int?,completionTokens: freezed == completionTokens ? _self.completionTokens : completionTokens // ignore: cast_nullable_to_non_nullable
as int?,reasoningTokens: freezed == reasoningTokens ? _self.reasoningTokens : reasoningTokens // ignore: cast_nullable_to_non_nullable
as int?,mcpToolAudit: null == mcpToolAudit ? _self._mcpToolAudit : mcpToolAudit // ignore: cast_nullable_to_non_nullable
as List<MCPToolAuditDTO>,hasWarning: null == hasWarning ? _self.hasWarning : hasWarning // ignore: cast_nullable_to_non_nullable
as bool,synthesizedMarkdown: freezed == synthesizedMarkdown ? _self.synthesizedMarkdown : synthesizedMarkdown // ignore: cast_nullable_to_non_nullable
as String?,visibleMetadata: null == visibleMetadata ? _self._visibleMetadata : visibleMetadata // ignore: cast_nullable_to_non_nullable
as List<String>,groupedExtensions: null == groupedExtensions ? _self._groupedExtensions : groupedExtensions // ignore: cast_nullable_to_non_nullable
as Map<String, List<dynamic>>,penaltiesApplied: null == penaltiesApplied ? _self._penaltiesApplied : penaltiesApplied // ignore: cast_nullable_to_non_nullable
as List<String>,evaluativeMatrices: null == evaluativeMatrices ? _self._evaluativeMatrices : evaluativeMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,informationalMatrices: null == informationalMatrices ? _self._informationalMatrices : informationalMatrices // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,
  ));
}

/// Create a copy of ReportDataDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get profileName {
    if (_self.profileName == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.profileName!, (value) {
    return _then(_self.copyWith(profileName: value));
  });
}
}

// dart format on
