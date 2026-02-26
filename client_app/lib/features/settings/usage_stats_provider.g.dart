// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'usage_stats_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(usageStats)
final usageStatsProvider = UsageStatsFamily._();

final class UsageStatsProvider
    extends
        $FunctionalProvider<
          AsyncValue<UsageStats>,
          UsageStats,
          FutureOr<UsageStats>
        >
    with $FutureModifier<UsageStats>, $FutureProvider<UsageStats> {
  UsageStatsProvider._({
    required UsageStatsFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'usageStatsProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$usageStatsHash();

  @override
  String toString() {
    return r'usageStatsProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<UsageStats> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<UsageStats> create(Ref ref) {
    final argument = this.argument as String;
    return usageStats(ref, scope: argument);
  }

  @override
  bool operator ==(Object other) {
    return other is UsageStatsProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$usageStatsHash() => r'04a35643a2d49447458b4d5e70fe764b9528f3c1';

final class UsageStatsFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<UsageStats>, String> {
  UsageStatsFamily._()
    : super(
        retry: null,
        name: r'usageStatsProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  UsageStatsProvider call({String scope = 'org'}) =>
      UsageStatsProvider._(argument: scope, from: this);

  @override
  String toString() => r'usageStatsProvider';
}
