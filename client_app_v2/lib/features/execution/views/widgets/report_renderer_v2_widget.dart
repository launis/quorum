import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/widgets/logic_matrix_chart.dart';
import 'package:client_app/shared/widgets/logic_radar_chart.dart';
import 'package:client_app/features/execution/views/widgets/sdui_blocks_renderer.dart';

// Phase 3, Step 2: Create ReportRendererV2Widget
class ReportRendererV2Widget extends StatelessWidget {
  final ReportDataDto payload;
  final String executionId;

  const ReportRendererV2Widget({
    super.key,
    required this.payload,
    required this.executionId,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final locale = Localizations.localeOf(context).languageCode;
    final widgets = <Widget>[];

    // 0. Top Titles (Profile Name & Description)
    final profileName = payload.profileName?.get(locale);
    if (profileName != null && profileName.isNotEmpty) {
      widgets.add(
        Padding(
          padding: const EdgeInsets.fromLTRB(
            AppSpacing.s24,
            AppSpacing.s24,
            AppSpacing.s24,
            AppSpacing.s8,
          ),
          child: Text(
            profileName,
            style: Theme.of(
              context,
            ).textTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
        ),
      );
    }

    final profileDescription = payload.profileDescription?.get(locale);
    if (profileDescription != null && profileDescription.isNotEmpty) {
      widgets.add(
        Padding(
          padding: const EdgeInsets.fromLTRB(
            AppSpacing.s24,
            0,
            AppSpacing.s24,
            AppSpacing.s16,
          ),
          child: Text(
            profileDescription,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          ),
        ),
      );
    }

    // 0.5 Cover Metadata
    if (payload.visibleMetadata.isNotEmpty) {
      final metaItems = <Widget>[];
      for (final meta in payload.visibleMetadata) {
        String? label;
        String? value;
        switch (meta) {
          case 'date':
            label = l10n.metaDate.split(' (')[0];
            value = payload.localTimeStr ?? payload.createdAt;
            break;
          case 'organization':
            label = l10n.metaOrganization.split(' (')[0];
            value = payload.orgName;
            break;
          case 'user':
            label = l10n.metaUser.split(' (')[0];
            value = payload.userName;
            break;
          case 'scoring_engine':
            label = l10n.metaScoringEngine.split(' (')[0];
            value = payload.scoringEngineName;
            break;
          case 'strictness':
            label = l10n.metaStrictness.split(' (')[0];
            value = payload.strictnessLevel?.toString();
            break;
          case 'cost':
            label = l10n.metaCost.split(' (')[0];
            value = payload.costEstimate != null
                ? '\$${payload.costEstimate!.toStringAsFixed(4)}'
                : null;
            break;
          case 'tokens':
            label = l10n.metaTokens.split(' (')[0];
            value = payload.totalTokens?.toString();
            break;
        }

        if (label != null && value != null && value.isNotEmpty) {
          metaItems.add(
            Padding(
              padding: const EdgeInsets.only(
                right: AppSpacing.s16,
                bottom: AppSpacing.s8,
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    '$label: ',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).colorScheme.outline,
                    ),
                  ),
                  Text(
                    value,
                    style: const TextStyle(fontWeight: FontWeight.w500),
                  ),
                ],
              ),
            ),
          );
        }
      }

