import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'dart:convert';

class McpGatewayView extends ConsumerStatefulWidget {
  final String id;
  final Map<String, dynamic>? initialData;

  const McpGatewayView({super.key, required this.id, this.initialData});

  @override
  ConsumerState<McpGatewayView> createState() => _McpGatewayViewState();
}

class _McpGatewayViewState extends ConsumerState<McpGatewayView> {
  final _formKey = GlobalKey<FormState>();
  Map<String, dynamic>? _editableState;

  @override
  void initState() {
    super.initState();
    if (widget.initialData != null) {
      _editableState = _deepCopy(widget.initialData!);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    if (_editableState != null) {
      return _buildScaffold(l10n, false);
    }

    final asyncData =
        (widget.id == 'new')
            ? AsyncValue.data({
              'id': 'mcpcfg_new',
              'slug': 'new-gateway',
              'type': 'mcp_gateways',
              'tools': [],
            })
            : ref.watch(mcpGatewayByIdProvider(widget.id));

    return asyncData.when(
      loading:
          () => Scaffold(
            appBar: AppBar(title: Text(l10n.studioDashboardGatewaysTitle)),
            body: const Center(child: CircularProgressIndicator()),
          ),
      error:
          (e, st) => Scaffold(
            appBar: AppBar(title: Text(l10n.studioDashboardGatewaysTitle)),
            body: ErrorView(
              error: e,
              stackTrace: st,
              compact: false,
              onRetry: () => ref.invalidate(mcpGatewayByIdProvider(widget.id)),
            ),
          ),
      data: (data) {
        _editableState ??= _deepCopy(data);
        return _buildScaffold(l10n, false);
      },
    );
  }

  Widget _buildScaffold(AppLocalizations l10n, bool isSaving) {
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.studioDashboardGatewaysTitle),
        actions: [
          if (widget.id != 'new')
            IconButton(
              icon: const Icon(Icons.delete, color: Colors.orange),
              onPressed: _deleteGateway,
              tooltip: 'Delete Gateway',
            ),
          FilledButton.icon(
            icon: const Icon(Icons.save),
            label: Text(l10n.studioSaveButton),
            onPressed: isSaving ? null : _saveGateway,
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16.0),
          children: [
            _buildSystemAttributes(l10n, _editableState!),
            const SizedBox(height: 24),
            _buildToolsSection(l10n, _editableState!),
          ],
        ),
      ),
    );
  }

  Widget _buildSystemAttributes(
    AppLocalizations l10n,
    Map<String, dynamic> data,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Gateway Metadata',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 16),
            TextFormField(
              initialValue: data['id']?.toString(),
              decoration: InputDecoration(labelText: l10n.configIdLabel),
              readOnly: true,
            ),
            const SizedBox(height: 8),
            TextFormField(
              initialValue: data['slug']?.toString(),
              decoration: const InputDecoration(labelText: 'Slug'),
              onSaved: (val) => data['slug'] = val,
            ),
            const SizedBox(height: 8),
            TextFormField(
              initialValue: data['type']?.toString(),
              decoration: InputDecoration(labelText: l10n.configTypeLabel),
              readOnly: true,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildToolsSection(AppLocalizations l10n, Map<String, dynamic> data) {
    final tools = List<Map<String, dynamic>>.from(data['tools'] ?? []);
    data['tools'] = tools; // Ensure reference binds

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Allowed MCP Tools',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            FilledButton.icon(
              onPressed: () {
                setState(() {
                  tools.add({
                    'tool_id': 'new_tool',
                    'name': {
                      'default_locale': 'en',
                      'translations': {'en': 'New Tool', 'fi': 'Uusi työkalu'},
                    },
                    'description': '',
                    'input_schema': {},
                  });
                });
              },
              icon: const Icon(Icons.add),
              label: const Text('Add Tool'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (tools.isEmpty) const Text('No tools defined for this gateway.'),
        ...tools.asMap().entries.map((entry) {
          final index = entry.key;
          final tool = entry.value;

          return Card(
            margin: const EdgeInsets.only(bottom: 16.0),
            child: ExpansionTile(
              initiallyExpanded: true,
              title: Text('Tool: ${tool['tool_id']}'),
              trailing: IconButton(
                icon: const Icon(Icons.delete, color: Colors.red),
                onPressed: () {
                  setState(() => tools.removeAt(index));
                },
              ),
              children: [
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      _buildStringField(tool, 'tool_id', 'Tool ID (Slug)'),
                      _buildI18nGroup(tool, l10n),
                      _buildLargeStringField(
                        tool,
                        'description',
                        'Tool Description (English only for LLM)',
                      ),
                      _buildJsonEditorField(
                        tool,
                        'input_schema',
                        'JSON Input Schema',
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }

  Widget _buildStringField(Map<String, dynamic> map, String key, String label) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: map[key]?.toString() ?? '',
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        onSaved: (val) => map[key] = val,
      ),
    );
  }

  Widget _buildLargeStringField(
    Map<String, dynamic> map,
    String key,
    String label,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: map[key]?.toString() ?? '',
        maxLines: 3,
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        onSaved: (val) => map[key] = val,
      ),
    );
  }

  Widget _buildJsonEditorField(
    Map<String, dynamic> map,
    String key,
    String label,
  ) {
    final currentObj = map[key] ?? {};
    final currentStr = const JsonEncoder.withIndent('  ').convert(currentObj);

    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: currentStr,
        maxLines: 5,
        style: const TextStyle(fontFamily: 'monospace'),
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        validator: (val) {
          if (val == null || val.trim().isEmpty) return null;
          try {
            jsonDecode(val);
            return null;
          } catch (e) {
            return 'Invalid JSON';
          }
        },
        onSaved: (val) {
          if (val != null && val.trim().isNotEmpty) {
            map[key] = jsonDecode(val);
          } else {
            map[key] = {};
          }
        },
      ),
    );
  }

  Widget _buildI18nGroup(Map<String, dynamic> tool, AppLocalizations l10n) {
    final nameObj =
        tool['name'] as Map<String, dynamic>? ??
        {
          'default_locale': 'en',
          'translations': {'en': '', 'fi': ''},
        };
    tool['name'] = nameObj;
    final translations =
        nameObj['translations'] as Map<String, dynamic>? ??
        {'en': '', 'fi': ''};
    nameObj['translations'] = translations;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'UI Display Name (I18nText)',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Padding(
          padding: const EdgeInsets.only(bottom: 12.0),
          child: TextFormField(
            initialValue: translations['en']?.toString() ?? '',
            decoration: const InputDecoration(
              labelText: 'English Name',
              border: OutlineInputBorder(),
            ),
            onSaved: (val) => translations['en'] = val,
          ),
        ),
        Padding(
          padding: const EdgeInsets.only(bottom: 12.0),
          child: TextFormField(
            initialValue: translations['fi']?.toString() ?? '',
            decoration: const InputDecoration(
              labelText: 'Finnish Name',
              border: OutlineInputBorder(),
            ),
            onSaved: (val) => translations['fi'] = val,
          ),
        ),
      ],
    );
  }

  Map<String, dynamic> _deepCopy(Map<String, dynamic> source) {
    return jsonDecode(jsonEncode(source)) as Map<String, dynamic>;
  }

  Future<void> _saveGateway() async {
    if (_formKey.currentState!.validate()) {
      _formKey.currentState!.save();
      try {
        final idToSave =
            widget.id == 'new'
                ? (_editableState!['id'] ?? 'mcpcfg_new')
                : widget.id;
        await ref
            .read(mcpGatewaysControllerProvider.notifier)
            .saveGateway(idToSave, _editableState!);
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('MCP Gateway saved successfully.')),
        );
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Save failed: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }

  Future<void> _deleteGateway() async {
    final String idToDelete = _editableState?['id']?.toString() ?? '';
    if (idToDelete.isEmpty || widget.id == 'new') return;

    final confirm = await showDialog<bool>(
      context: context,
      builder:
          (ctx) => AlertDialog(
            title: const Text('Delete MCP Gateway?'),
            content: Text(
              'Are you sure you want to delete gateway $idToDelete?',
            ),
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
      try {
        await ref
            .read(mcpGatewaysControllerProvider.notifier)
            .deleteGateway(idToDelete);
        if (!mounted) return;
        context.pop();
      } catch (e) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Delete failed: $e'),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      }
    }
  }
}
