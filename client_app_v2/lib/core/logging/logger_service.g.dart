// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'logger_service.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint, type=warning
/// Global Logger Provider (Singleton)

@ProviderFor(loggerService)
final loggerServiceProvider = LoggerServiceProvider._();

/// Global Logger Provider (Singleton)

final class LoggerServiceProvider
    extends $FunctionalProvider<LoggerService, LoggerService, LoggerService>
    with $Provider<LoggerService> {
  /// Global Logger Provider (Singleton)
  LoggerServiceProvider._()
    : super(
        from: null,
        argument: null,
        retry: null,
        name: r'loggerServiceProvider',
        isAutoDispose: true,
        dependencies: null,
        $allTransitiveDependencies: null,
      );

  @override
  String debugGetCreateSourceHash() => _$loggerServiceHash();

  @$internal
  @override
  $ProviderElement<LoggerService> $createElement($ProviderPointer pointer) =>
      $ProviderElement(pointer);

  @override
  LoggerService create(Ref ref) {
    return loggerService(ref);
  }

  /// {@macro riverpod.override_with_value}
  Override overrideWithValue(LoggerService value) {
    return $ProviderOverride(
      origin: this,
      providerOverride: $SyncValueProvider<LoggerService>(value),
    );
  }
}

String _$loggerServiceHash() => r'cc104855ec00db54237f00c80f82442b048c579c';
