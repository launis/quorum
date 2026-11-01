import 'package:flutter/material.dart';
import 'package:client_app/core/error/app_error_ext.dart';
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
  static int _boundaryCount = 0;
  static ErrorWidgetBuilder? _rootOriginalErrorBuilder;

  @override
  void initState() {
    super.initState();
    if (_boundaryCount == 0) {
      _rootOriginalErrorBuilder = ErrorWidget.builder;
    }
    _boundaryCount++;

    // Catch framework-level errors gracefully without causing the Red Screen of Death
    ErrorWidget.builder = (FlutterErrorDetails details) {
      if (!mounted) {
        return _rootOriginalErrorBuilder?.call(details) ??
            ErrorWidget(details.exception);
      }
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted && _error == null) {
          final l10n = AppLocalizations.of(context);
          final messenger = ScaffoldMessenger.maybeOf(context);
          if (l10n != null &&
              messenger != null &&
              Scaffold.maybeOf(context) != null) {
            messenger.showSnackBar(
              SnackBar(
                content: Text(l10n.errorUnknown),
                behavior: SnackBarBehavior.floating,
                backgroundColor: Theme.of(context).colorScheme.error,
              ),
            );
          }
          setState(() {
            _error = details.exception;
          });
        }
      });
      // Diagnostic Node Mandate: Immediately show error box instead of hiding it
      return _buildDiagnosticNode(context, details.exception);
    };
  }

  @override
  void dispose() {
    _boundaryCount--;
    if (_boundaryCount <= 0) {
      _boundaryCount = 0;
      if (_rootOriginalErrorBuilder != null) {
        ErrorWidget.builder = _rootOriginalErrorBuilder!;
        _rootOriginalErrorBuilder = null;
      }
    }
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
    final l10n = AppLocalizations.of(context)!;

    String displayError = AppExceptionX.extractLocalizedHint(error, l10n);
    final rawErrorStr = error.toString();
    if (error is CheckedFromJsonException) {
      final key = error.key ?? l10n.errorUnknown;
      if (error.innerError != null) {
        displayError = l10n.errorDataType(key, error.innerError.toString());
      } else {
        displayError = l10n.errorDataMapping(
          key,
          error.message ?? l10n.errorUnknown,
        );
      }
    } else if (rawErrorStr.contains('stp_') ||
        rawErrorStr.toLowerCase().contains('missing rule')) {
      displayError = l10n.virtualStepParsingFailure(rawErrorStr);
    }

    return Material(
      type: MaterialType.transparency,
      child: Container(
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
                    l10n.errorUnknown,
                    overflow: TextOverflow.ellipsis,
                    style: theme.textTheme.titleMedium?.copyWith(
                      color: theme.colorScheme.onErrorContainer,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Semantics(
                  button: true,
                  label: l10n.retry,
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
                          size: AppSpacing.s16,
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

/// Type alias supporting both naming conventions across Studio and Reports features.
typedef AppErrorBoundary = AppExceptionBoundary;
