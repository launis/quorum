// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'blueprint_editor_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Blueprint Editor Controller**
///
/// Manages the state of the active `render_blueprint` being edited in the GUI.
/// Strictly uses `Map<String, dynamic>` to adhere to the De-Generator Policy,
/// allowing Zero-Deploy UI structure updates.

@ProviderFor(BlueprintEditorController)
final blueprintEditorControllerProvider = BlueprintEditorControllerProvider._();

/// **Blueprint Editor Controller**
///
/// Manages the state of the active `render_blueprint` being edited in the GUI.
/// Strictly uses `Map<String, dynamic>` to adhere to the De-Generator Policy,
/// allowing Zero-Deploy UI structure updates.
final class BlueprintEditorControllerProvider
    extends $NotifierProvider<BlueprintEditorController, Map<String, dynamic>> {
  /// **Blueprint Editor Controller**
  ///
  /// Manages the state of the active `render_blueprint` being edited in the GUI.
  /// Strictly uses `Map<String, dynamic>` to adhere to the De-Generator Policy,
  /// allowing Zero-Deploy UI structure updates.
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
    r'a69a77a9cfe4b90ccbfce28bbe52408910ecdf82';

/// **Blueprint Editor Controller**
///
/// Manages the state of the active `render_blueprint` being edited in the GUI.
/// Strictly uses `Map<String, dynamic>` to adhere to the De-Generator Policy,
/// allowing Zero-Deploy UI structure updates.

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
