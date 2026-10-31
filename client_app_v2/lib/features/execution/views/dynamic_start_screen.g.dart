// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'dynamic_start_screen.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Riverpod Provider for UI Schema. Replaces manual `_fetchSchema()` side-effects.

@ProviderFor(workflowUiSchema)
final workflowUiSchemaProvider = WorkflowUiSchemaFamily._();

/// Riverpod Provider for UI Schema. Replaces manual `_fetchSchema()` side-effects.

final class WorkflowUiSchemaProvider
    extends
        $FunctionalProvider<
          AsyncValue<WorkflowUiSchema>,
          WorkflowUiSchema,
          FutureOr<WorkflowUiSchema>
        >
    with $FutureModifier<WorkflowUiSchema>, $FutureProvider<WorkflowUiSchema> {
  /// Riverpod Provider for UI Schema. Replaces manual `_fetchSchema()` side-effects.
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

/// Riverpod Provider for UI Schema. Replaces manual `_fetchSchema()` side-effects.

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

  /// Riverpod Provider for UI Schema. Replaces manual `_fetchSchema()` side-effects.

  WorkflowUiSchemaProvider call(String workflowId) =>
      WorkflowUiSchemaProvider._(argument: workflowId, from: this);

  @override
  String toString() => r'workflowUiSchemaProvider';
}
