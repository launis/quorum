// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'report_layout_dto.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ReportLayoutDto {

@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView) PresetView get presetView; I18nText? get title; I18nText? get description; List<MatrixScorecardRowDto> get axes;@JsonKey(name: 'target_blocks') List<String>? get targetBlocks;@JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full) TextDeliveryMode get textDeliveryMode;@JsonKey(name: 'is_synthesis_enabled') bool get isSynthesisEnabled; SynthesisConfigDto? get synthesis;@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO>? get synthesisBlocks;@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns;@JsonKey(name: 'matrix_column_labels') Map<String, I18nText> get matrixColumnLabels;
/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ReportLayoutDtoCopyWith<ReportLayoutDto> get copyWith => _$ReportLayoutDtoCopyWithImpl<ReportLayoutDto>(this as ReportLayoutDto, _$identity);

  /// Serializes this ReportLayoutDto to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'ReportLayoutDto(presetView: $presetView, title: $title, description: $description, axes: $axes, targetBlocks: $targetBlocks, textDeliveryMode: $textDeliveryMode, isSynthesisEnabled: $isSynthesisEnabled, synthesis: $synthesis, synthesisBlocks: $synthesisBlocks, matrixVisibleColumns: $matrixVisibleColumns, matrixColumnLabels: $matrixColumnLabels)';
}


}

/// @nodoc
abstract mixin class $ReportLayoutDtoCopyWith<$Res>  {
  factory $ReportLayoutDtoCopyWith(ReportLayoutDto value, $Res Function(ReportLayoutDto) _then) = _$ReportLayoutDtoCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView) PresetView presetView, I18nText? title, I18nText? description, List<MatrixScorecardRowDto> axes,@JsonKey(name: 'target_blocks') List<String>? targetBlocks,@JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full) TextDeliveryMode textDeliveryMode,@JsonKey(name: 'is_synthesis_enabled') bool isSynthesisEnabled, SynthesisConfigDto? synthesis,@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO>? synthesisBlocks,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns,@JsonKey(name: 'matrix_column_labels') Map<String, I18nText> matrixColumnLabels
});


$I18nTextCopyWith<$Res>? get title;$I18nTextCopyWith<$Res>? get description;$SynthesisConfigDtoCopyWith<$Res>? get synthesis;

}
/// @nodoc
class _$ReportLayoutDtoCopyWithImpl<$Res>
    implements $ReportLayoutDtoCopyWith<$Res> {
  _$ReportLayoutDtoCopyWithImpl(this._self, this._then);

  final ReportLayoutDto _self;
  final $Res Function(ReportLayoutDto) _then;

/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? presetView = null,Object? title = freezed,Object? description = freezed,Object? axes = null,Object? targetBlocks = freezed,Object? textDeliveryMode = null,Object? isSynthesisEnabled = null,Object? synthesis = freezed,Object? synthesisBlocks = freezed,Object? matrixVisibleColumns = null,Object? matrixColumnLabels = null,}) {
  return _then(_self.copyWith(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as PresetView,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self.axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,targetBlocks: freezed == targetBlocks ? _self.targetBlocks : targetBlocks // ignore: cast_nullable_to_non_nullable
as List<String>?,textDeliveryMode: null == textDeliveryMode ? _self.textDeliveryMode : textDeliveryMode // ignore: cast_nullable_to_non_nullable
as TextDeliveryMode,isSynthesisEnabled: null == isSynthesisEnabled ? _self.isSynthesisEnabled : isSynthesisEnabled // ignore: cast_nullable_to_non_nullable
as bool,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as SynthesisConfigDto?,synthesisBlocks: freezed == synthesisBlocks ? _self.synthesisBlocks : synthesisBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>?,matrixVisibleColumns: null == matrixVisibleColumns ? _self.matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,matrixColumnLabels: null == matrixColumnLabels ? _self.matrixColumnLabels : matrixColumnLabels // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,
  ));
}
/// Create a copy of ReportLayoutDto
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
}/// Create a copy of ReportLayoutDto
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
}/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SynthesisConfigDtoCopyWith<$Res>? get synthesis {
    if (_self.synthesis == null) {
    return null;
  }

  return $SynthesisConfigDtoCopyWith<$Res>(_self.synthesis!, (value) {
    return _then(_self.copyWith(synthesis: value));
  });
}
}


