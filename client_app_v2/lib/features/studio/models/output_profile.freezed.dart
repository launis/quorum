// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'output_profile.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$OutputLayoutBlock {

@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView) PresetView get presetView; I18nText? get title; I18nText? get description; List<String> get steps; List<String> get targetBlocks;@JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full) TextDeliveryMode get textDeliveryMode;@JsonKey(name: 'is_synthesis_enabled') bool get isSynthesisEnabled; SynthesisConfigDTO? get synthesis;@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO> get synthesisBlocks;@JsonKey(name: 'strictness_level') int? get strictnessLevel;@JsonKey(name: 'scoring_strategy') ScoringStrategy? get scoringStrategy;@JsonKey(name: 'matrix_column_labels') Map<String, I18nText> get matrixColumnLabels;@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns;
/// Create a copy of OutputLayoutBlock
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OutputLayoutBlockCopyWith<OutputLayoutBlock> get copyWith => _$OutputLayoutBlockCopyWithImpl<OutputLayoutBlock>(this as OutputLayoutBlock, _$identity);

  /// Serializes this OutputLayoutBlock to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'OutputLayoutBlock(presetView: $presetView, title: $title, description: $description, steps: $steps, targetBlocks: $targetBlocks, textDeliveryMode: $textDeliveryMode, isSynthesisEnabled: $isSynthesisEnabled, synthesis: $synthesis, synthesisBlocks: $synthesisBlocks, strictnessLevel: $strictnessLevel, scoringStrategy: $scoringStrategy, matrixColumnLabels: $matrixColumnLabels, matrixVisibleColumns: $matrixVisibleColumns)';
}


}

/// @nodoc
abstract mixin class $OutputLayoutBlockCopyWith<$Res>  {
  factory $OutputLayoutBlockCopyWith(OutputLayoutBlock value, $Res Function(OutputLayoutBlock) _then) = _$OutputLayoutBlockCopyWithImpl;
@useResult
$Res call({
@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView) PresetView presetView, I18nText? title, I18nText? description, List<String> steps, List<String> targetBlocks,@JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full) TextDeliveryMode textDeliveryMode,@JsonKey(name: 'is_synthesis_enabled') bool isSynthesisEnabled, SynthesisConfigDTO? synthesis,@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO> synthesisBlocks,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,@JsonKey(name: 'matrix_column_labels') Map<String, I18nText> matrixColumnLabels,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns
});


$I18nTextCopyWith<$Res>? get title;$I18nTextCopyWith<$Res>? get description;$SynthesisConfigDTOCopyWith<$Res>? get synthesis;

}
/// @nodoc
class _$OutputLayoutBlockCopyWithImpl<$Res>
    implements $OutputLayoutBlockCopyWith<$Res> {
  _$OutputLayoutBlockCopyWithImpl(this._self, this._then);

  final OutputLayoutBlock _self;
  final $Res Function(OutputLayoutBlock) _then;

/// Create a copy of OutputLayoutBlock
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? presetView = null,Object? title = freezed,Object? description = freezed,Object? steps = null,Object? targetBlocks = null,Object? textDeliveryMode = null,Object? isSynthesisEnabled = null,Object? synthesis = freezed,Object? synthesisBlocks = null,Object? strictnessLevel = freezed,Object? scoringStrategy = freezed,Object? matrixColumnLabels = null,Object? matrixVisibleColumns = null,}) {
  return _then(_self.copyWith(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as PresetView,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,steps: null == steps ? _self.steps : steps // ignore: cast_nullable_to_non_nullable
as List<String>,targetBlocks: null == targetBlocks ? _self.targetBlocks : targetBlocks // ignore: cast_nullable_to_non_nullable
as List<String>,textDeliveryMode: null == textDeliveryMode ? _self.textDeliveryMode : textDeliveryMode // ignore: cast_nullable_to_non_nullable
as TextDeliveryMode,isSynthesisEnabled: null == isSynthesisEnabled ? _self.isSynthesisEnabled : isSynthesisEnabled // ignore: cast_nullable_to_non_nullable
as bool,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as SynthesisConfigDTO?,synthesisBlocks: null == synthesisBlocks ? _self.synthesisBlocks : synthesisBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy?,matrixColumnLabels: null == matrixColumnLabels ? _self.matrixColumnLabels : matrixColumnLabels // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,matrixVisibleColumns: null == matrixVisibleColumns ? _self.matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}
/// Create a copy of OutputLayoutBlock
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
}/// Create a copy of OutputLayoutBlock
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
}/// Create a copy of OutputLayoutBlock
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SynthesisConfigDTOCopyWith<$Res>? get synthesis {
    if (_self.synthesis == null) {
    return null;
  }

  return $SynthesisConfigDTOCopyWith<$Res>(_self.synthesis!, (value) {
    return _then(_self.copyWith(synthesis: value));
  });
}
}


/// Adds pattern-matching-related methods to [OutputLayoutBlock].
extension OutputLayoutBlockPatterns on OutputLayoutBlock {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OutputLayoutBlock value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OutputLayoutBlock() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OutputLayoutBlock value)  $default,){
final _that = this;
switch (_that) {
case _OutputLayoutBlock():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OutputLayoutBlock value)?  $default,){
final _that = this;
switch (_that) {
case _OutputLayoutBlock() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView)  PresetView presetView,  I18nText? title,  I18nText? description,  List<String> steps,  List<String> targetBlocks, @JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full)  TextDeliveryMode textDeliveryMode, @JsonKey(name: 'is_synthesis_enabled')  bool isSynthesisEnabled,  SynthesisConfigDTO? synthesis, @JsonKey(name: 'synthesis_blocks')  List<SduiBlockDTO> synthesisBlocks, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'matrix_column_labels')  Map<String, I18nText> matrixColumnLabels, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OutputLayoutBlock() when $default != null:
return $default(_that.presetView,_that.title,_that.description,_that.steps,_that.targetBlocks,_that.textDeliveryMode,_that.isSynthesisEnabled,_that.synthesis,_that.synthesisBlocks,_that.strictnessLevel,_that.scoringStrategy,_that.matrixColumnLabels,_that.matrixVisibleColumns);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView)  PresetView presetView,  I18nText? title,  I18nText? description,  List<String> steps,  List<String> targetBlocks, @JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full)  TextDeliveryMode textDeliveryMode, @JsonKey(name: 'is_synthesis_enabled')  bool isSynthesisEnabled,  SynthesisConfigDTO? synthesis, @JsonKey(name: 'synthesis_blocks')  List<SduiBlockDTO> synthesisBlocks, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'matrix_column_labels')  Map<String, I18nText> matrixColumnLabels, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns)  $default,) {final _that = this;
switch (_that) {
case _OutputLayoutBlock():
return $default(_that.presetView,_that.title,_that.description,_that.steps,_that.targetBlocks,_that.textDeliveryMode,_that.isSynthesisEnabled,_that.synthesis,_that.synthesisBlocks,_that.strictnessLevel,_that.scoringStrategy,_that.matrixColumnLabels,_that.matrixVisibleColumns);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView)  PresetView presetView,  I18nText? title,  I18nText? description,  List<String> steps,  List<String> targetBlocks, @JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full)  TextDeliveryMode textDeliveryMode, @JsonKey(name: 'is_synthesis_enabled')  bool isSynthesisEnabled,  SynthesisConfigDTO? synthesis, @JsonKey(name: 'synthesis_blocks')  List<SduiBlockDTO> synthesisBlocks, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'matrix_column_labels')  Map<String, I18nText> matrixColumnLabels, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns)?  $default,) {final _that = this;
switch (_that) {
case _OutputLayoutBlock() when $default != null:
return $default(_that.presetView,_that.title,_that.description,_that.steps,_that.targetBlocks,_that.textDeliveryMode,_that.isSynthesisEnabled,_that.synthesis,_that.synthesisBlocks,_that.strictnessLevel,_that.scoringStrategy,_that.matrixColumnLabels,_that.matrixVisibleColumns);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _OutputLayoutBlock extends OutputLayoutBlock {
  const _OutputLayoutBlock({@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView) this.presetView = PresetView.defaultView, this.title, this.description, final  List<String> steps = const [], final  List<String> targetBlocks = const [], @JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full) this.textDeliveryMode = TextDeliveryMode.full, @JsonKey(name: 'is_synthesis_enabled') this.isSynthesisEnabled = true, this.synthesis, @JsonKey(name: 'synthesis_blocks') final  List<SduiBlockDTO> synthesisBlocks = const [], @JsonKey(name: 'strictness_level') this.strictnessLevel, @JsonKey(name: 'scoring_strategy') this.scoringStrategy, @JsonKey(name: 'matrix_column_labels') final  Map<String, I18nText> matrixColumnLabels = const {}, @JsonKey(name: 'matrix_visible_columns') final  List<String> matrixVisibleColumns = const []}): _steps = steps,_targetBlocks = targetBlocks,_synthesisBlocks = synthesisBlocks,_matrixColumnLabels = matrixColumnLabels,_matrixVisibleColumns = matrixVisibleColumns,super._();
  factory _OutputLayoutBlock.fromJson(Map<String, dynamic> json) => _$OutputLayoutBlockFromJson(json);

@override@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView) final  PresetView presetView;
@override final  I18nText? title;
@override final  I18nText? description;
 final  List<String> _steps;
@override@JsonKey() List<String> get steps {
  if (_steps is EqualUnmodifiableListView) return _steps;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_steps);
}

 final  List<String> _targetBlocks;
