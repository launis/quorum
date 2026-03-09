// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'sse_client.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(sseClient)
final sseClientProvider = SseClientProvider._();

final class SseClientProvider
    extends $FunctionalProvider<SseClient, SseClient, SseClient>
    with $Provider<SseClient> {
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

String _$sseClientHash() => r'aafabc50c06d32556064a5b39fdc0c445a4959ef';
