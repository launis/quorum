// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'available_matrices_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Available Matrices Controller**
///
/// Manages the list of available Evaluation Matrices using the modern
/// "Optimistic Update + Silent Invalidation" pattern (Riverpod 3.0 Best Practice).

@ProviderFor(AvailableMatricesController)
final availableMatricesControllerProvider =
    AvailableMatricesControllerProvider._();

/// **Available Matrices Controller**
///
/// Manages the list of available Evaluation Matrices using the modern
/// "Optimistic Update + Silent Invalidation" pattern (Riverpod 3.0 Best Practice).
final class AvailableMatricesControllerProvider
    extends
        $AsyncNotifierProvider<AvailableMatricesController, List<MatrixDef>> {
  /// **Available Matrices Controller**
  ///
  /// Manages the list of available Evaluation Matrices using the modern
  /// "Optimistic Update + Silent Invalidation" pattern (Riverpod 3.0 Best Practice).
  AvailableMatricesControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'availableMatricesControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$availableMatricesControllerHash();

  @$internal
  @override
  AvailableMatricesController create() => AvailableMatricesController();
}

String _$availableMatricesControllerHash() =>
    r'f91806aed21465eaf3438d12aef69fca4a938dfd';

/// **Available Matrices Controller**
///
/// Manages the list of available Evaluation Matrices using the modern
/// "Optimistic Update + Silent Invalidation" pattern (Riverpod 3.0 Best Practice).

abstract class _$AvailableMatricesController
    extends $AsyncNotifier<List<MatrixDef>> {
  FutureOr<List<MatrixDef>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<List<MatrixDef>>, List<MatrixDef>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<List<MatrixDef>>, List<MatrixDef>>,
              AsyncValue<List<MatrixDef>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
