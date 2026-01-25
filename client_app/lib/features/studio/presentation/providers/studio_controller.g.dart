// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'studio_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Studio Controller**
///
/// Manages the state and logic for the Cognitive Studio.

@ProviderFor(StudioController)
final studioControllerProvider = StudioControllerProvider._();

/// **Studio Controller**
///
/// Manages the state and logic for the Cognitive Studio.
final class StudioControllerProvider
    extends $AsyncNotifierProvider<StudioController, void> {
  /// **Studio Controller**
  ///
  /// Manages the state and logic for the Cognitive Studio.
  StudioControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'studioControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$studioControllerHash();

  @$internal
  @override
  StudioController create() => StudioController();
}

String _$studioControllerHash() => r'8aeea6da8c057a9804646e2230d4206ed6bb19d6';

/// **Studio Controller**
///
/// Manages the state and logic for the Cognitive Studio.

abstract class _$StudioController extends $AsyncNotifier<void> {
  FutureOr<void> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<void>, void>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<void>, void>,
              AsyncValue<void>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
