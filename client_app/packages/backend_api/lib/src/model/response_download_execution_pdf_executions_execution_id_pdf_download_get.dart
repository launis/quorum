//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/pdf_download_check_response.dart';
import 'package:backend_api/src/model/pdf_queued_response.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'response_download_execution_pdf_executions_execution_id_pdf_download_get.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet {
  /// Returns a new [ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet] instance.
  ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet({
    required this.status,

    required this.exists,

    this.localPath,

    required this.message,
  });

  @JsonKey(name: r'status', required: true)
  final String status;

  @JsonKey(name: r'exists', required: true)
  final bool exists;

  @JsonKey(name: r'local_path', required: false)
  final String? localPath;

  @JsonKey(name: r'message', required: true)
  final String message;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet &&
          other.status == status &&
          other.exists == exists &&
          other.localPath == localPath &&
          other.message == message;

  @override
  int get hashCode =>
      status.hashCode + exists.hashCode + localPath.hashCode + message.hashCode;

  factory ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGet.fromJson(
    Map<String, dynamic> json,
  ) =>
      _$ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGetFromJson(
        json,
      );

  Map<String, dynamic> toJson() =>
      _$ResponseDownloadExecutionPdfExecutionsExecutionIdPdfDownloadGetToJson(
        this,
      );

  @override
  String toString() {
    return toJson().toString();
  }
}
