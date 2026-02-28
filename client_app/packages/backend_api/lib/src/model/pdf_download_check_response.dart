//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'pdf_download_check_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PDFDownloadCheckResponse {
  /// Returns a new [PDFDownloadCheckResponse] instance.
  PDFDownloadCheckResponse({
    required this.status,

    required this.exists,

    this.localPath,
  });

  @JsonKey(name: r'status', required: true)
  final String status;

  @JsonKey(name: r'exists', required: true)
  final bool exists;

  @JsonKey(name: r'local_path', required: false)
  final String? localPath;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PDFDownloadCheckResponse &&
          other.status == status &&
          other.exists == exists &&
          other.localPath == localPath;

  @override
  int get hashCode =>
      status.hashCode +
      exists.hashCode +
      (localPath == null ? 0 : localPath.hashCode);

  factory PDFDownloadCheckResponse.fromJson(Map<String, dynamic> json) =>
      _$PDFDownloadCheckResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PDFDownloadCheckResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
