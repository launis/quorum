import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/blueprint_editor_controller.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// **Blueprint Editor View (Phase 9 Rebuild)**
///
/// Replaced the visual canvas builder with a clean parameter router
/// aligning strictly with the `ReportRendererWidget` MVC pattern.
class BlueprintEditorView extends ConsumerStatefulWidget {
  final Map<String, dynamic> initialBlueprint;
  final ValueChanged<Map<String, dynamic>> onSave;

  const BlueprintEditorView({
    super.key,
    required this.initialBlueprint,
    required this.onSave,
  });

  @override
  ConsumerState<BlueprintEditorView> createState() =>
      _BlueprintEditorViewState();
}

class _BlueprintEditorViewState extends ConsumerState<BlueprintEditorView> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref
          .read(blueprintEditorControllerProvider.notifier)
          .initialize(widget.initialBlueprint);
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final outputMapping = ref.watch(blueprintEditorControllerProvider);
    final controller = ref.read(blueprintEditorControllerProvider.notifier);

    final presetView = SafeCast.safeString(
      outputMapping['preset_view'],
      '1d_metrics',
    );

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.blueprintEditorTitle),
        actions: [
          FilledButton.icon(
            onPressed: () {
              widget.onSave(outputMapping);
              Navigator.of(context).pop();
            },
            icon: const Icon(Icons.check),
            label: Text(l10n.save),
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.studioViewsBlueprintRulesTitle,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: DropdownButtonFormField<String>(
                  initialValue: presetView.isEmpty ? '1d_metrics' : presetView,
                  decoration: InputDecoration(
                    labelText: l10n.studioViewsPresetViewTheme,
                    border: const OutlineInputBorder(),
                  ),
                  items: [
                    DropdownMenuItem(
                      value: '1d_metrics',
                      child: Text(l10n.studioViews1dMetricsList),
                    ),
                    DropdownMenuItem(
                      value: '2d_compare',
                      child: Text(l10n.studioViews2dCompare),
                    ),
                    DropdownMenuItem(
                      value: '3d_complex',
                      child: Text(l10n.studioViews3dComplex),
                    ),
                  ],
                  onChanged: (val) {
                    if (val != null) {
                      controller.setPresetView(val);
                    }
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
