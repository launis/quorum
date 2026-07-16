// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_client.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Execution API Client Provider

@ProviderFor(executionClient)
final executionClientProvider = ExecutionClientProvider._();

/// Execution API Client Provider

final class ExecutionClientProvider
    extends
        $FunctionalProvider<ExecutionClient, ExecutionClient, ExecutionClient>
    with $Provider<ExecutionClient> {
  /// Execution API Client Provider
  ExecutionClientProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'executionClientProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$executionClientHash();

  @$internal
  @override
  $ProviderElement<ExecutionClient> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  ExecutionClient create(Ref ref) {
    return executionClient(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ExecutionClient value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ExecutionClient>(value),
    );
  }
}

String _$executionClientHash() => r'4a525361bde7e206b0c9864764d0a0188e63a9b5';