@override@JsonKey() List<String> get targetBlocks {
  if (_targetBlocks is EqualUnmodifiableListView) return _targetBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_targetBlocks);
}

@override@JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full) final  TextDeliveryMode textDeliveryMode;
@override@JsonKey(name: 'is_synthesis_enabled') final  bool isSynthesisEnabled;
@override final  SynthesisConfigDTO? synthesis;
 final  List<SduiBlockDTO> _synthesisBlocks;
@override@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO> get synthesisBlocks {
  if (_synthesisBlocks is EqualUnmodifiableListView) return _synthesisBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_synthesisBlocks);
}

@override@JsonKey(name: 'strictness_level') final  int? strictnessLevel;
@override@JsonKey(name: 'scoring_strategy') final  ScoringStrategy? scoringStrategy;
 final  Map<String, I18nText> _matrixColumnLabels;
@override@JsonKey(name: 'matrix_column_labels') Map<String, I18nText> get matrixColumnLabels {
  if (_matrixColumnLabels is EqualUnmodifiableMapView) return _matrixColumnLabels;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_matrixColumnLabels);
}

 final  List<String> _matrixVisibleColumns;
@override@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns {
  if (_matrixVisibleColumns is EqualUnmodifiableListView) return _matrixVisibleColumns;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_matrixVisibleColumns);
}


/// Create a copy of OutputLayoutBlock
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OutputLayoutBlockCopyWith<_OutputLayoutBlock> get copyWith => __$OutputLayoutBlockCopyWithImpl<_OutputLayoutBlock>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OutputLayoutBlockToJson(this, );
}



@override
String toString() {
  return 'OutputLayoutBlock(presetView: $presetView, title: $title, description: $description, steps: $steps, targetBlocks: $targetBlocks, textDeliveryMode: $textDeliveryMode, isSynthesisEnabled: $isSynthesisEnabled, synthesis: $synthesis, synthesisBlocks: $synthesisBlocks, strictnessLevel: $strictnessLevel, scoringStrategy: $scoringStrategy, matrixColumnLabels: $matrixColumnLabels, matrixVisibleColumns: $matrixVisibleColumns)';
}


}

/// @nodoc
abstract mixin class _$OutputLayoutBlockCopyWith<$Res> implements $OutputLayoutBlockCopyWith<$Res> {
  factory _$OutputLayoutBlockCopyWith(_OutputLayoutBlock value, $Res Function(_OutputLayoutBlock) _then) = __$OutputLayoutBlockCopyWithImpl;
@override @useResult
$Res call({
@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView) PresetView presetView, I18nText? title, I18nText? description, List<String> steps, List<String> targetBlocks,@JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full) TextDeliveryMode textDeliveryMode,@JsonKey(name: 'is_synthesis_enabled') bool isSynthesisEnabled, SynthesisConfigDTO? synthesis,@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO> synthesisBlocks,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,@JsonKey(name: 'matrix_column_labels') Map<String, I18nText> matrixColumnLabels,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns
});


@override $I18nTextCopyWith<$Res>? get title;@override $I18nTextCopyWith<$Res>? get description;@override $SynthesisConfigDTOCopyWith<$Res>? get synthesis;

}
/// @nodoc
class __$OutputLayoutBlockCopyWithImpl<$Res>
    implements _$OutputLayoutBlockCopyWith<$Res> {
  __$OutputLayoutBlockCopyWithImpl(this._self, this._then);

  final _OutputLayoutBlock _self;
  final $Res Function(_OutputLayoutBlock) _then;

/// Create a copy of OutputLayoutBlock
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? presetView = null,Object? title = freezed,Object? description = freezed,Object? steps = null,Object? targetBlocks = null,Object? textDeliveryMode = null,Object? isSynthesisEnabled = null,Object? synthesis = freezed,Object? synthesisBlocks = null,Object? strictnessLevel = freezed,Object? scoringStrategy = freezed,Object? matrixColumnLabels = null,Object? matrixVisibleColumns = null,}) {
  return _then(_OutputLayoutBlock(
presetView: null == presetView ? _self.presetView : presetView // ignore: cast_nullable_to_non_nullable
as PresetView,title: freezed == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText?,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,steps: null == steps ? _self._steps : steps // ignore: cast_nullable_to_non_nullable
as List<String>,targetBlocks: null == targetBlocks ? _self._targetBlocks : targetBlocks // ignore: cast_nullable_to_non_nullable
as List<String>,textDeliveryMode: null == textDeliveryMode ? _self.textDeliveryMode : textDeliveryMode // ignore: cast_nullable_to_non_nullable
as TextDeliveryMode,isSynthesisEnabled: null == isSynthesisEnabled ? _self.isSynthesisEnabled : isSynthesisEnabled // ignore: cast_nullable_to_non_nullable
as bool,synthesis: freezed == synthesis ? _self.synthesis : synthesis // ignore: cast_nullable_to_non_nullable
as SynthesisConfigDTO?,synthesisBlocks: null == synthesisBlocks ? _self._synthesisBlocks : synthesisBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy?,matrixColumnLabels: null == matrixColumnLabels ? _self._matrixColumnLabels : matrixColumnLabels // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,matrixVisibleColumns: null == matrixVisibleColumns ? _self._matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,
  ));
}

/// Create a copy of OutputLayoutBlock
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
}/// Create a copy of OutputLayoutBlock
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
}/// Create a copy of OutputLayoutBlock
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$SynthesisConfigDTOCopyWith<$Res>? get synthesis {
    if (_self.synthesis == null) {
    return null;
  }

  return $SynthesisConfigDTOCopyWith<$Res>(_self.synthesis!, (value) {
    return _then(_self.copyWith(synthesis: value));
  });
}
}


/// @nodoc
mixin _$SynthesisConfigDTO {

 String? get systemPrompt; int? get lengthConstraint; I18nText? get preambleText;@JsonKey(name: 'historical_context_mode', unknownEnumValue: HistoricalContextMode.disabled) HistoricalContextMode get historicalContextMode; bool get enablePiiMasking; List<String> get allowedExports; bool get omitEmptySections; List<String> get allowedMcpTools;@JsonKey(name: 'model_strategy') String? get modelStrategy;@JsonKey(name: 'tone_instruction') I18nText? get toneInstruction;@JsonKey(name: 'synthesis_block_id') String? get synthesisBlockId;@JsonKey(name: 'row_explanations_block_id') String? get rowExplanationsBlockId;
/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$SynthesisConfigDTOCopyWith<SynthesisConfigDTO> get copyWith => _$SynthesisConfigDTOCopyWithImpl<SynthesisConfigDTO>(this as SynthesisConfigDTO, _$identity);

  /// Serializes this SynthesisConfigDTO to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'SynthesisConfigDTO(systemPrompt: $systemPrompt, lengthConstraint: $lengthConstraint, preambleText: $preambleText, historicalContextMode: $historicalContextMode, enablePiiMasking: $enablePiiMasking, allowedExports: $allowedExports, omitEmptySections: $omitEmptySections, allowedMcpTools: $allowedMcpTools, modelStrategy: $modelStrategy, toneInstruction: $toneInstruction, synthesisBlockId: $synthesisBlockId, rowExplanationsBlockId: $rowExplanationsBlockId)';
}


}

