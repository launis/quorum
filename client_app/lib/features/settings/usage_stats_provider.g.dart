// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'usage_stats_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(usageStats)
final usageStatsProvider = UsageStatsProvider._();

final class UsageStatsProvider
    extends
        $FunctionalProvider<
          AsyncValue<UsageStats>,
          UsageStats,
          FutureOr<UsageStats>
        >
    with $FutureModifier<UsageStats>, $FutureProvider<UsageStats> {
  UsageStatsProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'usageStatsProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$usageStatsHash();

  @$internal
  @override
  $FutureProviderElement<UsageStats> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<UsageStats> create(Ref ref) {
    return usageStats(ref);
  }
}

String _$usageStatsHash() => r'2e7517f7c2c1312d5857bfd4dbbf6ee9c1c47856';
