import 'package:client_app/core/logging/app_logger_observer.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

class _RecordingLoggerService implements LoggerService {
  final List<({String context, String message})> debugLogs = [];
  final List<({String context, String message})> infoLogs = [];
  final List<
    ({String context, String message, Object? error, StackTrace? stack})
  >
  warningLogs = [];
  final List<
    ({String context, String message, Object? error, StackTrace? stack})
  >
  errorLogs = [];

  @override
  Future<void> init() async {}

  @override
  void debug(String context, String message) {
    debugLogs.add((context: context, message: message));
  }

  @override
  void info(String context, String message) {
    infoLogs.add((context: context, message: message));
  }

  @override
  void warning(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {
    warningLogs.add((
      context: context,
      message: message,
      error: error,
      stack: stack,
    ));
  }

  @override
  void error(
    String context,
    String message, [
    Object? error,
    StackTrace? stack,
  ]) {
    errorLogs.add((
      context: context,
      message: message,
      error: error,
      stack: stack,
    ));
  }
}

class _TestAsyncNotifier extends AsyncNotifier<int> {
  @override
  Future<int> build() async => 1;

  void emitError(Object err, StackTrace st) {
    state = AsyncError<int>(err, st);
  }

  void emitData(int next) {
    state = AsyncData<int>(next);
  }
}

void main() {
  group('AppLoggerObserver Hardening Tests', () {
    test(
      'Positive: logs initialization and disposal for named providers without logging non-error updates',
      () async {
        final logger = _RecordingLoggerService();
        final observer = AppLoggerObserver(logger);
        final notifierProvider =
            AsyncNotifierProvider<_TestAsyncNotifier, int>(
              _TestAsyncNotifier.new,
              name: 'counterAsyncProvider',
            );

        final container = ProviderContainer(observers: [observer]);
        await container.read(notifierProvider.future);
        container.read(notifierProvider.notifier).emitData(42);
        container.dispose();

        expect(
          logger.debugLogs.map((e) => e.message),
          containsAll(<String>[
            'Initialized: counterAsyncProvider',
            'Disposed: counterAsyncProvider',
          ]),
        );
        expect(logger.errorLogs, isEmpty);
      },
    );

    test(
      'Negative/Boundary 1: logs AsyncError state updates and synchronous providerDidFail build crashes',
      () async {
        final logger = _RecordingLoggerService();
        final observer = AppLoggerObserver(logger);

        final notifierProvider =
            AsyncNotifierProvider<_TestAsyncNotifier, int>(
              _TestAsyncNotifier.new,
              name: 'faultyAsyncProvider',
            );
        final crashingSyncProvider = Provider<int>((ref) {
          throw StateError('Fail-Fast synchronous provider build failure');
        }, name: 'crashingSyncProvider');

        final container = ProviderContainer(observers: [observer]);
        addTearDown(container.dispose);

        await container.read(notifierProvider.future);
        final customStack = StackTrace.current;
        container
            .read(notifierProvider.notifier)
            .emitError(ArgumentError('Invalid state transition'), customStack);

        expect(
          () => container.read(crashingSyncProvider),
          throwsA(anything),
        );

        expect(logger.errorLogs, hasLength(3));
        expect(
          logger.errorLogs[0].message,
          equals('Provider Error [faultyAsyncProvider]'),
        );
        expect(logger.errorLogs[0].error, isA<ArgumentError>());
        expect(
          logger.errorLogs[1].message,
          equals('Provider Build Failed [faultyAsyncProvider]'),
        );
        expect(logger.errorLogs[1].error, isA<ArgumentError>());
        expect(
          logger.errorLogs[2].message,
          equals('Provider Build Failed [crashingSyncProvider]'),
        );
        expect(logger.errorLogs[2].error, isA<StateError>());
      },
    );

    test(
      'Negative/Boundary 2: respects ignoredProviderNames set and falls back to runtimeType when name is null or empty',
      () {
        final logger = _RecordingLoggerService();
        final observer = AppLoggerObserver(
          logger,
          ignoredProviderNames: const <String>{'noisyTelemetryProvider'},
        );

        final ignoredProvider = Provider<int>(
          (ref) => 10,
          name: 'noisyTelemetryProvider',
        );
        final unnamedProvider = Provider<String>((ref) => 'anonymous');
        final emptyNameProvider = Provider<String>(
          (ref) => 'empty-name',
          name: '',
        );

        final container = ProviderContainer(observers: [observer]);
        expect(container.read(ignoredProvider), equals(10));
        expect(container.read(unnamedProvider), equals('anonymous'));
        expect(container.read(emptyNameProvider), equals('empty-name'));
        container.dispose();

        expect(
          logger.debugLogs.where(
            (entry) => entry.message.contains('noisyTelemetryProvider'),
          ),
          isEmpty,
        );
        expect(
          logger.debugLogs.where(
            (entry) => entry.message.startsWith('Initialized: Provider<String>'),
          ),
          hasLength(2),
        );
      },
    );
  });
}
