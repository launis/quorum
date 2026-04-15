import 'dart:isolate';

import 'package:riverpod_annotation/riverpod_annotation.dart';

import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';

part 'scorecard_controller.g.dart';

/// Controller for fetching and rendering a complete Diagnostic Scorecard off the Main Thread.
/// Adheres to the Desktop Architecture "Fail-Fast" and "Isolate Parsing" mandates.
@riverpod
class ScorecardController extends _$ScorecardController {
  @override
  Future<ScorecardResponseDto> build(String executionId) async {
    final client = ref.watch(executionClientProvider);

    // Network call
    final rawData = await client.getScorecard(executionId);

    // Isolate.run to prevent heavy JSON dictionary mapping from dropping frame rates
    // on robust nested traces. Enforces strict DTO validation without jank.
    return await Isolate.run(() => ScorecardResponseDto.fromJson(rawData));
  }
}