/// @nodoc
abstract mixin class $SynthesisConfigDTOCopyWith<$Res>  {
  factory $SynthesisConfigDTOCopyWith(SynthesisConfigDTO value, $Res Function(SynthesisConfigDTO) _then) = _$SynthesisConfigDTOCopyWithImpl;
@useResult
$Res call({
 String? systemPrompt, int? lengthConstraint, I18nText? preambleText,@JsonKey(name: 'historical_context_mode', unknownEnumValue: HistoricalContextMode.disabled) HistoricalContextMode historicalContextMode, bool enablePiiMasking, List<String> allowedExports, bool omitEmptySections, List<String> allowedMcpTools,@JsonKey(name: 'model_strategy') String? modelStrategy,@JsonKey(name: 'tone_instruction') I18nText? toneInstruction,@JsonKey(name: 'synthesis_block_id') String? synthesisBlockId,@JsonKey(name: 'row_explanations_block_id') String? rowExplanationsBlockId
});


$I18nTextCopyWith<$Res>? get preambleText;$I18nTextCopyWith<$Res>? get toneInstruction;

}
/// @nodoc
class _$SynthesisConfigDTOCopyWithImpl<$Res>
    implements $SynthesisConfigDTOCopyWith<$Res> {
  _$SynthesisConfigDTOCopyWithImpl(this._self, this._then);

  final SynthesisConfigDTO _self;
  final $Res Function(SynthesisConfigDTO) _then;

/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? systemPrompt = freezed,Object? lengthConstraint = freezed,Object? preambleText = freezed,Object? historicalContextMode = null,Object? enablePiiMasking = null,Object? allowedExports = null,Object? omitEmptySections = null,Object? allowedMcpTools = null,Object? modelStrategy = freezed,Object? toneInstruction = freezed,Object? synthesisBlockId = freezed,Object? rowExplanationsBlockId = freezed,}) {
  return _then(_self.copyWith(
systemPrompt: freezed == systemPrompt ? _self.systemPrompt : systemPrompt // ignore: cast_nullable_to_non_nullable
as String?,lengthConstraint: freezed == lengthConstraint ? _self.lengthConstraint : lengthConstraint // ignore: cast_nullable_to_non_nullable
as int?,preambleText: freezed == preambleText ? _self.preambleText : preambleText // ignore: cast_nullable_to_non_nullable
as I18nText?,historicalContextMode: null == historicalContextMode ? _self.historicalContextMode : historicalContextMode // ignore: cast_nullable_to_non_nullable
as HistoricalContextMode,enablePiiMasking: null == enablePiiMasking ? _self.enablePiiMasking : enablePiiMasking // ignore: cast_nullable_to_non_nullable
as bool,allowedExports: null == allowedExports ? _self.allowedExports : allowedExports // ignore: cast_nullable_to_non_nullable
as List<String>,omitEmptySections: null == omitEmptySections ? _self.omitEmptySections : omitEmptySections // ignore: cast_nullable_to_non_nullable
as bool,allowedMcpTools: null == allowedMcpTools ? _self.allowedMcpTools : allowedMcpTools // ignore: cast_nullable_to_non_nullable
as List<String>,modelStrategy: freezed == modelStrategy ? _self.modelStrategy : modelStrategy // ignore: cast_nullable_to_non_nullable
as String?,toneInstruction: freezed == toneInstruction ? _self.toneInstruction : toneInstruction // ignore: cast_nullable_to_non_nullable
as I18nText?,synthesisBlockId: freezed == synthesisBlockId ? _self.synthesisBlockId : synthesisBlockId // ignore: cast_nullable_to_non_nullable
as String?,rowExplanationsBlockId: freezed == rowExplanationsBlockId ? _self.rowExplanationsBlockId : rowExplanationsBlockId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}
/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get preambleText {
    if (_self.preambleText == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.preambleText!, (value) {
    return _then(_self.copyWith(preambleText: value));
  });
}/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get toneInstruction {
    if (_self.toneInstruction == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.toneInstruction!, (value) {
    return _then(_self.copyWith(toneInstruction: value));
  });
}
}


/// Adds pattern-matching-related methods to [SynthesisConfigDTO].
extension SynthesisConfigDTOPatterns on SynthesisConfigDTO {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _SynthesisConfigDTO value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _SynthesisConfigDTO() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _SynthesisConfigDTO value)  $default,){
final _that = this;
switch (_that) {
case _SynthesisConfigDTO():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _SynthesisConfigDTO value)?  $default,){
final _that = this;
switch (_that) {
case _SynthesisConfigDTO() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String? systemPrompt,  int? lengthConstraint,  I18nText? preambleText, @JsonKey(name: 'historical_context_mode', unknownEnumValue: HistoricalContextMode.disabled)  HistoricalContextMode historicalContextMode,  bool enablePiiMasking,  List<String> allowedExports,  bool omitEmptySections,  List<String> allowedMcpTools, @JsonKey(name: 'model_strategy')  String? modelStrategy, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction, @JsonKey(name: 'synthesis_block_id')  String? synthesisBlockId, @JsonKey(name: 'row_explanations_block_id')  String? rowExplanationsBlockId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _SynthesisConfigDTO() when $default != null:
return $default(_that.systemPrompt,_that.lengthConstraint,_that.preambleText,_that.historicalContextMode,_that.enablePiiMasking,_that.allowedExports,_that.omitEmptySections,_that.allowedMcpTools,_that.modelStrategy,_that.toneInstruction,_that.synthesisBlockId,_that.rowExplanationsBlockId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String? systemPrompt,  int? lengthConstraint,  I18nText? preambleText, @JsonKey(name: 'historical_context_mode', unknownEnumValue: HistoricalContextMode.disabled)  HistoricalContextMode historicalContextMode,  bool enablePiiMasking,  List<String> allowedExports,  bool omitEmptySections,  List<String> allowedMcpTools, @JsonKey(name: 'model_strategy')  String? modelStrategy, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction, @JsonKey(name: 'synthesis_block_id')  String? synthesisBlockId, @JsonKey(name: 'row_explanations_block_id')  String? rowExplanationsBlockId)  $default,) {final _that = this;
switch (_that) {
case _SynthesisConfigDTO():
return $default(_that.systemPrompt,_that.lengthConstraint,_that.preambleText,_that.historicalContextMode,_that.enablePiiMasking,_that.allowedExports,_that.omitEmptySections,_that.allowedMcpTools,_that.modelStrategy,_that.toneInstruction,_that.synthesisBlockId,_that.rowExplanationsBlockId);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String? systemPrompt,  int? lengthConstraint,  I18nText? preambleText, @JsonKey(name: 'historical_context_mode', unknownEnumValue: HistoricalContextMode.disabled)  HistoricalContextMode historicalContextMode,  bool enablePiiMasking,  List<String> allowedExports,  bool omitEmptySections,  List<String> allowedMcpTools, @JsonKey(name: 'model_strategy')  String? modelStrategy, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction, @JsonKey(name: 'synthesis_block_id')  String? synthesisBlockId, @JsonKey(name: 'row_explanations_block_id')  String? rowExplanationsBlockId)?  $default,) {final _that = this;
switch (_that) {
case _SynthesisConfigDTO() when $default != null:
return $default(_that.systemPrompt,_that.lengthConstraint,_that.preambleText,_that.historicalContextMode,_that.enablePiiMasking,_that.allowedExports,_that.omitEmptySections,_that.allowedMcpTools,_that.modelStrategy,_that.toneInstruction,_that.synthesisBlockId,_that.rowExplanationsBlockId);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _SynthesisConfigDTO extends SynthesisConfigDTO {
  const _SynthesisConfigDTO({this.systemPrompt, this.lengthConstraint, this.preambleText, @JsonKey(name: 'historical_context_mode', unknownEnumValue: HistoricalContextMode.disabled) this.historicalContextMode = HistoricalContextMode.disabled, this.enablePiiMasking = false, final  List<String> allowedExports = const ['pdf', 'raw_json'], this.omitEmptySections = true, final  List<String> allowedMcpTools = const [], @JsonKey(name: 'model_strategy') this.modelStrategy, @JsonKey(name: 'tone_instruction') this.toneInstruction, @JsonKey(name: 'synthesis_block_id') this.synthesisBlockId, @JsonKey(name: 'row_explanations_block_id') this.rowExplanationsBlockId}): _allowedExports = allowedExports,_allowedMcpTools = allowedMcpTools,super._();
  factory _SynthesisConfigDTO.fromJson(Map<String, dynamic> json) => _$SynthesisConfigDTOFromJson(json);

@override final  String? systemPrompt;
@override final  int? lengthConstraint;
@override final  I18nText? preambleText;
@override@JsonKey(name: 'historical_context_mode', unknownEnumValue: HistoricalContextMode.disabled) final  HistoricalContextMode historicalContextMode;
@override@JsonKey() final  bool enablePiiMasking;
 final  List<String> _allowedExports;
@override@JsonKey() List<String> get allowedExports {
  if (_allowedExports is EqualUnmodifiableListView) return _allowedExports;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_allowedExports);
}

@override@JsonKey() final  bool omitEmptySections;
 final  List<String> _allowedMcpTools;
@override@JsonKey() List<String> get allowedMcpTools {
  if (_allowedMcpTools is EqualUnmodifiableListView) return _allowedMcpTools;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_allowedMcpTools);
}

@override@JsonKey(name: 'model_strategy') final  String? modelStrategy;
@override@JsonKey(name: 'tone_instruction') final  I18nText? toneInstruction;
@override@JsonKey(name: 'synthesis_block_id') final  String? synthesisBlockId;
@override@JsonKey(name: 'row_explanations_block_id') final  String? rowExplanationsBlockId;

/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$SynthesisConfigDTOCopyWith<_SynthesisConfigDTO> get copyWith => __$SynthesisConfigDTOCopyWithImpl<_SynthesisConfigDTO>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$SynthesisConfigDTOToJson(this, );
}



@override
String toString() {
  return 'SynthesisConfigDTO(systemPrompt: $systemPrompt, lengthConstraint: $lengthConstraint, preambleText: $preambleText, historicalContextMode: $historicalContextMode, enablePiiMasking: $enablePiiMasking, allowedExports: $allowedExports, omitEmptySections: $omitEmptySections, allowedMcpTools: $allowedMcpTools, modelStrategy: $modelStrategy, toneInstruction: $toneInstruction, synthesisBlockId: $synthesisBlockId, rowExplanationsBlockId: $rowExplanationsBlockId)';
}


}

