// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'schema_repository.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning

@ProviderFor(schemaRepository)
final schemaRepositoryProvider = SchemaRepositoryProvider._();

final class SchemaRepositoryProvider
    extends
        $FunctionalProvider<
          SchemaRepository,
          SchemaRepository,
          SchemaRepository
        >
    with $Provider<SchemaRepository> {
  SchemaRepositoryProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'schemaRepositoryProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$schemaRepositoryHash();

  @$internal
  @override
  $ProviderElement<SchemaRepository> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  SchemaRepository create(Ref ref) {
    return schemaRepository(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(SchemaRepository value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<SchemaRepository>(value),
    );
  }
}

String _$schemaRepositoryHash() => r'72e93f373a4a7fbec50c6038d46d48b3e66eb90b';
