import 'dart:io';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class DeepDiveExpander extends ConsumerWidget {
  final String title;
  final Widget child;
  final IconData icon;
  final bool initiallyExpanded;

  const DeepDiveExpander({
    super.key,
    required this.title,
    required this.child,
    this.icon = Icons.analytics_outlined,
    this.initiallyExpanded = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);

    try {
      if (title.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: DeepDiveExpander title cannot be empty.',
        );
      }

      return Card(
        elevation: 0,
        clipBehavior: Clip.antiAlias,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.s12),
          side: BorderSide(
            color: theme.colorScheme.outlineVariant.withValues(alpha: 0.5),
          ),
        ),
        child: Semantics(
          excludeSemantics: Platform.isWindows,
          child: ExpansionTile(
            initiallyExpanded: initiallyExpanded,
            shape: const Border(),
            collapsedShape: const Border(),
            leading: Icon(icon, color: theme.colorScheme.primary),
            title: Text(
              title,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),
            childrenPadding: AppSpacing.p16,
            children: [child],
          ),
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'DeepDiveExpander',
            'VALIDATION_FAILED: Failed to render deep dive expander',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
