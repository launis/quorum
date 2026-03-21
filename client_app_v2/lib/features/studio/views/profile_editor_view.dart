import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/core/error/app_error_boundary.dart';

/// **Profile Editor View**
///
/// Admin UI for defining strictly-typed Output Profiles for a specific Workflow.
/// Follows De-Generator Protocol by operating strictly on Map<String, dynamic>.
class ProfileEditorView extends ConsumerStatefulWidget {
  final String workflowSlug;
  final Map<String, dynamic>? initialData;

  const ProfileEditorView({
    super.key,
    required this.workflowSlug,
    this.initialData,
  });

  @override
  ConsumerState<ProfileEditorView> createState() => _ProfileEditorViewState();
}

class _ProfileEditorViewState extends ConsumerState<ProfileEditorView> {
  late Map<String, dynamic> _editableWorkflow;
  late Map<String, dynamic> _profiles;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    // Default to a blank workflow blueprint if initialData is somehow missing
    _editableWorkflow = Map<String, dynamic>.from(
      widget.initialData ?? {'id': widget.workflowSlug},
    );

    // Safely cast output_profiles map
    final dynamic rawProfiles = _editableWorkflow['output_profiles'];
    _profiles = Map<String, dynamic>.from(SafeCast.safeMap(rawProfiles));

