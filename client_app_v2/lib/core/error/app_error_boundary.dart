import 'package:flutter/material.dart';

/// V2 Forensic Boundary Protocol: AppErrorBoundary
///
/// Intercepts severe build or rendering exceptions. Instead of gray/red screen of death
/// or crashing the client application, it displays a graceful fallback screen.
/// Extremely critical for the V1 to V2 transition where models (PromptBlocks/SystemConfigs)
/// might momentarily mismatch in structure while updating.
class AppErrorBoundary extends StatefulWidget {
  final Widget child;

  const AppErrorBoundary({super.key, required this.child});

  @override
  AppErrorBoundaryState createState() => AppErrorBoundaryState();
}

class AppErrorBoundaryState extends State<AppErrorBoundary> {
  Object? _error;

  @override
  void initState() {
    super.initState();
    // Catch framework-level errors gracefully
    ErrorWidget.builder = (FlutterErrorDetails details) {
      if (!mounted) return const SizedBox.shrink();
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          setState(() {
            _error = details.exception;
          });
        }
      });
      return const SizedBox.shrink(); // Prevent the red screen from flashing
    };
  }

  /// Manually recover the Boundary state
  void resetError() {
    setState(() {
      _error = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('Render Integrity Violated (V2 Boundary)'),
          backgroundColor: Theme.of(context).colorScheme.errorContainer,
          foregroundColor: Theme.of(context).colorScheme.onErrorContainer,
        ),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.warning_amber_rounded,
                  size: 80,
                  color: Theme.of(context).colorScheme.error,
                ),
                const SizedBox(height: 24),
                Text(
                  'A schema migration or render constraint failed dynamically.',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color:
                        Theme.of(context).colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: SelectableText(
                    _error.toString(),
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 12,
                    ),
                  ),
                ),
                const SizedBox(height: 32),
                FilledButton.icon(
                  icon: const Icon(Icons.refresh),
                  label: const Text('Reset Component'),
                  onPressed: resetError,
                ),
              ],
            ),
          ),
        ),
      );
    }
    return widget.child;
  }
}
