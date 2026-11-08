// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dynamic_start_screen.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Fetches the workflow UI input schema from the backend API.

@ProviderFor(workflowUiSchema)
final workflowUiSchemaProvider = WorkflowUiSchemaFamily._();

/// Fetches the workflow UI input schema from the backend API.

final class WorkflowUiSchemaProvider
    extends
        $FunctionalProvider<
          AsyncValue<WorkflowUiSchema>,
          WorkflowUiSchema,
          FutureOr<WorkflowUiSchema>
        >
    with $FutureModifier<WorkflowUiSchema>, $FutureProvider<WorkflowUiSchema> {
  /// Fetches the workflow UI input schema from the backend API.
  WorkflowUiSchemaProvider._({
    required WorkflowUiSchemaFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'workflowUiSchemaProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$workflowUiSchemaHash();

  @override
  String toString() {
    return r'workflowUiSchemaProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<WorkflowUiSchema> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<WorkflowUiSchema> create(Ref ref) {
    final argument = this.argument as String;
    return workflowUiSchema(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is WorkflowUiSchemaProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$workflowUiSchemaHash() => r'bfd4b493c6f25960d72067b0e92c1e3a20f946a5';

/// Fetches the workflow UI input schema from the backend API.

final class WorkflowUiSchemaFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<WorkflowUiSchema>, String> {
  WorkflowUiSchemaFamily._()
    : super(
        retry: null,
        name: r'workflowUiSchemaProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches the workflow UI input schema from the backend API.

  WorkflowUiSchemaProvider call(String workflowId) =>
      WorkflowUiSchemaProvider._(argument: workflowId, from: this);

  @override
  String toString() => r'workflowUiSchemaProvider';
}
