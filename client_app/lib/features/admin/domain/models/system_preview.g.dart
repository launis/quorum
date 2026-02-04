// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'system_preview.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_SystemPreview _$SystemPreviewFromJson(Map<String, dynamic> json) =>
    _SystemPreview(
      systemInstruction: json['system_instruction'] as String,
      userPrompt: json['user_prompt'] as String,
      agentClass: json['agent_class'] as String,
    );

Map<String, dynamic> _$SystemPreviewToJson(_SystemPreview instance) =>
    <String, dynamic>{
      'system_instruction': instance.systemInstruction,
      'user_prompt': instance.userPrompt,
      'agent_class': instance.agentClass,
    };

_ChainPreview _$ChainPreviewFromJson(Map<String, dynamic> json) =>
    _ChainPreview(markdownContent: json['markdown_content'] as String);

Map<String, dynamic> _$ChainPreviewToJson(_ChainPreview instance) =>
    <String, dynamic>{'markdown_content': instance.markdownContent};
