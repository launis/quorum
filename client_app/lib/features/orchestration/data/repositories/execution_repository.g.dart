// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_repository.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Repository for managing Audit Execution data.
///
/// Handles interaction with the `/executions` endpoints of the backend API.
/// Uses strict functional error handling via [TaskEither] and [AppError].

@ProviderFor(executionRepository)
final executionRepositoryProvider = ExecutionRepositoryProvider._();

/// Repository for managing Audit Execution data.
///
/// Handles interaction with the `/executions` endpoints of the backend API.
/// Uses strict functional error handling via [TaskEither] and [AppError].

final class ExecutionRepositoryProvider
    extends
        $FunctionalProvider<
          ExecutionRepository,
          ExecutionRepository,
          ExecutionRepository
        >
    with $Provider<ExecutionRepository> {
  /// Repository for managing Audit Execution data.
  ///
  /// Handles interaction with the `/executions` endpoints of the backend API.
  /// Uses strict functional error handling via [TaskEither] and [AppError].
  ExecutionRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'executionRepositoryProvider',
        isAutoDispose: false,
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
    r'1ba73bed51807c49114ccafdaf79086c67a71791';
