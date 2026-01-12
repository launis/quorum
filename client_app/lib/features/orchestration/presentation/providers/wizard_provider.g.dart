// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'wizard_provider.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(WizardState)
final wizardStateProvider = WizardStateProvider._();

final class WizardStateProvider
    extends $NotifierProvider<WizardState, WizardStateModel> {
  WizardStateProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'wizardStateProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$wizardStateHash();

  @$internal
  @override
  WizardState create() => WizardState();

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(WizardStateModel value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<WizardStateModel>(value),
    );
  }
}

String _$wizardStateHash() => r'aff567897bda8608554d3b819f0fa3c489c90bb1';

abstract class _$WizardState extends $Notifier<WizardStateModel> {
  WizardStateModel build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref = this.ref as $Ref<WizardStateModel, WizardStateModel>;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<WizardStateModel, WizardStateModel>,
              WizardStateModel,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
