// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'usage_stats_card.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(UsageScope)
final usageScopeProvider = UsageScopeProvider._();

final class UsageScopeProvider extends $NotifierProvider<UsageScope, String> {
  UsageScopeProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'usageScopeProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$usageScopeHash();

  @$internal
  @override
  UsageScope create() => UsageScope();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(String value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<String>(value),
    );
  }
}

String _$usageScopeHash() => r'b6a235c2329b18960a32dfe1435cfa614cce51ac';

abstract class _$UsageScope extends $Notifier<String> {
  String build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<String, String>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<String, String>,
              String,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
