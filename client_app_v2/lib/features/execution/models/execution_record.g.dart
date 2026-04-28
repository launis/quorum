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
            'report_data',
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
          reportData: $checkedConvert(
            'report_data',
            (v) => v == null
                ? null
                : ReportDataDTO.fromJson(v as Map<String, dynamic>),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'workflowId': 'workflow_id',
        'traceVersion': 'trace_version',
        'reportData': 'report_data',
      },
    );

Map<String, dynamic> _$ExecutionRecordToJson(_ExecutionRecord instance) =>
    <String, dynamic>{
      'id': instance.id,
      'workflow_id': instance.workflowId,
      'status': instance.status,
      'trace_version': instance.traceVersion,
      'report_data': instance.reportData?.toJson(),
    };