/// @nodoc
abstract mixin class _$SynthesisConfigDTOCopyWith<$Res> implements $SynthesisConfigDTOCopyWith<$Res> {
  factory _$SynthesisConfigDTOCopyWith(_SynthesisConfigDTO value, $Res Function(_SynthesisConfigDTO) _then) = __$SynthesisConfigDTOCopyWithImpl;
@override @useResult
$Res call({
 String? systemPrompt, int? lengthConstraint, I18nText? preambleText,@JsonKey(name: 'historical_context_mode', unknownEnumValue: HistoricalContextMode.disabled) HistoricalContextMode historicalContextMode, bool enablePiiMasking, List<String> allowedExports, bool omitEmptySections, List<String> allowedMcpTools,@JsonKey(name: 'model_strategy') String? modelStrategy,@JsonKey(name: 'tone_instruction') I18nText? toneInstruction,@JsonKey(name: 'synthesis_block_id') String? synthesisBlockId,@JsonKey(name: 'row_explanations_block_id') String? rowExplanationsBlockId
});


@override $I18nTextCopyWith<$Res>? get preambleText;@override $I18nTextCopyWith<$Res>? get toneInstruction;

}
/// @nodoc
class __$SynthesisConfigDTOCopyWithImpl<$Res>
    implements _$SynthesisConfigDTOCopyWith<$Res> {
  __$SynthesisConfigDTOCopyWithImpl(this._self, this._then);

  final _SynthesisConfigDTO _self;
  final $Res Function(_SynthesisConfigDTO) _then;

/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? systemPrompt = freezed,Object? lengthConstraint = freezed,Object? preambleText = freezed,Object? historicalContextMode = null,Object? enablePiiMasking = null,Object? allowedExports = null,Object? omitEmptySections = null,Object? allowedMcpTools = null,Object? modelStrategy = freezed,Object? toneInstruction = freezed,Object? synthesisBlockId = freezed,Object? rowExplanationsBlockId = freezed,}) {
  return _then(_SynthesisConfigDTO(
systemPrompt: freezed == systemPrompt ? _self.systemPrompt : systemPrompt // ignore: cast_nullable_to_non_nullable
as String?,lengthConstraint: freezed == lengthConstraint ? _self.lengthConstraint : lengthConstraint // ignore: cast_nullable_to_non_nullable
as int?,preambleText: freezed == preambleText ? _self.preambleText : preambleText // ignore: cast_nullable_to_non_nullable
as I18nText?,historicalContextMode: null == historicalContextMode ? _self.historicalContextMode : historicalContextMode // ignore: cast_nullable_to_non_nullable
as HistoricalContextMode,enablePiiMasking: null == enablePiiMasking ? _self.enablePiiMasking : enablePiiMasking // ignore: cast_nullable_to_non_nullable
as bool,allowedExports: null == allowedExports ? _self._allowedExports : allowedExports // ignore: cast_nullable_to_non_nullable
as List<String>,omitEmptySections: null == omitEmptySections ? _self.omitEmptySections : omitEmptySections // ignore: cast_nullable_to_non_nullable
as bool,allowedMcpTools: null == allowedMcpTools ? _self._allowedMcpTools : allowedMcpTools // ignore: cast_nullable_to_non_nullable
as List<String>,modelStrategy: freezed == modelStrategy ? _self.modelStrategy : modelStrategy // ignore: cast_nullable_to_non_nullable
as String?,toneInstruction: freezed == toneInstruction ? _self.toneInstruction : toneInstruction // ignore: cast_nullable_to_non_nullable
as I18nText?,synthesisBlockId: freezed == synthesisBlockId ? _self.synthesisBlockId : synthesisBlockId // ignore: cast_nullable_to_non_nullable
as String?,rowExplanationsBlockId: freezed == rowExplanationsBlockId ? _self.rowExplanationsBlockId : rowExplanationsBlockId // ignore: cast_nullable_to_non_nullable
as String?,
  ));
}

/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get preambleText {
    if (_self.preambleText == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.preambleText!, (value) {
    return _then(_self.copyWith(preambleText: value));
  });
}/// Create a copy of SynthesisConfigDTO
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get toneInstruction {
    if (_self.toneInstruction == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.toneInstruction!, (value) {
    return _then(_self.copyWith(toneInstruction: value));
  });
}
}


/// @nodoc
mixin _$OutputProfile {

@StrictOpaqueIdConverter() String get id; String get slug;@StrictOpaqueIdConverter() String get workflowId; String? get organizationId; I18nText get name; I18nText? get description;@JsonKey(name: 'user_role_label') I18nText? get userRoleLabel;@JsonKey(name: 'custom_preface') I18nText? get customPreface; List<String> get visibleMetadata; List<XaiExtensionType> get visibleBlockExtensions; List<XaiExtensionType> get visibleWorkflowExtensions;@JsonKey(name: 'max_extension_items') int? get maxExtensionItems; String get displayScale;@JsonKey(name: 'include_diagnostic_scorecard') bool get includeDiagnosticScorecard;@JsonKey(name: 'strictness_level') int? get strictnessLevel;@JsonKey(name: 'scoring_strategy') ScoringStrategy? get scoringStrategy;@JsonKey(name: 'tone_instruction') I18nText? get toneInstruction; String? get language;@JsonKey(name: 'user_role_mappings') Map<String, I18nText> get userRoleMappings;@JsonKey(name: 'extension_labels') Map<String, I18nText> get extensionLabels; List<OutputLayoutBlock> get layouts;@JsonKey(name: 'content_blocks') List<SduiBlockDTO> get contentBlocks;
/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OutputProfileCopyWith<OutputProfile> get copyWith => _$OutputProfileCopyWithImpl<OutputProfile>(this as OutputProfile, _$identity);

  /// Serializes this OutputProfile to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'OutputProfile(id: $id, slug: $slug, workflowId: $workflowId, organizationId: $organizationId, name: $name, description: $description, userRoleLabel: $userRoleLabel, customPreface: $customPreface, visibleMetadata: $visibleMetadata, visibleBlockExtensions: $visibleBlockExtensions, visibleWorkflowExtensions: $visibleWorkflowExtensions, maxExtensionItems: $maxExtensionItems, displayScale: $displayScale, includeDiagnosticScorecard: $includeDiagnosticScorecard, strictnessLevel: $strictnessLevel, scoringStrategy: $scoringStrategy, toneInstruction: $toneInstruction, language: $language, userRoleMappings: $userRoleMappings, extensionLabels: $extensionLabels, layouts: $layouts, contentBlocks: $contentBlocks)';
}


}

/// @nodoc
abstract mixin class $OutputProfileCopyWith<$Res>  {
  factory $OutputProfileCopyWith(OutputProfile value, $Res Function(OutputProfile) _then) = _$OutputProfileCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug,@StrictOpaqueIdConverter() String workflowId, String? organizationId, I18nText name, I18nText? description,@JsonKey(name: 'user_role_label') I18nText? userRoleLabel,@JsonKey(name: 'custom_preface') I18nText? customPreface, List<String> visibleMetadata, List<XaiExtensionType> visibleBlockExtensions, List<XaiExtensionType> visibleWorkflowExtensions,@JsonKey(name: 'max_extension_items') int? maxExtensionItems, String displayScale,@JsonKey(name: 'include_diagnostic_scorecard') bool includeDiagnosticScorecard,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,@JsonKey(name: 'tone_instruction') I18nText? toneInstruction, String? language,@JsonKey(name: 'user_role_mappings') Map<String, I18nText> userRoleMappings,@JsonKey(name: 'extension_labels') Map<String, I18nText> extensionLabels, List<OutputLayoutBlock> layouts,@JsonKey(name: 'content_blocks') List<SduiBlockDTO> contentBlocks
});


