import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';
import 'package:client_app/core/api/execution_client.dart';

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
  late String _selectedStatus;
  final _reasonController = TextEditingController();
  final List<QuoteEvidenceDto> _quotes = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _selectedStatus =
        widget.atom.humanOverride?.newStatus ?? widget.atom.status ?? 'PASS';
    // Validate that it's one of PASS, FAIL, CONTESTED
    final upperStatus = _selectedStatus.toUpperCase();
    if (upperStatus != 'PASS' &&
        upperStatus != 'FAIL' &&
        upperStatus != 'CONTESTED') {
      _selectedStatus = 'PASS';
    } else {
      _selectedStatus = upperStatus;
    }

    _reasonController.text = widget.atom.humanOverride?.reason ?? '';
    _quotes.addAll(
      widget.atom.humanOverride?.evidenceQuotes ?? widget.atom.exactQuotes,
    );
  }

  Future<void> _submitOverride() async {
    final reason = _reasonController.text.trim();
    if (reason.isEmpty) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Perustelu on pakollinen.')));
      return;
    }

    setState(() => _isLoading = true);
    try {
      final client = ref.read(executionClientProvider);

      final payload = {
        'new_status': _selectedStatus,
        'reason': reason,
        'evidence_quotes': _quotes
            .map(
              (q) => {
                'source_id': q.sourceId,
                'quote_text': q.quoteText,
                'display_name': q.displayName,
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
        ScaffoldMessenger.of(
          context,
        ).showSnackBar(SnackBar(content: Text('Tallennus epäonnistui: $e')));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('👨‍⚖️ Yliohjaa päätös (EU AI Act)'),
      content: SizedBox(
        width: 500,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Väite: ${widget.atom.claimLabel}',
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                initialValue: _selectedStatus,
                items: const [
                  DropdownMenuItem(value: 'PASS', child: Text('PASS')),
                  DropdownMenuItem(value: 'FAIL', child: Text('FAIL')),
                  DropdownMenuItem(
                    value: 'CONTESTED',
                    child: Text('CONTESTED'),
                  ),
                ],
                onChanged: (val) {
                  if (val != null) setState(() => _selectedStatus = val);
                },
                decoration: const InputDecoration(
                  labelText: 'Uusi arvosana',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _reasonController,
                decoration: const InputDecoration(
                  labelText: 'Perustelu yliohjaukselle',
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 24),
              const Text(
                'Lainaukset (tekninen vedostus)',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              if (_quotes.isEmpty)
                const Text(
                  'Ei lainauksia.',
                  style: TextStyle(
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
                    title: Text(
                      q.quoteText,
                      style: const TextStyle(fontSize: 13),
                    ),
                    subtitle: Text(
                      q.displayName ?? q.sourceId ?? 'HUMAN_OVERRIDE',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                      ),
                    ),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete, size: 18),
                      onPressed: () => setState(() => _quotes.remove(q)),
                      tooltip: 'Poista',
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 8),
              TextButton.icon(
                onPressed: () {
                  setState(() {
                    _quotes.add(
                      const QuoteEvidenceDto(
                        sourceId: 'human_override',
                        displayName: 'HUMAN_OVERRIDE',
                        quoteText: 'Asiantuntijan vahvistama huomio',
                      ),
                    );
                  });
                },
                icon: const Icon(Icons.add, size: 16),
                label: const Text('Lisää todiste'),
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: _isLoading ? null : () => Navigator.of(context).pop(false),
          child: const Text('Peruuta'),
        ),
        ElevatedButton(
          onPressed: _isLoading ? null : _submitOverride,
          child: _isLoading
              ? const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Tallenna Override'),
        ),
      ],
    );
  }
}
