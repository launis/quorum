import 'package:flutter/material.dart';
import 'package:client_app/features/sdui/models/sdui_render_payload.dart';
import 'package:flutter_markdown_plus/flutter_markdown_plus.dart';
import 'package:client_app/features/sdui/utils/sdui_translator.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Render a percentage-based 2-dimensional dot matrix without layout assumptions.
class Matrix2DWidget extends StatelessWidget {
  final SduiComponent component;

  const Matrix2DWidget({super.key, required this.component});

  @override
  Widget build(BuildContext context) {
    // 1. Data constraints clamping safely without Math assumptions
    // Coordinates perfectly computed by backend
    final double xPct = component.xVisualPct;
    final double yPct = component.yVisualPct;

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (component.title.isNotEmpty)
              Text(
                SduiTranslator.translate(context, component.title),
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF2C3E50),
                ),
              ),
            const SizedBox(height: 24),

            // Flex Layout: Graph on Left, Data on Right
            LayoutBuilder(
              builder: (context, constraints) {
                final isSmall = constraints.maxWidth < 500;

                final graph = _buildGraph(context, xPct, yPct);
                final dataBoxes = _buildDataBoxes(context);

                if (isSmall) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [graph, const SizedBox(height: 32), dataBoxes],
                  );
                }

                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    graph,
                    const SizedBox(width: 32),
                    Expanded(child: dataBoxes),
                  ],
                );
              },
            ),

            const SizedBox(height: 24),
            // Justifications
            _buildJustificationBox(
              SduiTranslator.translate(context, component.xTitle),
              component.xNoteText,
              const Color(0xFF4CAF50),
              component.xDisplayValueOnly.isNotEmpty
                  ? component.xDisplayValueOnly
                  : '0.0',
              component.xDisplayMaxOnly.isNotEmpty
                  ? component.xDisplayMaxOnly
                  : '6.0',
            ),
            if (component.yNoteText.isNotEmpty)
              _buildJustificationBox(
                SduiTranslator.translate(context, component.yTitle),
                component.yNoteText,
                const Color(0xFFFF9800),
                component.yDisplayValueOnly.isNotEmpty
                    ? component.yDisplayValueOnly
                    : '0.0',
                component.yDisplayMaxOnly.isNotEmpty
                    ? component.yDisplayMaxOnly
                    : '6.0',
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildGraph(BuildContext context, double xPct, double yPct) {
    final l10n = AppLocalizations.of(context);
    final xLabel =
        '${l10n?.xAxisLabel ?? "X-Axis"} - ${SduiTranslator.translate(context, component.xTitle)}';
    final yLabel =
        '${l10n?.yAxisLabel ?? "Y-Axis"} - ${SduiTranslator.translate(context, component.yTitle)}';

    return Container(
      width: 200,
      height: 200,
      decoration: BoxDecoration(
        color: const Color(0xFFFAFAFA),
        border: Border.all(color: Colors.grey.shade300),
      ),
      margin: const EdgeInsets.only(left: 32, bottom: 24), // For labels
      child: Stack(
        clipBehavior: Clip.none,
        children: [
          // Grid lines
          Positioned(
            top: 200 / 3,
            left: 0,
            right: 0,
            child: _dashedLine(horizontal: true),
          ),
          Positioned(
            top: (200 / 3) * 2,
            left: 0,
            right: 0,
            child: _dashedLine(horizontal: true),
          ),
          Positioned(
            left: 200 / 3,
            top: 0,
            bottom: 0,
            child: _dashedLine(horizontal: false),
          ),
          Positioned(
            left: (200 / 3) * 2,
            top: 0,
            bottom: 0,
            child: _dashedLine(horizontal: false),
          ),

          // The Dot
          Positioned(
            left: ((xPct / 100) * 200) - 10,
            top: ((yPct / 100) * 200) - 10,
            child: MouseRegion(
              cursor: SystemMouseCursors.click,
              child: GestureDetector(
                onTap: () => _showNotesModal(context),
                child: Container(
                  width: 20,
                  height: 20,
                  decoration: BoxDecoration(
                    color: const Color(0xFFE91E63),
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white, width: 2),
                    boxShadow: const [
                      BoxShadow(
                        color: Colors.black26,
                        blurRadius: 4,
                        offset: Offset(0, 2),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // Axis Labels
          Positioned(
            bottom: -24,
            left: 0,
            right: 0,
            child: Text(
              xLabel,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.bold,
                color: Colors.black54,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          Positioned(
            left: -110,
            top: 90,
            width: 200,
            child: Transform.rotate(
              angle: -1.5708, // -90 degrees in radians
              child: Text(
                yLabel,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                  color: Colors.black54,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _dashedLine({required bool horizontal}) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final boxHeight = horizontal ? 1.0 : constraints.constrainHeight();
        final boxWidth = horizontal ? constraints.constrainWidth() : 1.0;
        final dashCount =
            (horizontal ? boxWidth : boxHeight) / 5.0; // 5 = dash + space

        return Flex(
          direction: horizontal ? Axis.horizontal : Axis.vertical,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: List.generate(dashCount.floor(), (_) {
            return SizedBox(
              width: horizontal ? 2.5 : 1,
              height: horizontal ? 1 : 2.5,
              child: const DecoratedBox(
                decoration: BoxDecoration(color: Colors.black26),
              ),
            );
          }),
        );
      },
    );
  }

  Widget _buildDataBoxes(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final xTitle = SduiTranslator.translate(context, component.xTitle);
    final yTitle = SduiTranslator.translate(context, component.yTitle);

    final xLabel = l10n?.xAxisLabel ?? "X-Axis";
    final yLabel = l10n?.yAxisLabel ?? "Y-Axis";

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: _buildDataBox(
            xLabel,
            xTitle,
            component.xDisplayValueOnly,
            component.xDisplayMaxOnly,
            const Color(0xFF4CAF50),
            component.xScaleText,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _buildDataBox(
            yLabel,
            yTitle,
            component.yDisplayValueOnly,
            component.yDisplayMaxOnly,
            const Color(0xFFFF9800),
            component.yScaleText,
          ),
        ),
      ],
    );
  }

  Widget _buildDataBox(
    String axisName,
    String axisTitle,
    String valStr,
    String maxStr,
    Color color,
    String scaleText,
  ) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(4),
      child: Container(
        width: double.infinity,
        decoration: BoxDecoration(
          color: Colors.grey.shade50,
          border: Border.all(color: Colors.grey.shade200),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(height: 3, width: double.infinity, color: color),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    axisName.toUpperCase(),
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.black54,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (axisTitle.isNotEmpty)
                    Text(
                      axisTitle.toUpperCase(),
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: Colors.black54,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  const SizedBox(height: 12),
                  Text(
                    '${valStr.isNotEmpty ? valStr : "0.0"} /',
                    style: TextStyle(
                      fontSize: 42,
                      fontWeight: FontWeight.bold,
                      color: color,
                      height: 1.0,
                    ),
                  ),
                  Text(
                    maxStr.isNotEmpty ? maxStr : "6.0",
                    style: TextStyle(
                      fontSize: 42,
                      fontWeight: FontWeight.bold,
                      color: color,
                      height: 1.0,
                    ),
                  ),
                  const SizedBox(height: 12),
                  if (scaleText.isNotEmpty)
                    Text(
                      scaleText,
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: color,
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildJustificationBox(
    String title,
    String note,
    Color color,
    String valStr,
    String maxStr,
  ) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(4),
      child: Container(
        margin: const EdgeInsets.only(top: 8, bottom: 12),
        decoration: BoxDecoration(color: color.withValues(alpha: 0.05)),
        child: IntrinsicHeight(
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(width: 4, color: color),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      RichText(
                        text: TextSpan(
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: color,
                          ),
                          children: [
                            TextSpan(text: "$title "),
                            TextSpan(
                              text: '($valStr / $maxStr):',
                              style: const TextStyle(color: Colors.black87),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 6),
                      MarkdownBody(
                        data: note,
                        styleSheet: MarkdownStyleSheet(
                          p: const TextStyle(
                            fontSize: 13,
                            height: 1.5,
                            color: Colors.black87,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showNotesModal(BuildContext context) {
    if (component.xNoteText.isEmpty && component.yNoteText.isEmpty) {
      return;
    }

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: Text(AppLocalizations.of(context)!.detailedBreakdown),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (component.xNoteText.isNotEmpty) ...[
                  Text(
                    SduiTranslator.translate(context, component.xTitle),
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF4CAF50),
                    ),
                  ),
                  const SizedBox(height: 8),
                  MarkdownBody(data: component.xNoteText),
                  const SizedBox(height: 16),
                ],
                if (component.yNoteText.isNotEmpty) ...[
                  Text(
                    SduiTranslator.translate(context, component.yTitle),
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Color(0xFFFF9800),
                    ),
                  ),
                  const SizedBox(height: 8),
                  MarkdownBody(data: component.yNoteText),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: Text(AppLocalizations.of(context)!.close),
            ),
          ],
        );
      },
    );
  }
}
