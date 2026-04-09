// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'blueprint_editor_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Blueprint Editor Controller (Phase 9 Rebuild)**
///
/// Stripped of the massive SDUI canvas logic. Now strictly manages the
/// `BlueprintConfig` ensuring seamless binding with Pydantic V2 schemas.

@ProviderFor(BlueprintEditorController)
final blueprintEditorControllerProvider = BlueprintEditorControllerProvider._();

/// **Blueprint Editor Controller (Phase 9 Rebuild)**
///
/// Stripped of the massive SDUI canvas logic. Now strictly manages the
/// `BlueprintConfig` ensuring seamless binding with Pydantic V2 schemas.
final class BlueprintEditorControllerProvider
    extends $NotifierProvider<BlueprintEditorController, BlueprintConfig> {
  /// **Blueprint Editor Controller (Phase 9 Rebuild)**
  ///
  /// Stripped of the massive SDUI canvas logic. Now strictly manages the
  /// `BlueprintConfig` ensuring seamless binding with Pydantic V2 schemas.
  BlueprintEditorControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'blueprintEditorControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$blueprintEditorControllerHash();

  @$internal
  @override
  BlueprintEditorController create() => BlueprintEditorController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(BlueprintConfig value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<BlueprintConfig>(value),
    );
  }
}

String _$blueprintEditorControllerHash() =>
    r'b7b4fb1ae6ecbf92791fd9a52ae9e078d076a82a';

/// **Blueprint Editor Controller (Phase 9 Rebuild)**
///
/// Stripped of the massive SDUI canvas logic. Now strictly manages the
/// `BlueprintConfig` ensuring seamless binding with Pydantic V2 schemas.

abstract class _$BlueprintEditorController extends $Notifier<BlueprintConfig> {
  BlueprintConfig build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<BlueprintConfig, BlueprintConfig>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<BlueprintConfig, BlueprintConfig>,
              BlueprintConfig,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
