import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/step_simulation.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/views/widgets/prompt_preview_dialog.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Desktop-class modal dialog for simulating and previewing compiled step prompts.
class StepSimulationDialog extends ConsumerStatefulWidget {
  final NodeStrategy step;

  const StepSimulationDialog({super.key, required this.step});

  @override
  ConsumerState<StepSimulationDialog> createState() =>
      _StepSimulationDialogState();
}

class _StepSimulationDialogState extends ConsumerState<StepSimulationDialog> {
  final _formKey = GlobalKey<FormState>();
  final Map<String, TextEditingController> _inputControllers = {};
  late final TextEditingController _contextTextController;
  String _targetLocale = 'en';
  bool _isRunning = false;
  StepSimulationResponse? _simulationResult;

  @override
  void initState() {
    super.initState();
    _contextTextController = TextEditingController(
      text: '[SIMULATED CONTEXT DOCUMENT]',
    );

    for (final inputName in widget.step.expectedInputs) {
      _inputControllers[inputName] = TextEditingController();
    }
  }

  @override
  void dispose() {
    _contextTextController.dispose();
    for (final controller in _inputControllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  Future<void> _runSimulation() async {
    if (_isRunning) return;
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();

    setState(() => _isRunning = true);

    final mockInputs = <String, dynamic>{};
    for (final entry in _inputControllers.entries) {
      mockInputs[entry.key] = entry.value.text;
    }

    final request = StepSimulationRequest(
      step: widget.step,
      mockInputs: mockInputs,
      targetLocale: _targetLocale,
      contextText: _contextTextController.text,
    );

    try {
      final response = await ref
          .read(stepsControllerProvider.notifier)
          .simulateStep(request);
      if (!mounted) return;
      setState(() {
        _simulationResult = response;
        _isRunning = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _isRunning = false);
      final l10n = AppLocalizations.of(context)!;
      await showDialog<void>(
        context: context,
        builder: (errCtx) => AlertDialog(
          title: Text(l10n.errorUnknown),
          content: Text(e.toString()),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(errCtx).pop(),
              child: Text(l10n.dialogOk),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Dialog(
      insetPadding: AppSpacing.p16,
      child: ConstrainedBox(
        constraints: const BoxConstraints(
          minWidth: 640,
          maxWidth: 1100,
          minHeight: 550,
          maxHeight: 850,
        ),
        child: Scaffold(
          appBar: AppBar(
            title: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(l10n.stepSimulationTitle),
                Text(
                  l10n.stepSimulationSubtitle,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ],
            ),
            leading: IconButton(
              icon: const Icon(Icons.close),
              onPressed: () => Navigator.of(context).pop(),
            ),
            actions: [
              Padding(
                padding: const EdgeInsets.only(right: 16.0),
                child: FilledButton.icon(
                  onPressed: _isRunning ? null : _runSimulation,
                  icon: _isRunning
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.play_arrow),
                  label: Text(l10n.runSimulationBtn),
                ),
              ),
            ],
          ),
          body: LayoutBuilder(
            builder: (context, constraints) {
              final isWide = constraints.maxWidth >= 900;
              if (isWide) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(width: 380, child: _buildConfigForm(context)),
                    const VerticalDivider(width: 1),
                    Expanded(child: _buildPreviewPane(context)),
                  ],
                );
              } else {
                return DefaultTabController(
                  length: 2,
                  child: Column(
                    children: [
                      TabBar(
                        tabs: [
                          Tab(text: l10n.expectedInputsSection),
                          Tab(text: l10n.previewPromptTitle),
                        ],
                      ),
                      Expanded(
                        child: TabBarView(
                          children: [
                            _buildConfigForm(context),
                            _buildPreviewPane(context),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              }
            },
          ),
        ),
      ),
    );
  }

  Widget _buildConfigForm(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return Form(
      key: _formKey,
      child: ListView(
        padding: AppSpacing.p16,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  l10n.targetLocaleLabel,
                  style: theme.textTheme.titleSmall,
                ),
              ),
              DropdownButton<String>(
                value: _targetLocale,
                isDense: true,
                items: const [
                  DropdownMenuItem(value: 'en', child: Text('English (en)')),
                  DropdownMenuItem(value: 'fi', child: Text('Suomi (fi)')),
                ],
                onChanged: (val) {
                  if (val != null) {
                    setState(() => _targetLocale = val);
                  }
                },
              ),
            ],
          ),
          AppSpacing.h16,
          Text(l10n.contextDocumentLabel, style: theme.textTheme.titleSmall),
          AppSpacing.h8,
          TextFormField(
            controller: _contextTextController,
            maxLines: 4,
            decoration: InputDecoration(
              border: const OutlineInputBorder(),
              hintText: l10n.contextDocumentLabel,
            ),
          ),
          AppSpacing.h16,
          Text(l10n.expectedInputsSection, style: theme.textTheme.titleSmall),
          AppSpacing.h8,
          if (widget.step.expectedInputs.isEmpty)
            Card(
              elevation: 0,
              color: theme.colorScheme.surfaceContainerHighest,
              child: Padding(
                padding: AppSpacing.p12,
                child: Text(
                  l10n.noExpectedInputsNotice,
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              ),
            )
          else
            ...widget.step.expectedInputs.map((inputName) {
              final controller = _inputControllers[inputName]!;
              return Padding(
                padding: const EdgeInsets.only(bottom: 12.0),
                child: TextFormField(
                  controller: controller,
                  decoration: InputDecoration(
                    labelText: inputName,
                    border: const OutlineInputBorder(),
                    isDense: true,
                  ),
                ),
              );
            }),
        ],
      ),
    );
  }

  Widget _buildPreviewPane(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final result = _simulationResult;

    if (result == null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.play_circle_outline,
              size: 48,
              color: theme.colorScheme.onSurfaceVariant,
            ),
            AppSpacing.h16,
            Text(
              l10n.runSimulationBtn,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
        ),
      );
    }

    final promptContext = result.promptContext;
    final staticText = promptContext != null
        ? PromptPreviewFormatter.formatMessages(promptContext.staticMessages)
        : '';
    final dynamicText = promptContext != null
        ? PromptPreviewFormatter.formatMessages(promptContext.dynamicMessages)
        : '';
    final schemaText = result.renderedPrompt;

    return Column(
      children: [
        if (!result.valid && result.errors.isNotEmpty)
          Container(
            width: double.infinity,
            padding: AppSpacing.p12,
            color: theme.colorScheme.errorContainer,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: result.errors
                  .map(
                    (err) => Text(
                      '• $err',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onErrorContainer,
                      ),
                    ),
                  )
                  .toList(),
            ),
          ),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          color: theme.colorScheme.surfaceContainerLowest,
          child: Row(
            children: [
              Text(
                '${l10n.stepSimulationExecutionTime}: ${result.trace.executionTimeMs.toStringAsFixed(1)} ms',
                style: theme.textTheme.labelSmall,
              ),
              AppSpacing.w16,
              Text(
                '${l10n.stepSimulationEstimatedTokens}: ~${result.trace.estimatedTokens}',
                style: theme.textTheme.labelSmall,
              ),
            ],
          ),
        ),
        const Divider(height: 1),
        Expanded(
          child: DefaultTabController(
            length: 3,
            child: Column(
              children: [
                TabBar(
                  isScrollable: true,
                  tabs: [
                    Tab(text: l10n.previewPromptStaticTab),
                    Tab(text: l10n.previewPromptDynamicTab),
                    Tab(text: l10n.previewPromptSchemaTab),
                  ],
                ),
                Expanded(
                  child: TabBarView(
                    children: [
                      _buildCodeContainer(context, staticText),
                      _buildCodeContainer(context, dynamicText),
                      _buildCodeContainer(context, schemaText),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildCodeContainer(BuildContext context, String content) {
    final theme = Theme.of(context);
    return Padding(
      padding: AppSpacing.p16,
      child: Container(
        width: double.infinity,
        padding: AppSpacing.p16,
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceContainerLowest,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: theme.colorScheme.outlineVariant),
        ),
        child: content.isEmpty
            ? Center(
                child: Text(
                  '---',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
              )
            : SingleChildScrollView(
                child: SelectableText(
                  content,
                  style: theme.textTheme.bodySmall?.copyWith(
                    fontFamily: 'monospace',
                    fontFamilyFallback: const ['Courier', 'Consolas'],
                  ),
                ),
              ),
      ),
    );
  }
}
