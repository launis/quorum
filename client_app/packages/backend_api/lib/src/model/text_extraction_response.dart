//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'text_extraction_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class TextExtractionResponse {
  /// Returns a new [TextExtractionResponse] instance.
  TextExtractionResponse({this.filename, required this.text});

  @JsonKey(name: r'filename', required: false)
  final String? filename;

  /// Extracted raw text content.
  @JsonKey(name: r'text', required: true)
  final String text;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is TextExtractionResponse &&
          other.filename == filename &&
          other.text == text;

  @override
  int get hashCode =>
      (filename == null ? 0 : filename.hashCode) + text.hashCode;

  factory TextExtractionResponse.fromJson(Map<String, dynamic> json) =>
      _$TextExtractionResponseFromJson(json);

  Map<String, dynamic> toJson() => _$TextExtractionResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
