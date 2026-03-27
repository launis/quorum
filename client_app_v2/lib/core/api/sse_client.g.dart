// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'sse_client.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// SSE API Client Provider

@ProviderFor(sseClient)
final sseClientProvider = SseClientProvider._();

/// SSE API Client Provider

final class SseClientProvider
    extends $FunctionalProvider<SseClient, SseClient, SseClient>
    with $Provider<SseClient> {
  /// SSE API Client Provider
  SseClientProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'sseClientProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$sseClientHash();

  @$internal
  @override
  $ProviderElement<SseClient> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  SseClient create(Ref ref) {
    return sseClient(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(SseClient value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<SseClient>(value),
    );
  }
}

String _$sseClientHash() => r'652cbc0f5b8db900ea207917da0a5e5aa659ef15';
