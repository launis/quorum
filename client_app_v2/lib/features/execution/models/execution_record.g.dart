// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_record.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ExecutionRecord _$ExecutionRecordFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_ExecutionRecord',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'id',
            'workflow_id',
            'status',
            'trace_version',
            'strictness_level',
            'report_data',
            'report_data_v2',
          ],
        );
        final val = _ExecutionRecord(
          id: $checkedConvert('id', (v) => v as String),
          workflowId: $checkedConvert('workflow_id', (v) => v as String),
          status: $checkedConvert(
            'status',
            (v) => _statusFromJson(v as String),
          ),
          traceVersion: $checkedConvert(
            'trace_version',
            (v) => _traceVersionFromJson(v),
          ),
          strictnessLevel: $checkedConvert(
            'strictness_level',
            (v) => (v as num?)?.toInt(),
          ),
          reportData: $checkedConvert(
            'report_data',
            (v) => v == null
                ? null
                : ReportDataDTO.fromJson(v as Map<String, dynamic>),
          ),
          reportDataV2: $checkedConvert(
            'report_data_v2',
            (v) => v == null
                ? null
                : ReportDataDto.fromJson(v as Map<String, dynamic>),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'workflowId': 'workflow_id',
        'traceVersion': 'trace_version',
        'strictnessLevel': 'strictness_level',
        'reportData': 'report_data',
        'reportDataV2': 'report_data_v2',
      },
    );

Map<String, dynamic> _$ExecutionRecordToJson(_ExecutionRecord instance) =>
    <String, dynamic>{
      'id': instance.id,
      'workflow_id': instance.workflowId,
      'status': instance.status,
      'trace_version': instance.traceVersion,
      'strictness_level': instance.strictnessLevel,
      'report_data': instance.reportData?.toJson(),
      'report_data_v2': instance.reportDataV2?.toJson(),
    };
