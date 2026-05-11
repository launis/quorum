// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'tda_state.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Pending _$PendingFromJson(Map<String, dynamic> json) =>
    $checkedCreate('Pending', json, ($checkedConvert) {
      $checkKeys(json, allowedKeys: const ['runtimeType']);
      final val = Pending(
        $type: $checkedConvert('runtimeType', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {r'$type': 'runtimeType'});

Map<String, dynamic> _$PendingToJson(Pending instance) => <String, dynamic>{
  'runtimeType': instance.$type,
};

Evaluated _$EvaluatedFromJson(Map<String, dynamic> json) => $checkedCreate(
  'Evaluated',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'passed',
        'display_quote',
        'raw_anchor',
        'runtimeType',
      ],
    );
    final val = Evaluated(
      passed: $checkedConvert('passed', (v) => v as bool),
      displayQuote: $checkedConvert('display_quote', (v) => v as String),
      rawAnchor: $checkedConvert('raw_anchor', (v) => v as String),
      $type: $checkedConvert('runtimeType', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'displayQuote': 'display_quote',
    'rawAnchor': 'raw_anchor',
    r'$type': 'runtimeType',
  },
);

Map<String, dynamic> _$EvaluatedToJson(Evaluated instance) => <String, dynamic>{
  'passed': instance.passed,
  'display_quote': instance.displayQuote,
  'raw_anchor': instance.rawAnchor,
  'runtimeType': instance.$type,
};

Dlq _$DlqFromJson(Map<String, dynamic> json) => $checkedCreate(
  'Dlq',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const ['user_reason', 'backend_trace', 'runtimeType'],
    );
    final val = Dlq(
      userReason: $checkedConvert('user_reason', (v) => v as String),
      backendTrace: $checkedConvert('backend_trace', (v) => v as String),
      $type: $checkedConvert('runtimeType', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'userReason': 'user_reason',
    'backendTrace': 'backend_trace',
    r'$type': 'runtimeType',
  },
);

Map<String, dynamic> _$DlqToJson(Dlq instance) => <String, dynamic>{
  'user_reason': instance.userReason,
  'backend_trace': instance.backendTrace,
  'runtimeType': instance.$type,
};
