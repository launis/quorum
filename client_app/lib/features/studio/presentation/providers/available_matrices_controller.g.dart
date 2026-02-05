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
        $AsyncNotifierProvider<
          AvailableMatricesController,
          List<StudioComponentDef>
        > {
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
    r'8626cd687cc8797a3ba0f22c25a7170946498b82';

/// **Available Matrices Controller**
///
/// Manages the list of available Evaluation Matrices using the modern
/// "Optimistic Update + Silent Invalidation" pattern (Riverpod 3.0 Best Practice).

abstract class _$AvailableMatricesController
    extends $AsyncNotifier<List<StudioComponentDef>> {
  FutureOr<List<StudioComponentDef>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<List<StudioComponentDef>>,
              List<StudioComponentDef>
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<List<StudioComponentDef>>,
                List<StudioComponentDef>
              >,
              AsyncValue<List<StudioComponentDef>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
