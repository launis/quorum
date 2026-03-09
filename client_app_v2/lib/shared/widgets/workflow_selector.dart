import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';

class WorkflowSelector extends StatelessWidget {
  final List<Map<String, dynamic>> workflows;
  final String? selectedId;
  final ValueChanged<String?> onChanged;
  final bool isLoading;

  const WorkflowSelector({
    super.key,
    required this.workflows,
    required this.selectedId,
    required this.onChanged,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    final items =
        workflows.map((wf) {
          return DropdownMenuItem<String>(
            value: wf['id']?.toString() ?? '',
            child: Text(wf['name']?.toString() ?? 'Unknown'),
          );
        }).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (isLoading) const LinearProgressIndicator(),
        InputDecorator(
          decoration: InputDecoration(
            labelText: l10n.chooseAnalysisType,
            border: const OutlineInputBorder(),
            prefixIcon: const Icon(Icons.settings_applications),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 12.0,
              vertical: 4.0,
            ),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value:
                  _isValidSelection(selectedId, workflows) ? selectedId : null,
              items: items,
              onChanged: onChanged,
              isExpanded: true,
            ),
          ),
        ),
      ],
    );
  }

  bool _isValidSelection(String? id, List<Map<String, dynamic>> workflows) {
    if (id == null) return false;
    return workflows.any((w) => w['id'] == id);
  }
}
