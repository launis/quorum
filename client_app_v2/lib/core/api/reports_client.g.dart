// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'reports_client.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Reports API Client Provider

@ProviderFor(reportsClient)
final reportsClientProvider = ReportsClientProvider._();

/// Reports API Client Provider

final class ReportsClientProvider
    extends $FunctionalProvider<ReportsClient, ReportsClient, ReportsClient>
    with $Provider<ReportsClient> {
  /// Reports API Client Provider
  ReportsClientProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'reportsClientProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$reportsClientHash();

  @$internal
  @override
  $ProviderElement<ReportsClient> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  ReportsClient create(Ref ref) {
    return reportsClient(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ReportsClient value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ReportsClient>(value),
    );
  }
}

String _$reportsClientHash() => r'1deb1abb93312b8d503ac770a5bd0e044b22b7ca';
