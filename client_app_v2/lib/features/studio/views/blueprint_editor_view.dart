import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/studio/controllers/blueprint_editor_controller.dart';
import 'package:client_app/features/studio/models/blueprint_config.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Studio view for configuring report blueprint layout presets.
///
/// Provides a clean parameter router aligning strictly with the
/// `ReportRendererWidget` MVC pattern.
class BlueprintEditorView extends ConsumerStatefulWidget {
  final BlueprintConfig initialBlueprint;
  final ValueChanged<BlueprintConfig> onSave;

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
  Object? _initializationError;
  StackTrace? _initializationStackTrace;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      try {
        ref
            .read(blueprintEditorControllerProvider.notifier)
            .initialize(widget.initialBlueprint);
      } catch (e, st) {
        if (!mounted) return;
        setState(() {
          _initializationError = e;
          _initializationStackTrace = st;
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final config = ref.watch(blueprintEditorControllerProvider);

    final PresetView presetView = config.presetView;

    return AppErrorBoundary(
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            l10n.blueprintEditorTitle,
            overflow: TextOverflow.ellipsis,
          ),
          actions: [
            if (_initializationError == null) ...[
              FilledButton.icon(
                onPressed: () {
                  widget.onSave(config);
                  Navigator.of(context).pop();
                },
                icon: const Icon(Icons.check),
                label: Text(l10n.save, overflow: TextOverflow.ellipsis),
              ),
              AppSpacing.w16,
            ],
          ],
        ),
        body: _initializationError != null
            ? ErrorView(
                error: _initializationError!,
                stackTrace: _initializationStackTrace,
                compact: false,
              )
            : Padding(
                padding: AppSpacing.p24,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.studioViewsBlueprintRulesTitle,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                      overflow: TextOverflow.ellipsis,
                    ),
                    AppSpacing.h16,
                    Card(
                      elevation: AppSpacing.s2,
                      margin: const EdgeInsets.only(bottom: AppSpacing.s16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(AppSpacing.s12),
                      ),
                      child: Padding(
                        padding: AppSpacing.p16,
                        child: DropdownButtonFormField<PresetView>(
                          isExpanded: true,
                          initialValue: presetView,
                          decoration: InputDecoration(
                            labelText: l10n.studioViewsPresetViewTheme,
                            border: const OutlineInputBorder(),
                          ),
                          items: [
                            DropdownMenuItem(
                              value: PresetView.metrics1d,
                              child: Text(
                                l10n.studioViews1dMetricsList,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            DropdownMenuItem(
                              value: PresetView.compare2d,
                              child: Text(
                                l10n.studioViews2dCompare,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            DropdownMenuItem(
                              value: PresetView.matrix3d,
                              child: Text(
                                l10n.studioViewsMatrix3d,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                          ],
                          onChanged: (val) {
                            if (val != null) {
                              ref
                                  .read(
                                    blueprintEditorControllerProvider.notifier,
                                  )
                                  .setPresetView(val);
                            }
                          },
                        ),
                      ),
                    ),
                  ],
                ),
              ),
      ),
    );
  }
}
