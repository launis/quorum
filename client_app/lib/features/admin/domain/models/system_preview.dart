// ignore_for_file: invalid_annotation_target, non_abstract_class_inherits_abstract_member
import 'package:freezed_annotation/freezed_annotation.dart';

part 'system_preview.freezed.dart';
part 'system_preview.g.dart';

@freezed
abstract class SystemPreview with _$SystemPreview {
  const factory SystemPreview({
    @JsonKey(name: 'system_instruction') required String systemInstruction,
    @JsonKey(name: 'user_prompt') required String userPrompt,
    @JsonKey(name: 'agent_class') required String agentClass,
  }) = _SystemPreview;

  factory SystemPreview.fromJson(Map<String, dynamic> json) =>
      _$SystemPreviewFromJson(json);
}

@freezed
abstract class ChainPreview with _$ChainPreview {
  const factory ChainPreview({
    @JsonKey(name: 'markdown_content') required String markdownContent,
  }) = _ChainPreview;

  factory ChainPreview.fromJson(Map<String, dynamic> json) =>
      _$ChainPreviewFromJson(json);
}
