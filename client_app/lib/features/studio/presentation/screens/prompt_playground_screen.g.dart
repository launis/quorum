// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prompt_playground_screen.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Playground Controller**

@ProviderFor(PlaygroundController)
final playgroundControllerProvider = PlaygroundControllerProvider._();

/// **Playground Controller**
final class PlaygroundControllerProvider
    extends $NotifierProvider<PlaygroundController, PlaygroundState> {
  /// **Playground Controller**
  PlaygroundControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'playgroundControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$playgroundControllerHash();

  @$internal
  @override
  PlaygroundController create() => PlaygroundController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(PlaygroundState value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<PlaygroundState>(value),
    );
  }
}

String _$playgroundControllerHash() =>
    r'b3fe0b8656bb70af2afdd008bee09b60d344c738';

/// **Playground Controller**

abstract class _$PlaygroundController extends $Notifier<PlaygroundState> {
  PlaygroundState build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<PlaygroundState, PlaygroundState>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<PlaygroundState, PlaygroundState>,
              PlaygroundState,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