      if (metaItems.isNotEmpty) {
        widgets.add(
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.s24,
              vertical: AppSpacing.s8,
            ),
            child: Wrap(children: metaItems),
          ),
        );
      }
    }

    // 1. Inner SDUI Blocks (e.g. Header)
    if (payload.innerSduiBlocks.isNotEmpty) {
      widgets.add(
        Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSpacing.s24,
            vertical: AppSpacing.s8,
          ),
          child: SduiBlocksRenderer(blocks: payload.innerSduiBlocks),
        ),
      );
    }

    // 2. Global Score
    if (payload.globalScore != null) {
      widgets.add(
        Container(
          margin: const EdgeInsets.symmetric(
            horizontal: AppSpacing.s24,
            vertical: AppSpacing.s16,
          ),
          padding: const EdgeInsets.all(AppSpacing.s16),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primaryContainer,
            borderRadius: BorderRadius.circular(AppSpacing.s8),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                l10n.scorecard_global_average,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                '${payload.globalScore!.toStringAsFixed(2)}/100',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      );
    }

    // 3. Layouts
    for (final layout in payload.layouts) {
      final title = layout.title?.get(locale);
      if (title != null && title.isNotEmpty) {
        widgets.add(
          Padding(
            padding: const EdgeInsets.fromLTRB(
              AppSpacing.s24,
              AppSpacing.s24,
              AppSpacing.s24,
              AppSpacing.s8,
            ),
            child: Text(
              title,
              style: Theme.of(
                context,
              ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
            ),
          ),
        );
      }

      final description = layout.description?.get(locale);
      if (description != null && description.isNotEmpty) {
        widgets.add(
          Padding(
            padding: const EdgeInsets.fromLTRB(
              AppSpacing.s24,
              0,
              AppSpacing.s24,
              AppSpacing.s16,
            ),
            child: Text(
              description,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        );
      }

      // 4. Setup variables for axes and graphs
      final presetView = layout.presetView;
      final showGraph = const [
        PresetView.matrix3d,
        PresetView.compare2d,
        PresetView.complex3d,
        PresetView.metrics1d,
      ].contains(presetView);

      // 4.1. Layout Synthesis Blocks (Explanations printed BEFORE the graph)
      if (layout.synthesisBlocks != null &&
          layout.synthesisBlocks!.isNotEmpty) {
        widgets.add(
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.s24,
              vertical: AppSpacing.s8,
            ),
            child: SduiBlocksRenderer(blocks: layout.synthesisBlocks!),
          ),
        );
      }

      if (showGraph && layout.axes.isNotEmpty) {
        widgets.add(
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.s24,
              vertical: AppSpacing.s16,
            ),
            child: Builder(
              builder: (context) {
                if (presetView == PresetView.metrics1d) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: layout.axes
                        .map((axis) => SduiBlocksRenderer(blocks: axis.innerSduiBlocks))
                        .toList(),
                  );
                }

                if (layout.axes.length >= 2) {
                  return SizedBox(
                    height: AppSpacing.s300,
                    child: presetView == PresetView.complex3d
                        ? LogicRadarChart(axes: layout.axes)
                        : LogicMatrixChart(
                            xAxis: layout.axes[0],
                            yAxis: layout.axes[1],
                            zAxis: layout.axes.length > 2 ? layout.axes[2] : null,
                          ),
                  );
                }
                return const SizedBox.shrink();
              },
            ),
          ),
        );
      }

      // 4.6. Render Matrix Summary Table
      if (presetView == PresetView.matrixSummary && layout.axes.isNotEmpty) {
        final visibleCols = layout.matrixVisibleColumns;
        final labels = layout.matrixColumnLabels;

        if (visibleCols.isNotEmpty) {
          widgets.add(
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.s24,
                vertical: AppSpacing.s16,
              ),
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: DataTable(
                  headingRowColor: WidgetStateProperty.all(
                    Theme.of(context).colorScheme.surfaceContainerHighest,
                  ),
                  dataRowMaxHeight: double.infinity,
                  dataRowMinHeight: 48.0,
                  columnSpacing: AppSpacing.s24,
                  columns: visibleCols.map((colKey) {
                    final headerText = labels[colKey]?.get(locale) ?? colKey;
                    return DataColumn(
                      label: Expanded(
                        child: Text(
                          headerText,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                    );
                  }).toList(),
                  rows: layout.axes.map((axis) {
                    return DataRow(
                      cells: visibleCols.map((colKey) {
                        Widget cellContent;
                        switch (colKey) {
                          case 'label':
                            cellContent = Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  axis.name + (axis.isEvaluative ? ' *' : ''),
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                if (axis.description != null &&
                                    axis.description!.isNotEmpty)
                                  Padding(
                                    padding: const EdgeInsets.only(
                                      top: AppSpacing.s4,
                                    ),
                                    child: Text(
                                      axis.description!,
                                      style: Theme.of(context)
                                          .textTheme
                                          .bodySmall
                                          ?.copyWith(
                                            color: Theme.of(
                                              context,
                                            ).colorScheme.onSurfaceVariant,
                                          ),
                                    ),
                                  ),
                              ],
                            );
                            break;
                          case 'distribution':
                          case 'atomic_breakdown':
                            final breakdown = axis.levelBreakdown ?? {};
                            final names = axis.levelNames ?? {};
                            if (breakdown.isNotEmpty) {
                              final sortedKeys = breakdown.keys.toList()
                                ..sort((a, b) => b.compareTo(a));
                              cellContent = Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                mainAxisSize: MainAxisSize.min,
                                children: sortedKeys.map((k) {
                                  final numStr = int.tryParse(k) != null
                                      ? int.parse(k).toString()
                                      : k;
                                  final hitStr = breakdown[k];
                                  final name = names[k] ?? 'T$k';
                                  return Text(
                                    '$numStr - $name: $hitStr',
                                    style: const TextStyle(fontSize: 12),
                                  );
                                }).toList(),
                              );
                            } else {
                              cellContent = const Text('-');
                            }
                            break;
                          case 'row_explanation':
                            cellContent = Text(
                              axis.rowExplanation,
                              style: const TextStyle(
                                fontStyle: FontStyle.italic,
                                fontSize: 12,
                              ),
                            );
                            break;
                          case 'score':
                            cellContent = Text(
                              axis.scoreDisplayLabel ?? '-',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.blue,
                              ),
                            );
                            break;
                          default:
                            cellContent = const Text('-');
                        }
                        return DataCell(
                          Padding(
                            padding: const EdgeInsets.symmetric(
                              vertical: AppSpacing.s8,
                            ),
                            child: SizedBox(
                              width: colKey == 'label'
                                  ? 250
                                  : colKey == 'row_explanation'
                                  ? 300
                                  : null,
                              child: cellContent,
                            ),
                          ),
                        );
                      }).toList(),
                    );
                  }).toList(),
                ),
              ),
            ),
          );
        }
      }
    }

    if (widgets.isEmpty) {
      return const SizedBox();
    }

    return ListView(
      padding: EdgeInsets.zero,
      shrinkWrap: true,
      primary: false,
      children: widgets,
    );
  }
}
