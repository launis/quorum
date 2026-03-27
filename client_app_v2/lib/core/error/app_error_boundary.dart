import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// V2 Forensic Boundary Protocol: AppExceptionBoundary
///
/// Intercepts severe build or rendering exceptions. Instead of gray/red screen of death
/// or crashing the client application, it displays a graceful fallback screen.
/// Extremely critical for the V1 to V2 transition where models (PromptBlocks/SystemConfigs)
/// might momentarily mismatch in structure while updating.
class AppExceptionBoundary extends StatefulWidget {
  final Widget child;

  const AppExceptionBoundary({super.key, required this.child});

  @override
  AppExceptionBoundaryState createState() => AppExceptionBoundaryState();
}

class AppExceptionBoundaryState extends State<AppExceptionBoundary> {
  Object? _error;

  @override
  void initState() {
    super.initState();
    // Catch framework-level errors gracefully
    ErrorWidget.builder = (FlutterErrorDetails details) {
      if (!mounted) return const SizedBox.shrink();
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted && _error == null) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(AppLocalizations.of(context)!.errorUnknown),
              behavior: SnackBarBehavior.floating,
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
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
      // Graceful degradation per Desktop Phase 9 Mandate
      return const SizedBox.shrink();
    }
    return widget.child;
  }
}
