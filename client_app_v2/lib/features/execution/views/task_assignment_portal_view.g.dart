// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'task_assignment_portal_view.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(taskAssignmentPreview)
final taskAssignmentPreviewProvider = TaskAssignmentPreviewFamily._();

final class TaskAssignmentPreviewProvider
    extends
        $FunctionalProvider<
          AsyncValue<ExecutionAssignmentPreviewDto>,
          ExecutionAssignmentPreviewDto,
          FutureOr<ExecutionAssignmentPreviewDto>
        >
    with
        $FutureModifier<ExecutionAssignmentPreviewDto>,
        $FutureProvider<ExecutionAssignmentPreviewDto> {
  TaskAssignmentPreviewProvider._({
    required TaskAssignmentPreviewFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'taskAssignmentPreviewProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$taskAssignmentPreviewHash();

  @override
  String toString() {
    return r'taskAssignmentPreviewProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<ExecutionAssignmentPreviewDto> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<ExecutionAssignmentPreviewDto> create(Ref ref) {
    final argument = this.argument as String;
    return taskAssignmentPreview(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is TaskAssignmentPreviewProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$taskAssignmentPreviewHash() =>
    r'e27ad7d40dfee0f9ef29bc3d9a94eb034d1a2eb9';

final class TaskAssignmentPreviewFamily extends $Family
    with
        $FunctionalFamilyOverride<
          FutureOr<ExecutionAssignmentPreviewDto>,
          String
        > {
  TaskAssignmentPreviewFamily._()
    : super(
        retry: null,
        name: r'taskAssignmentPreviewProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  TaskAssignmentPreviewProvider call(String token) =>
      TaskAssignmentPreviewProvider._(argument: token, from: this);

  @override
  String toString() => r'taskAssignmentPreviewProvider';
}
