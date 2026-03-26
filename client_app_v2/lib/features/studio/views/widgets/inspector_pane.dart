import 'package:flutter/material.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/error/app_exception.dart';

class InspectorPane extends StatelessWidget {
  final String? selectedStepId;
  final Map<String, dynamic> workflow;
  final List<Map<String, dynamic>> availableBlueprints;
  final Function(String stepId, Map<String, dynamic> updatedStep) onStepUpdated;
  final VoidCallback onAddStep;
  final Function(String stepId) onDeleteStep;

  const InspectorPane({
    super.key,
    required this.selectedStepId,
    required this.workflow,
    required this.availableBlueprints,
    required this.onStepUpdated,
    required this.onAddStep,
    required this.onDeleteStep,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    if (selectedStepId == null) {
      return Container(
        width: 350,
        color: Theme.of(context).cardColor,
        child: Column(
          children: [
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Text(
                'Inspector',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            const Spacer(),
            const Text(
              'Select a node to inspect',
              style: TextStyle(color: Colors.grey),
            ),
            const Spacer(),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: FilledButton.icon(
                onPressed: onAddStep,
                icon: const Icon(Icons.add),
                label: const Text('Add Node'),
              ),
            ),
          ],
        ),
      );
    }

    final steps = SafeCast.safeList(workflow['steps']);
    final stepDef = steps.firstWhere(
      (s) => SafeCast.safeString(SafeCast.safeMap(s)['id']) == selectedStepId,
      orElse: () => <String, dynamic>{},
    );

    if (stepDef.isEmpty) {
      throw AppException.validation(
        'Selected step definition not found: $selectedStepId. Data is corrupted.',
      );
    }

    return Container(
      width: 350,
      color: Theme.of(context).cardColor,
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Node Inspector',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () => onDeleteStep(selectedStepId!),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: _buildInspectorForm(
                context,
                SafeCast.safeMap(stepDef),
                l10n,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInspectorForm(
    BuildContext context,
    Map<String, dynamic> stepDef,
    AppLocalizations l10n,
  ) {
    final rawId = stepDef['id'];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (rawId != null) ...[
          const Text(
            'Node ID',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 12,
              color: Colors.grey,
            ),
          ),
          SelectableText(
            SafeCast.safeString(rawId),
            style: const TextStyle(fontFamily: 'monospace'),
          ),
          const SizedBox(height: 16),
        ],
        DropdownButtonFormField<String>(
          decoration: const InputDecoration(
            labelText: 'Task Blueprint',
            isDense: true,
          ),
          isExpanded: true,
          initialValue:
              availableBlueprints.any(
                    (bp) => bp['slug'] == stepDef['task_blueprint'],
                  )
                  ? stepDef['task_blueprint'] as String?
                  : null,
          items:
              availableBlueprints.map((bp) {
                final slug = SafeCast.safeString(bp['slug']);
                final nameMap = SafeCast.safeMap(bp['name']);
                final transMap = SafeCast.safeMap(nameMap['translations']);

                // Nomenclature Resolution: Fetch based on locale, fallback to 'en', then slug.
                final currentLocale =
                    Localizations.localeOf(context).languageCode;
                final label = SafeCast.safeString(
                  transMap[currentLocale],
                  SafeCast.safeString(transMap['en'], slug),
                );

                return DropdownMenuItem(
                  value: slug,
                  child: Text(label, overflow: TextOverflow.ellipsis),
                );
              }).toList(),
          onChanged: (val) {
            final copy = Map<String, dynamic>.from(stepDef);
            copy['task_blueprint'] = val;
            onStepUpdated(selectedStepId!, copy);
          },
        ),
        const SizedBox(height: 16),
        const Text(
          'Depends On (Comma separated IDs)',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
        ),
        const SizedBox(height: 4),
        TextFormField(
          initialValue: SafeCast.safeList(stepDef['depends_on']).join(', '),
          decoration: const InputDecoration(
            isDense: true,
            border: OutlineInputBorder(),
          ),
          onFieldSubmitted: (val) {
            final copy = Map<String, dynamic>.from(stepDef);
            copy['depends_on'] =
                val
                    .split(',')
                    .map((e) => e.trim())
                    .where((e) => e.isNotEmpty)
                    .toList();
            onStepUpdated(selectedStepId!, copy);
          },
        ),
        const SizedBox(height: 16),
        const Text(
          'Input Mappings (Press Enter to apply)',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
        ),
        ...SafeCast.safeMap(stepDef['input_mappings']).entries.map((e) {
          return Padding(
            padding: const EdgeInsets.only(top: 8.0),
            child: Row(
              children: [
                Expanded(
                  flex: 1,
                  child: TextFormField(
                    initialValue: e.key,
                    decoration: const InputDecoration(
                      isDense: true,
                      border: OutlineInputBorder(),
                      hintText: 'Key',
                    ),
                    onFieldSubmitted: (newKey) {
                      newKey = newKey.trim();
                      if (newKey.isNotEmpty && newKey != e.key) {
                        final copy = Map<String, dynamic>.from(stepDef);
                        final maps = SafeCast.safeMap(copy['input_mappings']);
                        final val = maps.remove(e.key);
                        maps[newKey] = val;
                        copy['input_mappings'] = maps;
                        onStepUpdated(selectedStepId!, copy);
                      }
                    },
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  flex: 2,
                  child: TextFormField(
                    initialValue: e.value.toString(),
                    decoration: const InputDecoration(
                      isDense: true,
                      border: OutlineInputBorder(),
                      hintText: '\$inputs.value',
                    ),
                    onFieldSubmitted: (newVal) {
                      final copy = Map<String, dynamic>.from(stepDef);
                      final maps = SafeCast.safeMap(copy['input_mappings']);
                      maps[e.key] = newVal.trim();
                      copy['input_mappings'] = maps;
                      onStepUpdated(selectedStepId!, copy);
                    },
                  ),
                ),
                IconButton(
                  icon: const Icon(
                    Icons.remove_circle,
                    color: Colors.red,
                    size: 20,
                  ),
                  onPressed: () {
                    final copy = Map<String, dynamic>.from(stepDef);
                    final maps = SafeCast.safeMap(copy['input_mappings']);
                    maps.remove(e.key);
                    copy['input_mappings'] = maps;
                    onStepUpdated(selectedStepId!, copy);
                  },
                ),
              ],
            ),
          );
        }),
        const SizedBox(height: 8),
        Align(
          alignment: Alignment.centerLeft,
          child: TextButton.icon(
            onPressed: () {
              final copy = Map<String, dynamic>.from(stepDef);
              final maps = SafeCast.safeMap(copy['input_mappings']);
              maps['new_param_${maps.length}'] = '\$inputs.';
              copy['input_mappings'] = maps;
              onStepUpdated(selectedStepId!, copy);
            },
            icon: const Icon(Icons.add, size: 16),
            label: const Text('Add Mapping'),
          ),
        ),
      ],
    );
  }
}
