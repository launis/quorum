// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'env.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// **Environment Configuration Service**
///
/// Manages environment-specific variables and configuration secrets.
/// This abstraction ensures the app is not hardcoded to specific URLs or keys,
/// facilitating movement between Dev and Production.
///
/// **Source**:
/// Loads values from the `.env` file via `flutter_dotenv`.
///
/// **Business Logic**:
/// - Enforces the Zero-Compromise Pledge (Fail-Fast) by requiring all variables
///   to be present in the `.env` file. No silent fallbacks exist.

@ProviderFor(env)
final envProvider = EnvProvider._();

/// **Environment Configuration Service**
///
/// Manages environment-specific variables and configuration secrets.
/// This abstraction ensures the app is not hardcoded to specific URLs or keys,
/// facilitating movement between Dev and Production.
///
/// **Source**:
/// Loads values from the `.env` file via `flutter_dotenv`.
///
/// **Business Logic**:
/// - Enforces the Zero-Compromise Pledge (Fail-Fast) by requiring all variables
///   to be present in the `.env` file. No silent fallbacks exist.

final class EnvProvider extends $FunctionalProvider<Env, Env, Env>
    with $Provider<Env> {
  /// **Environment Configuration Service**
  ///
  /// Manages environment-specific variables and configuration secrets.
  /// This abstraction ensures the app is not hardcoded to specific URLs or keys,
  /// facilitating movement between Dev and Production.
  ///
  /// **Source**:
  /// Loads values from the `.env` file via `flutter_dotenv`.
  ///
  /// **Business Logic**:
  /// - Enforces the Zero-Compromise Pledge (Fail-Fast) by requiring all variables
  ///   to be present in the `.env` file. No silent fallbacks exist.
  EnvProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'envProvider',
        isAutoDispose: false,
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

String _$envHash() => r'551c350d209c4d6d44be42789be84c4cf99fdc69';
