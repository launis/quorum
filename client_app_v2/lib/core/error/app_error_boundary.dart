import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:json_annotation/json_annotation.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// V2 Forensic Boundary Protocol: AppExceptionBoundary
///
/// Intercepts severe build or rendering exceptions. Instead of gray/red screen of death
/// or hiding the error (Graceful Degradation), it displays a localized Diagnostic Node
/// (Error Box) to enforce the Fail-Fast and Absolute Death mandates.
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
  late final ErrorWidgetBuilder _originalErrorBuilder;

  @override
  void initState() {
    super.initState();
    _originalErrorBuilder = ErrorWidget.builder;
    // Catch framework-level errors gracefully without causing the Red Screen of Death
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
      // Diagnostic Node Mandate: Immediately show error box instead of hiding it (No SizedBox.shrink())
      return _buildDiagnosticNode(context, details.exception);
    };
  }

  @override
  void dispose() {
    ErrorWidget.builder = _originalErrorBuilder;
    super.dispose();
  }

  /// Manually recover the Boundary state
  void resetError() {
    setState(() {
      _error = null;
    });
  }

  Widget _buildDiagnosticNode(BuildContext context, Object error) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context);

    String displayError = error.toString();
    if (error is CheckedFromJsonException) {
      final key = error.key ?? 'unknown';
      if (error.innerError != null) {
        displayError =
            l10n?.errorDataType(key, error.innerError.toString()) ??
            '[Type Error in field "$key"]\n${error.innerError}';
      } else {
        displayError =
            l10n?.errorDataMapping(key, error.message ?? 'null') ??
            '[Mapping Error in field "$key"]\n${error.message}';
      }
    } else if (displayError.contains('stp_') ||
        displayError.toLowerCase().contains('missing rule')) {
      displayError =
          '[Virtual Step Parsing Failure]\nDynamic step injection could not be parsed: $displayError';
    }

    return Container(
      margin: AppSpacing.p8,
      padding: AppSpacing.p16,
      decoration: BoxDecoration(
        color: theme.colorScheme.errorContainer,
        border: Border.all(
          color: theme.colorScheme.error,
          width: AppSpacing.s2,
        ),
        borderRadius: BorderRadius.circular(AppSpacing.s8),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.report_problem,
                color: theme.colorScheme.onErrorContainer,
              ),
              AppSpacing.w8,
              Expanded(
                child: Text(
                  l10n?.errorUnknown ?? 'Data Corruption / Render Error',
                  style: theme.textTheme.titleMedium?.copyWith(
                    color: theme.colorScheme.onErrorContainer,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              Semantics(
                button: true,
                label: 'Reset',
                child: MouseRegion(
                  cursor: SystemMouseCursors.click,
                  child: InkWell(
                    borderRadius: BorderRadius.circular(AppSpacing.s4),
                    onTap: resetError,
                    child: Padding(
                      padding: const EdgeInsets.all(AppSpacing.s4),
                      child: Icon(
                        Icons.refresh,
                        color: theme.colorScheme.onErrorContainer,
                        size: 20,
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
          AppSpacing.h8,
          Text(
            displayError,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onErrorContainer,
              fontFamily: 'monospace',
            ),
            maxLines: 4,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      // Phase 9 Mandate: Diagnostic Node (Absolute Death), NO Graceful Degradation
      return _buildDiagnosticNode(context, _error!);
    }
    return widget.child;
  }
}
