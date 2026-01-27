import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:intl/intl.dart';
import 'package:logger/logger.dart';
import 'package:path_provider/path_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Global Logger Provider (Singleton)
final loggerServiceProvider = Provider<LoggerService>((ref) {
  return LoggerService();
});

class LoggerService {
  late Logger _logger;
  File? _logFile;

  LoggerService() {
    // Initialize with buffer and console output
    _logger = Logger(
      printer: CustomPrinter(),
      output: ConsoleOutput(),
      filter: ProductionFilter(),
    );
    _initFileLogging();
  }

  Future<void> _initFileLogging() async {
    if (kIsWeb) return;

    try {
      // Use CWD (root) -> Parent for shared visibility
      final file = File('../client_debug.log');
      _logFile = file;
      
      // Re-initialize 
      _logger = Logger(
        filter: ProductionFilter(),
        printer: CustomPrinter(),
        output: MultiOutput([
          ConsoleOutput(),
          FileOutput(file),
        ]),
      );
      
      info('SYSTEM', 'Logging initialized. Writing to: ${file.absolute.path}');
    } catch (e) {
      debugPrint("Failed to initialize file logging: $e");
    }
  }

  void debug(String context, String message) => _logger.d('[$context] | $message');
  void info(String context, String message) => _logger.i('[$context] | $message');
  void warning(String context, String message, [Object? error, StackTrace? stack]) => 
      _logger.w('[$context] | $message', error: error, stackTrace: stack);
  void error(String context, String message, [Object? error, StackTrace? stack]) => 
      _logger.e('[$context] | $message', error: error, stackTrace: stack);
}

// --- Custom Components ---

class CustomPrinter extends LogPrinter {
  final DateFormat _formatter = DateFormat('yyyy-MM-dd HH:mm:ss');

  @override
  List<String> log(LogEvent event) {
    final time = _formatter.format(event.time);
    final levelStr = event.level.name.toUpperCase();
    
    // Message already contains [CONTEXT] from helper
    final message = event.message;
    
    // Check if error/stacktrace
    String? errorStr;
    if (event.error != null) {
      errorStr = "ERROR: ${event.error}";
    }
    
    final output = '$time | $levelStr | $message';
    
    final result = <String>[output];
    if (errorStr != null) result.add(errorStr);
    if (event.stackTrace != null) result.add(event.stackTrace.toString());
    
    return result;
  }
}

class FileOutput extends LogOutput {
  final File file;
  
  FileOutput(this.file);

  @override
  void output(OutputEvent event) {
    if (event.lines.isEmpty) return;
    
    try {
      for (var line in event.lines) {
        file.writeAsStringSync('$line\n', mode: FileMode.append);
      }
    } catch (e) {
      // Fail silently
    }
  }
}