$I18nTextCopyWith<$Res> get name;$I18nTextCopyWith<$Res>? get description;$I18nTextCopyWith<$Res>? get userRoleLabel;$I18nTextCopyWith<$Res>? get customPreface;$I18nTextCopyWith<$Res>? get toneInstruction;

}
/// @nodoc
class _$OutputProfileCopyWithImpl<$Res>
    implements $OutputProfileCopyWith<$Res> {
  _$OutputProfileCopyWithImpl(this._self, this._then);

  final OutputProfile _self;
  final $Res Function(OutputProfile) _then;

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? workflowId = null,Object? organizationId = freezed,Object? name = null,Object? description = freezed,Object? userRoleLabel = freezed,Object? customPreface = freezed,Object? visibleMetadata = null,Object? visibleBlockExtensions = null,Object? visibleWorkflowExtensions = null,Object? maxExtensionItems = freezed,Object? displayScale = null,Object? includeDiagnosticScorecard = null,Object? strictnessLevel = freezed,Object? scoringStrategy = freezed,Object? toneInstruction = freezed,Object? language = freezed,Object? userRoleMappings = null,Object? extensionLabels = null,Object? layouts = null,Object? contentBlocks = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,userRoleLabel: freezed == userRoleLabel ? _self.userRoleLabel : userRoleLabel // ignore: cast_nullable_to_non_nullable
as I18nText?,customPreface: freezed == customPreface ? _self.customPreface : customPreface // ignore: cast_nullable_to_non_nullable
as I18nText?,visibleMetadata: null == visibleMetadata ? _self.visibleMetadata : visibleMetadata // ignore: cast_nullable_to_non_nullable
as List<String>,visibleBlockExtensions: null == visibleBlockExtensions ? _self.visibleBlockExtensions : visibleBlockExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,visibleWorkflowExtensions: null == visibleWorkflowExtensions ? _self.visibleWorkflowExtensions : visibleWorkflowExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,maxExtensionItems: freezed == maxExtensionItems ? _self.maxExtensionItems : maxExtensionItems // ignore: cast_nullable_to_non_nullable
as int?,displayScale: null == displayScale ? _self.displayScale : displayScale // ignore: cast_nullable_to_non_nullable
as String,includeDiagnosticScorecard: null == includeDiagnosticScorecard ? _self.includeDiagnosticScorecard : includeDiagnosticScorecard // ignore: cast_nullable_to_non_nullable
as bool,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy?,toneInstruction: freezed == toneInstruction ? _self.toneInstruction : toneInstruction // ignore: cast_nullable_to_non_nullable
as I18nText?,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String?,userRoleMappings: null == userRoleMappings ? _self.userRoleMappings : userRoleMappings // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,extensionLabels: null == extensionLabels ? _self.extensionLabels : extensionLabels // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,layouts: null == layouts ? _self.layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<OutputLayoutBlock>,contentBlocks: null == contentBlocks ? _self.contentBlocks : contentBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,
  ));
}
/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of OutputProfile
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
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get userRoleLabel {
    if (_self.userRoleLabel == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.userRoleLabel!, (value) {
    return _then(_self.copyWith(userRoleLabel: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get customPreface {
    if (_self.customPreface == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.customPreface!, (value) {
    return _then(_self.copyWith(customPreface: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get toneInstruction {
    if (_self.toneInstruction == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.toneInstruction!, (value) {
    return _then(_self.copyWith(toneInstruction: value));
  });
}
}


/// Adds pattern-matching-related methods to [OutputProfile].
extension OutputProfilePatterns on OutputProfile {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _OutputProfile value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _OutputProfile value)  $default,){
final _that = this;
switch (_that) {
case _OutputProfile():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _OutputProfile value)?  $default,){
final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()  String workflowId,  String? organizationId,  I18nText name,  I18nText? description, @JsonKey(name: 'user_role_label')  I18nText? userRoleLabel, @JsonKey(name: 'custom_preface')  I18nText? customPreface,  List<String> visibleMetadata,  List<XaiExtensionType> visibleBlockExtensions,  List<XaiExtensionType> visibleWorkflowExtensions, @JsonKey(name: 'max_extension_items')  int? maxExtensionItems,  String displayScale, @JsonKey(name: 'include_diagnostic_scorecard')  bool includeDiagnosticScorecard, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction,  String? language, @JsonKey(name: 'user_role_mappings')  Map<String, I18nText> userRoleMappings, @JsonKey(name: 'extension_labels')  Map<String, I18nText> extensionLabels,  List<OutputLayoutBlock> layouts, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
return $default(_that.id,_that.slug,_that.workflowId,_that.organizationId,_that.name,_that.description,_that.userRoleLabel,_that.customPreface,_that.visibleMetadata,_that.visibleBlockExtensions,_that.visibleWorkflowExtensions,_that.maxExtensionItems,_that.displayScale,_that.includeDiagnosticScorecard,_that.strictnessLevel,_that.scoringStrategy,_that.toneInstruction,_that.language,_that.userRoleMappings,_that.extensionLabels,_that.layouts,_that.contentBlocks);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()  String workflowId,  String? organizationId,  I18nText name,  I18nText? description, @JsonKey(name: 'user_role_label')  I18nText? userRoleLabel, @JsonKey(name: 'custom_preface')  I18nText? customPreface,  List<String> visibleMetadata,  List<XaiExtensionType> visibleBlockExtensions,  List<XaiExtensionType> visibleWorkflowExtensions, @JsonKey(name: 'max_extension_items')  int? maxExtensionItems,  String displayScale, @JsonKey(name: 'include_diagnostic_scorecard')  bool includeDiagnosticScorecard, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction,  String? language, @JsonKey(name: 'user_role_mappings')  Map<String, I18nText> userRoleMappings, @JsonKey(name: 'extension_labels')  Map<String, I18nText> extensionLabels,  List<OutputLayoutBlock> layouts, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks)  $default,) {final _that = this;
switch (_that) {
case _OutputProfile():
return $default(_that.id,_that.slug,_that.workflowId,_that.organizationId,_that.name,_that.description,_that.userRoleLabel,_that.customPreface,_that.visibleMetadata,_that.visibleBlockExtensions,_that.visibleWorkflowExtensions,_that.maxExtensionItems,_that.displayScale,_that.includeDiagnosticScorecard,_that.strictnessLevel,_that.scoringStrategy,_that.toneInstruction,_that.language,_that.userRoleMappings,_that.extensionLabels,_that.layouts,_that.contentBlocks);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()  String workflowId,  String? organizationId,  I18nText name,  I18nText? description, @JsonKey(name: 'user_role_label')  I18nText? userRoleLabel, @JsonKey(name: 'custom_preface')  I18nText? customPreface,  List<String> visibleMetadata,  List<XaiExtensionType> visibleBlockExtensions,  List<XaiExtensionType> visibleWorkflowExtensions, @JsonKey(name: 'max_extension_items')  int? maxExtensionItems,  String displayScale, @JsonKey(name: 'include_diagnostic_scorecard')  bool includeDiagnosticScorecard, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction,  String? language, @JsonKey(name: 'user_role_mappings')  Map<String, I18nText> userRoleMappings, @JsonKey(name: 'extension_labels')  Map<String, I18nText> extensionLabels,  List<OutputLayoutBlock> layouts, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks)?  $default,) {final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
return $default(_that.id,_that.slug,_that.workflowId,_that.organizationId,_that.name,_that.description,_that.userRoleLabel,_that.customPreface,_that.visibleMetadata,_that.visibleBlockExtensions,_that.visibleWorkflowExtensions,_that.maxExtensionItems,_that.displayScale,_that.includeDiagnosticScorecard,_that.strictnessLevel,_that.scoringStrategy,_that.toneInstruction,_that.language,_that.userRoleMappings,_that.extensionLabels,_that.layouts,_that.contentBlocks);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _OutputProfile extends OutputProfile {
  const _OutputProfile({@StrictOpaqueIdConverter() required this.id, this.slug = '', @StrictOpaqueIdConverter() required this.workflowId, this.organizationId, required this.name, this.description, @JsonKey(name: 'user_role_label') this.userRoleLabel, @JsonKey(name: 'custom_preface') this.customPreface, final  List<String> visibleMetadata = const ['date', 'organization'], final  List<XaiExtensionType> visibleBlockExtensions = const [], final  List<XaiExtensionType> visibleWorkflowExtensions = const [], @JsonKey(name: 'max_extension_items') this.maxExtensionItems, this.displayScale = 'original', @JsonKey(name: 'include_diagnostic_scorecard') this.includeDiagnosticScorecard = false, @JsonKey(name: 'strictness_level') this.strictnessLevel, @JsonKey(name: 'scoring_strategy') this.scoringStrategy, @JsonKey(name: 'tone_instruction') this.toneInstruction, this.language, @JsonKey(name: 'user_role_mappings') final  Map<String, I18nText> userRoleMappings = const {}, @JsonKey(name: 'extension_labels') final  Map<String, I18nText> extensionLabels = const {}, final  List<OutputLayoutBlock> layouts = const [], @JsonKey(name: 'content_blocks') final  List<SduiBlockDTO> contentBlocks = const []}): _visibleMetadata = visibleMetadata,_visibleBlockExtensions = visibleBlockExtensions,_visibleWorkflowExtensions = visibleWorkflowExtensions,_userRoleMappings = userRoleMappings,_extensionLabels = extensionLabels,_layouts = layouts,_contentBlocks = contentBlocks,super._();
  factory _OutputProfile.fromJson(Map<String, dynamic> json) => _$OutputProfileFromJson(json);

@override@StrictOpaqueIdConverter() final  String id;
@override@JsonKey() final  String slug;
@override@StrictOpaqueIdConverter() final  String workflowId;
@override final  String? organizationId;
@override final  I18nText name;
@override final  I18nText? description;
@override@JsonKey(name: 'user_role_label') final  I18nText? userRoleLabel;
@override@JsonKey(name: 'custom_preface') final  I18nText? customPreface;
 final  List<String> _visibleMetadata;
@override@JsonKey() List<String> get visibleMetadata {
  if (_visibleMetadata is EqualUnmodifiableListView) return _visibleMetadata;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleMetadata);
}

 final  List<XaiExtensionType> _visibleBlockExtensions;
@override@JsonKey() List<XaiExtensionType> get visibleBlockExtensions {
  if (_visibleBlockExtensions is EqualUnmodifiableListView) return _visibleBlockExtensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleBlockExtensions);
}

 final  List<XaiExtensionType> _visibleWorkflowExtensions;
@override@JsonKey() List<XaiExtensionType> get visibleWorkflowExtensions {
  if (_visibleWorkflowExtensions is EqualUnmodifiableListView) return _visibleWorkflowExtensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleWorkflowExtensions);
}

@override@JsonKey(name: 'max_extension_items') final  int? maxExtensionItems;
@override@JsonKey() final  String displayScale;
@override@JsonKey(name: 'include_diagnostic_scorecard') final  bool includeDiagnosticScorecard;
@override@JsonKey(name: 'strictness_level') final  int? strictnessLevel;
@override@JsonKey(name: 'scoring_strategy') final  ScoringStrategy? scoringStrategy;
@override@JsonKey(name: 'tone_instruction') final  I18nText? toneInstruction;
@override final  String? language;
 final  Map<String, I18nText> _userRoleMappings;
@override@JsonKey(name: 'user_role_mappings') Map<String, I18nText> get userRoleMappings {
  if (_userRoleMappings is EqualUnmodifiableMapView) return _userRoleMappings;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_userRoleMappings);
}

 final  Map<String, I18nText> _extensionLabels;
@override@JsonKey(name: 'extension_labels') Map<String, I18nText> get extensionLabels {
  if (_extensionLabels is EqualUnmodifiableMapView) return _extensionLabels;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_extensionLabels);
}

 final  List<OutputLayoutBlock> _layouts;
@override@JsonKey() List<OutputLayoutBlock> get layouts {
  if (_layouts is EqualUnmodifiableListView) return _layouts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_layouts);
}

 final  List<SduiBlockDTO> _contentBlocks;
@override@JsonKey(name: 'content_blocks') List<SduiBlockDTO> get contentBlocks {
  if (_contentBlocks is EqualUnmodifiableListView) return _contentBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_contentBlocks);
}


/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$OutputProfileCopyWith<_OutputProfile> get copyWith => __$OutputProfileCopyWithImpl<_OutputProfile>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$OutputProfileToJson(this, );
}



@override
String toString() {
  return 'OutputProfile(id: $id, slug: $slug, workflowId: $workflowId, organizationId: $organizationId, name: $name, description: $description, userRoleLabel: $userRoleLabel, customPreface: $customPreface, visibleMetadata: $visibleMetadata, visibleBlockExtensions: $visibleBlockExtensions, visibleWorkflowExtensions: $visibleWorkflowExtensions, maxExtensionItems: $maxExtensionItems, displayScale: $displayScale, includeDiagnosticScorecard: $includeDiagnosticScorecard, strictnessLevel: $strictnessLevel, scoringStrategy: $scoringStrategy, toneInstruction: $toneInstruction, language: $language, userRoleMappings: $userRoleMappings, extensionLabels: $extensionLabels, layouts: $layouts, contentBlocks: $contentBlocks)';
}


}

