import 'package:freezed_annotation/freezed_annotation.dart';

part 'component_def.freezed.dart';
part 'component_def.g.dart';

@freezed
abstract class StudioComponentDef with _$StudioComponentDef {
  const factory StudioComponentDef({
    required String id,
    required String name,
    required String type,
    String? description,
    required Map<String, dynamic> content,
  }) = _StudioComponentDef;

  const StudioComponentDef._();

  factory StudioComponentDef.fromJson(Map<String, dynamic> json) =>
      _$StudioComponentDefFromJson(json);

  bool get isMatrix => type == 'evaluation_matrix';
}
