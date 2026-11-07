// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'workflow_inputs.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_RawFileInputDto _$RawFileInputDtoFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_RawFileInputDto',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'filename',
            'content_type',
            'data_base64',
            'content_base64',
          ],
        );
        final val = _RawFileInputDto(
          filename: $checkedConvert('filename', (v) => v as String),
          contentType: $checkedConvert(
            'content_type',
            (v) => v as String? ?? 'application/octet-stream',
          ),
          dataBase64: $checkedConvert('data_base64', (v) => v as String?),
          contentBase64: $checkedConvert('content_base64', (v) => v as String?),
        );
        return val;
      },
      fieldKeyMap: const {
        'contentType': 'content_type',
        'dataBase64': 'data_base64',
        'contentBase64': 'content_base64',
      },
    );

Map<String, dynamic> _$RawFileInputDtoToJson(_RawFileInputDto instance) =>
    <String, dynamic>{
      'filename': instance.filename,
      'content_type': instance.contentType,
      'data_base64': instance.dataBase64,
      'content_base64': instance.contentBase64,
    };

_WorkflowInputValue _$WorkflowInputValueFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      '_WorkflowInputValue',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          allowedKeys: const [
            'text_value',
            'file_value',
            'questionnaire_value',
          ],
        );
        final val = _WorkflowInputValue(
          textValue: $checkedConvert('text_value', (v) => v as String?),
          fileValue: $checkedConvert(
            'file_value',
            (v) => v == null
                ? null
                : RawFileInputDto.fromJson(v as Map<String, dynamic>),
          ),
          questionnaireValue: $checkedConvert(
            'questionnaire_value',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as String),
            ),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'textValue': 'text_value',
        'fileValue': 'file_value',
        'questionnaireValue': 'questionnaire_value',
      },
    );

Map<String, dynamic> _$WorkflowInputValueToJson(_WorkflowInputValue instance) =>
    <String, dynamic>{
      'text_value': instance.textValue,
      'file_value': instance.fileValue?.toJson(),
      'questionnaire_value': instance.questionnaireValue,
    };

_WorkflowInputs _$WorkflowInputsFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  '_WorkflowInputs',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      allowedKeys: const [
        'organization_id',
        'user_id',
        'simulation_mode',
        'language',
        'dynamic_inputs',
      ],
    );
    final val = _WorkflowInputs(
      organizationId: $checkedConvert('organization_id', (v) => v as String?),
      userId: $checkedConvert('user_id', (v) => v as String?),
      simulationMode: $checkedConvert(
        'simulation_mode',
        (v) => v as bool? ?? false,
      ),
      language: $checkedConvert('language', (v) => v as String? ?? 'en'),
      dynamicInputs: $checkedConvert(
        'dynamic_inputs',
        (v) =>
            (v as Map<String, dynamic>?)?.map(
              (k, e) =>
                  MapEntry(k, const WorkflowInputValueConverter().fromJson(e)),
            ) ??
            const <String, WorkflowInputValue>{},
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'organizationId': 'organization_id',
    'userId': 'user_id',
    'simulationMode': 'simulation_mode',
    'dynamicInputs': 'dynamic_inputs',
  },
);

Map<String, dynamic> _$WorkflowInputsToJson(_WorkflowInputs instance) =>
    <String, dynamic>{
      'organization_id': instance.organizationId,
      'user_id': instance.userId,
      'simulation_mode': instance.simulationMode,
      'language': instance.language,
      'dynamic_inputs': instance.dynamicInputs.map(
        (k, e) => MapEntry(k, const WorkflowInputValueConverter().toJson(e)),
      ),
    };
