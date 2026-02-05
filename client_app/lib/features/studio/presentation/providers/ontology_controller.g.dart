// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'ontology_controller.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(OntologyController)
final ontologyControllerProvider = OntologyControllerProvider._();

final class OntologyControllerProvider
    extends
        $AsyncNotifierProvider<OntologyController, List<OntologyDimension>> {
  OntologyControllerProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'ontologyControllerProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$ontologyControllerHash();

  @$internal
  @override
  OntologyController create() => OntologyController();
}

String _$ontologyControllerHash() =>
    r'cac8b5518a98bfc041cfa459b755d725112a13bf';

abstract class _$OntologyController
    extends $AsyncNotifier<List<OntologyDimension>> {
  FutureOr<List<OntologyDimension>> build();
  @$mustCallSuper
  @override
  void runBuild() {
    final ref =
        this.ref
            as $Ref<
              AsyncValue<List<OntologyDimension>>,
              List<OntologyDimension>
            >;
    final element =
        ref.element
            as $ClassProviderElement<
              AnyNotifier<
                AsyncValue<List<OntologyDimension>>,
                List<OntologyDimension>
              >,
              AsyncValue<List<OntologyDimension>>,
              Object?,
              Object?
            >;
    element.handleCreate(ref, build);
  }
}
