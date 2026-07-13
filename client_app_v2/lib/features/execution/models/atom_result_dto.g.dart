// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'atom_result_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_ExtractedValueDTO _$ExtractedValueDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_ExtractedValueDTO', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['value', 'unit']);
      final val = _ExtractedValueDTO(
        value: $checkedConvert('value', (v) => v),
        unit: $checkedConvert('unit', (v) => v as String?),
      );
      return val;
    });

Map<String, dynamic> _$ExtractedValueDTOToJson(_ExtractedValueDTO instance) =>
    <String, dynamic>{'value': instance.value, 'unit': instance.unit};

_ErrorDetailsDTO _$ErrorDetailsDTOFromJson(Map<String, dynamic> json) =>
    $checkedCreate('_ErrorDetailsDTO', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['error_code', 'message']);
      final val = _ErrorDetailsDTO(
        errorCode: $checkedConvert('error_code', (v) => v as String),
        message: $checkedConvert('message', (v) => v as String),
      );
      return val;
    }, fieldKeyMap: const {'errorCode': 'error_code'});

Map<String, dynamic> _$ErrorDetailsDTOToJson(_ErrorDetailsDTO instance) =>
    <String, dynamic>{
      'error_code': instance.errorCode,
      'message': instance.message,
    };

_AtomResultDTO _$AtomResultDTOFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_AtomResultDTO',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'tda_id',
        'status',
        'extracted_data',
        'source_quote',
        'contextual_override',
        'evaluation_reasoning',
        'error_details',
        'depends_on_tda_ids',
        'short_circuit_reason_tda_ids',
      ],
    );
    final val = _AtomResultDTO(
      tdaId: $checkedConvert('tda_id', (v) => v as String),
      status: $checkedConvert(
        'status',
        (v) => $enumDecode(_$ExecutionStatusEnumMap, v),
      ),
      extractedData: $checkedConvert(
        'extracted_data',
        (v) => v == null
            ? null
            : ExtractedValueDTO.fromJson(v as Map<String, dynamic>),
      ),
      sourceQuote: $checkedConvert('source_quote', (v) => v as String?),
      contextualOverride: $checkedConvert(
        'contextual_override',
        (v) => v as bool? ?? false,
      ),
      evaluationReasoning: $checkedConvert(
        'evaluation_reasoning',
        (v) => v as String?,
      ),
      errorDetails: $checkedConvert(
        'error_details',
        (v) => v == null
            ? null
            : ErrorDetailsDTO.fromJson(v as Map<String, dynamic>),
      ),
      dependsOnTdaIds: $checkedConvert(
        'depends_on_tda_ids',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
      shortCircuitReasonTdaIds: $checkedConvert(
        'short_circuit_reason_tda_ids',
        (v) =>
            (v as List<dynamic>?)?.map((e) => e as String).toList() ?? const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'tdaId': 'tda_id',
    'extractedData': 'extracted_data',
    'sourceQuote': 'source_quote',
    'contextualOverride': 'contextual_override',
    'evaluationReasoning': 'evaluation_reasoning',
    'errorDetails': 'error_details',
    'dependsOnTdaIds': 'depends_on_tda_ids',
    'shortCircuitReasonTdaIds': 'short_circuit_reason_tda_ids',
  },
);

Map<String, dynamic> _$AtomResultDTOToJson(_AtomResultDTO instance) =>
    <String, dynamic>{
      'tda_id': instance.tdaId,
      'status': _$ExecutionStatusEnumMap[instance.status]!,
      'extracted_data': instance.extractedData?.toJson(),
      'source_quote': instance.sourceQuote,
      'contextual_override': instance.contextualOverride,
      'evaluation_reasoning': instance.evaluationReasoning,
      'error_details': instance.errorDetails?.toJson(),
      'depends_on_tda_ids': instance.dependsOnTdaIds,
      'short_circuit_reason_tda_ids': instance.shortCircuitReasonTdaIds,
    };

const _$ExecutionStatusEnumMap = {
  ExecutionStatus.passed: 'PASSED',
  ExecutionStatus.failed: 'FAILED',
  ExecutionStatus.nA: 'N_A',
  ExecutionStatus.systemError: 'SYSTEM_ERROR',
  ExecutionStatus.blocked: 'BLOCKED',
  ExecutionStatus.pending: 'PENDING',
  ExecutionStatus.running: 'RUNNING',
  ExecutionStatus.queued: 'QUEUED',
};
