// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'component_def.freezed.dart';
part 'component_def.g.dart';

@freezed
@freezed
abstract class OntologyDimension with _$OntologyDimension {
  const factory OntologyDimension({
    required String id,
    @JsonKey(name: 'label') required String name,
    required String description,
    @Default(false) @JsonKey(name: 'is_system') bool isSystem,
  }) = _OntologyDimension;

  factory OntologyDimension.fromJson(Map<String, dynamic> json) =>
      _$OntologyDimensionFromJson(json);
}

@freezed
@freezed
abstract class MatrixCriterion with _$MatrixCriterion {
  const factory MatrixCriterion({
    @JsonKey(name: 'id') required String dimensionId,
    @Default('') String label,
    @JsonKey(name: 'instruction') @Default('') String prompt,
    @Default({}) Map<String, String> anchors,
    @Default(1.0) double weight,
  }) = _MatrixCriterion;

  factory MatrixCriterion.fromJson(Map<String, dynamic> json) =>
      _$MatrixCriterionFromJson(json);
}

@freezed
@freezed
abstract class MatrixDef with _$MatrixDef {
  const factory MatrixDef({
    required String id,
    required String name,
    required String description,
    required Map<String, int> scale,
    @JsonKey(name: 'role_description') String? roleDescription,
    @Default([]) List<MatrixCriterion> criteria,
  }) = _MatrixDef;

  factory MatrixDef.fromJson(Map<String, dynamic> json) =>
      _$MatrixDefFromJson(json);
}

@freezed
abstract class StudioComponentDef with _$StudioComponentDef {
  const factory StudioComponentDef({
    required String id,
    String? slug,
    String? name,
    required String type,
    String? description,
    String? citation, // Added citation
    required dynamic content, // Changed to dynamic
  }) = _StudioComponentDef;

  const StudioComponentDef._();

  factory StudioComponentDef.fromJson(Map<String, dynamic> json) =>
      _$StudioComponentDefFromJson(json);

  bool get isMatrix => type == 'evaluation_matrix';
}
