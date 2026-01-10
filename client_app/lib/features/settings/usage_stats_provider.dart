import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'usage_stats_provider.g.dart';

class UsageStats {
  final int usedTokens;
  final int tokenLimit;
  final double percentage;

  UsageStats({required this.usedTokens, required this.tokenLimit})
    : percentage = (usedTokens / tokenLimit).clamp(0.0, 1.0);
}

@riverpod
Future<UsageStats> usageStats(Ref ref) async {
  // Mock API call delay
  await Future<void>.delayed(const Duration(seconds: 1));

  // Return mock data
  return UsageStats(usedTokens: 15420, tokenLimit: 50000);
}
