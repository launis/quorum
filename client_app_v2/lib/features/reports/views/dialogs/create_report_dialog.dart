import 'dart:convert';

import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/reports/controllers/report_artifact_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Modal dialog for requesting report compilation adhering strictly to Desktop Pro Tool UX.
class CreateReportDialog extends ConsumerStatefulWidget {
  final String executionId;
  final String? workflowId;
  final String? initialProfileId;

  const CreateReportDialog({
    super.key,
    required this.executionId,
    this.workflowId,
    this.initialProfileId,
  });

  @override
  ConsumerState<CreateReportDialog> createState() => _CreateReportDialogState();
}

class _CreateReportDialogState extends ConsumerState<CreateReportDialog> {
  final _formKey = GlobalKey<FormState>();
  final _profileFieldKey = GlobalKey();
  final _prefaceFieldKey = GlobalKey();

  final _prefaceController = TextEditingController();
  final _profileFocusNode = FocusNode();
  final _prefaceFocusNode = FocusNode();

  static const _labelFi = 'Suomi (FI)';
  static const _labelEn = 'English (EN)';

  String? _selectedProfileId;
  String _selectedLocale = 'fi';
  List<OutputProfile> _availableProfiles = [];
  bool _isLoadingProfiles = true;
  String? _inlineError;
  bool _isSaving = false;
  late final String _initialStateJson;

  @override
  void initState() {
    super.initState();
    _selectedProfileId = widget.initialProfileId;
    _initialStateJson = _computeStateJson();
    _loadProfiles();
  }

  @override
  void dispose() {
    _prefaceController.dispose();
    _profileFocusNode.dispose();
    _prefaceFocusNode.dispose();
    super.dispose();
  }

  String _computeStateJson() {
    return jsonEncode({
      'profile_id': _selectedProfileId,
      'locale': _selectedLocale,
      'preface': _prefaceController.text.trim(),
    });
  }

  bool _isModelDirty() => _computeStateJson() != _initialStateJson;

  bool _hasPendingInputBuffers() => _prefaceController.text.isNotEmpty;

  Future<void> _loadProfiles() async {
    try {
      String? targetWorkflowId = widget.workflowId;
      if (targetWorkflowId == null) {
        final execClient = ref.read(executionClientProvider);
        final execStatus = await execClient.getExecutionStatus(
          widget.executionId,
        );
        targetWorkflowId = execStatus.workflowId;
      }

      final client = ref.read(studioClientProvider);
      final allProfiles = await client.getOutputProfiles();
      if (!mounted) return;
      final profiles = allProfiles
          .where((p) => p.workflowId == targetWorkflowId)
          .toList();
      setState(() {
        _availableProfiles = profiles;
        _isLoadingProfiles = false;
        if (_selectedProfileId == null && profiles.isNotEmpty) {
          _selectedProfileId = profiles.first.id;
        }
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _inlineError = e.toString();
        _isLoadingProfiles = false;
      });
    }
  }

