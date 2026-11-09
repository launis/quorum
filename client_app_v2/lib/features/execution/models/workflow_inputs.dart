import 'package:freezed_annotation/freezed_annotation.dart';

part 'workflow_inputs.freezed.dart';
part 'workflow_inputs.g.dart';

/// Strongly typed file upload payload for workflow execution inputs.
@freezed
abstract class RawFileInputDto with _$RawFileInputDto {
  const RawFileInputDto._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory RawFileInputDto({
    required String filename,
    @JsonKey(name: 'content_type')
    @Default('application/octet-stream')
    String contentType,
    @JsonKey(name: 'data_base64') String? dataBase64,
    @JsonKey(name: 'content_base64') String? contentBase64,
  }) = _RawFileInputDto;

  factory RawFileInputDto.fromJson(Map<String, dynamic> json) =>
      _$RawFileInputDtoFromJson(json);
}

/// Strongly typed value container for a workflow dynamic input entry.
@freezed
abstract class WorkflowInputValue with _$WorkflowInputValue {
  const WorkflowInputValue._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory WorkflowInputValue({
    @JsonKey(name: 'text_value') String? textValue,
    @JsonKey(name: 'file_value') RawFileInputDto? fileValue,
    @JsonKey(name: 'questionnaire_value')
    Map<String, String>? questionnaireValue,
  }) = _WorkflowInputValue;

  factory WorkflowInputValue.text(String value) =>
      WorkflowInputValue(textValue: value);

  factory WorkflowInputValue.file({
    required String filename,
    String contentType = 'application/octet-stream',
    String? dataBase64,
    String? contentBase64,
  }) => WorkflowInputValue(
    fileValue: RawFileInputDto(
      filename: filename,
      contentType: contentType,
      dataBase64: dataBase64,
      contentBase64: contentBase64,
    ),
  );

  factory WorkflowInputValue.questionnaire(Map<String, String> answers) =>
      WorkflowInputValue(questionnaireValue: answers);

  factory WorkflowInputValue.fromJson(Map<String, dynamic> json) =>
      _$WorkflowInputValueFromJson(json);

  bool get isNotEmpty {
    if (textValue != null && textValue!.trim().isNotEmpty) {
      return true;
    }
    if (fileValue != null &&
        ((fileValue!.dataBase64?.isNotEmpty ?? false) ||
            (fileValue!.contentBase64?.isNotEmpty ?? false))) {
      return true;
    }
    if (questionnaireValue != null && questionnaireValue!.isNotEmpty) {
      return questionnaireValue!.values.any((String v) => v.trim().isNotEmpty);
    }
    return false;
  }

  Object? toWireJson() {
    if (fileValue != null) {
      final file = fileValue!;
      if (file.dataBase64 != null) {
        return <String, String>{
          'filename': file.filename,
          'content_type': file.contentType,
          'data_base64': file.dataBase64!,
        };
      }
      return <String, String>{
        'filename': file.filename,
        if (file.contentBase64 != null) 'content_base64': file.contentBase64!,
      };
    }
    if (questionnaireValue != null) {
      return questionnaireValue;
    }
    return textValue ?? '';
  }
}

/// Converter mapping heterogeneous JSON wire values into [WorkflowInputValue].
class WorkflowInputValueConverter
    implements JsonConverter<WorkflowInputValue, Object?> {
  const WorkflowInputValueConverter();

  @override
  WorkflowInputValue fromJson(Object? json) {
    if (json is String) {
      return WorkflowInputValue.text(json);
    }
    if (json is Map) {
      if (json.containsKey('filename') &&
          (json.containsKey('data_base64') ||
              json.containsKey('content_base64'))) {
        return WorkflowInputValue.file(
          filename: json['filename']?.toString() ?? '',
          contentType:
              json['content_type']?.toString() ?? 'application/octet-stream',
          dataBase64: json['data_base64']?.toString(),
          contentBase64: json['content_base64']?.toString(),
        );
      }
      return WorkflowInputValue.questionnaire(<String, String>{
        for (final MapEntry<Object?, Object?> entry in json.entries)
          entry.key.toString(): entry.value?.toString() ?? '',
      });
    }
    return WorkflowInputValue.text(json?.toString() ?? '');
  }

  @override
  Object? toJson(WorkflowInputValue object) => object.toWireJson();
}

/// Strongly typed dynamic inputs container for client DAG execution (SSOT).
@Freezed(equal: false)
abstract class WorkflowInputs with _$WorkflowInputs {
  const WorkflowInputs._();

  @JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)
  const factory WorkflowInputs({
    @JsonKey(name: 'organization_id') String? organizationId,
    @JsonKey(name: 'user_id') String? userId,
    @JsonKey(name: 'simulation_mode') @Default(false) bool simulationMode,
    @Default('en') String language,
    @JsonKey(name: 'dynamic_inputs')
    @WorkflowInputValueConverter()
    @Default(<String, WorkflowInputValue>{})
    Map<String, WorkflowInputValue> dynamicInputs,
  }) = _WorkflowInputs;

  /// Instantiates a strictly typed [WorkflowInputs] from raw JSON.
  factory WorkflowInputs.fromJson(Map<String, dynamic> json) =>
      _$WorkflowInputsFromJson(json);
}
