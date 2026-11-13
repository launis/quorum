import 'dart:convert';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/utils/safe_isolate.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:freezed_annotation/freezed_annotation.dart';

part 'task_brief.freezed.dart';
part 'task_brief.g.dart';

/// Immutable domain model for a reusable human-facing TaskBrief and case description.
/// Enforces 1:1 wire parity with backend TaskBriefResponseDTO.
@Freezed(equal: false)
abstract class TaskBrief with _$TaskBrief {
  const TaskBrief._();

  @JsonSerializable(disallowUnrecognizedKeys: true)
  const factory TaskBrief({
    @StrictOpaqueIdConverter() required String id,
    required String slug,
    @StrictOpaqueIdConverter()
    @JsonKey(name: 'organization_id')
    required String organizationId,
    required I18nText label,
    required I18nText description,
    @JsonKey(name: 'instruction_text') String? instructionText,
    @JsonKey(name: 'source_url') String? sourceUrl,
  }) = _TaskBrief;

  factory TaskBrief.fromJson(Map<String, dynamic> json) =>
      _$TaskBriefFromJson(json);

  /// Parses raw JSON string to TaskBrief in a background isolate.
  static Future<TaskBrief> parseInBackground(String rawJson) async {
    return safeIsolateRun(() {
      final Object? decoded = jsonDecode(rawJson);
      if (decoded is! Map) {
        throw AppException.validation(
          'Malformed TaskBrief JSON payload: expected JSON object.',
        );
      }
      return TaskBrief.fromJson(Map.from(decoded));
    });
  }

  /// Parses a raw JSON list into a list of TaskBrief instances in a background isolate.
  static Future<List<TaskBrief>> parseListInBackground(
    List<Object?> rawList,
  ) async {
    return safeIsolateRun(() {
      return rawList
          .map((Object? item) {
            if (item is! Map) {
              throw AppException.validation(
                'Malformed TaskBrief list item: expected JSON object.',
              );
            }
            return TaskBrief.fromJson(Map.from(item));
          })
          .toList(growable: false);
    });
  }
}
