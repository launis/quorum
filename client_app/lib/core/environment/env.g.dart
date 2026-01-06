// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'env.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Environment Provider**
///
/// Exposes the [Env] configuration properties to the Riverpod dependency graph.
/// Although [Env] properties are static, this provider allows mocking or overriding
/// configuration for testing purposes.

@ProviderFor(env)
final envProvider = EnvProvider._();

/// **Environment Provider**
///
/// Exposes the [Env] configuration properties to the Riverpod dependency graph.
/// Although [Env] properties are static, this provider allows mocking or overriding
/// configuration for testing purposes.

final class EnvProvider extends $FunctionalProvider<Env, Env, Env>
    with $Provider<Env> {
  /// **Environment Provider**
  ///
  /// Exposes the [Env] configuration properties to the Riverpod dependency graph.
  /// Although [Env] properties are static, this provider allows mocking or overriding
  /// configuration for testing purposes.
  EnvProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'envProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$envHash();

  @$internal
  @override
  $ProviderElement<Env> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  Env create(Ref ref) {
    return env(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(Env value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<Env>(value),
    );
  }
}

String _$envHash() => r'a665c523416853586d601e8a69a8caacb7b65fec';
