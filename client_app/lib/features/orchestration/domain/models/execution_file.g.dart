// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_file.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ExecutionFile _$ExecutionFileFromJson(Map<String, dynamic> json) =>
    _ExecutionFile(
      name: json['name'] as String,
      path: json['path'] as String?,
      bytes:
          (json['bytes'] as List<dynamic>?)
              ?.map((e) => (e as num).toInt())
              .toList(),
    );

Map<String, dynamic> _$ExecutionFileToJson(_ExecutionFile instance) =>
    <String, dynamic>{
      'name': instance.name,
      'path': instance.path,
      'bytes': instance.bytes,
    };
