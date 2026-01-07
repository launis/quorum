// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'execution_details_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(executionDetails)
final executionDetailsProvider = ExecutionDetailsFamily._();

final class ExecutionDetailsProvider
    extends
        $FunctionalProvider<
          AsyncValue<Execution>,
          Execution,
          FutureOr<Execution>
        >
    with $FutureModifier<Execution>, $FutureProvider<Execution> {
  ExecutionDetailsProvider._({
    required ExecutionDetailsFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'executionDetailsProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$executionDetailsHash();

  @override
  String toString() {
    return r'executionDetailsProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<Execution> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<Execution> create(Ref ref) {
    final argument = this.argument as String;
    return executionDetails(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is ExecutionDetailsProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$executionDetailsHash() => r'23e4e55eda1901a95b2236c078d884dcee1607e7';

final class ExecutionDetailsFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Execution>, String> {
  ExecutionDetailsFamily._()
    : super(
        retry: null,
        name: r'executionDetailsProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  ExecutionDetailsProvider call(String executionId) =>
      ExecutionDetailsProvider._(argument: executionId, from: this);

  @override
  String toString() => r'executionDetailsProvider';
}
