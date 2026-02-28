//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'ingest_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class IngestRequest {
  /// Returns a new [IngestRequest] instance.
  IngestRequest({
    this.filePath = 'data/Holistinen Mestaruus.docx',

    this.resetDb = false,

    this.modelStrategy,
  });

  /// Path to the source document.
  @JsonKey(
    defaultValue: 'data/Holistinen Mestaruus.docx',
    name: r'file_path',
    required: false,
  )
  final String? filePath;

  /// Clear DB before ingestion.
  @JsonKey(defaultValue: false, name: r'reset_db', required: false)
  final bool? resetDb;

  @JsonKey(name: r'model_strategy', required: false)
  final String? modelStrategy;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is IngestRequest &&
          other.filePath == filePath &&
          other.resetDb == resetDb &&
          other.modelStrategy == modelStrategy;

  @override
  int get hashCode =>
      filePath.hashCode +
      resetDb.hashCode +
      (modelStrategy == null ? 0 : modelStrategy.hashCode);

  factory IngestRequest.fromJson(Map<String, dynamic> json) =>
      _$IngestRequestFromJson(json);

  Map<String, dynamic> toJson() => _$IngestRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
