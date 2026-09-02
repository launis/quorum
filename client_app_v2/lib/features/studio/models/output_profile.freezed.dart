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
mixin _$MatrixSynthesisGroup {

 String get id; I18nText get title;@JsonKey(name: 'target_blocks') List<String> get targetBlocks;@JsonKey(name: 'view_type') PresetView get viewType;
/// Create a copy of MatrixSynthesisGroup
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$MatrixSynthesisGroupCopyWith<MatrixSynthesisGroup> get copyWith => _$MatrixSynthesisGroupCopyWithImpl<MatrixSynthesisGroup>(this as MatrixSynthesisGroup, _$identity);

  /// Serializes this MatrixSynthesisGroup to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'MatrixSynthesisGroup(id: $id, title: $title, targetBlocks: $targetBlocks, viewType: $viewType)';
}


}

/// @nodoc
abstract mixin class $MatrixSynthesisGroupCopyWith<$Res>  {
  factory $MatrixSynthesisGroupCopyWith(MatrixSynthesisGroup value, $Res Function(MatrixSynthesisGroup) _then) = _$MatrixSynthesisGroupCopyWithImpl;
@useResult
$Res call({
 String id, I18nText title,@JsonKey(name: 'target_blocks') List<String> targetBlocks,@JsonKey(name: 'view_type') PresetView viewType
});


$I18nTextCopyWith<$Res> get title;

}
/// @nodoc
class _$MatrixSynthesisGroupCopyWithImpl<$Res>
    implements $MatrixSynthesisGroupCopyWith<$Res> {
  _$MatrixSynthesisGroupCopyWithImpl(this._self, this._then);

  final MatrixSynthesisGroup _self;
  final $Res Function(MatrixSynthesisGroup) _then;

/// Create a copy of MatrixSynthesisGroup
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? title = null,Object? targetBlocks = null,Object? viewType = null,}) {
  return _then(_self.copyWith(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText,targetBlocks: null == targetBlocks ? _self.targetBlocks : targetBlocks // ignore: cast_nullable_to_non_nullable
as List<String>,viewType: null == viewType ? _self.viewType : viewType // ignore: cast_nullable_to_non_nullable
as PresetView,
  ));
}
/// Create a copy of MatrixSynthesisGroup
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get title {
  
  return $I18nTextCopyWith<$Res>(_self.title, (value) {
    return _then(_self.copyWith(title: value));
  });
}
}


/// Adds pattern-matching-related methods to [MatrixSynthesisGroup].
extension MatrixSynthesisGroupPatterns on MatrixSynthesisGroup {
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

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _MatrixSynthesisGroup value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _MatrixSynthesisGroup() when $default != null:
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

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _MatrixSynthesisGroup value)  $default,){
final _that = this;
switch (_that) {
case _MatrixSynthesisGroup():
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

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _MatrixSynthesisGroup value)?  $default,){
final _that = this;
switch (_that) {
case _MatrixSynthesisGroup() when $default != null:
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( String id,  I18nText title, @JsonKey(name: 'target_blocks')  List<String> targetBlocks, @JsonKey(name: 'view_type')  PresetView viewType)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _MatrixSynthesisGroup() when $default != null:
return $default(_that.id,_that.title,_that.targetBlocks,_that.viewType);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( String id,  I18nText title, @JsonKey(name: 'target_blocks')  List<String> targetBlocks, @JsonKey(name: 'view_type')  PresetView viewType)  $default,) {final _that = this;
switch (_that) {
case _MatrixSynthesisGroup():
return $default(_that.id,_that.title,_that.targetBlocks,_that.viewType);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( String id,  I18nText title, @JsonKey(name: 'target_blocks')  List<String> targetBlocks, @JsonKey(name: 'view_type')  PresetView viewType)?  $default,) {final _that = this;
switch (_that) {
case _MatrixSynthesisGroup() when $default != null:
return $default(_that.id,_that.title,_that.targetBlocks,_that.viewType);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _MatrixSynthesisGroup extends MatrixSynthesisGroup {
  const _MatrixSynthesisGroup({required this.id, required this.title, @JsonKey(name: 'target_blocks') required final  List<String> targetBlocks, @JsonKey(name: 'view_type') this.viewType = PresetView.metrics1d}): _targetBlocks = targetBlocks,super._();
  factory _MatrixSynthesisGroup.fromJson(Map<String, dynamic> json) => _$MatrixSynthesisGroupFromJson(json);

@override final  String id;
@override final  I18nText title;
 final  List<String> _targetBlocks;
@override@JsonKey(name: 'target_blocks') List<String> get targetBlocks {
  if (_targetBlocks is EqualUnmodifiableListView) return _targetBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_targetBlocks);
}

@override@JsonKey(name: 'view_type') final  PresetView viewType;

/// Create a copy of MatrixSynthesisGroup
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$MatrixSynthesisGroupCopyWith<_MatrixSynthesisGroup> get copyWith => __$MatrixSynthesisGroupCopyWithImpl<_MatrixSynthesisGroup>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$MatrixSynthesisGroupToJson(this, );
}



@override
String toString() {
  return 'MatrixSynthesisGroup(id: $id, title: $title, targetBlocks: $targetBlocks, viewType: $viewType)';
}


}

/// @nodoc
abstract mixin class _$MatrixSynthesisGroupCopyWith<$Res> implements $MatrixSynthesisGroupCopyWith<$Res> {
  factory _$MatrixSynthesisGroupCopyWith(_MatrixSynthesisGroup value, $Res Function(_MatrixSynthesisGroup) _then) = __$MatrixSynthesisGroupCopyWithImpl;
@override @useResult
$Res call({
 String id, I18nText title,@JsonKey(name: 'target_blocks') List<String> targetBlocks,@JsonKey(name: 'view_type') PresetView viewType
});


@override $I18nTextCopyWith<$Res> get title;

}
/// @nodoc
class __$MatrixSynthesisGroupCopyWithImpl<$Res>
    implements _$MatrixSynthesisGroupCopyWith<$Res> {
  __$MatrixSynthesisGroupCopyWithImpl(this._self, this._then);

  final _MatrixSynthesisGroup _self;
  final $Res Function(_MatrixSynthesisGroup) _then;

/// Create a copy of MatrixSynthesisGroup
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? title = null,Object? targetBlocks = null,Object? viewType = null,}) {
  return _then(_MatrixSynthesisGroup(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as String,title: null == title ? _self.title : title // ignore: cast_nullable_to_non_nullable
as I18nText,targetBlocks: null == targetBlocks ? _self._targetBlocks : targetBlocks // ignore: cast_nullable_to_non_nullable
as List<String>,viewType: null == viewType ? _self.viewType : viewType // ignore: cast_nullable_to_non_nullable
as PresetView,
  ));
}

/// Create a copy of MatrixSynthesisGroup
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res> get title {
  
  return $I18nTextCopyWith<$Res>(_self.title, (value) {
    return _then(_self.copyWith(title: value));
  });
}
}


