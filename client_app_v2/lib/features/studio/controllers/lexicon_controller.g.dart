// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'lexicon_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(LexiconController)
final lexiconControllerProvider = LexiconControllerProvider._();

final class LexiconControllerProvider
    extends
        $AsyncNotifierProvider<
          LexiconController,
          SystemConfigPerformativeLexicons
        > {
  LexiconControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'lexiconControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$lexiconControllerHash();

  @$internal
  @override
  LexiconController create() => LexiconController();
}

String _$lexiconControllerHash() => r'2076ac9f566a6a96af4562426432135358d42d79';

abstract class _$LexiconController
    extends $AsyncNotifier<SystemConfigPerformativeLexicons> {
  FutureOr<SystemConfigPerformativeLexicons> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<SystemConfigPerformativeLexicons>,
              SystemConfigPerformativeLexicons
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<SystemConfigPerformativeLexicons>,
                SystemConfigPerformativeLexicons
              >,
              AsyncValue<SystemConfigPerformativeLexicons>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
