import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/sdui/models/sdui_render_payload.dart';
import 'package:client_app/core/logging/logger_service.dart';

// Assuming creating local widgets for each
import 'gauge_1d_widget.dart';
import 'matrix_2d_widget.dart';
import 'scatter_3d_widget.dart';
import 'notes_panel_widget.dart';
import 'package:client_app/features/sdui/utils/sdui_translator.dart';

/// Systematically render the Server-Driven UI blueprint into an ordered list of widgets.
class SduiRenderer extends ConsumerWidget {
  final SduiRenderPayload payload;

  const SduiRenderer({super.key, required this.payload});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Loop through the components and build the UI
    final components = payload.blueprint.components;

    return LayoutBuilder(
      builder: (context, constraints) {
        return ConstrainedBox(
          constraints: const BoxConstraints(
            maxWidth: 800,
          ), // Max width for sanity
          child: ListView.builder(
            padding: const EdgeInsets.symmetric(
              horizontal: 16.0,
              vertical: 24.0,
            ),
            itemCount:
                components.length + 1, // +1 for the notes panel at the bottom
            itemBuilder: (context, index) {
              final logger = ref.read(loggerServiceProvider);

              if (index == components.length) {
                try {
                  return NotesPanelWidget(
                    notes: payload.resolvedNotes,
                    locale:
                        payload
                            .targetLocale, // Passed but unused for fallback titles now
                  );
                } catch (e, st) {
                  logger.error(
                    'SDUI Builder',
                    'VALIDATION_FAILED: NotesPanel render error',
                    e,
                    st,
                  );
                  return const SizedBox.shrink();
                }
              }

              final comp = components[index];
              try {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 24.0),
                  child: _buildComponent(context, comp, payload.targetLocale),
                );
              } catch (e, st) {
                logger.error(
                  'SDUI Builder',
                  'VALIDATION_FAILED: Widget render error for component ${comp.type}',
                  e,
                  st,
                );
                return const SizedBox.shrink();
              }
            },
          ),
        );
      },
    );
  }

  Widget _buildComponent(
    BuildContext context,
    SduiComponent comp,
    String locale,
  ) {
    switch (comp.type) {
      case 'grid_row':
        return _buildGridRow(context, comp, locale);
      case 'header':
        return _buildHeader(context, comp);
      case '1d_gauge':
        return Gauge1DWidget(component: comp);
      case '2d_matrix':
        return Matrix2DWidget(component: comp);
      case '3d_scatter':
        return Scatter3DWidget(component: comp);
      case 'metadata_header':
      case 'bibliography_footer':
        // Silently skip or add generic widgets if needed.
        return const SizedBox.shrink();
      default:
        // Graceful degradation for unknown components
        return const SizedBox.shrink();
    }
  }

  Widget _buildHeader(BuildContext context, SduiComponent comp) {
    final localizedTitle =
        SduiTranslator.translate(context, comp.title).toUpperCase();
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.green, width: 2),
        borderRadius: BorderRadius.circular(12),
        color: Colors.grey.shade50,
      ),
      child: Center(
        child: Text(
          localizedTitle,
          style: const TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.bold,
            color: Color(0xFF1A237E),
            letterSpacing: 1.0,
          ),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }

  Widget _buildGridRow(
    BuildContext context,
    SduiComponent comp,
    String locale,
  ) {
    if (comp.children.isEmpty) return const SizedBox.shrink();

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children:
          comp.children.map((child) {
            return Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 8.0),
                child: _buildComponent(context, child, locale),
              ),
            );
          }).toList(),
    );
  }
}
