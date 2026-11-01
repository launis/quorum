import 'dart:convert';
import 'dart:io';

import 'package:client_app/core/logging/logger_service.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:logger/logger.dart' hide FileOutput;

class _MemoryLogOutput extends LogOutput {
  final List<String> lines = <String>[];

  @override
  void output(OutputEvent event) {
    lines.addAll(event.lines);
  }
}

class _CapturingInterceptor extends Interceptor {
  RequestOptions? lastOptions;
  bool shouldFail = false;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    lastOptions = options;
    if (shouldFail) {
      handler.reject(
        DioException(
          requestOptions: options,
          error: 'Simulated telemetry network failure',
        ),
      );
      return;
    }
    handler.resolve(
      Response(
        requestOptions: options,
        statusCode: 200,
        data: <String, Object?>{'status': 'ok'},
      ),
    );
  }
}

void main() {
  group('LoggerService & Printers ISTQB Suite', () {
    test(
      'Positive: CustomPrinter formats standard log event with error and stackTrace',
      () {
        final printer = CustomPrinter();
        final trace = StackTrace.fromString('#0 main (test.dart:1:1)');
        final event = LogEvent(
          Level.warning,
          '[AUTH] | client | Token refresh near expiry',
          time: DateTime.utc(2026, 10, 31, 12, 30, 45),
          error: StateError('Expired'),
          stackTrace: trace,
        );

        final output = printer.log(event);
        expect(output.length, 3);
        expect(
          output[0],
          contains('WARNING | [AUTH] | client | Token refresh near expiry'),
        );
        expect(output[1], 'ERROR: Bad state: Expired');
        expect(output[2], contains('#0 main'));
      },
    );

    test(
      'Positive: JsonPrinter extracts structured context_id and strips prefix',
      () {
        final printer = JsonPrinter();
        final event = LogEvent(
          Level.info,
          '[exe_0195f000000070008000000000000001] | client | Execution started',
          error: 'Minor warning',
        );

        final lines = printer.log(event);
        expect(lines.length, 1);

        final decoded = jsonDecode(lines.first) as Map<String, Object?>;
        expect(decoded['level'], 'INFO');
        expect(decoded['logger'], 'client');
        expect(decoded['context_id'], 'exe_0195f000000070008000000000000001');
        expect(decoded['execution_id'], 'exe_0195f000000070008000000000000001');
        expect(decoded['message'], 'Execution started');
        expect(decoded['error'], 'Minor warning');
      },
    );

    test(
      'Negative / Boundary 1: JsonPrinter handles malformed unprefixed message and empty context brackets',
      () {
        final printer = JsonPrinter();
        final unprefixedEvent = LogEvent(
          Level.error,
          'Raw unformatted message',
        );
        final unprefixedDecoded =
            jsonDecode(printer.log(unprefixedEvent).first)
                as Map<String, Object?>;

        expect(unprefixedDecoded['context_id'], 'UNKNOWN');
        expect(unprefixedDecoded['message'], 'Raw unformatted message');

        final emptyBracketEvent = LogEvent(
          Level.debug,
          '[] | client | Missing context identifier',
        );
        final emptyBracketDecoded =
            jsonDecode(printer.log(emptyBracketEvent).first)
                as Map<String, Object?>;

        expect(emptyBracketDecoded['context_id'], 'UNKNOWN');
        expect(
          emptyBracketDecoded['message'],
          '[] | client | Missing context identifier',
        );
      },
    );

    test(
      'Negative / Boundary 2: LoggerService.error gracefully absorbs telemetry network failure without throwing',
      () async {
        final interceptor = _CapturingInterceptor()..shouldFail = true;
        final dio = Dio(BaseOptions(baseUrl: 'https://telemetry.invalid'))
          ..interceptors.add(interceptor);
        final memoryOutput = _MemoryLogOutput();
        final customLogger = Logger(
          printer: CustomPrinter(),
          output: memoryOutput,
          filter: ProductionFilter(),
          level: Level.all,
        );

        final service = LoggerService(telemetryDio: dio, logger: customLogger);
        service.error(
          'NETWORK',
          'Connection dropped',
          Exception('Socket closed'),
          StackTrace.current,
        );

        await Future<void>.delayed(const Duration(milliseconds: 20));

        expect(memoryOutput.lines, isNotEmpty);
        expect(
          memoryOutput.lines.first,
          contains('[NETWORK] | client | Connection dropped'),
        );
        expect(interceptor.lastOptions, isNotNull);
        expect(
          interceptor.lastOptions!.path,
          contains('/api/v2/system/telemetry/client-error'),
        );
      },
    );

    test(
      'Negative / Boundary 3: FileOutput handles empty OutputEvent and writes non-empty lines to temp file',
      () {
        final tempDir = Directory.systemTemp.createTempSync('logger_test_');
        addTearDown(() {
          if (tempDir.existsSync()) {
            tempDir.deleteSync(recursive: true);
          }
        });

        final logFile = File('${tempDir.path}/test.log');
        final fileOutput = FileOutput(logFile);

        final emptyEvent = OutputEvent(
          LogEvent(Level.info, 'ignored'),
          const <String>[],
        );
        fileOutput.output(emptyEvent);
        expect(logFile.existsSync(), isFalse);

        final populatedEvent = OutputEvent(
          LogEvent(Level.info, 'written'),
          const <String>['line 1', 'line 2'],
        );
        fileOutput.output(populatedEvent);
        expect(logFile.existsSync(), isTrue);
        expect(logFile.readAsStringSync(), 'line 1\nline 2\n');
      },
    );

    test(
      'Provider: loggerServiceProvider instantiates singleton LoggerService',
      () {
        final container = ProviderContainer();
        addTearDown(container.dispose);

        final first = container.read(loggerServiceProvider);
        final second = container.read(loggerServiceProvider);
        expect(identical(first, second), isTrue);
      },
    );
  });
}
