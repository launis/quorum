// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'studio_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Fetches a single Workflow natively by ID

@ProviderFor(workflowById)
final workflowByIdProvider = WorkflowByIdFamily._();

/// Fetches a single Workflow natively by ID

final class WorkflowByIdProvider
    extends
        $FunctionalProvider<AsyncValue<Workflow>, Workflow, FutureOr<Workflow>>
    with $FutureModifier<Workflow>, $FutureProvider<Workflow> {
  /// Fetches a single Workflow natively by ID
  WorkflowByIdProvider._({
    required WorkflowByIdFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'workflowByIdProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$workflowByIdHash();

  @override
  String toString() {
    return r'workflowByIdProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<Workflow> $createElement($ProviderPointer pointer) =>
      $FutureProviderElement(pointer);

  @override
  FutureOr<Workflow> create(Ref ref) {
    final argument = this.argument as String;
    return workflowById(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is WorkflowByIdProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$workflowByIdHash() => r'bd7910a463824b12a17dceda1ae6d215dc406cfe';

/// Fetches a single Workflow natively by ID

final class WorkflowByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Workflow>, String> {
  WorkflowByIdFamily._()
    : super(
        retry: null,
        name: r'workflowByIdProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches a single Workflow natively by ID

  WorkflowByIdProvider call(String id) =>
      WorkflowByIdProvider._(argument: id, from: this);

  @override
  String toString() => r'workflowByIdProvider';
}

/// Fetches a single Step natively by ID

@ProviderFor(stepById)
final stepByIdProvider = StepByIdFamily._();

/// Fetches a single Step natively by ID

final class StepByIdProvider
    extends
        $FunctionalProvider<
          AsyncValue<NodeStrategy>,
          NodeStrategy,
          FutureOr<NodeStrategy>
        >
    with $FutureModifier<NodeStrategy>, $FutureProvider<NodeStrategy> {
  /// Fetches a single Step natively by ID
  StepByIdProvider._({
    required StepByIdFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'stepByIdProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$stepByIdHash();

  @override
  String toString() {
    return r'stepByIdProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<NodeStrategy> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<NodeStrategy> create(Ref ref) {
    final argument = this.argument as String;
    return stepById(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is StepByIdProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$stepByIdHash() => r'c5aec2866dc6c4f483b43c2fa0cf163453346e50';

/// Fetches a single Step natively by ID

final class StepByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<NodeStrategy>, String> {
  StepByIdFamily._()
    : super(
        retry: null,
        name: r'stepByIdProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// Fetches a single Step natively by ID

  StepByIdProvider call(String id) =>
      StepByIdProvider._(argument: id, from: this);

  @override
  String toString() => r'stepByIdProvider';
}

@ProviderFor(WorkflowForm)
final workflowFormProvider = WorkflowFormFamily._();

final class WorkflowFormProvider
    extends $AsyncNotifierProvider<WorkflowForm, Workflow> {
  WorkflowFormProvider._({
    required WorkflowFormFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'workflowFormProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$workflowFormHash();

  @override
  String toString() {
    return r'workflowFormProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  WorkflowForm create() => WorkflowForm();

  @override
  bool operator ==(Object other) {
    return other is WorkflowFormProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$workflowFormHash() => r'2fa3d13eb7fa2b3a2e6150fdaf6322b711222942';

final class WorkflowFormFamily extends $Family
    with
        $ClassFamilyOverride<
          WorkflowForm,
          AsyncValue<Workflow>,
          Workflow,
          FutureOr<Workflow>,
          String
        > {
  WorkflowFormFamily._()
    : super(
        retry: null,
        name: r'workflowFormProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  WorkflowFormProvider call(String configId) =>
      WorkflowFormProvider._(argument: configId, from: this);

  @override
  String toString() => r'workflowFormProvider';
}

abstract class _$WorkflowForm extends $AsyncNotifier<Workflow> {
  late final _$args = ref.$arg as String;
  String get configId => _$args;

  FutureOr<Workflow> build(String configId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<Workflow>, Workflow>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<Workflow>, Workflow>,
              AsyncValue<Workflow>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}

@ProviderFor(StepForm)
final stepFormProvider = StepFormFamily._();

final class StepFormProvider
    extends $AsyncNotifierProvider<StepForm, NodeStrategy> {
  StepFormProvider._({
    required StepFormFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'stepFormProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$stepFormHash();

  @override
  String toString() {
    return r'stepFormProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  StepForm create() => StepForm();

  @override
  bool operator ==(Object other) {
    return other is StepFormProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$stepFormHash() => r'a191b3ab632b9a7c5db8eb2bf417769764b48067';

final class StepFormFamily extends $Family
    with
        $ClassFamilyOverride<
          StepForm,
          AsyncValue<NodeStrategy>,
          NodeStrategy,
          FutureOr<NodeStrategy>,
          String
        > {
  StepFormFamily._()
    : super(
        retry: null,
        name: r'stepFormProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  StepFormProvider call(String configId) =>
      StepFormProvider._(argument: configId, from: this);

  @override
  String toString() => r'stepFormProvider';
}

abstract class _$StepForm extends $AsyncNotifier<NodeStrategy> {
  late final _$args = ref.$arg as String;
  String get configId => _$args;

  FutureOr<NodeStrategy> build(String configId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<NodeStrategy>, NodeStrategy>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<NodeStrategy>, NodeStrategy>,
              AsyncValue<NodeStrategy>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}

/// Controller managing Studio Workflows (DAGs) strictly using `Workflow` mapped domain model.
/// Implements Optimistic UI principles where possible.

@ProviderFor(WorkflowsController)
final workflowsControllerProvider = WorkflowsControllerProvider._();

/// Controller managing Studio Workflows (DAGs) strictly using `Workflow` mapped domain model.
/// Implements Optimistic UI principles where possible.
final class WorkflowsControllerProvider
    extends $AsyncNotifierProvider<WorkflowsController, List<Workflow>> {
  /// Controller managing Studio Workflows (DAGs) strictly using `Workflow` mapped domain model.
  /// Implements Optimistic UI principles where possible.
  WorkflowsControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'workflowsControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$workflowsControllerHash();

  @$internal
  @override
  WorkflowsController create() => WorkflowsController();
}

String _$workflowsControllerHash() =>
    r'74f1283575487de0f148847c838447958506efbf';

/// Controller managing Studio Workflows (DAGs) strictly using `Workflow` mapped domain model.
/// Implements Optimistic UI principles where possible.

abstract class _$WorkflowsController extends $AsyncNotifier<List<Workflow>> {
  FutureOr<List<Workflow>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<List<Workflow>>, List<Workflow>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<Workflow>>, List<Workflow>>,
              AsyncValue<List<Workflow>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// Controller managing Studio Steps strictly using `NodeStrategy` mapping.
/// Implements Optimistic UI principles where possible.

@ProviderFor(StepsController)
final stepsControllerProvider = StepsControllerProvider._();

/// Controller managing Studio Steps strictly using `NodeStrategy` mapping.
/// Implements Optimistic UI principles where possible.
final class StepsControllerProvider
    extends $AsyncNotifierProvider<StepsController, List<NodeStrategy>> {
  /// Controller managing Studio Steps strictly using `NodeStrategy` mapping.
  /// Implements Optimistic UI principles where possible.
  StepsControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'stepsControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$stepsControllerHash();

  @$internal
  @override
  StepsController create() => StepsController();
}

String _$stepsControllerHash() => r'bac41a230d68c36191b4224ab0ce33a5c09f2435';

/// Controller managing Studio Steps strictly using `NodeStrategy` mapping.
/// Implements Optimistic UI principles where possible.

abstract class _$StepsController extends $AsyncNotifier<List<NodeStrategy>> {
  FutureOr<List<NodeStrategy>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref as $Ref<AsyncValue<List<NodeStrategy>>, List<NodeStrategy>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<NodeStrategy>>, List<NodeStrategy>>,
              AsyncValue<List<NodeStrategy>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
