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
        $FunctionalProvider<
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>
        >
    with
        $FutureModifier<Map<String, dynamic>>,
        $FutureProvider<Map<String, dynamic>> {
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
  $FutureProviderElement<Map<String, dynamic>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<Map<String, dynamic>> create(Ref ref) {
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

String _$workflowByIdHash() => r'c1b21cb0785f253930d2e7c49c117e019ff28cd1';

/// Fetches a single Workflow natively by ID

final class WorkflowByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Map<String, dynamic>>, String> {
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
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>
        >
    with
        $FutureModifier<Map<String, dynamic>>,
        $FutureProvider<Map<String, dynamic>> {
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
  $FutureProviderElement<Map<String, dynamic>> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<Map<String, dynamic>> create(Ref ref) {
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

String _$stepByIdHash() => r'ba68aa75b311796ebf0df31bd4115f828b4babb2';

/// Fetches a single Step natively by ID

final class StepByIdFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<Map<String, dynamic>>, String> {
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
    extends $AsyncNotifierProvider<WorkflowForm, Map<String, dynamic>> {
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

String _$workflowFormHash() => r'd27ab5150bec47d3bba53b013551bfe4440ac5fa';

final class WorkflowFormFamily extends $Family
    with
        $ClassFamilyOverride<
          WorkflowForm,
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>,
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

abstract class _$WorkflowForm extends $AsyncNotifier<Map<String, dynamic>> {
  late final _$args = ref.$arg as String;
  String get configId => _$args;

  FutureOr<Map<String, dynamic>> build(String configId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<AsyncValue<Map<String, dynamic>>, Map<String, dynamic>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<Map<String, dynamic>>,
                Map<String, dynamic>
              >,
              AsyncValue<Map<String, dynamic>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}

@ProviderFor(StepForm)
final stepFormProvider = StepFormFamily._();

final class StepFormProvider
    extends $AsyncNotifierProvider<StepForm, Map<String, dynamic>> {
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

String _$stepFormHash() => r'a29bc4aff6d97a0e3649e5c106c4082654f79471';

final class StepFormFamily extends $Family
    with
        $ClassFamilyOverride<
          StepForm,
          AsyncValue<Map<String, dynamic>>,
          Map<String, dynamic>,
          FutureOr<Map<String, dynamic>>,
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

abstract class _$StepForm extends $AsyncNotifier<Map<String, dynamic>> {
  late final _$args = ref.$arg as String;
  String get configId => _$args;

  FutureOr<Map<String, dynamic>> build(String configId);
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<AsyncValue<Map<String, dynamic>>, Map<String, dynamic>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<Map<String, dynamic>>,
                Map<String, dynamic>
              >,
              AsyncValue<Map<String, dynamic>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, () => build(_$args));
  }
}

/// Controller managing Studio Workflows (DAGs) strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

@ProviderFor(WorkflowsController)
final workflowsControllerProvider = WorkflowsControllerProvider._();

/// Controller managing Studio Workflows (DAGs) strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
final class WorkflowsControllerProvider
    extends
        $AsyncNotifierProvider<
          WorkflowsController,
          List<Map<String, dynamic>>
        > {
  /// Controller managing Studio Workflows (DAGs) strictly using `Map<String, dynamic>`.
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
    r'02331f770c2480276c64a20551c62bbd6d4002ac';

/// Controller managing Studio Workflows (DAGs) strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

abstract class _$WorkflowsController
    extends $AsyncNotifier<List<Map<String, dynamic>>> {
  FutureOr<List<Map<String, dynamic>>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<List<Map<String, dynamic>>>,
              List<Map<String, dynamic>>
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<List<Map<String, dynamic>>>,
                List<Map<String, dynamic>>
              >,
              AsyncValue<List<Map<String, dynamic>>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// Controller managing Studio Steps strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

@ProviderFor(StepsController)
final stepsControllerProvider = StepsControllerProvider._();

/// Controller managing Studio Steps strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.
final class StepsControllerProvider
    extends
        $AsyncNotifierProvider<StepsController, List<Map<String, dynamic>>> {
  /// Controller managing Studio Steps strictly using `Map<String, dynamic>`.
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

String _$stepsControllerHash() => r'bc4dea24ddb5b5948fe0c4d9a8d1add61a86796f';

/// Controller managing Studio Steps strictly using `Map<String, dynamic>`.
/// Implements Optimistic UI principles where possible.

abstract class _$StepsController
    extends $AsyncNotifier<List<Map<String, dynamic>>> {
  FutureOr<List<Map<String, dynamic>>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<List<Map<String, dynamic>>>,
              List<Map<String, dynamic>>
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<List<Map<String, dynamic>>>,
                List<Map<String, dynamic>>
              >,
              AsyncValue<List<Map<String, dynamic>>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