/// Adds pattern-matching-related methods to [ReportLayoutDto].
extension ReportLayoutDtoPatterns on ReportLayoutDto {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ReportLayoutDto value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ReportLayoutDto() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ReportLayoutDto value)  $default,){
final _that = this;
switch (_that) {
case _ReportLayoutDto():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ReportLayoutDto value)?  $default,){
final _that = this;
switch (_that) {
case _ReportLayoutDto() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView)  PresetView presetView,  I18nText? title,  I18nText? description,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'target_blocks')  List<String>? targetBlocks, @JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full)  TextDeliveryMode textDeliveryMode, @JsonKey(name: 'is_synthesis_enabled')  bool isSynthesisEnabled,  SynthesisConfigDto? synthesis, @JsonKey(name: 'synthesis_blocks')  List<SduiBlockDTO>? synthesisBlocks, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns, @JsonKey(name: 'matrix_column_labels')  Map<String, I18nText> matrixColumnLabels)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ReportLayoutDto() when $default != null:
return $default(_that.presetView,_that.title,_that.description,_that.axes,_that.targetBlocks,_that.textDeliveryMode,_that.isSynthesisEnabled,_that.synthesis,_that.synthesisBlocks,_that.matrixVisibleColumns,_that.matrixColumnLabels);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView)  PresetView presetView,  I18nText? title,  I18nText? description,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'target_blocks')  List<String>? targetBlocks, @JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full)  TextDeliveryMode textDeliveryMode, @JsonKey(name: 'is_synthesis_enabled')  bool isSynthesisEnabled,  SynthesisConfigDto? synthesis, @JsonKey(name: 'synthesis_blocks')  List<SduiBlockDTO>? synthesisBlocks, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns, @JsonKey(name: 'matrix_column_labels')  Map<String, I18nText> matrixColumnLabels)  $default,) {final _that = this;
switch (_that) {
case _ReportLayoutDto():
return $default(_that.presetView,_that.title,_that.description,_that.axes,_that.targetBlocks,_that.textDeliveryMode,_that.isSynthesisEnabled,_that.synthesis,_that.synthesisBlocks,_that.matrixVisibleColumns,_that.matrixColumnLabels);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView)  PresetView presetView,  I18nText? title,  I18nText? description,  List<MatrixScorecardRowDto> axes, @JsonKey(name: 'target_blocks')  List<String>? targetBlocks, @JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full)  TextDeliveryMode textDeliveryMode, @JsonKey(name: 'is_synthesis_enabled')  bool isSynthesisEnabled,  SynthesisConfigDto? synthesis, @JsonKey(name: 'synthesis_blocks')  List<SduiBlockDTO>? synthesisBlocks, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns, @JsonKey(name: 'matrix_column_labels')  Map<String, I18nText> matrixColumnLabels)?  $default,) {final _that = this;
switch (_that) {
case _ReportLayoutDto() when $default != null:
return $default(_that.presetView,_that.title,_that.description,_that.axes,_that.targetBlocks,_that.textDeliveryMode,_that.isSynthesisEnabled,_that.synthesis,_that.synthesisBlocks,_that.matrixVisibleColumns,_that.matrixColumnLabels);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _ReportLayoutDto implements ReportLayoutDto {
  const _ReportLayoutDto({@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView) this.presetView = PresetView.defaultView, this.title, this.description, final  List<MatrixScorecardRowDto> axes = const [], @JsonKey(name: 'target_blocks') final  List<String>? targetBlocks, @JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full) this.textDeliveryMode = TextDeliveryMode.full, @JsonKey(name: 'is_synthesis_enabled') this.isSynthesisEnabled = true, this.synthesis, @JsonKey(name: 'synthesis_blocks') final  List<SduiBlockDTO>? synthesisBlocks, @JsonKey(name: 'matrix_visible_columns') final  List<String> matrixVisibleColumns = const [], @JsonKey(name: 'matrix_column_labels') final  Map<String, I18nText> matrixColumnLabels = const {}}): _axes = axes,_targetBlocks = targetBlocks,_synthesisBlocks = synthesisBlocks,_matrixVisibleColumns = matrixVisibleColumns,_matrixColumnLabels = matrixColumnLabels;
  factory _ReportLayoutDto.fromJson(Map<String, dynamic> json) => _$ReportLayoutDtoFromJson(json);

@override@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView) final  PresetView presetView;
@override final  I18nText? title;
@override final  I18nText? description;
 final  List<MatrixScorecardRowDto> _axes;
@override@JsonKey() List<MatrixScorecardRowDto> get axes {
  if (_axes is EqualUnmodifiableListView) return _axes;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_axes);
}

 final  List<String>? _targetBlocks;
@override@JsonKey(name: 'target_blocks') List<String>? get targetBlocks {
  final value = _targetBlocks;
  if (value == null) return null;
  if (_targetBlocks is EqualUnmodifiableListView) return _targetBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

@override@JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full) final  TextDeliveryMode textDeliveryMode;
@override@JsonKey(name: 'is_synthesis_enabled') final  bool isSynthesisEnabled;
@override final  SynthesisConfigDto? synthesis;
 final  List<SduiBlockDTO>? _synthesisBlocks;
