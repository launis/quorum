import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/features/execution/models/human_override_request_dto.dart';
import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class HumanOverrideDialog extends ConsumerStatefulWidget {
  final ScorecardAtomDto atom;
  final String executionId;

  const HumanOverrideDialog({
    super.key,
    required this.atom,
    required this.executionId,
  });

  @override
  ConsumerState<HumanOverrideDialog> createState() =>
      _HumanOverrideDialogState();
}

class _HumanOverrideDialogState extends ConsumerState<HumanOverrideDialog> {
  final _formKey = GlobalKey<FormState>();
  late ExecutionStatus _selectedStatus;
  final _reasonController = TextEditingController();
  final List<QuoteEvidenceDto> _quotes = [];
  bool _isSaving = false;
  String? _errorMessage;
  late final String _initialRequestJson;

  @override
  void initState() {
    super.initState();
    _selectedStatus =
        widget.atom.humanOverride?.newStatus ??
        widget.atom.status ??
        ExecutionStatus.passed;

    if (_selectedStatus != ExecutionStatus.passed &&
        _selectedStatus != ExecutionStatus.failed) {
      _selectedStatus = ExecutionStatus.passed;
    }

    _reasonController.text = widget.atom.humanOverride?.reason ?? '';
    _quotes.addAll(
      widget.atom.humanOverride?.evidenceQuotes ?? widget.atom.exactQuotes,
    );
    _initialRequestJson = jsonEncode(_buildRequestDto().toJson());
  }

  @override
  void dispose() {
    _reasonController.dispose();
    super.dispose();
  }

  HumanOverrideRequestDto _buildRequestDto() {
    return HumanOverrideRequestDto(
      newStatus: _selectedStatus,
      reason: _reasonController.text.trim(),
      evidenceQuotes: List<QuoteEvidenceDto>.from(_quotes),
    );
  }

  bool _isDirty() {
    return jsonEncode(_buildRequestDto().toJson()) != _initialRequestJson;
  }

  void _handleDismiss() {
    FocusScope.of(context).unfocus();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      if (!_isDirty()) {
        Navigator.of(context).pop(false);
        return;
      }

      final l10n = AppLocalizations.of(context)!;
      showDialog<void>(
        context: context,
        builder: (dialogCtx) => AlertDialog(
          title: Text(l10n.discardChangesConfirmTitle),
          content: Text(l10n.discardChangesConfirmMessage),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogCtx).pop(),
              child: Text(l10n.keepEditingButtonLabel),
            ),
            FilledButton(
              onPressed: () {
                Navigator.of(dialogCtx).pop();
                Navigator.of(context).pop(false);
              },
              child: Text(l10n.discardButtonLabel),
            ),
          ],
        ),
      );
    });
  }

  Future<void> _submitOverride() async {
    final l10n = AppLocalizations.of(context)!;
    if (_isSaving) return;
    _isSaving = true;

    if (!_formKey.currentState!.validate()) {
      _isSaving = false;
      return;
    }
    final reason = _reasonController.text.trim();

    setState(() {
      _errorMessage = null;
    });

    try {
      final client = ref.read(executionClientProvider);

      final payload = HumanOverrideRequestDto(
        newStatus: _selectedStatus,
        reason: reason,
        evidenceQuotes: List<QuoteEvidenceDto>.from(_quotes),
      );

      await client.overrideAtom(
        executionId: widget.executionId,
        atomId: widget.atom.atomId,
        payload: payload,
      );

      if (mounted) {
        Navigator.of(context).pop(true);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = l10n.humanOverrideSaveFailed(e.toString());
        });
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (!didPop) _handleDismiss();
      },
      child: AlertDialog(
        title: Text(l10n.humanOverrideTitle),
        content: ConstrainedBox(
          constraints: const BoxConstraints(
            minWidth: 480,
            maxWidth: 1400,
            minHeight: 600,
          ),
          child: SizedBox(
            width: 500,
            child: SingleChildScrollView(
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    if (_errorMessage != null) ...[
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.errorContainer,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          _errorMessage!,
                          style: TextStyle(
                            color: theme.colorScheme.onErrorContainer,
                            fontSize: 12,
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                    ],
                    Text(
                      l10n.humanOverrideClaimLabel(widget.atom.claimLabel),
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<ExecutionStatus>(
                      initialValue: _selectedStatus,
                      items: [
                        DropdownMenuItem(
                          value: ExecutionStatus.passed,
                          child: Text(
                            ExecutionStatus.passed.name.toUpperCase(),
                          ),
                        ),
                        DropdownMenuItem(
                          value: ExecutionStatus.failed,
                          child: Text(
                            ExecutionStatus.failed.name.toUpperCase(),
                          ),
                        ),
                      ],
                      onChanged: (val) {
                        if (val != null) setState(() => _selectedStatus = val);
                      },
                      decoration: InputDecoration(
                        labelText: l10n.humanOverrideNewStatusLabel,
                        border: const OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _reasonController,
                      decoration: InputDecoration(
                        labelText: l10n.humanOverrideReasonLabel,
                        border: const OutlineInputBorder(),
                      ),
                      maxLines: 3,
                      validator: (val) {
                        if (val == null || val.trim().isEmpty) {
                          return l10n.humanOverrideReasonRequired;
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 24),
                    Text(
                      l10n.humanOverrideQuotesTitle,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    if (_quotes.isEmpty)
                      Text(
                        l10n.humanOverrideNoQuotes,
                        style: TextStyle(
                          fontStyle: FontStyle.italic,
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ..._quotes.map(
                      (q) => Card(
                        elevation: 0,
                        color: theme.colorScheme.surfaceContainerLow,
                        shape: RoundedRectangleBorder(
                          side: BorderSide(
                            color: theme.colorScheme.outlineVariant,
                          ),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: ListTile(
                          dense: true,
                          title: Text(
                            q.quote,
                            style: const TextStyle(fontSize: 13),
                          ),
                          subtitle: Text(
                            q.verifiedSourceIds.isNotEmpty
                                ? q.verifiedSourceIds.join(', ')
                                : (q.unverifiedAliases.isNotEmpty
                                      ? q.unverifiedAliases.join(', ')
                                      : 'HUMAN_OVERRIDE'),
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 11,
                            ),
                          ),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete, size: 18),
                            onPressed: () => setState(() => _quotes.remove(q)),
                            tooltip: l10n.humanOverrideDeleteQuoteTooltip,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextButton.icon(
                      onPressed: () {
                        setState(() {
                          _quotes.add(
                            QuoteEvidenceDto(
                              verifiedSourceIds: const ['human_override'],
                              quote: l10n.humanOverrideExpertNote,
                              isVerified: true,
                            ),
                          );
                        });
                      },
                      icon: const Icon(Icons.add, size: 16),
                      label: Text(l10n.humanOverrideAddEvidenceBtn),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: _isSaving ? null : _handleDismiss,
            child: Text(l10n.cancel),
          ),
          ElevatedButton(
            onPressed: _isSaving ? null : _submitOverride,
            child: _isSaving
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Text(l10n.humanOverrideSaveBtn),
          ),
        ],
      ),
    );
  }
}
