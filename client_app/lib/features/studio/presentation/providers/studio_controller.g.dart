// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'studio_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(StudioController)
final studioControllerProvider = StudioControllerProvider._();

final class StudioControllerProvider
    extends $NotifierProvider<StudioController, StudioState> {
  StudioControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'studioControllerProvider',
        isAutoDispose: false,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$studioControllerHash();

  @$internal
  @override
  StudioController create() => StudioController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(StudioState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<StudioState>(value),
    );
  }
}

String _$studioControllerHash() => r'edca70c3c3b93d67fc20f42509982015f0d41a78';

abstract class _$StudioController extends $Notifier<StudioState> {
  StudioState build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<StudioState, StudioState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<StudioState, StudioState>,
              StudioState,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