@override@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO>? get synthesisBlocks {
  final value = _synthesisBlocks;
  if (value == null) return null;
  if (_synthesisBlocks is EqualUnmodifiableListView) return _synthesisBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(value);
}

 final  List<String> _matrixVisibleColumns;
@override@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns {
  if (_matrixVisibleColumns is EqualUnmodifiableListView) return _matrixVisibleColumns;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_matrixVisibleColumns);
}

 final  Map<String, I18nText> _matrixColumnLabels;
@override@JsonKey(name: 'matrix_column_labels') Map<String, I18nText> get matrixColumnLabels {
  if (_matrixColumnLabels is EqualUnmodifiableMapView) return _matrixColumnLabels;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_matrixColumnLabels);
}


/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ReportLayoutDtoCopyWith<_ReportLayoutDto> get copyWith => __$ReportLayoutDtoCopyWithImpl<_ReportLayoutDto>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ReportLayoutDtoToJson(this, );
}



@override
String toString() {
  return 'ReportLayoutDto(presetView: $presetView, title: $title, description: $description, axes: $axes, targetBlocks: $targetBlocks, textDeliveryMode: $textDeliveryMode, isSynthesisEnabled: $isSynthesisEnabled, synthesis: $synthesis, synthesisBlocks: $synthesisBlocks, matrixVisibleColumns: $matrixVisibleColumns, matrixColumnLabels: $matrixColumnLabels)';
}


}

/// @nodoc
abstract mixin class _$ReportLayoutDtoCopyWith<$Res> implements $ReportLayoutDtoCopyWith<$Res> {
  factory _$ReportLayoutDtoCopyWith(_ReportLayoutDto value, $Res Function(_ReportLayoutDto) _then) = __$ReportLayoutDtoCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView) PresetView presetView, I18nText? title, I18nText? description, List<MatrixScorecardRowDto> axes,@JsonKey(name: 'target_blocks') List<String>? targetBlocks,@JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full) TextDeliveryMode textDeliveryMode,@JsonKey(name: 'is_synthesis_enabled') bool isSynthesisEnabled, SynthesisConfigDto? synthesis,@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO>? synthesisBlocks,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns,@JsonKey(name: 'matrix_column_labels') Map<String, I18nText> matrixColumnLabels
});


@override $I18nTextCopyWith<$Res>? get title;@override $I18nTextCopyWith<$Res>? get description;@override $SynthesisConfigDtoCopyWith<$Res>? get synthesis;

}
/// @nodoc
class __$ReportLayoutDtoCopyWithImpl<$Res>
    implements _$ReportLayoutDtoCopyWith<$Res> {
  __$ReportLayoutDtoCopyWithImpl(this._self, this._then);

  final _ReportLayoutDto _self;
  final $Res Function(_ReportLayoutDto) _then;

/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? presetView = null,Object? title = freezed,Object? description = freezed,Object? axes = null,Object? targetBlocks = freezed,Object? textDeliveryMode = null,Object? isSynthesisEnabled = null,Object? synthesis = freezed,Object? synthesisBlocks = freezed,Object? matrixVisibleColumns = null,Object? matrixColumnLabels = null,}) {
  return _then(_ReportLayoutDto(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as PresetView,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,axes: null == axes ? _self._axes : axes // ignore: cast_nullable_to_non_nullable
as List<MatrixScorecardRowDto>,targetBlocks: freezed == targetBlocks ? _self._targetBlocks : targetBlocks // ignore: cast_nullable_to_non_nullable
as List<String>?,textDeliveryMode: null == textDeliveryMode ? _self.textDeliveryMode : textDeliveryMode // ignore: cast_nullable_to_non_nullable
as TextDeliveryMode,isSynthesisEnabled: null == isSynthesisEnabled ? _self.isSynthesisEnabled : isSynthesisEnabled // ignore: cast_nullable_to_non_nullable
as bool,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as SynthesisConfigDto?,synthesisBlocks: freezed == synthesisBlocks ? _self._synthesisBlocks : synthesisBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>?,matrixVisibleColumns: null == matrixVisibleColumns ? _self._matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,matrixColumnLabels: null == matrixColumnLabels ? _self._matrixColumnLabels : matrixColumnLabels // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,
  ));
}

/// Create a copy of ReportLayoutDto
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
}/// Create a copy of ReportLayoutDto
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
}/// Create a copy of ReportLayoutDto
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SynthesisConfigDtoCopyWith<$Res>? get synthesis {
    if (_self.synthesis == null) {
    return null;
  }

  return $SynthesisConfigDtoCopyWith<$Res>(_self.synthesis!, (value) {
    return _then(_self.copyWith(synthesis: value));
  });
}
}

// dart format on
