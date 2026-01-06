// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_repository.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Execution Repository Provider**
///
/// The single source of truth for accessing Execution data.
/// It abstracts the underlying API network calls and serialization logic.

@ProviderFor(executionRepository)
final executionRepositoryProvider = ExecutionRepositoryProvider._();

/// **Execution Repository Provider**
///
/// The single source of truth for accessing Execution data.
/// It abstracts the underlying API network calls and serialization logic.

final class ExecutionRepositoryProvider
    extends
        $FunctionalProvider<
          ExecutionRepository,
          ExecutionRepository,
          ExecutionRepository
        >
    with $Provider<ExecutionRepository> {
  /// **Execution Repository Provider**
  ///
  /// The single source of truth for accessing Execution data.
  /// It abstracts the underlying API network calls and serialization logic.
  ExecutionRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'executionRepositoryProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$executionRepositoryHash();

  @$internal
  @override
  $ProviderElement<ExecutionRepository> $createElement(
    $ProviderPointer pointer,
  ) => $ProviderElement(pointer);

  @override
  ExecutionRepository create(Ref ref) {
    return executionRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(ExecutionRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<ExecutionRepository>(value),
    );
  }
}

String _$executionRepositoryHash() =>
    r'7d845ff897ef1891adb63315cc96f7f3f8f2ff99';
