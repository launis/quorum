//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'problem_detail.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ProblemDetail {
  /// Returns a new [ProblemDetail] instance.
  ProblemDetail({
    required this.type,

    required this.title,

    required this.status,

    required this.detail,

    this.instance,

    this.extensions,
  });

  /// URI identifying the error type
  @JsonKey(name: r'type', required: true)
  final String type;

  /// Human-readable error title
  @JsonKey(name: r'title', required: true)
  final String title;

  /// HTTP status code
  @JsonKey(name: r'status', required: true)
  final int status;

  /// Specific error message for this occurrence
  @JsonKey(name: r'detail', required: true)
  final String detail;

  @JsonKey(name: r'instance', required: false)
  final String? instance;

  @JsonKey(name: r'extensions', required: false)
  final Map<String, Object>? extensions;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ProblemDetail &&
          other.type == type &&
          other.title == title &&
          other.status == status &&
          other.detail == detail &&
          other.instance == instance &&
          other.extensions == extensions;

  @override
  int get hashCode =>
      type.hashCode +
      title.hashCode +
      status.hashCode +
      detail.hashCode +
      (instance == null ? 0 : instance.hashCode) +
      (extensions == null ? 0 : extensions.hashCode);

  factory ProblemDetail.fromJson(Map<String, dynamic> json) =>
      _$ProblemDetailFromJson(json);

  Map<String, dynamic> toJson() => _$ProblemDetailToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