  void _handleDismiss() {
    FocusScope.of(context).unfocus();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      final isDirty = _isModelDirty() || _hasPendingInputBuffers();
      if (!isDirty) {
        Navigator.of(context).pop(null);
      } else {
        _showDiscardConfirm();
      }
    });
  }

  void _showDiscardConfirm() {
    final l10n = AppLocalizations.of(context)!;
    showDialog<bool>(
      context: context,
      builder: (confirmCtx) => AlertDialog(
        title: Text(l10n.discardChangesConfirmTitle),
        content: Text(l10n.discardChangesConfirmMessage),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(confirmCtx).pop(false),
            child: Text(l10n.keepEditingButtonLabel),
          ),
          FilledButton(
            style: FilledButton.styleFrom(
              backgroundColor: Theme.of(confirmCtx).colorScheme.error,
              foregroundColor: Theme.of(confirmCtx).colorScheme.onError,
            ),
            onPressed: () {
              Navigator.of(confirmCtx).pop(true);
              Navigator.of(context).pop(null);
            },
            child: Text(l10n.discardButtonLabel),
          ),
        ],
      ),
    );
  }

  Future<void> _handleSave() async {
    if (_isSaving) return;

    // Reset error surface
    setState(() {
      _inlineError = null;
      _isSaving = true;
    });

    FocusScope.of(context).unfocus();

    if (!_formKey.currentState!.validate()) {
      setState(() {
        _isSaving = false;
      });
      // Auto-scroll to first invalid input
      if (_selectedProfileId == null) {
        Scrollable.ensureVisible(_profileFieldKey.currentContext ?? context);
        _profileFocusNode.requestFocus();
      }
      return;
    }

    _formKey.currentState!.save();

    try {
      final summary = await ref
          .read(reportArtifactActionsProvider.notifier)
          .createReport(
            executionId: widget.executionId,
            profileId: _selectedProfileId!,
            locale: _selectedLocale,
            customPrefaceMd: _prefaceController.text.trim().isEmpty
                ? null
                : _prefaceController.text.trim(),
          );

      if (!mounted) return;
      Navigator.of(context).pop(summary);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _inlineError = e.toString();
        _isSaving = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final l10n = AppLocalizations.of(context)!;

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (!didPop) _handleDismiss();
      },
      child: CallbackShortcuts(
        bindings: {
          const SingleActivator(LogicalKeyboardKey.escape): _handleDismiss,
          const SingleActivator(LogicalKeyboardKey.keyS, control: true):
              _handleSave,
          const SingleActivator(LogicalKeyboardKey.keyS, meta: true):
              _handleSave,
        },
        child: FocusScope(
          child: AppErrorBoundary(
            child: Dialog(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: ConstrainedBox(
                constraints: const BoxConstraints(
                  minWidth: 480,
                  maxWidth: 640,
                  minHeight: 400,
                  maxHeight: 720,
                ),
                child: Padding(
                  padding: AppSpacing.p24,
                  child: FocusTraversalGroup(
                    child: Form(
                      key: _formKey,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // Header
                          Row(
                            children: [
                              Expanded(
                                child: Text(
                                  l10n.createReportDialogTitle,
                                  style: theme.textTheme.titleLarge?.copyWith(
                                    fontWeight: FontWeight.bold,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              IconButton(
                                icon: const Icon(Icons.close),
                                tooltip: l10n.close,
                                mouseCursor: SystemMouseCursors.click,
                                onPressed: _handleDismiss,
                              ),
                            ],
                          ),
                          const Divider(),
                          AppSpacing.h16,

                          // Modal-Internal Error Surface (Absolute SnackBar Ban)
                          if (_inlineError != null) ...[
                            Container(
                              padding: AppSpacing.p12,
                              decoration: BoxDecoration(
                                color: colorScheme.errorContainer,
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: colorScheme.error),
                              ),
                              child: Row(
                                children: [
                                  Icon(
                                    Icons.error_outline,
                                    color: colorScheme.onErrorContainer,
                                  ),
                                  AppSpacing.w12,
                                  Expanded(
                                    child: Text(
                                      _inlineError!,
                                      style: theme.textTheme.bodyMedium
                                          ?.copyWith(
                                            color: colorScheme.onErrorContainer,
                                          ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            AppSpacing.h16,
                          ],

                          // Form Content Body
                          Expanded(
                            child: SingleChildScrollView(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.stretch,
                                children: [
                                  // Profile selector dropdown
                                  if (_isLoadingProfiles)
                                    const Center(
                                      child: CircularProgressIndicator(),
                                    )
                                  else if (_availableProfiles.isEmpty)
                                    Container(
                                      padding: AppSpacing.p12,
                                      decoration: BoxDecoration(
                                        color:
                                            colorScheme.surfaceContainerHighest,
                                        borderRadius: BorderRadius.circular(8),
                                        border: Border.all(
                                          color: colorScheme.outlineVariant,
                                        ),
                                      ),
                                      child: Row(
                                        children: [
                                          Icon(
                                            Icons.info_outline,
                                            color: colorScheme.primary,
                                          ),
                                          AppSpacing.w12,
                                          Expanded(
                                            child: Text(
                                              l10n.noProfilesForWorkflow,
                                              style: theme.textTheme.bodyMedium
                                                  ?.copyWith(
                                                    color: colorScheme
                                                        .onSurfaceVariant,
                                                  ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    )
                                  else
                                    DropdownButtonFormField<String>(
                                      key: _profileFieldKey,
                                      focusNode: _profileFocusNode,
                                      isExpanded: true,
                                      initialValue: _selectedProfileId,
                                      decoration: InputDecoration(
                                        labelText:
                                            l10n.outputProfileSelectLabel,
                                        border: const OutlineInputBorder(),
                                        prefixIcon: const Icon(
                                          Icons.palette_outlined,
                                        ),
                                      ),
                                      items: _availableProfiles
                                          .map(
                                            (p) => DropdownMenuItem(
                                              value: p.id,
                                              child: Text(
                                                p.name.get(_selectedLocale),
                                                overflow: TextOverflow.ellipsis,
                                              ),
                                            ),
                                          )
                                          .toList(),
                                      validator: (val) {
                                        if (val == null || val.isEmpty) {
                                          return l10n.outputProfileSelectLabel;
                                        }
                                        return null;
                                      },
                                      onChanged: (val) {
                                        setState(() {
                                          _selectedProfileId = val;
                                        });
                                      },
                                    ),
                                  AppSpacing.h16,

                                  // Locale selector dropdown
                                  DropdownButtonFormField<String>(
                                    isExpanded: true,
                                    initialValue: _selectedLocale,
                                    decoration: InputDecoration(
                                      labelText: l10n.localeSelectLabel,
                                      border: const OutlineInputBorder(),
                                      prefixIcon: const Icon(
                                        Icons.language_outlined,
                                      ),
                                    ),
                                    items: const [
                                      DropdownMenuItem(
                                        value: 'fi',
                                        child: Text(_labelFi),
                                      ),
                                      DropdownMenuItem(
                                        value: 'en',
                                        child: Text(_labelEn),
                                      ),
                                    ],
                                    onChanged: (val) {
                                      if (val != null) {
                                        setState(() {
                                          _selectedLocale = val;
                                        });
                                      }
                                    },
                                  ),
                                  AppSpacing.h16,

                                  // Custom preface text area
                                  TextFormField(
                                    key: _prefaceFieldKey,
                                    focusNode: _prefaceFocusNode,
                                    controller: _prefaceController,
                                    maxLines: 4,
                                    decoration: InputDecoration(
                                      labelText: l10n.customPrefaceLabel,
                                      alignLabelWithHint: true,
                                      border: const OutlineInputBorder(),
                                      prefixIcon: const Icon(
                                        Icons.format_quote_outlined,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),

                          AppSpacing.h16,
                          const Divider(),
                          AppSpacing.h8,

                          // Action Buttons
                          Row(
                            mainAxisAlignment: MainAxisAlignment.end,
                            children: [
                              TextButton(
                                onPressed: _isSaving ? null : _handleDismiss,
                                child: Text(l10n.close),
                              ),
                              AppSpacing.w12,
                              FilledButton.icon(
                                icon: _isSaving
                                    ? const SizedBox(
                                        width: 16,
                                        height: 16,
                                        child: CircularProgressIndicator(
                                          strokeWidth: 2,
                                        ),
                                      )
                                    : const Icon(Icons.auto_awesome),
                                label: Text(l10n.saveReportButtonLabel),
                                onPressed:
                                    _isSaving || _availableProfiles.isEmpty
                                    ? null
                                    : _handleSave,
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
