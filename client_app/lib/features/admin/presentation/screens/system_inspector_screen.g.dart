// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'system_inspector_screen.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Step Preview Provider**
///
/// Fetches the preview for a single step.

@ProviderFor(stepPreview)
final stepPreviewProvider = StepPreviewFamily._();

/// **Step Preview Provider**
///
/// Fetches the preview for a single step.

final class StepPreviewProvider
    extends
        $FunctionalProvider<
          AsyncValue<SystemPreview>,
          SystemPreview,
          FutureOr<SystemPreview>
        >
    with $FutureModifier<SystemPreview>, $FutureProvider<SystemPreview> {
  /// **Step Preview Provider**
  ///
  /// Fetches the preview for a single step.
  StepPreviewProvider._({
    required StepPreviewFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'stepPreviewProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$stepPreviewHash();

  @override
  String toString() {
    return r'stepPreviewProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<SystemPreview> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<SystemPreview> create(Ref ref) {
    final argument = this.argument as String;
    return stepPreview(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is StepPreviewProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$stepPreviewHash() => r'567a1b297f1cc98d79e200734944b9cbb1df5a38';

/// **Step Preview Provider**
///
/// Fetches the preview for a single step.

final class StepPreviewFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<SystemPreview>, String> {
  StepPreviewFamily._()
    : super(
        retry: null,
        name: r'stepPreviewProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// **Step Preview Provider**
  ///
  /// Fetches the preview for a single step.

  StepPreviewProvider call(String stepId) =>
      StepPreviewProvider._(argument: stepId, from: this);

  @override
  String toString() => r'stepPreviewProvider';
}

/// **Chain Preview Provider**
///
/// Fetches the full chain preview for a workflow.

@ProviderFor(chainPreview)
final chainPreviewProvider = ChainPreviewFamily._();

/// **Chain Preview Provider**
///
/// Fetches the full chain preview for a workflow.

final class ChainPreviewProvider
    extends
        $FunctionalProvider<
          AsyncValue<ChainPreview>,
          ChainPreview,
          FutureOr<ChainPreview>
        >
    with $FutureModifier<ChainPreview>, $FutureProvider<ChainPreview> {
  /// **Chain Preview Provider**
  ///
  /// Fetches the full chain preview for a workflow.
  ChainPreviewProvider._({
    required ChainPreviewFamily super.from,
    required String super.argument,
  }) : super(
         retry: null,
         name: r'chainPreviewProvider',
         isAutoDispose: true,
         dependencies: null,
         $allTransitiveDependencies: null,
       );

  @override
  String debugGetCreateSourceHash() => _$chainPreviewHash();

  @override
  String toString() {
    return r'chainPreviewProvider'
        ''
        '($argument)';
  }

  @$internal
  @override
  $FutureProviderElement<ChainPreview> $createElement(
    $ProviderPointer pointer,
  ) => $FutureProviderElement(pointer);

  @override
  FutureOr<ChainPreview> create(Ref ref) {
    final argument = this.argument as String;
    return chainPreview(ref, argument);
  }

  @override
  bool operator ==(Object other) {
    return other is ChainPreviewProvider && other.argument == argument;
  }

  @override
  int get hashCode {
    return argument.hashCode;
  }
}

String _$chainPreviewHash() => r'494e438a47c577870cfedbfe29ec3ade6972f29b';

/// **Chain Preview Provider**
///
/// Fetches the full chain preview for a workflow.

final class ChainPreviewFamily extends $Family
    with $FunctionalFamilyOverride<FutureOr<ChainPreview>, String> {
  ChainPreviewFamily._()
    : super(
        retry: null,
        name: r'chainPreviewProvider',
        dependencies: null,
        $allTransitiveDependencies: null,
        isAutoDispose: true,
      );

  /// **Chain Preview Provider**
  ///
  /// Fetches the full chain preview for a workflow.

  ChainPreviewProvider call(String workflowId) =>
      ChainPreviewProvider._(argument: workflowId, from: this);

  @override
  String toString() => r'chainPreviewProvider';
}
