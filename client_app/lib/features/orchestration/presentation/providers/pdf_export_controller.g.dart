// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pdf_export_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(PdfExportController)
final pdfExportControllerProvider = PdfExportControllerProvider._();

final class PdfExportControllerProvider
    extends $NotifierProvider<PdfExportController, AsyncValue<double>> {
  PdfExportControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'pdfExportControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$pdfExportControllerHash();

  @$internal
  @override
  PdfExportController create() => PdfExportController();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(AsyncValue<double> value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<AsyncValue<double>>(value),
    );
  }
}

String _$pdfExportControllerHash() =>
    r'7378d7a8b6c9582f61ec862c3b9becb309d5566a';

abstract class _$PdfExportController extends $Notifier<AsyncValue<double>> {
  AsyncValue<double> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<AsyncValue<double>, AsyncValue<double>>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<AsyncValue<double>, AsyncValue<double>>,
              AsyncValue<double>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