    // If empty initially, seed a 'default' profile
    if (_profiles.isEmpty) {
      _profiles['default'] = {
        'name': {'fi': 'Oletusraportti', 'en': 'Default Report'},
        'layouts': [
          {'preset_view': '1d_metrics', 'show_text': true, 'steps': <String>[]},
        ],
      };
    }
  }

  Future<void> _saveWorkflow() async {
    setState(() => _isSaving = true);
    try {
      // 1. Mutate local copy
      final String idToSave = SafeCast.safeString(_editableWorkflow['id']);
      if (idToSave.isEmpty) throw Exception("Workflow ID is missing");

      _editableWorkflow['output_profiles'] = _profiles;

      // 2. Dispatch via Optimistic SWR Controller
      await ref
          .read(workflowsControllerProvider.notifier)
          .saveWorkflow(idToSave, _editableWorkflow);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Profiles saved successfully.'),
            backgroundColor: Colors.green,
          ),
        );
        context.pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Save failed: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  void _addProfileDialog() {
    String newId = '';
    showDialog(
      context: context,
      builder:
          (ctx) => AlertDialog(
            title: const Text('New Profile ID'),
            content: TextField(
              decoration: const InputDecoration(
                labelText: 'Profile ID (e.g. executive)',
              ),
              onChanged: (val) => newId = val.trim(),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Cancel'),
              ),
              FilledButton(
                onPressed: () {
                  if (newId.isEmpty || _profiles.containsKey(newId)) return;
                  setState(() {
                    _profiles[newId] = {
                      'name': {'fi': 'Uusi profiili', 'en': 'New Profile'},
                      'layouts': [],
                    };
                  });
                  Navigator.pop(ctx);
                },
                child: const Text('Add'),
              ),
            ],
          ),
    );
  }

  void _addLayout(String profileId) {
    setState(() {
      final profile = SafeCast.safeMap(_profiles[profileId]);
      final layouts = SafeCast.safeList(profile['layouts']);
      layouts.add({
        'preset_view': '1d_metrics',
        'show_text': true,
        'steps': <String>[],
      });
      profile['layouts'] = layouts;
      _profiles[profileId] = profile;
    });
  }

  @override
  Widget build(BuildContext context) {
    return AppExceptionBoundary(
      child: Scaffold(
        appBar: AppBar(
          title: Text('Edit Profiles: ${widget.workflowSlug}'),
          actions: [
            if (_isSaving)
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16.0),
                child: Center(
                  child: SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                ),
              )
            else
              TextButton.icon(
                onPressed: _saveWorkflow,
                icon: const Icon(Icons.save),
                label: const Text('Save Form'),
              ),
          ],
        ),
        body: ListView(
          padding: const EdgeInsets.all(16.0),
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Output Profiles Dictionary',
                  style: Theme.of(context).textTheme.headlineSmall,
                ),
                FilledButton.icon(
                  onPressed: _addProfileDialog,
                  icon: const Icon(Icons.add),
                  label: const Text('Add Variant'),
                ),
              ],
            ),
            const SizedBox(height: 16),
            ..._profiles.entries.map(
              (entry) =>
                  _buildProfileCard(entry.key, SafeCast.safeMap(entry.value)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileCard(String profileId, Map<String, dynamic> profileDef) {
    final layouts = SafeCast.safeList(profileDef['layouts']);

    return Card(
      margin: const EdgeInsets.only(bottom: 24.0),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  "Variant ID: $profileId",
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                    color: Colors.blueGrey,
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () {
                    setState(() {
                      _profiles.remove(profileId);
                    });
                  },
                ),
              ],
            ),
            const SizedBox(height: 12),
            I18nTextField(
              label: 'Display Name',
              initialData: SafeCast.safeMap(profileDef['name']),
              onChanged: (val) {
                setState(() {
                  profileDef['name'] = val;
                });
              },
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Report Layout Sequence',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                TextButton.icon(
                  onPressed: () => _addLayout(profileId),
                  icon: const Icon(Icons.add_box),
                  label: const Text('Add Layout Block'),
                ),
              ],
            ),
            const Divider(),
            if (layouts.isEmpty)
              const Padding(
                padding: EdgeInsets.all(16.0),
                child: Text('No layout blocks defined. Report will be empty.'),
              )
            else
              ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: layouts.length,
                itemBuilder: (context, index) {
                  final layout = SafeCast.safeMap(layouts[index]);
                  return _buildLayoutEditor(profileId, index, layout);
                },
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildLayoutEditor(
    String profileId,
    int index,
    Map<String, dynamic> layout,
  ) {
    final blocksList =
        SafeCast.safeList(
          layout['target_blocks'],
        ).map((e) => e.toString()).toList();

    final xCtrl = TextEditingController(
      text: blocksList.isNotEmpty ? blocksList[0] : '',
    );
    final yCtrl = TextEditingController(
      text: blocksList.length > 1 ? blocksList[1] : '',
    );
    final zCtrl = TextEditingController(
      text: blocksList.length > 2 ? blocksList[2] : '',
    );

    void updateCoords() {
      final List<String> b = [];
      if (xCtrl.text.trim().isNotEmpty) b.add(xCtrl.text.trim());
      if (yCtrl.text.trim().isNotEmpty) b.add(yCtrl.text.trim());
      if (zCtrl.text.trim().isNotEmpty) b.add(zCtrl.text.trim());
      layout['target_blocks'] = b;
    }

    String currentPreset = SafeCast.safeString(
      layout['preset_view'],
      '1d_metrics',
    );
    if (![
      '1d_metrics',
      '2d_compare',
      '3d_complex',
      'text_only',
      'default',
    ].contains(currentPreset)) {
      currentPreset = '1d_metrics';
    }
    final bool showText = layout['show_text'] as bool? ?? true;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 12,
                child: Text(
                  '${index + 1}',
                  style: const TextStyle(fontSize: 12),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: DropdownButtonFormField<String>(
                  initialValue: currentPreset,
                  decoration: const InputDecoration(
                    labelText: 'Preset View',
                    isDense: true,
                  ),
                  items: const [
                    DropdownMenuItem(
                      value: '1d_metrics',
                      child: Text('1D Table'),
                    ),
                    DropdownMenuItem(
                      value: '2d_compare',
                      child: Text('2D Grid'),
                    ),
                    DropdownMenuItem(
                      value: '3d_complex',
                      child: Text('3D Composite'),
                    ),
                    DropdownMenuItem(
                      value: 'text_only',
                      child: Text('Text/Synthesis Only'),
                    ),
                    DropdownMenuItem(
                      value: 'default',
                      child: Text('Default View'),
                    ),
                  ],
                  onChanged: (val) {
                    if (val != null) {
                      setState(() {
                        layout['preset_view'] = val;
                      });
                    }
                  },
                ),
              ),
              const SizedBox(width: 12),
              Row(
                children: [
                  const Text('Show Text'),
                  Switch(
                    value: showText,
                    onChanged: (val) {
                      setState(() {
                        layout['show_text'] = val;
                      });
                    },
                  ),
                ],
              ),
              IconButton(
                icon: const Icon(Icons.delete_outline, color: Colors.orange),
                onPressed: () {
                  setState(() {
                    final profile = _profiles[profileId];
                    final layouts = SafeCast.safeList(profile['layouts']);
                    layouts.removeAt(index);
                  });
                },
              ),
            ],
          ),
          const SizedBox(height: 12),
          I18nTextField(
            label: 'Osion Otsikko (Title - Optional)',
            initialData: SafeCast.safeMap(layout['title']),
            onChanged: (val) {
              setState(() {
                layout['title'] = val;
              });
            },
          ),
          const SizedBox(height: 12),
          I18nTextField(
            label: 'Osion Kuvaus (Description - Optional)',
            initialData: SafeCast.safeMap(layout['description']),
            onChanged: (val) {
              setState(() {
                layout['description'] = val;
              });
            },
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: TextFormField(
                  controller: xCtrl,
                  decoration: const InputDecoration(
                    labelText: 'X-Akseli (Matriisi ID)',
                    isDense: true,
                  ),
                  onChanged: (_) => updateCoords(),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: TextFormField(
                  controller: yCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Y-Akseli (Matriisi ID)',
                    isDense: true,
                  ),
                  onChanged: (_) => updateCoords(),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: TextFormField(
                  controller: zCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Z-Akseli (Matriisi ID)',
                    isDense: true,
                  ),
                  onChanged: (_) => updateCoords(),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
