import 'package:flutter/material.dart';
import 'package:client_app/features/execution/models/report_data_v2_dto.dart';
import 'package:client_app/shared/widgets/output_renderer.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';

import 'package:client_app/features/execution/views/widgets/xai_axis_telemetry_grid.dart';
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

    // 2. Global Score (Kokonaiskeskiarvo)
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

      // 4. Layout Synthesis Blocks
      if (layout.synthesisBlocks != null) {
        for (final block in layout.synthesisBlocks!) {
          String? text;
          if (block is SduiMarkdownBlock) {
            text = block.text;
          } else if (block is SduiParagraphBlock) {
            text = block.text;
          }

          if (text != null && text.isNotEmpty) {
            widgets.add(
              Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.s24,
                  vertical: AppSpacing.s8,
                ),
                child: OutputRenderer(markdownContent: text),
              ),
            );
          }
        }
      }

      // 5. Axes (XAIAxisTelemetryGrid)
      final presetView = layout.presetView;
      final showGraph = const [
        PresetView.matrix3d,
        PresetView.compare2d,
        PresetView.complex3d,
      ].contains(presetView);

      final hideAxes =
          presetView == PresetView.textOnly ||
          (showGraph && layout.textDeliveryMode == TextDeliveryMode.none);

      // 4.5. Render Graph if requested by layout presetView
      if (showGraph && layout.axes.length >= 2) {
        widgets.add(
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.s24,
              vertical: AppSpacing.s16,
            ),
            child: SizedBox(
              height: 300,
              child: presetView == PresetView.complex3d
                  ? LogicRadarChart(axes: layout.axes)
                  : LogicMatrixChart(
                      xAxis: layout.axes[0],
                      yAxis: layout.axes[1],
                      zAxis: layout.axes.length > 2 ? layout.axes[2] : null,
                    ),
            ),
          ),
        );
      }

      if (!hideAxes && layout.axes.isNotEmpty) {
        widgets.add(
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSpacing.s24,
              vertical: AppSpacing.s16,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
              children: layout.axes.map((axis) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: AppSpacing.s16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // 1. Axis Name & Score
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        crossAxisAlignment: CrossAxisAlignment.baseline,
                        textBaseline: TextBaseline.alphabetic,
                        children: [
                          Expanded(
                            child: Text(
                              axis.name,
                              style: Theme.of(context).textTheme.titleMedium
                                  ?.copyWith(fontWeight: FontWeight.bold),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          if (axis.score != null)
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: AppSpacing.s12,
                                vertical: AppSpacing.s4,
                              ),
                              decoration: BoxDecoration(
                                color: Theme.of(
                                  context,
                                ).colorScheme.primaryContainer,
                                borderRadius: BorderRadius.circular(
                                  AppSpacing.s12,
                                ),
                              ),
                              child: Text(
                                axis.scoreDisplayLabel ?? '-',
                                style: Theme.of(context).textTheme.titleSmall
                                    ?.copyWith(
                                      color: Theme.of(
                                        context,
                                      ).colorScheme.onPrimaryContainer,
                                      fontWeight: FontWeight.bold,
                                    ),
                              ),
                            ),
                        ],
                      ),
                      AppSpacing.h8,

                      // 2. Axis Description
                      if (axis.description != null &&
                          axis.description!.isNotEmpty)
                        Padding(
                          padding: const EdgeInsets.only(bottom: AppSpacing.s8),
                          child: Text(
                            axis.description!,
                            style: Theme.of(context).textTheme.bodySmall
                                ?.copyWith(
                                  fontStyle: FontStyle.italic,
                                  color: Theme.of(
                                    context,
                                  ).colorScheme.onSurfaceVariant,
                                ),
                          ),
                        ),

                      // 3. UI Plot Ratio (Progress Bar for metrics1d)
                      if (presetView == PresetView.metrics1d &&
                          axis.uiPlotRatio != null)
                        Container(
                          height: AppSpacing.s12,
                          margin: const EdgeInsets.only(
                            top: AppSpacing.s4,
                            bottom: AppSpacing.s12,
                          ),
                          decoration: BoxDecoration(
                            color: Theme.of(
                              context,
                            ).colorScheme.surfaceContainerHighest,
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: FractionallySizedBox(
                            alignment: Alignment.centerLeft,
                            widthFactor: axis.uiPlotRatio!.clamp(0.0, 1.0),
                            child: Container(
                              decoration: BoxDecoration(
                                color: Theme.of(context).colorScheme.primary,
                                borderRadius: BorderRadius.circular(6),
                              ),
                            ),
                          ),
                        ),

                      // 4. Telemetry Grid (Text Explanations)
                      XAIAxisTelemetryGrid(
                        axis: axis,
                        textDeliveryMode: layout.textDeliveryMode,
                        showQuote: true,
                      ),
                      if (axis.innerSduiBlocks.isNotEmpty) ...[
                        const SizedBox(height: 12.0),
                        SduiBlocksRenderer(blocks: axis.innerSduiBlocks),
                      ],
                    ],
                  ),
                );
              }).toList(),
            ),
          ),
        );
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
