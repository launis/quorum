// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'blueprint_editor_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Manages [BlueprintConfig] state for the Studio Blueprint Editor,
/// enforcing strict schema binding with backend Pydantic V2 models.

@ProviderFor(BlueprintEditorController)
final blueprintEditorControllerProvider = BlueprintEditorControllerProvider._();

/// Manages [BlueprintConfig] state for the Studio Blueprint Editor,
/// enforcing strict schema binding with backend Pydantic V2 models.
final class BlueprintEditorControllerProvider
    extends $NotifierProvider<BlueprintEditorController, BlueprintConfig> {
  /// Manages [BlueprintConfig] state for the Studio Blueprint Editor,
  /// enforcing strict schema binding with backend Pydantic V2 models.
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
    r'1c03eec993518b4b7ac8b363a0b8ce9cda788f4d';

/// Manages [BlueprintConfig] state for the Studio Blueprint Editor,
/// enforcing strict schema binding with backend Pydantic V2 models.

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