/// @nodoc
abstract mixin class _$OutputProfileCopyWith<$Res> implements $OutputProfileCopyWith<$Res> {
  factory _$OutputProfileCopyWith(_OutputProfile value, $Res Function(_OutputProfile) _then) = __$OutputProfileCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug,@StrictOpaqueIdConverter() String workflowId, String? organizationId, I18nText name, I18nText? description,@JsonKey(name: 'user_role_label') I18nText? userRoleLabel,@JsonKey(name: 'custom_preface') I18nText? customPreface, List<String> visibleMetadata, List<XaiExtensionType> visibleBlockExtensions, List<XaiExtensionType> visibleWorkflowExtensions,@JsonKey(name: 'max_extension_items') int? maxExtensionItems, String displayScale,@JsonKey(name: 'include_diagnostic_scorecard') bool includeDiagnosticScorecard,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,@JsonKey(name: 'tone_instruction') I18nText? toneInstruction, String? language,@JsonKey(name: 'user_role_mappings') Map<String, I18nText> userRoleMappings,@JsonKey(name: 'extension_labels') Map<String, I18nText> extensionLabels, List<OutputLayoutBlock> layouts,@JsonKey(name: 'content_blocks') List<SduiBlockDTO> contentBlocks
});


@override $I18nTextCopyWith<$Res> get name;@override $I18nTextCopyWith<$Res>? get description;@override $I18nTextCopyWith<$Res>? get userRoleLabel;@override $I18nTextCopyWith<$Res>? get customPreface;@override $I18nTextCopyWith<$Res>? get toneInstruction;

}
/// @nodoc
class __$OutputProfileCopyWithImpl<$Res>
    implements _$OutputProfileCopyWith<$Res> {
  __$OutputProfileCopyWithImpl(this._self, this._then);

  final _OutputProfile _self;
  final $Res Function(_OutputProfile) _then;

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? workflowId = null,Object? organizationId = freezed,Object? name = null,Object? description = freezed,Object? userRoleLabel = freezed,Object? customPreface = freezed,Object? visibleMetadata = null,Object? visibleBlockExtensions = null,Object? visibleWorkflowExtensions = null,Object? maxExtensionItems = freezed,Object? displayScale = null,Object? includeDiagnosticScorecard = null,Object? strictnessLevel = freezed,Object? scoringStrategy = freezed,Object? toneInstruction = freezed,Object? language = freezed,Object? userRoleMappings = null,Object? extensionLabels = null,Object? layouts = null,Object? contentBlocks = null,}) {
  return _then(_OutputProfile(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,slug: null == slug ? _self.slug : slug // ignore: cast_nullable_to_non_nullable
as String,workflowId: null == workflowId ? _self.workflowId : workflowId // ignore: cast_nullable_to_non_nullable
as String,organizationId: freezed == organizationId ? _self.organizationId : organizationId // ignore: cast_nullable_to_non_nullable
as String?,name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,userRoleLabel: freezed == userRoleLabel ? _self.userRoleLabel : userRoleLabel // ignore: cast_nullable_to_non_nullable
as I18nText?,customPreface: freezed == customPreface ? _self.customPreface : customPreface // ignore: cast_nullable_to_non_nullable
as I18nText?,visibleMetadata: null == visibleMetadata ? _self._visibleMetadata : visibleMetadata // ignore: cast_nullable_to_non_nullable
as List<String>,visibleBlockExtensions: null == visibleBlockExtensions ? _self._visibleBlockExtensions : visibleBlockExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,visibleWorkflowExtensions: null == visibleWorkflowExtensions ? _self._visibleWorkflowExtensions : visibleWorkflowExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,maxExtensionItems: freezed == maxExtensionItems ? _self.maxExtensionItems : maxExtensionItems // ignore: cast_nullable_to_non_nullable
as int?,displayScale: null == displayScale ? _self.displayScale : displayScale // ignore: cast_nullable_to_non_nullable
as String,includeDiagnosticScorecard: null == includeDiagnosticScorecard ? _self.includeDiagnosticScorecard : includeDiagnosticScorecard // ignore: cast_nullable_to_non_nullable
as bool,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy?,toneInstruction: freezed == toneInstruction ? _self.toneInstruction : toneInstruction // ignore: cast_nullable_to_non_nullable
as I18nText?,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String?,userRoleMappings: null == userRoleMappings ? _self._userRoleMappings : userRoleMappings // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,extensionLabels: null == extensionLabels ? _self._extensionLabels : extensionLabels // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,layouts: null == layouts ? _self._layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<OutputLayoutBlock>,contentBlocks: null == contentBlocks ? _self._contentBlocks : contentBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,
  ));
}

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of OutputProfile
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
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get userRoleLabel {
    if (_self.userRoleLabel == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.userRoleLabel!, (value) {
    return _then(_self.copyWith(userRoleLabel: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get customPreface {
    if (_self.customPreface == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.customPreface!, (value) {
    return _then(_self.copyWith(customPreface: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get toneInstruction {
    if (_self.toneInstruction == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.toneInstruction!, (value) {
    return _then(_self.copyWith(toneInstruction: value));
  });
}
}


/// @nodoc
mixin _$EmbeddedOutputProfile {

 I18nText get name; I18nText? get description;@JsonKey(name: 'user_role_label') I18nText? get userRoleLabel;@JsonKey(name: 'custom_preface') I18nText? get customPreface; List<String> get visibleMetadata; List<XaiExtensionType> get visibleBlockExtensions; List<XaiExtensionType> get visibleWorkflowExtensions;@JsonKey(name: 'max_extension_items') int? get maxExtensionItems; String get displayScale;@JsonKey(name: 'include_diagnostic_scorecard') bool get includeDiagnosticScorecard;@JsonKey(name: 'strictness_level') int? get strictnessLevel;@JsonKey(name: 'scoring_strategy') ScoringStrategy? get scoringStrategy;@JsonKey(name: 'tone_instruction') I18nText? get toneInstruction; String? get language;@JsonKey(name: 'user_role_mappings') Map<String, I18nText> get userRoleMappings;@JsonKey(name: 'extension_labels') Map<String, I18nText> get extensionLabels; List<OutputLayoutBlock> get layouts;@JsonKey(name: 'content_blocks') List<SduiBlockDTO> get contentBlocks;
/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$EmbeddedOutputProfileCopyWith<EmbeddedOutputProfile> get copyWith => _$EmbeddedOutputProfileCopyWithImpl<EmbeddedOutputProfile>(this as EmbeddedOutputProfile, _$identity);

  /// Serializes this EmbeddedOutputProfile to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'EmbeddedOutputProfile(name: $name, description: $description, userRoleLabel: $userRoleLabel, customPreface: $customPreface, visibleMetadata: $visibleMetadata, visibleBlockExtensions: $visibleBlockExtensions, visibleWorkflowExtensions: $visibleWorkflowExtensions, maxExtensionItems: $maxExtensionItems, displayScale: $displayScale, includeDiagnosticScorecard: $includeDiagnosticScorecard, strictnessLevel: $strictnessLevel, scoringStrategy: $scoringStrategy, toneInstruction: $toneInstruction, language: $language, userRoleMappings: $userRoleMappings, extensionLabels: $extensionLabels, layouts: $layouts, contentBlocks: $contentBlocks)';
}


}

/// @nodoc
abstract mixin class $EmbeddedOutputProfileCopyWith<$Res>  {
  factory $EmbeddedOutputProfileCopyWith(EmbeddedOutputProfile value, $Res Function(EmbeddedOutputProfile) _then) = _$EmbeddedOutputProfileCopyWithImpl;
@useResult
$Res call({
 I18nText name, I18nText? description,@JsonKey(name: 'user_role_label') I18nText? userRoleLabel,@JsonKey(name: 'custom_preface') I18nText? customPreface, List<String> visibleMetadata, List<XaiExtensionType> visibleBlockExtensions, List<XaiExtensionType> visibleWorkflowExtensions,@JsonKey(name: 'max_extension_items') int? maxExtensionItems, String displayScale,@JsonKey(name: 'include_diagnostic_scorecard') bool includeDiagnosticScorecard,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,@JsonKey(name: 'tone_instruction') I18nText? toneInstruction, String? language,@JsonKey(name: 'user_role_mappings') Map<String, I18nText> userRoleMappings,@JsonKey(name: 'extension_labels') Map<String, I18nText> extensionLabels, List<OutputLayoutBlock> layouts,@JsonKey(name: 'content_blocks') List<SduiBlockDTO> contentBlocks
});


$I18nTextCopyWith<$Res> get name;$I18nTextCopyWith<$Res>? get description;$I18nTextCopyWith<$Res>? get userRoleLabel;$I18nTextCopyWith<$Res>? get customPreface;$I18nTextCopyWith<$Res>? get toneInstruction;

}
/// @nodoc
class _$EmbeddedOutputProfileCopyWithImpl<$Res>
    implements $EmbeddedOutputProfileCopyWith<$Res> {
  _$EmbeddedOutputProfileCopyWithImpl(this._self, this._then);

  final EmbeddedOutputProfile _self;
  final $Res Function(EmbeddedOutputProfile) _then;

/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? name = null,Object? description = freezed,Object? userRoleLabel = freezed,Object? customPreface = freezed,Object? visibleMetadata = null,Object? visibleBlockExtensions = null,Object? visibleWorkflowExtensions = null,Object? maxExtensionItems = freezed,Object? displayScale = null,Object? includeDiagnosticScorecard = null,Object? strictnessLevel = freezed,Object? scoringStrategy = freezed,Object? toneInstruction = freezed,Object? language = freezed,Object? userRoleMappings = null,Object? extensionLabels = null,Object? layouts = null,Object? contentBlocks = null,}) {
  return _then(_self.copyWith(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,userRoleLabel: freezed == userRoleLabel ? _self.userRoleLabel : userRoleLabel // ignore: cast_nullable_to_non_nullable
as I18nText?,customPreface: freezed == customPreface ? _self.customPreface : customPreface // ignore: cast_nullable_to_non_nullable
as I18nText?,visibleMetadata: null == visibleMetadata ? _self.visibleMetadata : visibleMetadata // ignore: cast_nullable_to_non_nullable
as List<String>,visibleBlockExtensions: null == visibleBlockExtensions ? _self.visibleBlockExtensions : visibleBlockExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,visibleWorkflowExtensions: null == visibleWorkflowExtensions ? _self.visibleWorkflowExtensions : visibleWorkflowExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,maxExtensionItems: freezed == maxExtensionItems ? _self.maxExtensionItems : maxExtensionItems // ignore: cast_nullable_to_non_nullable
as int?,displayScale: null == displayScale ? _self.displayScale : displayScale // ignore: cast_nullable_to_non_nullable
as String,includeDiagnosticScorecard: null == includeDiagnosticScorecard ? _self.includeDiagnosticScorecard : includeDiagnosticScorecard // ignore: cast_nullable_to_non_nullable
as bool,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy?,toneInstruction: freezed == toneInstruction ? _self.toneInstruction : toneInstruction // ignore: cast_nullable_to_non_nullable
as I18nText?,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String?,userRoleMappings: null == userRoleMappings ? _self.userRoleMappings : userRoleMappings // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,extensionLabels: null == extensionLabels ? _self.extensionLabels : extensionLabels // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,layouts: null == layouts ? _self.layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<OutputLayoutBlock>,contentBlocks: null == contentBlocks ? _self.contentBlocks : contentBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,
  ));
}
/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of EmbeddedOutputProfile
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
}/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get userRoleLabel {
    if (_self.userRoleLabel == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.userRoleLabel!, (value) {
    return _then(_self.copyWith(userRoleLabel: value));
  });
}/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get customPreface {
    if (_self.customPreface == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.customPreface!, (value) {
    return _then(_self.copyWith(customPreface: value));
  });
}/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get toneInstruction {
    if (_self.toneInstruction == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.toneInstruction!, (value) {
    return _then(_self.copyWith(toneInstruction: value));
  });
}
}


/// Adds pattern-matching-related methods to [EmbeddedOutputProfile].
extension EmbeddedOutputProfilePatterns on EmbeddedOutputProfile {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _EmbeddedOutputProfile value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _EmbeddedOutputProfile() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _EmbeddedOutputProfile value)  $default,){
final _that = this;
switch (_that) {
case _EmbeddedOutputProfile():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _EmbeddedOutputProfile value)?  $default,){
final _that = this;
switch (_that) {
case _EmbeddedOutputProfile() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( I18nText name,  I18nText? description, @JsonKey(name: 'user_role_label')  I18nText? userRoleLabel, @JsonKey(name: 'custom_preface')  I18nText? customPreface,  List<String> visibleMetadata,  List<XaiExtensionType> visibleBlockExtensions,  List<XaiExtensionType> visibleWorkflowExtensions, @JsonKey(name: 'max_extension_items')  int? maxExtensionItems,  String displayScale, @JsonKey(name: 'include_diagnostic_scorecard')  bool includeDiagnosticScorecard, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction,  String? language, @JsonKey(name: 'user_role_mappings')  Map<String, I18nText> userRoleMappings, @JsonKey(name: 'extension_labels')  Map<String, I18nText> extensionLabels,  List<OutputLayoutBlock> layouts, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _EmbeddedOutputProfile() when $default != null:
return $default(_that.name,_that.description,_that.userRoleLabel,_that.customPreface,_that.visibleMetadata,_that.visibleBlockExtensions,_that.visibleWorkflowExtensions,_that.maxExtensionItems,_that.displayScale,_that.includeDiagnosticScorecard,_that.strictnessLevel,_that.scoringStrategy,_that.toneInstruction,_that.language,_that.userRoleMappings,_that.extensionLabels,_that.layouts,_that.contentBlocks);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( I18nText name,  I18nText? description, @JsonKey(name: 'user_role_label')  I18nText? userRoleLabel, @JsonKey(name: 'custom_preface')  I18nText? customPreface,  List<String> visibleMetadata,  List<XaiExtensionType> visibleBlockExtensions,  List<XaiExtensionType> visibleWorkflowExtensions, @JsonKey(name: 'max_extension_items')  int? maxExtensionItems,  String displayScale, @JsonKey(name: 'include_diagnostic_scorecard')  bool includeDiagnosticScorecard, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction,  String? language, @JsonKey(name: 'user_role_mappings')  Map<String, I18nText> userRoleMappings, @JsonKey(name: 'extension_labels')  Map<String, I18nText> extensionLabels,  List<OutputLayoutBlock> layouts, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks)  $default,) {final _that = this;
switch (_that) {
case _EmbeddedOutputProfile():
return $default(_that.name,_that.description,_that.userRoleLabel,_that.customPreface,_that.visibleMetadata,_that.visibleBlockExtensions,_that.visibleWorkflowExtensions,_that.maxExtensionItems,_that.displayScale,_that.includeDiagnosticScorecard,_that.strictnessLevel,_that.scoringStrategy,_that.toneInstruction,_that.language,_that.userRoleMappings,_that.extensionLabels,_that.layouts,_that.contentBlocks);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( I18nText name,  I18nText? description, @JsonKey(name: 'user_role_label')  I18nText? userRoleLabel, @JsonKey(name: 'custom_preface')  I18nText? customPreface,  List<String> visibleMetadata,  List<XaiExtensionType> visibleBlockExtensions,  List<XaiExtensionType> visibleWorkflowExtensions, @JsonKey(name: 'max_extension_items')  int? maxExtensionItems,  String displayScale, @JsonKey(name: 'include_diagnostic_scorecard')  bool includeDiagnosticScorecard, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction,  String? language, @JsonKey(name: 'user_role_mappings')  Map<String, I18nText> userRoleMappings, @JsonKey(name: 'extension_labels')  Map<String, I18nText> extensionLabels,  List<OutputLayoutBlock> layouts, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks)?  $default,) {final _that = this;
switch (_that) {
case _EmbeddedOutputProfile() when $default != null:
return $default(_that.name,_that.description,_that.userRoleLabel,_that.customPreface,_that.visibleMetadata,_that.visibleBlockExtensions,_that.visibleWorkflowExtensions,_that.maxExtensionItems,_that.displayScale,_that.includeDiagnosticScorecard,_that.strictnessLevel,_that.scoringStrategy,_that.toneInstruction,_that.language,_that.userRoleMappings,_that.extensionLabels,_that.layouts,_that.contentBlocks);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _EmbeddedOutputProfile extends EmbeddedOutputProfile {
  const _EmbeddedOutputProfile({required this.name, this.description, @JsonKey(name: 'user_role_label') this.userRoleLabel, @JsonKey(name: 'custom_preface') this.customPreface, final  List<String> visibleMetadata = const ['date', 'organization'], final  List<XaiExtensionType> visibleBlockExtensions = const [], final  List<XaiExtensionType> visibleWorkflowExtensions = const [], @JsonKey(name: 'max_extension_items') this.maxExtensionItems, this.displayScale = 'original', @JsonKey(name: 'include_diagnostic_scorecard') this.includeDiagnosticScorecard = false, @JsonKey(name: 'strictness_level') this.strictnessLevel, @JsonKey(name: 'scoring_strategy') this.scoringStrategy, @JsonKey(name: 'tone_instruction') this.toneInstruction, this.language, @JsonKey(name: 'user_role_mappings') final  Map<String, I18nText> userRoleMappings = const {}, @JsonKey(name: 'extension_labels') final  Map<String, I18nText> extensionLabels = const {}, final  List<OutputLayoutBlock> layouts = const [], @JsonKey(name: 'content_blocks') final  List<SduiBlockDTO> contentBlocks = const []}): _visibleMetadata = visibleMetadata,_visibleBlockExtensions = visibleBlockExtensions,_visibleWorkflowExtensions = visibleWorkflowExtensions,_userRoleMappings = userRoleMappings,_extensionLabels = extensionLabels,_layouts = layouts,_contentBlocks = contentBlocks,super._();
  factory _EmbeddedOutputProfile.fromJson(Map<String, dynamic> json) => _$EmbeddedOutputProfileFromJson(json);

@override final  I18nText name;
@override final  I18nText? description;
@override@JsonKey(name: 'user_role_label') final  I18nText? userRoleLabel;
@override@JsonKey(name: 'custom_preface') final  I18nText? customPreface;
 final  List<String> _visibleMetadata;
@override@JsonKey() List<String> get visibleMetadata {
  if (_visibleMetadata is EqualUnmodifiableListView) return _visibleMetadata;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleMetadata);
}

 final  List<XaiExtensionType> _visibleBlockExtensions;
@override@JsonKey() List<XaiExtensionType> get visibleBlockExtensions {
  if (_visibleBlockExtensions is EqualUnmodifiableListView) return _visibleBlockExtensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleBlockExtensions);
}

 final  List<XaiExtensionType> _visibleWorkflowExtensions;
@override@JsonKey() List<XaiExtensionType> get visibleWorkflowExtensions {
  if (_visibleWorkflowExtensions is EqualUnmodifiableListView) return _visibleWorkflowExtensions;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_visibleWorkflowExtensions);
}

@override@JsonKey(name: 'max_extension_items') final  int? maxExtensionItems;
@override@JsonKey() final  String displayScale;
@override@JsonKey(name: 'include_diagnostic_scorecard') final  bool includeDiagnosticScorecard;
@override@JsonKey(name: 'strictness_level') final  int? strictnessLevel;
@override@JsonKey(name: 'scoring_strategy') final  ScoringStrategy? scoringStrategy;
@override@JsonKey(name: 'tone_instruction') final  I18nText? toneInstruction;
@override final  String? language;
 final  Map<String, I18nText> _userRoleMappings;
@override@JsonKey(name: 'user_role_mappings') Map<String, I18nText> get userRoleMappings {
  if (_userRoleMappings is EqualUnmodifiableMapView) return _userRoleMappings;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_userRoleMappings);
}

 final  Map<String, I18nText> _extensionLabels;
@override@JsonKey(name: 'extension_labels') Map<String, I18nText> get extensionLabels {
  if (_extensionLabels is EqualUnmodifiableMapView) return _extensionLabels;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableMapView(_extensionLabels);
}

 final  List<OutputLayoutBlock> _layouts;
@override@JsonKey() List<OutputLayoutBlock> get layouts {
  if (_layouts is EqualUnmodifiableListView) return _layouts;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_layouts);
}

 final  List<SduiBlockDTO> _contentBlocks;
@override@JsonKey(name: 'content_blocks') List<SduiBlockDTO> get contentBlocks {
  if (_contentBlocks is EqualUnmodifiableListView) return _contentBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_contentBlocks);
}


/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$EmbeddedOutputProfileCopyWith<_EmbeddedOutputProfile> get copyWith => __$EmbeddedOutputProfileCopyWithImpl<_EmbeddedOutputProfile>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$EmbeddedOutputProfileToJson(this, );
}



@override
String toString() {
  return 'EmbeddedOutputProfile(name: $name, description: $description, userRoleLabel: $userRoleLabel, customPreface: $customPreface, visibleMetadata: $visibleMetadata, visibleBlockExtensions: $visibleBlockExtensions, visibleWorkflowExtensions: $visibleWorkflowExtensions, maxExtensionItems: $maxExtensionItems, displayScale: $displayScale, includeDiagnosticScorecard: $includeDiagnosticScorecard, strictnessLevel: $strictnessLevel, scoringStrategy: $scoringStrategy, toneInstruction: $toneInstruction, language: $language, userRoleMappings: $userRoleMappings, extensionLabels: $extensionLabels, layouts: $layouts, contentBlocks: $contentBlocks)';
}


}

/// @nodoc
abstract mixin class _$EmbeddedOutputProfileCopyWith<$Res> implements $EmbeddedOutputProfileCopyWith<$Res> {
  factory _$EmbeddedOutputProfileCopyWith(_EmbeddedOutputProfile value, $Res Function(_EmbeddedOutputProfile) _then) = __$EmbeddedOutputProfileCopyWithImpl;
@override @useResult
$Res call({
 I18nText name, I18nText? description,@JsonKey(name: 'user_role_label') I18nText? userRoleLabel,@JsonKey(name: 'custom_preface') I18nText? customPreface, List<String> visibleMetadata, List<XaiExtensionType> visibleBlockExtensions, List<XaiExtensionType> visibleWorkflowExtensions,@JsonKey(name: 'max_extension_items') int? maxExtensionItems, String displayScale,@JsonKey(name: 'include_diagnostic_scorecard') bool includeDiagnosticScorecard,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,@JsonKey(name: 'tone_instruction') I18nText? toneInstruction, String? language,@JsonKey(name: 'user_role_mappings') Map<String, I18nText> userRoleMappings,@JsonKey(name: 'extension_labels') Map<String, I18nText> extensionLabels, List<OutputLayoutBlock> layouts,@JsonKey(name: 'content_blocks') List<SduiBlockDTO> contentBlocks
});


@override $I18nTextCopyWith<$Res> get name;@override $I18nTextCopyWith<$Res>? get description;@override $I18nTextCopyWith<$Res>? get userRoleLabel;@override $I18nTextCopyWith<$Res>? get customPreface;@override $I18nTextCopyWith<$Res>? get toneInstruction;

}
/// @nodoc
class __$EmbeddedOutputProfileCopyWithImpl<$Res>
    implements _$EmbeddedOutputProfileCopyWith<$Res> {
  __$EmbeddedOutputProfileCopyWithImpl(this._self, this._then);

  final _EmbeddedOutputProfile _self;
  final $Res Function(_EmbeddedOutputProfile) _then;

/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? name = null,Object? description = freezed,Object? userRoleLabel = freezed,Object? customPreface = freezed,Object? visibleMetadata = null,Object? visibleBlockExtensions = null,Object? visibleWorkflowExtensions = null,Object? maxExtensionItems = freezed,Object? displayScale = null,Object? includeDiagnosticScorecard = null,Object? strictnessLevel = freezed,Object? scoringStrategy = freezed,Object? toneInstruction = freezed,Object? language = freezed,Object? userRoleMappings = null,Object? extensionLabels = null,Object? layouts = null,Object? contentBlocks = null,}) {
  return _then(_EmbeddedOutputProfile(
name: null == name ? _self.name : name // ignore: cast_nullable_to_non_nullable
as I18nText,description: freezed == description ? _self.description : description // ignore: cast_nullable_to_non_nullable
as I18nText?,userRoleLabel: freezed == userRoleLabel ? _self.userRoleLabel : userRoleLabel // ignore: cast_nullable_to_non_nullable
as I18nText?,customPreface: freezed == customPreface ? _self.customPreface : customPreface // ignore: cast_nullable_to_non_nullable
as I18nText?,visibleMetadata: null == visibleMetadata ? _self._visibleMetadata : visibleMetadata // ignore: cast_nullable_to_non_nullable
as List<String>,visibleBlockExtensions: null == visibleBlockExtensions ? _self._visibleBlockExtensions : visibleBlockExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,visibleWorkflowExtensions: null == visibleWorkflowExtensions ? _self._visibleWorkflowExtensions : visibleWorkflowExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,maxExtensionItems: freezed == maxExtensionItems ? _self.maxExtensionItems : maxExtensionItems // ignore: cast_nullable_to_non_nullable
as int?,displayScale: null == displayScale ? _self.displayScale : displayScale // ignore: cast_nullable_to_non_nullable
as String,includeDiagnosticScorecard: null == includeDiagnosticScorecard ? _self.includeDiagnosticScorecard : includeDiagnosticScorecard // ignore: cast_nullable_to_non_nullable
as bool,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy?,toneInstruction: freezed == toneInstruction ? _self.toneInstruction : toneInstruction // ignore: cast_nullable_to_non_nullable
as I18nText?,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as String?,userRoleMappings: null == userRoleMappings ? _self._userRoleMappings : userRoleMappings // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,extensionLabels: null == extensionLabels ? _self._extensionLabels : extensionLabels // ignore: cast_nullable_to_non_nullable
as Map<String, I18nText>,layouts: null == layouts ? _self._layouts : layouts // ignore: cast_nullable_to_non_nullable
as List<OutputLayoutBlock>,contentBlocks: null == contentBlocks ? _self._contentBlocks : contentBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,
  ));
}

/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get name {
  
  return $I18nTextCopyWith<$Res>(_self.name, (value) {
    return _then(_self.copyWith(name: value));
  });
}/// Create a copy of EmbeddedOutputProfile
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
}/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get userRoleLabel {
    if (_self.userRoleLabel == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.userRoleLabel!, (value) {
    return _then(_self.copyWith(userRoleLabel: value));
  });
}/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get customPreface {
    if (_self.customPreface == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.customPreface!, (value) {
    return _then(_self.copyWith(customPreface: value));
  });
}/// Create a copy of EmbeddedOutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get toneInstruction {
    if (_self.toneInstruction == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.toneInstruction!, (value) {
    return _then(_self.copyWith(toneInstruction: value));
  });
}
}

// dart format on
