import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/utils/safe_cast.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';

class OutputProfileCrudView extends ConsumerStatefulWidget {
  final String id;
  final Map<String, dynamic>? initialData;

  const OutputProfileCrudView({super.key, required this.id, this.initialData});

  @override
  ConsumerState<OutputProfileCrudView> createState() =>
      _OutputProfileCrudViewState();
}

class _OutputProfileCrudViewState extends ConsumerState<OutputProfileCrudView> {
  late Map<String, dynamic> _editableProfile;
  late List<dynamic> _layouts;
  bool _isSaving = false;
  final _idController = TextEditingController();
  final _slugController = TextEditingController();
  final _workflowIdController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _editableProfile = Map<String, dynamic>.from(
      widget.initialData ??
          {
            'id': widget.id == 'new' ? '' : widget.id,
            'name': {'fi': 'Uusi profiili', 'en': 'New Profile'},
            'layouts': [],
            'workflow_id': '',
          },
    );

    _layouts = SafeCast.safeList(_editableProfile['layouts']);
    _idController.text = _editableProfile['id']?.toString() ?? '';
    _slugController.text = _editableProfile['slug']?.toString() ?? '';
    _workflowIdController.text =
        _editableProfile['workflow_id']?.toString() ?? '';
  }

  @override
  void dispose() {
    _idController.dispose();
    _slugController.dispose();
    _workflowIdController.dispose();
    super.dispose();
  }

  Future<void> _saveProfile() async {
    setState(() => _isSaving = true);
    try {
      final String idToSave = _idController.text.trim();
      if (idToSave.isEmpty) throw Exception("Profile ID is required");

      _editableProfile['id'] = idToSave;
      _editableProfile['slug'] =
          _slugController.text.trim().isNotEmpty
              ? _slugController.text.trim()
              : idToSave; // Fallback sync
      _editableProfile['workflow_id'] = _workflowIdController.text.trim();
      _editableProfile['layouts'] = _layouts;

      await ref
          .read(outputProfilesControllerProvider.notifier)
          .saveProfile(idToSave, _editableProfile);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Profile saved successfully.'),
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

  Future<void> _deleteProfile() async {
    final String idToDelete = _editableProfile['id']?.toString() ?? '';
    if (idToDelete.isEmpty || widget.id == 'new') return;

    final confirm = await showDialog<bool>(
      context: context,
      builder:
          (ctx) => AlertDialog(
            title: const Text('Delete Profile?'),
            content: Text('Are you sure you want to delete $idToDelete?'),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(ctx, false),
                child: const Text('Cancel'),
              ),
              FilledButton(
                style: FilledButton.styleFrom(backgroundColor: Colors.red),
                onPressed: () => Navigator.pop(ctx, true),
                child: const Text('Delete'),
              ),
            ],
          ),
    );

    if (confirm == true) {
      setState(() => _isSaving = true);
      try {
        await ref
            .read(outputProfilesControllerProvider.notifier)
            .deleteProfile(idToDelete);
        if (mounted) {
          context.pop();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text('Delete failed: $e')));
        }
      } finally {
        if (mounted) setState(() => _isSaving = false);
      }
    }
  }

  void _addLayout() {
    setState(() {
      _layouts.add({
        'layout_type': 'box_1d',
        'title': {
          'default_locale': 'en',
          'translations': <String, dynamic>{'en': 'New Layout Block'},
        },
        'show_text': true,
        'components': <String>[],
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final promptBlocksState = ref.watch(promptBlocksControllerProvider);
    final workflowsState = ref.watch(workflowsControllerProvider);
    final stepsState = ref.watch(stepsControllerProvider);

    final String selectedWorkflowId = _workflowIdController.text;
    Set<String> allowedBlockIds = {};

    if (selectedWorkflowId.isNotEmpty &&
        workflowsState.hasValue &&
        stepsState.hasValue) {
      final workflows = workflowsState.value!;
      final steps = stepsState.value!;

      final workflow = workflows.cast<Map<String, dynamic>?>().firstWhere(
        (w) => w != null && w['id']?.toString() == selectedWorkflowId,
        orElse: () => null,
      );

      if (workflow != null) {
        final stepRules = SafeCast.safeList(workflow['steps']);
        final taskBlueprintIds =
            stepRules
                .map((s) => SafeCast.safeMap(s)['task_blueprint']?.toString())
                .where((s) => s != null)
                .cast<String>()
                .toSet();

        for (final step in steps) {
          final stepId = step['id']?.toString() ?? '';
          final stepSlug = step['slug']?.toString() ?? stepId;
          if (taskBlueprintIds.contains(stepId) ||
              taskBlueprintIds.contains(stepSlug)) {
            final promptBlocks = SafeCast.safeList(
              step['prompt_blocks'],
            ).map((b) => b.toString());
            allowedBlockIds.addAll(promptBlocks);
          }
        }
      }
    }

    return AppExceptionBoundary(
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            widget.id == 'new' ? 'New Output Profile' : 'Edit Output Profile',
          ),
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
            else ...[
              if (widget.id != 'new')
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.orange),
                  onPressed: _deleteProfile,
                ),
              TextButton.icon(
                onPressed: _saveProfile,
                icon: const Icon(Icons.save),
                label: const Text('Save'),
              ),
            ],
          ],
        ),
        body: ListView(
          padding: const EdgeInsets.all(16.0),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    TextFormField(
                      controller: _idController,
                      decoration: const InputDecoration(
                        labelText: 'Profile ID (e.g. general_executive)',
                        border: OutlineInputBorder(),
                      ),
                      enabled:
                          widget.id == 'new', // Cannot change ID after creation
                    ),
                    const SizedBox(height: 16),
                    TextFormField(
                      controller: _slugController,
                      decoration: const InputDecoration(
                        labelText: 'URL Slug (e.g. default)',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    workflowsState.when(
                      data: (workflows) {
                        String? currentValue =
                            _workflowIdController.text.isNotEmpty
                                ? _workflowIdController.text
                                : null;
                        final bool hasValidValue =
                            currentValue != null &&
                            (workflows.any(
                                  (w) => w['id']?.toString() == currentValue,
                                ) ||
                                currentValue == '');

                        return DropdownButtonFormField<String>(
                          initialValue: hasValidValue ? currentValue : null,
                          decoration: const InputDecoration(
                            labelText: 'Workflow ID Binding',
                            border: OutlineInputBorder(),
                          ),
                          hint: const Text('Select a Workflow...'),
                          items: [
                            const DropdownMenuItem(
                              value: '',
                              child: Text('None (Default)'),
                            ),
                            ...workflows.map((flow) {
                              final flowId = flow['id']?.toString() ?? '';
                              final labelDict = SafeCast.safeMap(flow['name']);
                              final translations = SafeCast.safeMap(
                                labelDict['translations'],
                              );
                              final localeCode =
                                  Localizations.localeOf(context).languageCode;
                              final displayName =
                                  translations[localeCode] ??
                                  translations['fi'] ??
                                  translations['en'] ??
                                  flowId;

                              return DropdownMenuItem(
                                value: flowId,
                                child: Text('$displayName ($flowId)'),
                              );
                            }),
                          ],
                          onChanged: (val) {
                            if (val != null) {
                              setState(() {
                                _workflowIdController.text = val;
                                _editableProfile['workflow_id'] = val;
                              });
                            }
                          },
                        );
                      },
                      loading:
                          () =>
                              const Center(child: CircularProgressIndicator()),
                      error: (e, _) => Text('Error loading workflows: $e'),
                    ),
                    const SizedBox(height: 16),
                    I18nTextField(
                      label: 'Profile Display Name',
                      initialData: SafeCast.safeMap(_editableProfile['name']),
                      onChanged: (val) {
                        setState(() {
                          _editableProfile['name'] = val;
                        });
                      },
                    ),
                    const SizedBox(height: 16),
                    I18nTextField(
                      label: 'Profile Description (Optional)',
                      initialData: SafeCast.safeMap(
                        _editableProfile['description'],
                      ),
                      onChanged: (val) {
                        setState(() {
                          _editableProfile['description'] = val;
                        });
                      },
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            if (selectedWorkflowId.isEmpty)
              const Padding(
                padding: EdgeInsets.all(16.0),
                child: Center(
                  child: Text(
                    '⚠️ Please select a Workflow ID Binding above to configure report layouts.',
                    style: TextStyle(
                      color: Colors.orange,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              )
            else ...[
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Layout Blocks',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                  ),
                  FilledButton.icon(
                    onPressed: _addLayout,
                    icon: const Icon(Icons.add_box),
                    label: const Text('Add Layout Block'),
                  ),
                ],
              ),
              const Divider(),
              if (_layouts.isEmpty)
                const Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Text(
                    'No layout blocks defined. Report will be empty.',
                  ),
                )
              else
                ListView.builder(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _layouts.length,
                  itemBuilder: (context, index) {
                    final layout = SafeCast.safeMap(_layouts[index]);
                    return _buildLayoutEditor(
                      index,
                      layout,
                      promptBlocksState,
                      allowedBlockIds,
                    );
                  },
                ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildLayoutEditor(
    int index,
    Map<String, dynamic> layout,
    AsyncValue<List<Map<String, dynamic>>> promptBlocksState,
    Set<String> allowedBlockIds,
  ) {
    final blocksList =
        SafeCast.safeList(
          layout['components'],
        ).map((e) => e.toString()).toList();

    String currentPreset = SafeCast.safeString(
      layout['layout_type'] ?? layout['preset_view'],
      'box_1d',
    );
    if (![
      'box_1d',
      'matrix_2d',
      'radar_3d',
      'text_only',
      'automatic',
    ].contains(currentPreset)) {
      currentPreset = 'box_1d';
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
                  '\${index + 1}',
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
                    DropdownMenuItem(value: 'box_1d', child: Text('1D Table')),
                    DropdownMenuItem(
                      value: 'matrix_2d',
                      child: Text('2D Grid'),
                    ),
                    DropdownMenuItem(
                      value: 'radar_3d',
                      child: Text('3D Radar/Composite'),
                    ),
                    DropdownMenuItem(
                      value: 'text_only',
                      child: Text('Text/Synthesis Only'),
                    ),
                    DropdownMenuItem(
                      value: 'automatic',
                      child: Text('Automatic Validation'),
                    ),
                  ],
                  onChanged: (val) {
                    if (val != null)
                      setState(() {
                        layout['layout_type'] = val;
                        layout.remove('preset_view'); // Cleanup legacy keys
                      });
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
                    _layouts.removeAt(index);
                  });
                },
              ),
            ],
          ),

          const SizedBox(height: 12),
          I18nTextField(
            label: 'Layout Block Title',
            initialData: SafeCast.safeMap(layout['title']),
            onChanged: (val) {
              setState(() {
                layout['title'] = val;
              });
            },
          ),
          const SizedBox(height: 12),
          const Align(
            alignment: Alignment.centerLeft,
            child: Text(
              'Target Components',
              style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
            ),
          ),
          const SizedBox(height: 8),
          promptBlocksState.when(
            data: (blocks) {
              final targetBlocks =
                  blocks.where((b) {
                    final id = b['id']?.toString() ?? '';
                    final slug = b['slug']?.toString() ?? id;
                    final isAllowed =
                        allowedBlockIds.contains(id) ||
                        allowedBlockIds.contains(slug);
                    if (!isAllowed) return false;

                    // Exclude silent utility blocks (must have visual text extensions or be a scoring matrix)
                    final isMatrix = b['category_id']?.toString() == 'matrix';
                    final extensions = SafeCast.safeList(
                      b['output_extensions'],
                    );
                    return isMatrix || extensions.isNotEmpty;
                  }).toList();

              final int requiredDropdowns = switch (currentPreset) {
                'box_1d' => 1,
                'matrix_2d' => 2,
                'radar_3d' => 3,
                _ => 1,
              };

              final List<Widget> dropdowns = [];
              for (int i = 0; i < requiredDropdowns; i++) {
                String? selectedValue;
                if (i < blocksList.length) {
                  final val = blocksList[i];
                  if (val == '*' ||
                      targetBlocks.any((b) => b['id'].toString() == val)) {
                    selectedValue = val;
                  }
                }

                final String axisLabel = switch (i) {
                  0 => 'Component 1 (X-Axis/Primary)',
                  1 => 'Component 2 (Y-Axis)',
                  2 => 'Component 3 (Z-Axis)',
                  _ => 'Component \${i + 1}',
                };

                dropdowns.add(
                  Padding(
                    padding: const EdgeInsets.only(bottom: 8.0),
                    child: DropdownButtonFormField<String>(
                      initialValue: selectedValue,
                      decoration: InputDecoration(
                        labelText: axisLabel,
                        isDense: true,
                        border: const OutlineInputBorder(),
                      ),
                      hint: const Text('Select component...'),
                      items: [
                        const DropdownMenuItem(
                          value: '*',
                          child: Text('All Components (*)'),
                        ),
                        ...targetBlocks.map((block) {
                          final blockId = block['id']?.toString() ?? '';
                          final labelDict = SafeCast.safeMap(block['label']);
                          final translations = SafeCast.safeMap(
                            labelDict['translations'],
                          );
                          final localeCode =
                              Localizations.localeOf(context).languageCode;
                          final blockName =
                              translations[localeCode] ??
                              translations['fi'] ??
                              translations['en'] ??
                              blockId;
                          return DropdownMenuItem(
                            value: blockId,
                            child: Text(blockName),
                          );
                        }),
                      ],
                      onChanged: (val) {
                        if (val != null) {
                          setState(() {
                            while (blocksList.length <= i) {
                              blocksList.add('');
                            }
                            blocksList[i] = val;
                            layout['components'] =
                                blocksList.where((b) => b.isNotEmpty).toList();
                          });
                        }
                      },
                    ),
                  ),
                );
              }

              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: dropdowns,
              );
            },
            loading:
                () => const Align(
                  alignment: Alignment.centerLeft,
                  child: CircularProgressIndicator(),
                ),
            error: (e, _) => Text('Error loading blocks: $e'),
          ),
        ],
      ),
    );
  }
}
