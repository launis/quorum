import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:riverpod/riverpod.dart';

/// Observer to log Riverpod provider changes and errors.
final class AppLoggerObserver extends ProviderObserver {
  final LoggerService _logger;

  AppLoggerObserver(this._logger);

  @override
  void didAddProvider(ProviderObserverContext context, Object? value) {
    if (_shouldIgnore(context.provider)) return;
    _logger.debug(
      'RIVERPOD',
      'Initialized: ${context.provider.name ?? context.provider.runtimeType}',
    );
  }

  @override
  void didDisposeProvider(ProviderObserverContext context) {
    if (_shouldIgnore(context.provider)) return;
    _logger.debug(
      'RIVERPOD',
      'Disposed: ${context.provider.name ?? context.provider.runtimeType}',
    );
  }

  @override
  void didUpdateProvider(
    ProviderObserverContext context,
    Object? previousValue,
    Object? newValue,
  ) {
    if (_shouldIgnore(context.provider)) return;

    // Use AsyncValue check to avoid AsyncError type conflict/visibility issues
    if (newValue is AsyncValue) {
      final errorState = newValue.asError;
      if (errorState != null) {
        _logger.error(
          'RIVERPOD',
          'Provider Error [${context.provider.name ?? context.provider.runtimeType}]',
          errorState.error,
          errorState.stackTrace,
        );
      }
    }
  }

  @override
  void providerDidFail(
    ProviderObserverContext context,
    Object error,
    StackTrace stackTrace,
  ) {
    _logger.error(
      'RIVERPOD',
      'Provider Build Failed [${context.provider.name ?? context.provider.runtimeType}]',
      error,
      stackTrace,
    );
  }

  // Filter out internal or noisy providers if needed
  bool _shouldIgnore(Object? provider) {
    // If we need to check properties, strict type might be needed, but dynamic/Object prevents build error if type is hidden
    return false;
  }
}
