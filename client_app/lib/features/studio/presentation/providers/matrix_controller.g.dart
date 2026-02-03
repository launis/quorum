// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'matrix_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Holds the scratchpad/unsaved changes of the currently active matrix.

@ProviderFor(MatrixEditorState)
final matrixEditorStateProvider = MatrixEditorStateProvider._();

/// Holds the scratchpad/unsaved changes of the currently active matrix.
final class MatrixEditorStateProvider
    extends $NotifierProvider<MatrixEditorState, MatrixDef?> {
  /// Holds the scratchpad/unsaved changes of the currently active matrix.
  MatrixEditorStateProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'matrixEditorStateProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$matrixEditorStateHash();

  @$internal
  @override
  MatrixEditorState create() => MatrixEditorState();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(MatrixDef? value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<MatrixDef?>(value),
    );
  }
}

String _$matrixEditorStateHash() => r'96dc8c580ada72c7bf07d61653fc09a513f44469';

/// Holds the scratchpad/unsaved changes of the currently active matrix.

abstract class _$MatrixEditorState extends $Notifier<MatrixDef?> {
  MatrixDef? build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<MatrixDef?, MatrixDef?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<MatrixDef?, MatrixDef?>,
              MatrixDef?,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}

/// Manages the lifecycle and persistence of the current matrix.

@ProviderFor(MatrixController)
final matrixControllerProvider = MatrixControllerProvider._();

/// Manages the lifecycle and persistence of the current matrix.
final class MatrixControllerProvider
    extends $AsyncNotifierProvider<MatrixController, MatrixDef?> {
  /// Manages the lifecycle and persistence of the current matrix.
  MatrixControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'matrixControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$matrixControllerHash();

  @$internal
  @override
  MatrixController create() => MatrixController();
}

String _$matrixControllerHash() => r'9c589320166d118a704752809c4f1bf5fc0b71c3';

/// Manages the lifecycle and persistence of the current matrix.

abstract class _$MatrixController extends $AsyncNotifier<MatrixDef?> {
  FutureOr<MatrixDef?> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<MatrixDef?>, MatrixDef?>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<MatrixDef?>, MatrixDef?>,
              AsyncValue<MatrixDef?>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
