// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'studio_client.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Studio API Client Provider

@ProviderFor(studioClient)
final studioClientProvider = StudioClientProvider._();

/// Studio API Client Provider

final class StudioClientProvider
    extends $FunctionalProvider<StudioClient, StudioClient, StudioClient>
    with $Provider<StudioClient> {
  /// Studio API Client Provider
  StudioClientProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'studioClientProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$studioClientHash();

  @$internal
  @override
  $ProviderElement<StudioClient> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  StudioClient create(Ref ref) {
    return studioClient(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(StudioClient value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<StudioClient>(value),
    );
  }
}

String _$studioClientHash() => r'e1a37783d61e279b0fa80fee6d4e41fd316d21a9';
