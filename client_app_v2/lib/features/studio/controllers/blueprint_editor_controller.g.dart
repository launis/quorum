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
/// `output_mapping` dictionary ensuring seamless binding with Pydantic V2 schemas.

@ProviderFor(BlueprintEditorController)
final blueprintEditorControllerProvider = BlueprintEditorControllerProvider._();

/// **Blueprint Editor Controller (Phase 9 Rebuild)**
///
/// Stripped of the massive SDUI canvas logic. Now strictly manages the
/// `output_mapping` dictionary ensuring seamless binding with Pydantic V2 schemas.
final class BlueprintEditorControllerProvider
    extends $NotifierProvider<BlueprintEditorController, Map<String, dynamic>> {
  /// **Blueprint Editor Controller (Phase 9 Rebuild)**
  ///
  /// Stripped of the massive SDUI canvas logic. Now strictly manages the
  /// `output_mapping` dictionary ensuring seamless binding with Pydantic V2 schemas.
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
  Override overrideWithValue(Map<String, dynamic> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<Map<String, dynamic>>(value),
    );
  }
}

String _$blueprintEditorControllerHash() =>
    r'fb98049241913677d29f98aae1f8205c5b10be79';

/// **Blueprint Editor Controller (Phase 9 Rebuild)**
///
/// Stripped of the massive SDUI canvas logic. Now strictly manages the
/// `output_mapping` dictionary ensuring seamless binding with Pydantic V2 schemas.

abstract class _$BlueprintEditorController
    extends $Notifier<Map<String, dynamic>> {
  Map<String, dynamic> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<Map<String, dynamic>, Map<String, dynamic>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<Map<String, dynamic>, Map<String, dynamic>>,
              Map<String, dynamic>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
