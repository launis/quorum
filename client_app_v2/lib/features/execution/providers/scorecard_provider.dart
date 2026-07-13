import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/features/execution/models/scorecard_dto.dart';

part 'scorecard_provider.g.dart';

@riverpod
Future<ScorecardResponseDto> scorecard(Ref ref, String executionId) async {
  final client = ref.watch(executionClientProvider);
  final rawData = await client.getScorecard(executionId);
  return ScorecardResponseDto.fromJson(rawData);
}
