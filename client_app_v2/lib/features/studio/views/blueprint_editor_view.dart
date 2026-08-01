import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/blueprint_editor_controller.dart';

import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// **Blueprint Editor View (Phase 9 Rebuild)**
///
/// Provides a clean parameter router
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
    final config = ref.watch(blueprintEditorControllerProvider);

    final PresetView presetView = config.presetView;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.blueprintEditorTitle),
        actions: [
          FilledButton.icon(
            onPressed: () {
              widget.onSave(config.toJson());
              Navigator.of(context).pop();
            },
            icon: const Icon(Icons.check),
            label: Text(l10n.save),
          ),
          AppSpacing.w16,
        ],
      ),
      body: Padding(
        padding: AppSpacing.p24,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.studioViewsBlueprintRulesTitle,
              style: Theme.of(context).textTheme.titleLarge,
            ),
            AppSpacing.h16,
            Card(
              child: Padding(
                padding: AppSpacing.p16,
                child: DropdownButtonFormField<PresetView>(
                  initialValue: presetView,
                  decoration: InputDecoration(
                    labelText: l10n.studioViewsPresetViewTheme,
                    border: const OutlineInputBorder(),
                  ),
                  items: [
                    DropdownMenuItem(
                      value: PresetView.metrics1d,
                      child: Text(l10n.studioViews1dMetricsList),
                    ),
                    DropdownMenuItem(
                      value: PresetView.compare2d,
                      child: Text(l10n.studioViews2dCompare),
                    ),

                    DropdownMenuItem(
                      value: PresetView.matrix3d,
                      child: Text(l10n.studioViewsMatrix3d),
                    ),
                  ],
                  onChanged: (val) {
                    if (val != null) {
                      ref
                          .read(blueprintEditorControllerProvider.notifier)
                          .setPresetView(val);
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
