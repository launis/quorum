// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'human_override_request_dto.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_HumanOverrideRequestDto _$HumanOverrideRequestDtoFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_HumanOverrideRequestDto',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const ['new_status', 'reason', 'evidence_quotes'],
    );
    final val = _HumanOverrideRequestDto(
      newStatus: $checkedConvert(
        'new_status',
        (v) => $enumDecode(_$ExecutionStatusEnumMap, v),
      ),
      reason: $checkedConvert('reason', (v) => v as String),
      evidenceQuotes: $checkedConvert(
        'evidence_quotes',
        (v) =>
            (v as List<dynamic>?)
                ?.map(
                  (e) => QuoteEvidenceDto.fromJson(e as Map<String, dynamic>),
                )
                .toList() ??
            const [],
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'newStatus': 'new_status',
    'evidenceQuotes': 'evidence_quotes',
  },
);

Map<String, dynamic> _$HumanOverrideRequestDtoToJson(
  _HumanOverrideRequestDto instance,
) => <String, dynamic>{
  'new_status': _$ExecutionStatusEnumMap[instance.newStatus]!,
  'reason': instance.reason,
  'evidence_quotes': instance.evidenceQuotes.map((e) => e.toJson()).toList(),
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
