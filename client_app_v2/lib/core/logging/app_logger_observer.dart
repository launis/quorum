import 'package:client_app/core/logging/logger_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Observer that records Riverpod provider lifecycle transitions and errors.
final class AppLoggerObserver extends ProviderObserver {
  final LoggerService _logger;
  final Set<String> _ignoredProviderNames;

  AppLoggerObserver(
    this._logger, {
    Set<String> ignoredProviderNames = const <String>{},
  }) : _ignoredProviderNames = ignoredProviderNames;

  @override
  void didAddProvider(ProviderObserverContext context, Object? value) {
    if (_shouldIgnore(context)) return;
    _logger.debug('RIVERPOD', 'Initialized: ${_resolveProviderLabel(context)}');
  }

  @override
  void didDisposeProvider(ProviderObserverContext context) {
    if (_shouldIgnore(context)) return;
    _logger.debug('RIVERPOD', 'Disposed: ${_resolveProviderLabel(context)}');
  }

  @override
  void didUpdateProvider(
    ProviderObserverContext context,
    Object? previousValue,
    Object? newValue,
  ) {
    if (_shouldIgnore(context)) return;

    switch (newValue) {
      case AsyncError(:final error, :final stackTrace):
        _logger.error(
          'RIVERPOD',
          'Provider Error [${_resolveProviderLabel(context)}]',
          error,
          stackTrace,
        );
      case AsyncData():
      case AsyncLoading():
      default:
        break;
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
      'Provider Build Failed [${_resolveProviderLabel(context)}]',
      error,
      stackTrace,
    );
  }

  String _resolveProviderLabel(ProviderObserverContext context) {
    final name = context.provider.name;
    if (name != null && name.isNotEmpty) {
      return name;
    }
    return context.provider.runtimeType.toString();
  }

  bool _shouldIgnore(ProviderObserverContext context) {
    final name = context.provider.name;
    return name != null && _ignoredProviderNames.contains(name);
  }
}
