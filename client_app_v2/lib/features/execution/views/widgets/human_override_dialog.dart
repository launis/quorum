import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
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
  late ExecutionStatus _selectedStatus;
  final _reasonController = TextEditingController();
  final List<QuoteEvidenceDto> _quotes = [];
  bool _isLoading = false;

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
  }

  Future<void> _submitOverride() async {
    final l10n = AppLocalizations.of(context)!;
    final reason = _reasonController.text.trim();
    if (reason.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(l10n.humanOverrideReasonRequired)));
      return;
    }

    setState(() => _isLoading = true);
    try {
      final client = ref.read(executionClientProvider);

      final payload = {
        'new_status': _selectedStatus == ExecutionStatus.passed
            ? 'PASSED'
            : 'FAILED',
        'reason': reason,
        'evidence_quotes': _quotes
            .map(
              (q) => {
                'quote': q.quote,
                'verified_source_ids': q.verifiedSourceIds,
                'unverified_aliases': q.unverifiedAliases,
                'is_verified': q.isVerified,
              },
            )
            .toList(),
      };

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
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.humanOverrideSaveFailed(e.toString()))),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return AlertDialog(
      title: Text('👨‍⚖️ ${l10n.humanOverrideTitle}'),
      content: SizedBox(
        width: 500,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                l10n.humanOverrideClaimLabel(widget.atom.claimLabel),
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<ExecutionStatus>(
                initialValue: _selectedStatus,
                items: const [
                  DropdownMenuItem(
                    value: ExecutionStatus.passed,
                    child: Text('PASS'),
                  ),
                  DropdownMenuItem(
                    value: ExecutionStatus.failed,
                    child: Text('FAIL'),
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
              TextField(
                controller: _reasonController,
                decoration: InputDecoration(
                  labelText: l10n.humanOverrideReasonLabel,
                  border: const OutlineInputBorder(),
                ),
                maxLines: 3,
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
                  style: const TextStyle(
                    fontStyle: FontStyle.italic,
                    color: Colors.grey,
                  ),
                ),
              ..._quotes.map(
                (q) => Card(
                  elevation: 0,
                  color: Colors.grey.shade50,
                  shape: RoundedRectangleBorder(
                    side: BorderSide(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: ListTile(
                    dense: true,
                    title: Text(q.quote, style: const TextStyle(fontSize: 13)),
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
      actions: [
        TextButton(
          onPressed: _isLoading ? null : () => Navigator.of(context).pop(false),
          child: Text(l10n.cancel),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _submitOverride,
          child: _isLoading
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : Text(l10n.humanOverrideSaveBtn),
        ),
      ],
    );
  }
}