/// @nodoc
mixin _$OutputProfile {

@StrictOpaqueIdConverter() String get id; String get slug;@StrictOpaqueIdConverter() String get workflowId; String? get organizationId; I18nText get name; I18nText? get description;@JsonKey(name: 'user_role_label') I18nText? get userRoleLabel;@JsonKey(name: 'custom_preface') I18nText? get customPreface; List<String> get visibleMetadata;@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns; List<XaiExtensionType> get visibleBlockExtensions; List<XaiExtensionType> get visibleWorkflowExtensions;@JsonKey(name: 'max_extension_items') int get maxExtensionItems;@JsonKey(name: 'display_scale') DisplayScale get displayScale;@JsonKey(name: 'custom_scale_min') double? get customScaleMin;@JsonKey(name: 'custom_scale_max') double? get customScaleMax;@JsonKey(name: 'strictness_level') int? get strictnessLevel;@JsonKey(name: 'scoring_strategy') ScoringStrategy? get scoringStrategy;@JsonKey(name: 'synthesis_length_constraint') int? get synthesisLengthConstraint;@JsonKey(name: 'max_quotes_per_matrix') int? get maxQuotesPerMatrix;@JsonKey(name: 'max_unmet_criteria') int? get maxUnmetCriteria;@JsonKey(name: 'tone_instruction') I18nText? get toneInstruction;@JsonKey(name: 'executive_summary_directive') I18nText? get executiveSummaryDirective;@JsonKey(name: 'matrix_1d_synthesis_directive') I18nText? get matrix1dSynthesisDirective;@JsonKey(name: 'matrix_2d_synthesis_directive') I18nText? get matrix2dSynthesisDirective;@JsonKey(name: 'matrix_3d_synthesis_directive') I18nText? get matrix3dSynthesisDirective;@JsonKey(name: 'matrix_text_synthesis_directive') I18nText? get matrixTextSynthesisDirective;@JsonKey(name: 'row_explanation_directive') I18nText? get rowExplanationDirective;@JsonKey(name: 'xai_synthesis_directive') I18nText? get xaiSynthesisDirective;@JsonKey(name: 'variance_synthesis_directive') I18nText? get varianceSynthesisDirective; SystemLocale? get language;@JsonKey(name: 'matrix_synthesis_groups') List<MatrixSynthesisGroup> get matrixSynthesisGroups;@JsonKey(name: 'content_blocks') List<SduiBlockDTO> get contentBlocks;@JsonKey(name: 'target_block_order') List<TargetBlockType> get targetBlockOrder;@JsonKey(name: 'show_sources_summary_box') bool get showSourcesSummaryBox;@JsonKey(name: 'sources_display_mode') SourcesDisplayMode get sourcesDisplayMode;@JsonKey(name: 'performativity_detector_step_id') String? get performativityDetectorStepId;
/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$OutputProfileCopyWith<OutputProfile> get copyWith => _$OutputProfileCopyWithImpl<OutputProfile>(this as OutputProfile, _$identity);

  /// Serializes this OutputProfile to a JSON map.
  Map<String, dynamic> toJson();




@override
String toString() {
  return 'OutputProfile(id: $id, slug: $slug, workflowId: $workflowId, organizationId: $organizationId, name: $name, description: $description, userRoleLabel: $userRoleLabel, customPreface: $customPreface, visibleMetadata: $visibleMetadata, matrixVisibleColumns: $matrixVisibleColumns, visibleBlockExtensions: $visibleBlockExtensions, visibleWorkflowExtensions: $visibleWorkflowExtensions, maxExtensionItems: $maxExtensionItems, displayScale: $displayScale, customScaleMin: $customScaleMin, customScaleMax: $customScaleMax, strictnessLevel: $strictnessLevel, scoringStrategy: $scoringStrategy, synthesisLengthConstraint: $synthesisLengthConstraint, maxQuotesPerMatrix: $maxQuotesPerMatrix, maxUnmetCriteria: $maxUnmetCriteria, toneInstruction: $toneInstruction, executiveSummaryDirective: $executiveSummaryDirective, matrix1dSynthesisDirective: $matrix1dSynthesisDirective, matrix2dSynthesisDirective: $matrix2dSynthesisDirective, matrix3dSynthesisDirective: $matrix3dSynthesisDirective, matrixTextSynthesisDirective: $matrixTextSynthesisDirective, rowExplanationDirective: $rowExplanationDirective, xaiSynthesisDirective: $xaiSynthesisDirective, varianceSynthesisDirective: $varianceSynthesisDirective, language: $language, matrixSynthesisGroups: $matrixSynthesisGroups, contentBlocks: $contentBlocks, targetBlockOrder: $targetBlockOrder, showSourcesSummaryBox: $showSourcesSummaryBox, sourcesDisplayMode: $sourcesDisplayMode, performativityDetectorStepId: $performativityDetectorStepId)';
}


}

/// @nodoc
abstract mixin class $OutputProfileCopyWith<$Res>  {
  factory $OutputProfileCopyWith(OutputProfile value, $Res Function(OutputProfile) _then) = _$OutputProfileCopyWithImpl;
@useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug,@StrictOpaqueIdConverter() String workflowId, String? organizationId, I18nText name, I18nText? description,@JsonKey(name: 'user_role_label') I18nText? userRoleLabel,@JsonKey(name: 'custom_preface') I18nText? customPreface, List<String> visibleMetadata,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns, List<XaiExtensionType> visibleBlockExtensions, List<XaiExtensionType> visibleWorkflowExtensions,@JsonKey(name: 'max_extension_items') int maxExtensionItems,@JsonKey(name: 'display_scale') DisplayScale displayScale,@JsonKey(name: 'custom_scale_min') double? customScaleMin,@JsonKey(name: 'custom_scale_max') double? customScaleMax,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,@JsonKey(name: 'synthesis_length_constraint') int? synthesisLengthConstraint,@JsonKey(name: 'max_quotes_per_matrix') int? maxQuotesPerMatrix,@JsonKey(name: 'max_unmet_criteria') int? maxUnmetCriteria,@JsonKey(name: 'tone_instruction') I18nText? toneInstruction,@JsonKey(name: 'executive_summary_directive') I18nText? executiveSummaryDirective,@JsonKey(name: 'matrix_1d_synthesis_directive') I18nText? matrix1dSynthesisDirective,@JsonKey(name: 'matrix_2d_synthesis_directive') I18nText? matrix2dSynthesisDirective,@JsonKey(name: 'matrix_3d_synthesis_directive') I18nText? matrix3dSynthesisDirective,@JsonKey(name: 'matrix_text_synthesis_directive') I18nText? matrixTextSynthesisDirective,@JsonKey(name: 'row_explanation_directive') I18nText? rowExplanationDirective,@JsonKey(name: 'xai_synthesis_directive') I18nText? xaiSynthesisDirective,@JsonKey(name: 'variance_synthesis_directive') I18nText? varianceSynthesisDirective, SystemLocale? language,@JsonKey(name: 'matrix_synthesis_groups') List<MatrixSynthesisGroup> matrixSynthesisGroups,@JsonKey(name: 'content_blocks') List<SduiBlockDTO> contentBlocks,@JsonKey(name: 'target_block_order') List<TargetBlockType> targetBlockOrder,@JsonKey(name: 'show_sources_summary_box') bool showSourcesSummaryBox,@JsonKey(name: 'sources_display_mode') SourcesDisplayMode sourcesDisplayMode,@JsonKey(name: 'performativity_detector_step_id') String? performativityDetectorStepId
});


