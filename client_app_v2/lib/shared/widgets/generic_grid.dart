import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

@immutable
class GenericGridItem {
  final String label;
  final String value;
  final bool highlight;

  const GenericGridItem({
    required this.label,
    required this.value,
    this.highlight = false,
  });
}

@immutable
class GenericGridData {
  final List<GenericGridItem> items;
  final bool isCorrupted;

  const GenericGridData({
    this.items = const <GenericGridItem>[],
    this.isCorrupted = false,
  });
}

class GenericGrid extends ConsumerWidget {
  final String title;
  final GenericGridData data;

  const GenericGrid({super.key, required this.title, required this.data});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    try {
      if (title.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: GenericGrid title cannot be empty.',
        );
      }

      if (data.isCorrupted) {
        throw AppException.validation(
          'Fail-Fast: GenericGrid data is corrupted.',
        );
      }

      final parsedItems = <({String label, String value, bool highlight})>[];

      for (final item in data.items) {
        final rawLabel = item.label.trim();
        final rawValue = item.value.trim();
        if (rawLabel.isEmpty) {
          throw AppException.validation(
            'Fail-Fast: GenericGrid item label cannot be empty.',
          );
        }
        if (rawValue.isEmpty) {
          throw AppException.validation(
            'Fail-Fast: GenericGrid item value cannot be empty.',
          );
        }
        parsedItems.add((
          label: rawLabel,
          value: rawValue,
          highlight: item.highlight,
        ));
      }

      return Card(
        elevation: AppSpacing.s2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppSpacing.s8),
        ),
        clipBehavior: Clip.antiAlias,
        child: Container(
          decoration: BoxDecoration(
            border: Border(
              left: BorderSide(
                color: colorScheme.onSurfaceVariant,
                width: AppSpacing.s4,
              ),
            ),
          ),
          padding: AppSpacing.p16,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                  color: colorScheme.onSurfaceVariant,
                ),
              ),
              AppSpacing.h16,
              LayoutBuilder(
                builder: (context, constraints) {
                  final isTwoColumn = constraints.maxWidth >= AppSpacing.s300;
                  final rows = <Widget>[];

                  if (isTwoColumn) {
                    for (var i = 0; i < parsedItems.length; i += 2) {
                      if (i > 0) {
                        rows.add(AppSpacing.h12);
                      }
                      final first = parsedItems[i];
                      final second = i + 1 < parsedItems.length
                          ? parsedItems[i + 1]
                          : null;
                      rows.add(
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Expanded(child: _buildGridTile(theme, first)),
                            AppSpacing.w16,
                            Expanded(
                              child: second != null
                                  ? _buildGridTile(theme, second)
                                  : const SizedBox(),
                            ),
                          ],
                        ),
                      );
                    }
                  } else {
                    for (var i = 0; i < parsedItems.length; i++) {
                      if (i > 0) {
                        rows.add(AppSpacing.h12);
                      }
                      rows.add(_buildGridTile(theme, parsedItems[i]));
                    }
                  }

                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: rows,
                  );
                },
              ),
            ],
          ),
        ),
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'GenericGrid',
            'VALIDATION_FAILED: Failed to render GenericGrid',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }

  Widget _buildGridTile(
    ThemeData theme,
    ({String label, String value, bool highlight}) item,
  ) {
    final colorScheme = theme.colorScheme;

    return Container(
      padding: AppSpacing.p8,
      decoration: BoxDecoration(
        color: item.highlight
            ? colorScheme.primaryContainer.withValues(alpha: 0.3)
            : colorScheme.surfaceContainerLowest,
        borderRadius: BorderRadius.circular(AppSpacing.s6),
        border: Border.all(
          color: item.highlight
              ? colorScheme.primary
              : colorScheme.surfaceContainerHighest,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            item.label,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: theme.textTheme.labelSmall?.copyWith(
              color: colorScheme.onSurfaceVariant,
              fontWeight: FontWeight.bold,
            ),
          ),
          AppSpacing.h2,
          Text(
            item.value,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: item.highlight ? FontWeight.bold : FontWeight.w600,
              color: item.highlight
                  ? colorScheme.primary
                  : colorScheme.onSurfaceVariant,
            ),
          ),
        ],
      ),
    );
  }
}
