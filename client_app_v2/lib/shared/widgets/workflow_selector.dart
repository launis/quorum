import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
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
    final locale = Localizations.localeOf(context).languageCode;

    final items = workflows.map((wf) {
      final nameRaw = wf['name'];
      String nameStr = l10n.sharedUnknown;
      if (nameRaw is Map) {
        nameStr = I18nText.fromJson(
          Map<String, dynamic>.from(nameRaw),
        ).get(locale);
      } else if (nameRaw is String && nameRaw.isNotEmpty) {
        nameStr = nameRaw;
      }
      return DropdownMenuItem<String>(
        value: wf['id']?.toString() ?? '',
        child: Text(nameStr),
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
              value: _isValidSelection(selectedId, workflows)
                  ? selectedId
                  : null,
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