$I18nTextCopyWith<$Res> get name;$I18nTextCopyWith<$Res>? get description;$I18nTextCopyWith<$Res>? get userRoleLabel;$I18nTextCopyWith<$Res>? get customPreface;$I18nTextCopyWith<$Res>? get toneInstruction;$I18nTextCopyWith<$Res>? get executiveSummaryDirective;$I18nTextCopyWith<$Res>? get matrix1dSynthesisDirective;$I18nTextCopyWith<$Res>? get matrix2dSynthesisDirective;$I18nTextCopyWith<$Res>? get matrix3dSynthesisDirective;$I18nTextCopyWith<$Res>? get matrixTextSynthesisDirective;$I18nTextCopyWith<$Res>? get rowExplanationDirective;$I18nTextCopyWith<$Res>? get xaiSynthesisDirective;$I18nTextCopyWith<$Res>? get varianceSynthesisDirective;

}
/// @nodoc
class _$OutputProfileCopyWithImpl<$Res>
    implements $OutputProfileCopyWith<$Res> {
  _$OutputProfileCopyWithImpl(this._self, this._then);

  final OutputProfile _self;
  final $Res Function(OutputProfile) _then;

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? slug = null,Object? workflowId = null,Object? organizationId = freezed,Object? name = null,Object? description = freezed,Object? userRoleLabel = freezed,Object? customPreface = freezed,Object? visibleMetadata = null,Object? matrixVisibleColumns = null,Object? visibleBlockExtensions = null,Object? visibleWorkflowExtensions = null,Object? maxExtensionItems = null,Object? displayScale = null,Object? customScaleMin = freezed,Object? customScaleMax = freezed,Object? strictnessLevel = freezed,Object? scoringStrategy = freezed,Object? synthesisLengthConstraint = freezed,Object? maxQuotesPerMatrix = freezed,Object? maxUnmetCriteria = freezed,Object? toneInstruction = freezed,Object? executiveSummaryDirective = freezed,Object? matrix1dSynthesisDirective = freezed,Object? matrix2dSynthesisDirective = freezed,Object? matrix3dSynthesisDirective = freezed,Object? matrixTextSynthesisDirective = freezed,Object? rowExplanationDirective = freezed,Object? xaiSynthesisDirective = freezed,Object? varianceSynthesisDirective = freezed,Object? language = freezed,Object? matrixSynthesisGroups = null,Object? contentBlocks = null,Object? targetBlockOrder = null,Object? showSourcesSummaryBox = null,Object? sourcesDisplayMode = null,Object? performativityDetectorStepId = freezed,}) {
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
as List<String>,matrixVisibleColumns: null == matrixVisibleColumns ? _self.matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,visibleBlockExtensions: null == visibleBlockExtensions ? _self.visibleBlockExtensions : visibleBlockExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,visibleWorkflowExtensions: null == visibleWorkflowExtensions ? _self.visibleWorkflowExtensions : visibleWorkflowExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,maxExtensionItems: null == maxExtensionItems ? _self.maxExtensionItems : maxExtensionItems // ignore: cast_nullable_to_non_nullable
as int,displayScale: null == displayScale ? _self.displayScale : displayScale // ignore: cast_nullable_to_non_nullable
as DisplayScale,customScaleMin: freezed == customScaleMin ? _self.customScaleMin : customScaleMin // ignore: cast_nullable_to_non_nullable
as double?,customScaleMax: freezed == customScaleMax ? _self.customScaleMax : customScaleMax // ignore: cast_nullable_to_non_nullable
as double?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy?,synthesisLengthConstraint: freezed == synthesisLengthConstraint ? _self.synthesisLengthConstraint : synthesisLengthConstraint // ignore: cast_nullable_to_non_nullable
as int?,maxQuotesPerMatrix: freezed == maxQuotesPerMatrix ? _self.maxQuotesPerMatrix : maxQuotesPerMatrix // ignore: cast_nullable_to_non_nullable
as int?,maxUnmetCriteria: freezed == maxUnmetCriteria ? _self.maxUnmetCriteria : maxUnmetCriteria // ignore: cast_nullable_to_non_nullable
as int?,toneInstruction: freezed == toneInstruction ? _self.toneInstruction : toneInstruction // ignore: cast_nullable_to_non_nullable
as I18nText?,executiveSummaryDirective: freezed == executiveSummaryDirective ? _self.executiveSummaryDirective : executiveSummaryDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,matrix1dSynthesisDirective: freezed == matrix1dSynthesisDirective ? _self.matrix1dSynthesisDirective : matrix1dSynthesisDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,matrix2dSynthesisDirective: freezed == matrix2dSynthesisDirective ? _self.matrix2dSynthesisDirective : matrix2dSynthesisDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,matrix3dSynthesisDirective: freezed == matrix3dSynthesisDirective ? _self.matrix3dSynthesisDirective : matrix3dSynthesisDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,matrixTextSynthesisDirective: freezed == matrixTextSynthesisDirective ? _self.matrixTextSynthesisDirective : matrixTextSynthesisDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,rowExplanationDirective: freezed == rowExplanationDirective ? _self.rowExplanationDirective : rowExplanationDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,xaiSynthesisDirective: freezed == xaiSynthesisDirective ? _self.xaiSynthesisDirective : xaiSynthesisDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,varianceSynthesisDirective: freezed == varianceSynthesisDirective ? _self.varianceSynthesisDirective : varianceSynthesisDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as SystemLocale?,matrixSynthesisGroups: null == matrixSynthesisGroups ? _self.matrixSynthesisGroups : matrixSynthesisGroups // ignore: cast_nullable_to_non_nullable
as List<MatrixSynthesisGroup>,contentBlocks: null == contentBlocks ? _self.contentBlocks : contentBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,targetBlockOrder: null == targetBlockOrder ? _self.targetBlockOrder : targetBlockOrder // ignore: cast_nullable_to_non_nullable
as List<TargetBlockType>,showSourcesSummaryBox: null == showSourcesSummaryBox ? _self.showSourcesSummaryBox : showSourcesSummaryBox // ignore: cast_nullable_to_non_nullable
as bool,sourcesDisplayMode: null == sourcesDisplayMode ? _self.sourcesDisplayMode : sourcesDisplayMode // ignore: cast_nullable_to_non_nullable
as SourcesDisplayMode,performativityDetectorStepId: freezed == performativityDetectorStepId ? _self.performativityDetectorStepId : performativityDetectorStepId // ignore: cast_nullable_to_non_nullable
as String?,
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
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get executiveSummaryDirective {
    if (_self.executiveSummaryDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.executiveSummaryDirective!, (value) {
    return _then(_self.copyWith(executiveSummaryDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get matrix1dSynthesisDirective {
    if (_self.matrix1dSynthesisDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.matrix1dSynthesisDirective!, (value) {
    return _then(_self.copyWith(matrix1dSynthesisDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get matrix2dSynthesisDirective {
    if (_self.matrix2dSynthesisDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.matrix2dSynthesisDirective!, (value) {
    return _then(_self.copyWith(matrix2dSynthesisDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get matrix3dSynthesisDirective {
    if (_self.matrix3dSynthesisDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.matrix3dSynthesisDirective!, (value) {
    return _then(_self.copyWith(matrix3dSynthesisDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get matrixTextSynthesisDirective {
    if (_self.matrixTextSynthesisDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.matrixTextSynthesisDirective!, (value) {
    return _then(_self.copyWith(matrixTextSynthesisDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get rowExplanationDirective {
    if (_self.rowExplanationDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.rowExplanationDirective!, (value) {
    return _then(_self.copyWith(rowExplanationDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get xaiSynthesisDirective {
    if (_self.xaiSynthesisDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.xaiSynthesisDirective!, (value) {
    return _then(_self.copyWith(xaiSynthesisDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get varianceSynthesisDirective {
    if (_self.varianceSynthesisDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.varianceSynthesisDirective!, (value) {
    return _then(_self.copyWith(varianceSynthesisDirective: value));
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

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()  String workflowId,  String? organizationId,  I18nText name,  I18nText? description, @JsonKey(name: 'user_role_label')  I18nText? userRoleLabel, @JsonKey(name: 'custom_preface')  I18nText? customPreface,  List<String> visibleMetadata, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns,  List<XaiExtensionType> visibleBlockExtensions,  List<XaiExtensionType> visibleWorkflowExtensions, @JsonKey(name: 'max_extension_items')  int maxExtensionItems, @JsonKey(name: 'display_scale')  DisplayScale displayScale, @JsonKey(name: 'custom_scale_min')  double? customScaleMin, @JsonKey(name: 'custom_scale_max')  double? customScaleMax, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'synthesis_length_constraint')  int? synthesisLengthConstraint, @JsonKey(name: 'max_quotes_per_matrix')  int? maxQuotesPerMatrix, @JsonKey(name: 'max_unmet_criteria')  int? maxUnmetCriteria, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction, @JsonKey(name: 'executive_summary_directive')  I18nText? executiveSummaryDirective, @JsonKey(name: 'matrix_1d_synthesis_directive')  I18nText? matrix1dSynthesisDirective, @JsonKey(name: 'matrix_2d_synthesis_directive')  I18nText? matrix2dSynthesisDirective, @JsonKey(name: 'matrix_3d_synthesis_directive')  I18nText? matrix3dSynthesisDirective, @JsonKey(name: 'matrix_text_synthesis_directive')  I18nText? matrixTextSynthesisDirective, @JsonKey(name: 'row_explanation_directive')  I18nText? rowExplanationDirective, @JsonKey(name: 'xai_synthesis_directive')  I18nText? xaiSynthesisDirective, @JsonKey(name: 'variance_synthesis_directive')  I18nText? varianceSynthesisDirective,  SystemLocale? language, @JsonKey(name: 'matrix_synthesis_groups')  List<MatrixSynthesisGroup> matrixSynthesisGroups, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks, @JsonKey(name: 'target_block_order')  List<TargetBlockType> targetBlockOrder, @JsonKey(name: 'show_sources_summary_box')  bool showSourcesSummaryBox, @JsonKey(name: 'sources_display_mode')  SourcesDisplayMode sourcesDisplayMode, @JsonKey(name: 'performativity_detector_step_id')  String? performativityDetectorStepId)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
return $default(_that.id,_that.slug,_that.workflowId,_that.organizationId,_that.name,_that.description,_that.userRoleLabel,_that.customPreface,_that.visibleMetadata,_that.matrixVisibleColumns,_that.visibleBlockExtensions,_that.visibleWorkflowExtensions,_that.maxExtensionItems,_that.displayScale,_that.customScaleMin,_that.customScaleMax,_that.strictnessLevel,_that.scoringStrategy,_that.synthesisLengthConstraint,_that.maxQuotesPerMatrix,_that.maxUnmetCriteria,_that.toneInstruction,_that.executiveSummaryDirective,_that.matrix1dSynthesisDirective,_that.matrix2dSynthesisDirective,_that.matrix3dSynthesisDirective,_that.matrixTextSynthesisDirective,_that.rowExplanationDirective,_that.xaiSynthesisDirective,_that.varianceSynthesisDirective,_that.language,_that.matrixSynthesisGroups,_that.contentBlocks,_that.targetBlockOrder,_that.showSourcesSummaryBox,_that.sourcesDisplayMode,_that.performativityDetectorStepId);case _:
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

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()  String workflowId,  String? organizationId,  I18nText name,  I18nText? description, @JsonKey(name: 'user_role_label')  I18nText? userRoleLabel, @JsonKey(name: 'custom_preface')  I18nText? customPreface,  List<String> visibleMetadata, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns,  List<XaiExtensionType> visibleBlockExtensions,  List<XaiExtensionType> visibleWorkflowExtensions, @JsonKey(name: 'max_extension_items')  int maxExtensionItems, @JsonKey(name: 'display_scale')  DisplayScale displayScale, @JsonKey(name: 'custom_scale_min')  double? customScaleMin, @JsonKey(name: 'custom_scale_max')  double? customScaleMax, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'synthesis_length_constraint')  int? synthesisLengthConstraint, @JsonKey(name: 'max_quotes_per_matrix')  int? maxQuotesPerMatrix, @JsonKey(name: 'max_unmet_criteria')  int? maxUnmetCriteria, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction, @JsonKey(name: 'executive_summary_directive')  I18nText? executiveSummaryDirective, @JsonKey(name: 'matrix_1d_synthesis_directive')  I18nText? matrix1dSynthesisDirective, @JsonKey(name: 'matrix_2d_synthesis_directive')  I18nText? matrix2dSynthesisDirective, @JsonKey(name: 'matrix_3d_synthesis_directive')  I18nText? matrix3dSynthesisDirective, @JsonKey(name: 'matrix_text_synthesis_directive')  I18nText? matrixTextSynthesisDirective, @JsonKey(name: 'row_explanation_directive')  I18nText? rowExplanationDirective, @JsonKey(name: 'xai_synthesis_directive')  I18nText? xaiSynthesisDirective, @JsonKey(name: 'variance_synthesis_directive')  I18nText? varianceSynthesisDirective,  SystemLocale? language, @JsonKey(name: 'matrix_synthesis_groups')  List<MatrixSynthesisGroup> matrixSynthesisGroups, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks, @JsonKey(name: 'target_block_order')  List<TargetBlockType> targetBlockOrder, @JsonKey(name: 'show_sources_summary_box')  bool showSourcesSummaryBox, @JsonKey(name: 'sources_display_mode')  SourcesDisplayMode sourcesDisplayMode, @JsonKey(name: 'performativity_detector_step_id')  String? performativityDetectorStepId)  $default,) {final _that = this;
switch (_that) {
case _OutputProfile():
return $default(_that.id,_that.slug,_that.workflowId,_that.organizationId,_that.name,_that.description,_that.userRoleLabel,_that.customPreface,_that.visibleMetadata,_that.matrixVisibleColumns,_that.visibleBlockExtensions,_that.visibleWorkflowExtensions,_that.maxExtensionItems,_that.displayScale,_that.customScaleMin,_that.customScaleMax,_that.strictnessLevel,_that.scoringStrategy,_that.synthesisLengthConstraint,_that.maxQuotesPerMatrix,_that.maxUnmetCriteria,_that.toneInstruction,_that.executiveSummaryDirective,_that.matrix1dSynthesisDirective,_that.matrix2dSynthesisDirective,_that.matrix3dSynthesisDirective,_that.matrixTextSynthesisDirective,_that.rowExplanationDirective,_that.xaiSynthesisDirective,_that.varianceSynthesisDirective,_that.language,_that.matrixSynthesisGroups,_that.contentBlocks,_that.targetBlockOrder,_that.showSourcesSummaryBox,_that.sourcesDisplayMode,_that.performativityDetectorStepId);case _:
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

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function(@StrictOpaqueIdConverter()  String id,  String slug, @StrictOpaqueIdConverter()  String workflowId,  String? organizationId,  I18nText name,  I18nText? description, @JsonKey(name: 'user_role_label')  I18nText? userRoleLabel, @JsonKey(name: 'custom_preface')  I18nText? customPreface,  List<String> visibleMetadata, @JsonKey(name: 'matrix_visible_columns')  List<String> matrixVisibleColumns,  List<XaiExtensionType> visibleBlockExtensions,  List<XaiExtensionType> visibleWorkflowExtensions, @JsonKey(name: 'max_extension_items')  int maxExtensionItems, @JsonKey(name: 'display_scale')  DisplayScale displayScale, @JsonKey(name: 'custom_scale_min')  double? customScaleMin, @JsonKey(name: 'custom_scale_max')  double? customScaleMax, @JsonKey(name: 'strictness_level')  int? strictnessLevel, @JsonKey(name: 'scoring_strategy')  ScoringStrategy? scoringStrategy, @JsonKey(name: 'synthesis_length_constraint')  int? synthesisLengthConstraint, @JsonKey(name: 'max_quotes_per_matrix')  int? maxQuotesPerMatrix, @JsonKey(name: 'max_unmet_criteria')  int? maxUnmetCriteria, @JsonKey(name: 'tone_instruction')  I18nText? toneInstruction, @JsonKey(name: 'executive_summary_directive')  I18nText? executiveSummaryDirective, @JsonKey(name: 'matrix_1d_synthesis_directive')  I18nText? matrix1dSynthesisDirective, @JsonKey(name: 'matrix_2d_synthesis_directive')  I18nText? matrix2dSynthesisDirective, @JsonKey(name: 'matrix_3d_synthesis_directive')  I18nText? matrix3dSynthesisDirective, @JsonKey(name: 'matrix_text_synthesis_directive')  I18nText? matrixTextSynthesisDirective, @JsonKey(name: 'row_explanation_directive')  I18nText? rowExplanationDirective, @JsonKey(name: 'xai_synthesis_directive')  I18nText? xaiSynthesisDirective, @JsonKey(name: 'variance_synthesis_directive')  I18nText? varianceSynthesisDirective,  SystemLocale? language, @JsonKey(name: 'matrix_synthesis_groups')  List<MatrixSynthesisGroup> matrixSynthesisGroups, @JsonKey(name: 'content_blocks')  List<SduiBlockDTO> contentBlocks, @JsonKey(name: 'target_block_order')  List<TargetBlockType> targetBlockOrder, @JsonKey(name: 'show_sources_summary_box')  bool showSourcesSummaryBox, @JsonKey(name: 'sources_display_mode')  SourcesDisplayMode sourcesDisplayMode, @JsonKey(name: 'performativity_detector_step_id')  String? performativityDetectorStepId)?  $default,) {final _that = this;
switch (_that) {
case _OutputProfile() when $default != null:
return $default(_that.id,_that.slug,_that.workflowId,_that.organizationId,_that.name,_that.description,_that.userRoleLabel,_that.customPreface,_that.visibleMetadata,_that.matrixVisibleColumns,_that.visibleBlockExtensions,_that.visibleWorkflowExtensions,_that.maxExtensionItems,_that.displayScale,_that.customScaleMin,_that.customScaleMax,_that.strictnessLevel,_that.scoringStrategy,_that.synthesisLengthConstraint,_that.maxQuotesPerMatrix,_that.maxUnmetCriteria,_that.toneInstruction,_that.executiveSummaryDirective,_that.matrix1dSynthesisDirective,_that.matrix2dSynthesisDirective,_that.matrix3dSynthesisDirective,_that.matrixTextSynthesisDirective,_that.rowExplanationDirective,_that.xaiSynthesisDirective,_that.varianceSynthesisDirective,_that.language,_that.matrixSynthesisGroups,_that.contentBlocks,_that.targetBlockOrder,_that.showSourcesSummaryBox,_that.sourcesDisplayMode,_that.performativityDetectorStepId);case _:
  return null;

}
}

}

/// @nodoc

@JsonSerializable(disallowUnrecognizedKeys: true)
class _OutputProfile extends OutputProfile {
  const _OutputProfile({@StrictOpaqueIdConverter() required this.id, this.slug = '', @StrictOpaqueIdConverter() required this.workflowId, this.organizationId, required this.name, this.description, @JsonKey(name: 'user_role_label') this.userRoleLabel, @JsonKey(name: 'custom_preface') this.customPreface, final  List<String> visibleMetadata = const ['date', 'organization', 'user', 'scoring_engine', 'strictness'], @JsonKey(name: 'matrix_visible_columns') final  List<String> matrixVisibleColumns = const ['label', 'distribution', 'row_explanation', 'quotes', 'normalized_score', 'score'], final  List<XaiExtensionType> visibleBlockExtensions = const [], final  List<XaiExtensionType> visibleWorkflowExtensions = const [], @JsonKey(name: 'max_extension_items') this.maxExtensionItems = 3, @JsonKey(name: 'display_scale') this.displayScale = DisplayScale.original, @JsonKey(name: 'custom_scale_min') this.customScaleMin, @JsonKey(name: 'custom_scale_max') this.customScaleMax, @JsonKey(name: 'strictness_level') this.strictnessLevel, @JsonKey(name: 'scoring_strategy') this.scoringStrategy, @JsonKey(name: 'synthesis_length_constraint') this.synthesisLengthConstraint, @JsonKey(name: 'max_quotes_per_matrix') this.maxQuotesPerMatrix, @JsonKey(name: 'max_unmet_criteria') this.maxUnmetCriteria, @JsonKey(name: 'tone_instruction') this.toneInstruction, @JsonKey(name: 'executive_summary_directive') this.executiveSummaryDirective, @JsonKey(name: 'matrix_1d_synthesis_directive') this.matrix1dSynthesisDirective, @JsonKey(name: 'matrix_2d_synthesis_directive') this.matrix2dSynthesisDirective, @JsonKey(name: 'matrix_3d_synthesis_directive') this.matrix3dSynthesisDirective, @JsonKey(name: 'matrix_text_synthesis_directive') this.matrixTextSynthesisDirective, @JsonKey(name: 'row_explanation_directive') this.rowExplanationDirective, @JsonKey(name: 'xai_synthesis_directive') this.xaiSynthesisDirective, @JsonKey(name: 'variance_synthesis_directive') this.varianceSynthesisDirective, this.language, @JsonKey(name: 'matrix_synthesis_groups') final  List<MatrixSynthesisGroup> matrixSynthesisGroups = const [], @JsonKey(name: 'content_blocks') final  List<SduiBlockDTO> contentBlocks = const [], @JsonKey(name: 'target_block_order') final  List<TargetBlockType> targetBlockOrder = const [TargetBlockType.metadataBlock, TargetBlockType.executiveSummaryBlock, TargetBlockType.synthesisTextBlock, TargetBlockType.matrixGraphsBlock, TargetBlockType.groupedExtensionsBlock, TargetBlockType.penaltiesBlock, TargetBlockType.matrixSummaryTableBlock, TargetBlockType.varianceValidationBlock, TargetBlockType.authenticityEvaluationBlock, TargetBlockType.printableSourcesBlock, TargetBlockType.globalScoreBlock, TargetBlockType.auditTrailBlock], @JsonKey(name: 'show_sources_summary_box') this.showSourcesSummaryBox = true, @JsonKey(name: 'sources_display_mode') this.sourcesDisplayMode = SourcesDisplayMode.verifiedEvidence, @JsonKey(name: 'performativity_detector_step_id') this.performativityDetectorStepId}): _visibleMetadata = visibleMetadata,_matrixVisibleColumns = matrixVisibleColumns,_visibleBlockExtensions = visibleBlockExtensions,_visibleWorkflowExtensions = visibleWorkflowExtensions,_matrixSynthesisGroups = matrixSynthesisGroups,_contentBlocks = contentBlocks,_targetBlockOrder = targetBlockOrder,super._();
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

 final  List<String> _matrixVisibleColumns;
@override@JsonKey(name: 'matrix_visible_columns') List<String> get matrixVisibleColumns {
  if (_matrixVisibleColumns is EqualUnmodifiableListView) return _matrixVisibleColumns;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_matrixVisibleColumns);
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

@override@JsonKey(name: 'max_extension_items') final  int maxExtensionItems;
@override@JsonKey(name: 'display_scale') final  DisplayScale displayScale;
@override@JsonKey(name: 'custom_scale_min') final  double? customScaleMin;
@override@JsonKey(name: 'custom_scale_max') final  double? customScaleMax;
@override@JsonKey(name: 'strictness_level') final  int? strictnessLevel;
@override@JsonKey(name: 'scoring_strategy') final  ScoringStrategy? scoringStrategy;
@override@JsonKey(name: 'synthesis_length_constraint') final  int? synthesisLengthConstraint;
@override@JsonKey(name: 'max_quotes_per_matrix') final  int? maxQuotesPerMatrix;
@override@JsonKey(name: 'max_unmet_criteria') final  int? maxUnmetCriteria;
@override@JsonKey(name: 'tone_instruction') final  I18nText? toneInstruction;
@override@JsonKey(name: 'executive_summary_directive') final  I18nText? executiveSummaryDirective;
@override@JsonKey(name: 'matrix_1d_synthesis_directive') final  I18nText? matrix1dSynthesisDirective;
@override@JsonKey(name: 'matrix_2d_synthesis_directive') final  I18nText? matrix2dSynthesisDirective;
@override@JsonKey(name: 'matrix_3d_synthesis_directive') final  I18nText? matrix3dSynthesisDirective;
@override@JsonKey(name: 'matrix_text_synthesis_directive') final  I18nText? matrixTextSynthesisDirective;
@override@JsonKey(name: 'row_explanation_directive') final  I18nText? rowExplanationDirective;
@override@JsonKey(name: 'xai_synthesis_directive') final  I18nText? xaiSynthesisDirective;
@override@JsonKey(name: 'variance_synthesis_directive') final  I18nText? varianceSynthesisDirective;
@override final  SystemLocale? language;
 final  List<MatrixSynthesisGroup> _matrixSynthesisGroups;
@override@JsonKey(name: 'matrix_synthesis_groups') List<MatrixSynthesisGroup> get matrixSynthesisGroups {
  if (_matrixSynthesisGroups is EqualUnmodifiableListView) return _matrixSynthesisGroups;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_matrixSynthesisGroups);
}

 final  List<SduiBlockDTO> _contentBlocks;
@override@JsonKey(name: 'content_blocks') List<SduiBlockDTO> get contentBlocks {
  if (_contentBlocks is EqualUnmodifiableListView) return _contentBlocks;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_contentBlocks);
}

 final  List<TargetBlockType> _targetBlockOrder;
@override@JsonKey(name: 'target_block_order') List<TargetBlockType> get targetBlockOrder {
  if (_targetBlockOrder is EqualUnmodifiableListView) return _targetBlockOrder;
  // ignore: implicit_dynamic_type
  return EqualUnmodifiableListView(_targetBlockOrder);
}

@override@JsonKey(name: 'show_sources_summary_box') final  bool showSourcesSummaryBox;
@override@JsonKey(name: 'sources_display_mode') final  SourcesDisplayMode sourcesDisplayMode;
@override@JsonKey(name: 'performativity_detector_step_id') final  String? performativityDetectorStepId;

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
  return 'OutputProfile(id: $id, slug: $slug, workflowId: $workflowId, organizationId: $organizationId, name: $name, description: $description, userRoleLabel: $userRoleLabel, customPreface: $customPreface, visibleMetadata: $visibleMetadata, matrixVisibleColumns: $matrixVisibleColumns, visibleBlockExtensions: $visibleBlockExtensions, visibleWorkflowExtensions: $visibleWorkflowExtensions, maxExtensionItems: $maxExtensionItems, displayScale: $displayScale, customScaleMin: $customScaleMin, customScaleMax: $customScaleMax, strictnessLevel: $strictnessLevel, scoringStrategy: $scoringStrategy, synthesisLengthConstraint: $synthesisLengthConstraint, maxQuotesPerMatrix: $maxQuotesPerMatrix, maxUnmetCriteria: $maxUnmetCriteria, toneInstruction: $toneInstruction, executiveSummaryDirective: $executiveSummaryDirective, matrix1dSynthesisDirective: $matrix1dSynthesisDirective, matrix2dSynthesisDirective: $matrix2dSynthesisDirective, matrix3dSynthesisDirective: $matrix3dSynthesisDirective, matrixTextSynthesisDirective: $matrixTextSynthesisDirective, rowExplanationDirective: $rowExplanationDirective, xaiSynthesisDirective: $xaiSynthesisDirective, varianceSynthesisDirective: $varianceSynthesisDirective, language: $language, matrixSynthesisGroups: $matrixSynthesisGroups, contentBlocks: $contentBlocks, targetBlockOrder: $targetBlockOrder, showSourcesSummaryBox: $showSourcesSummaryBox, sourcesDisplayMode: $sourcesDisplayMode, performativityDetectorStepId: $performativityDetectorStepId)';
}


}

/// @nodoc
abstract mixin class _$OutputProfileCopyWith<$Res> implements $OutputProfileCopyWith<$Res> {
  factory _$OutputProfileCopyWith(_OutputProfile value, $Res Function(_OutputProfile) _then) = __$OutputProfileCopyWithImpl;
@override @useResult
$Res call({
@StrictOpaqueIdConverter() String id, String slug,@StrictOpaqueIdConverter() String workflowId, String? organizationId, I18nText name, I18nText? description,@JsonKey(name: 'user_role_label') I18nText? userRoleLabel,@JsonKey(name: 'custom_preface') I18nText? customPreface, List<String> visibleMetadata,@JsonKey(name: 'matrix_visible_columns') List<String> matrixVisibleColumns, List<XaiExtensionType> visibleBlockExtensions, List<XaiExtensionType> visibleWorkflowExtensions,@JsonKey(name: 'max_extension_items') int maxExtensionItems,@JsonKey(name: 'display_scale') DisplayScale displayScale,@JsonKey(name: 'custom_scale_min') double? customScaleMin,@JsonKey(name: 'custom_scale_max') double? customScaleMax,@JsonKey(name: 'strictness_level') int? strictnessLevel,@JsonKey(name: 'scoring_strategy') ScoringStrategy? scoringStrategy,@JsonKey(name: 'synthesis_length_constraint') int? synthesisLengthConstraint,@JsonKey(name: 'max_quotes_per_matrix') int? maxQuotesPerMatrix,@JsonKey(name: 'max_unmet_criteria') int? maxUnmetCriteria,@JsonKey(name: 'tone_instruction') I18nText? toneInstruction,@JsonKey(name: 'executive_summary_directive') I18nText? executiveSummaryDirective,@JsonKey(name: 'matrix_1d_synthesis_directive') I18nText? matrix1dSynthesisDirective,@JsonKey(name: 'matrix_2d_synthesis_directive') I18nText? matrix2dSynthesisDirective,@JsonKey(name: 'matrix_3d_synthesis_directive') I18nText? matrix3dSynthesisDirective,@JsonKey(name: 'matrix_text_synthesis_directive') I18nText? matrixTextSynthesisDirective,@JsonKey(name: 'row_explanation_directive') I18nText? rowExplanationDirective,@JsonKey(name: 'xai_synthesis_directive') I18nText? xaiSynthesisDirective,@JsonKey(name: 'variance_synthesis_directive') I18nText? varianceSynthesisDirective, SystemLocale? language,@JsonKey(name: 'matrix_synthesis_groups') List<MatrixSynthesisGroup> matrixSynthesisGroups,@JsonKey(name: 'content_blocks') List<SduiBlockDTO> contentBlocks,@JsonKey(name: 'target_block_order') List<TargetBlockType> targetBlockOrder,@JsonKey(name: 'show_sources_summary_box') bool showSourcesSummaryBox,@JsonKey(name: 'sources_display_mode') SourcesDisplayMode sourcesDisplayMode,@JsonKey(name: 'performativity_detector_step_id') String? performativityDetectorStepId
});


@override $I18nTextCopyWith<$Res> get name;@override $I18nTextCopyWith<$Res>? get description;@override $I18nTextCopyWith<$Res>? get userRoleLabel;@override $I18nTextCopyWith<$Res>? get customPreface;@override $I18nTextCopyWith<$Res>? get toneInstruction;@override $I18nTextCopyWith<$Res>? get executiveSummaryDirective;@override $I18nTextCopyWith<$Res>? get matrix1dSynthesisDirective;@override $I18nTextCopyWith<$Res>? get matrix2dSynthesisDirective;@override $I18nTextCopyWith<$Res>? get matrix3dSynthesisDirective;@override $I18nTextCopyWith<$Res>? get matrixTextSynthesisDirective;@override $I18nTextCopyWith<$Res>? get rowExplanationDirective;@override $I18nTextCopyWith<$Res>? get xaiSynthesisDirective;@override $I18nTextCopyWith<$Res>? get varianceSynthesisDirective;

}
/// @nodoc
class __$OutputProfileCopyWithImpl<$Res>
    implements _$OutputProfileCopyWith<$Res> {
  __$OutputProfileCopyWithImpl(this._self, this._then);

  final _OutputProfile _self;
  final $Res Function(_OutputProfile) _then;

/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? slug = null,Object? workflowId = null,Object? organizationId = freezed,Object? name = null,Object? description = freezed,Object? userRoleLabel = freezed,Object? customPreface = freezed,Object? visibleMetadata = null,Object? matrixVisibleColumns = null,Object? visibleBlockExtensions = null,Object? visibleWorkflowExtensions = null,Object? maxExtensionItems = null,Object? displayScale = null,Object? customScaleMin = freezed,Object? customScaleMax = freezed,Object? strictnessLevel = freezed,Object? scoringStrategy = freezed,Object? synthesisLengthConstraint = freezed,Object? maxQuotesPerMatrix = freezed,Object? maxUnmetCriteria = freezed,Object? toneInstruction = freezed,Object? executiveSummaryDirective = freezed,Object? matrix1dSynthesisDirective = freezed,Object? matrix2dSynthesisDirective = freezed,Object? matrix3dSynthesisDirective = freezed,Object? matrixTextSynthesisDirective = freezed,Object? rowExplanationDirective = freezed,Object? xaiSynthesisDirective = freezed,Object? varianceSynthesisDirective = freezed,Object? language = freezed,Object? matrixSynthesisGroups = null,Object? contentBlocks = null,Object? targetBlockOrder = null,Object? showSourcesSummaryBox = null,Object? sourcesDisplayMode = null,Object? performativityDetectorStepId = freezed,}) {
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
as List<String>,matrixVisibleColumns: null == matrixVisibleColumns ? _self._matrixVisibleColumns : matrixVisibleColumns // ignore: cast_nullable_to_non_nullable
as List<String>,visibleBlockExtensions: null == visibleBlockExtensions ? _self._visibleBlockExtensions : visibleBlockExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,visibleWorkflowExtensions: null == visibleWorkflowExtensions ? _self._visibleWorkflowExtensions : visibleWorkflowExtensions // ignore: cast_nullable_to_non_nullable
as List<XaiExtensionType>,maxExtensionItems: null == maxExtensionItems ? _self.maxExtensionItems : maxExtensionItems // ignore: cast_nullable_to_non_nullable
as int,displayScale: null == displayScale ? _self.displayScale : displayScale // ignore: cast_nullable_to_non_nullable
as DisplayScale,customScaleMin: freezed == customScaleMin ? _self.customScaleMin : customScaleMin // ignore: cast_nullable_to_non_nullable
as double?,customScaleMax: freezed == customScaleMax ? _self.customScaleMax : customScaleMax // ignore: cast_nullable_to_non_nullable
as double?,strictnessLevel: freezed == strictnessLevel ? _self.strictnessLevel : strictnessLevel // ignore: cast_nullable_to_non_nullable
as int?,scoringStrategy: freezed == scoringStrategy ? _self.scoringStrategy : scoringStrategy // ignore: cast_nullable_to_non_nullable
as ScoringStrategy?,synthesisLengthConstraint: freezed == synthesisLengthConstraint ? _self.synthesisLengthConstraint : synthesisLengthConstraint // ignore: cast_nullable_to_non_nullable
as int?,maxQuotesPerMatrix: freezed == maxQuotesPerMatrix ? _self.maxQuotesPerMatrix : maxQuotesPerMatrix // ignore: cast_nullable_to_non_nullable
as int?,maxUnmetCriteria: freezed == maxUnmetCriteria ? _self.maxUnmetCriteria : maxUnmetCriteria // ignore: cast_nullable_to_non_nullable
as int?,toneInstruction: freezed == toneInstruction ? _self.toneInstruction : toneInstruction // ignore: cast_nullable_to_non_nullable
as I18nText?,executiveSummaryDirective: freezed == executiveSummaryDirective ? _self.executiveSummaryDirective : executiveSummaryDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,matrix1dSynthesisDirective: freezed == matrix1dSynthesisDirective ? _self.matrix1dSynthesisDirective : matrix1dSynthesisDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,matrix2dSynthesisDirective: freezed == matrix2dSynthesisDirective ? _self.matrix2dSynthesisDirective : matrix2dSynthesisDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,matrix3dSynthesisDirective: freezed == matrix3dSynthesisDirective ? _self.matrix3dSynthesisDirective : matrix3dSynthesisDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,matrixTextSynthesisDirective: freezed == matrixTextSynthesisDirective ? _self.matrixTextSynthesisDirective : matrixTextSynthesisDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,rowExplanationDirective: freezed == rowExplanationDirective ? _self.rowExplanationDirective : rowExplanationDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,xaiSynthesisDirective: freezed == xaiSynthesisDirective ? _self.xaiSynthesisDirective : xaiSynthesisDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,varianceSynthesisDirective: freezed == varianceSynthesisDirective ? _self.varianceSynthesisDirective : varianceSynthesisDirective // ignore: cast_nullable_to_non_nullable
as I18nText?,language: freezed == language ? _self.language : language // ignore: cast_nullable_to_non_nullable
as SystemLocale?,matrixSynthesisGroups: null == matrixSynthesisGroups ? _self._matrixSynthesisGroups : matrixSynthesisGroups // ignore: cast_nullable_to_non_nullable
as List<MatrixSynthesisGroup>,contentBlocks: null == contentBlocks ? _self._contentBlocks : contentBlocks // ignore: cast_nullable_to_non_nullable
as List<SduiBlockDTO>,targetBlockOrder: null == targetBlockOrder ? _self._targetBlockOrder : targetBlockOrder // ignore: cast_nullable_to_non_nullable
as List<TargetBlockType>,showSourcesSummaryBox: null == showSourcesSummaryBox ? _self.showSourcesSummaryBox : showSourcesSummaryBox // ignore: cast_nullable_to_non_nullable
as bool,sourcesDisplayMode: null == sourcesDisplayMode ? _self.sourcesDisplayMode : sourcesDisplayMode // ignore: cast_nullable_to_non_nullable
as SourcesDisplayMode,performativityDetectorStepId: freezed == performativityDetectorStepId ? _self.performativityDetectorStepId : performativityDetectorStepId // ignore: cast_nullable_to_non_nullable
as String?,
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
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get executiveSummaryDirective {
    if (_self.executiveSummaryDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.executiveSummaryDirective!, (value) {
    return _then(_self.copyWith(executiveSummaryDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get matrix1dSynthesisDirective {
    if (_self.matrix1dSynthesisDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.matrix1dSynthesisDirective!, (value) {
    return _then(_self.copyWith(matrix1dSynthesisDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get matrix2dSynthesisDirective {
    if (_self.matrix2dSynthesisDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.matrix2dSynthesisDirective!, (value) {
    return _then(_self.copyWith(matrix2dSynthesisDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get matrix3dSynthesisDirective {
    if (_self.matrix3dSynthesisDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.matrix3dSynthesisDirective!, (value) {
    return _then(_self.copyWith(matrix3dSynthesisDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get matrixTextSynthesisDirective {
    if (_self.matrixTextSynthesisDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.matrixTextSynthesisDirective!, (value) {
    return _then(_self.copyWith(matrixTextSynthesisDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get rowExplanationDirective {
    if (_self.rowExplanationDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.rowExplanationDirective!, (value) {
    return _then(_self.copyWith(rowExplanationDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get xaiSynthesisDirective {
    if (_self.xaiSynthesisDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.xaiSynthesisDirective!, (value) {
    return _then(_self.copyWith(xaiSynthesisDirective: value));
  });
}/// Create a copy of OutputProfile
/// with the given fields replaced by the non-null parameter values.
@override
@pragma('vm:prefer-inline')
$I18nTextCopyWith<$Res>? get varianceSynthesisDirective {
    if (_self.varianceSynthesisDirective == null) {
    return null;
  }

  return $I18nTextCopyWith<$Res>(_self.varianceSynthesisDirective!, (value) {
    return _then(_self.copyWith(varianceSynthesisDirective: value));
  });
}
}

// dart format on
