// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'studio_repository.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(studioRepository)
final studioRepositoryProvider = StudioRepositoryProvider._();

final class StudioRepositoryProvider
    extends
        $FunctionalProvider<
          StudioRepository,
          StudioRepository,
          StudioRepository
        >
    with $Provider<StudioRepository> {
  StudioRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'studioRepositoryProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$studioRepositoryHash();

  @$internal
  @override
  $ProviderElement<StudioRepository> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  StudioRepository create(Ref ref) {
    return studioRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(StudioRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<StudioRepository>(value),
    );
  }
}

String _$studioRepositoryHash() => r'4f3cb445d07794f7fa8ca56553f0391cba34baa3';
