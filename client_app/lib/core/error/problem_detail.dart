import 'package:json_annotation/json_annotation.dart';

part 'problem_detail.g.dart';

/// RFC 7807 Problem Details response model.
///
/// This is the standardized error format returned by the backend API.
/// All API errors conform to this structure.
///
/// **Fields:**
/// - `type`: URI identifying the error type (links to documentation)
/// - `title`: Human-readable error title
/// - `status`: HTTP status code
/// - `detail`: Specific error message for this occurrence
/// - `instance`: Optional URI for this specific error
/// - `extensions`: Additional context (step_id, cause, etc.)
///
/// **Example Response:**
/// ```json
/// {
///   "type": "https://api.quorum.fi/errors/execution-not-found",
///   "title": "Execution Not Found",
///   "status": 404,
///   "detail": "Execution 'abc-123' not found.",
///   "instance": "/executions/abc-123"
/// }
/// ```
@JsonSerializable()
class ProblemDetail {
  /// URI identifying the error type.
  final String type;

  /// Human-readable error title.
  final String title;

  /// HTTP status code.
  final int status;

  /// Specific error message for this occurrence.
  final String detail;

  /// Optional URI identifying this specific error occurrence.
  final String? instance;

  /// Additional context (step_id, cause, agent, etc.).
  final Map<String, dynamic>? extensions;

  const ProblemDetail({
    required this.type,
    required this.title,
    required this.status,
    required this.detail,
    this.instance,
    this.extensions,
  });

  factory ProblemDetail.fromJson(Map<String, dynamic> json) =>
      _$ProblemDetailFromJson(json);

  Map<String, dynamic> toJson() => _$ProblemDetailToJson(this);

  /// Extracts error code from type URI for localization lookup.
  ///
  /// Converts: `https://api.quorum.fi/errors/execution-not-found`
  /// To: `EXECUTION_NOT_FOUND`
  String get errorCode {
    final slug = type.split('/').last;
    return slug.replaceAll('-', '_').toUpperCase();
  }

  /// Checks if this is a specific error type.
  bool isErrorCode(String code) => errorCode == code;

  /// Common error code checks.
  bool get isNotFound => status == 404;
  bool get isUnauthorized => status == 401;
  bool get isForbidden => status == 403;
  bool get isServerError => status >= 500;
  bool get isClientError => status >= 400 && status < 500;

  @override
  String toString() =>
      'ProblemDetail(type: $type, title: $title, status: $status, detail: $detail)';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ProblemDetail &&
          type == other.type &&
          status == other.status &&
          detail == other.detail;

  @override
  int get hashCode => Object.hash(type, status, detail);
}
