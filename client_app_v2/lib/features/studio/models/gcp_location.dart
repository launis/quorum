// ignore_for_file: invalid_annotation_target
import 'package:freezed_annotation/freezed_annotation.dart';

part 'gcp_location.freezed.dart';
part 'gcp_location.g.dart';

/// Freezed domain model for GCP Vertex AI locations.
@Freezed(equal: false)
abstract class GcpLocation with _$GcpLocation {
  const GcpLocation._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory GcpLocation({
    required String id,
    required String label,
    required String description,
  }) = _GcpLocation;

  factory GcpLocation.fromJson(Map<String, dynamic> json) =>
      _$GcpLocationFromJson(json);
}
