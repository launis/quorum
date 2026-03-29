import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'dart:convert';

/// Admin Studio View for managing the MCP Gateways.
/// Uses the 2026 Gold Standard Flat MVC Architecture (Dumb UI).
class McpGatewayView extends HookConsumerWidget {
  final String id;
  // initialData is dropped here if any exists, deep-links should fetch fresh native data
  const McpGatewayView({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formKey = useMemoized(() => GlobalKey<FormState>());

    // 1. Data and loading states are read from Riverpod! No useEffect for fetching!
    final formState = ref.watch(mcpGatewayFormProvider(id));

    return formState.when(
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
              onRetry: () => ref.invalidate(mcpGatewayFormProvider(id)),
            ),
          ),
      data: (payload) {
        // The UI is a pure renderer of the business payload
        return _buildScaffold(context, ref, l10n, formKey, formState, payload);
      },
    );
  }

  Widget _buildScaffold(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    GlobalKey<FormState> formKey,
    AsyncValue<Map<String, dynamic>> formState,
    Map<String, dynamic> payload,
  ) {
    Future<void> deleteGateway() async {
      final String idToDelete = payload['id']?.toString() ?? '';
      if (idToDelete.isEmpty || id == 'new') return;

      final confirm = await showDialog<bool>(
        context: context,
        builder:
            (ctx) => AlertDialog(
              title: Text(l10n.deleteGatewayTitle),
              content: Text(l10n.deleteGatewayConfirmation(idToDelete)),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(ctx, false),
                  child: Text(l10n.cancelButton),
                ),
                FilledButton(
                  style: FilledButton.styleFrom(
                    backgroundColor: Theme.of(context).colorScheme.error,
                  ),
                  onPressed: () => Navigator.pop(ctx, true),
                  child: Text(l10n.deleteButton),
                ),
              ],
            ),
      );

      if (confirm == true) {
        try {
          await ref
              .read(mcpGatewaysControllerProvider.notifier)
              .deleteGateway(idToDelete);
          if (!context.mounted) return;
          context.pop();
        } catch (e) {
          if (!context.mounted) return;
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to delete gateway: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.deleteFailedError(e.toString())),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      }
    }

    Future<void> saveGateway() async {
      if (formKey.currentState!.validate()) {
        formKey.currentState!.save();
        try {
          final notifier = ref.read(mcpGatewayFormProvider(id).notifier);
          await notifier.submit(payload);
          if (!context.mounted) return;
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(SnackBar(content: Text(l10n.gatewaySavedSuccess)));
        } catch (e) {
          if (!context.mounted) return;
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to save gateway: $e', e);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(l10n.saveFailedError(e.toString())),
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
          );
        }
      }
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.studioDashboardGatewaysTitle),
        actions: [
          if (formState.isLoading)
            const Center(
              child: Padding(
                padding: EdgeInsets.only(right: 16.0),
                child: SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            ),
          if (id != 'new')
            IconButton(
              icon: Icon(
                Icons.delete,
                color: Theme.of(context).colorScheme.error,
              ),
              onPressed: formState.isLoading ? null : deleteGateway,
              tooltip: l10n.deleteGatewayTitle,
            ),
          FilledButton.icon(
            icon: const Icon(Icons.save),
            label: Text(l10n.studioSaveButton),
            onPressed:
                formState.isLoading
                    ? null
                    : saveGateway, // Read isLoading directly from Riverpod!
          ),
          const SizedBox(width: 16),
        ],
      ),
      body: Form(
        key: formKey,
        child: ListView(
          padding: const EdgeInsets.all(16.0),
          children: [
            _buildSystemAttributes(l10n, payload),
            const SizedBox(height: 24),
            _buildToolsSection(context, ref, l10n, payload),
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
              l10n.gatewayMetadataTitle,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 16),
            TextFormField(
              initialValue: data['id']?.toString(),
              decoration: InputDecoration(labelText: l10n.configIdLabel),
              readOnly: true, // Opaque ID Mandate: NEVER editable manually
            ),
            const SizedBox(height: 8),
            TextFormField(
              initialValue: data['slug']?.toString(),
              decoration: InputDecoration(labelText: l10n.slugLabel),
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

  Widget _buildToolsSection(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    Map<String, dynamic> data,
  ) {
    final tools = List<Map<String, dynamic>>.from(data['tools'] ?? []);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              l10n.allowedMcpToolsTitle,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
            ),
            FilledButton.icon(
              onPressed: () {
                ref.read(mcpGatewayFormProvider(id).notifier).addTool();
              },
              icon: const Icon(Icons.add),
              label: Text(l10n.addToolButton),
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (tools.isEmpty) Text(l10n.noToolsDefinedGateway),
        ...tools.asMap().entries.map((entry) {
          final index = entry.key;
          final tool = entry.value;

          return Card(
            margin: const EdgeInsets.only(bottom: 16.0),
            child: ExpansionTile(
              initiallyExpanded: true,
              title: Text(l10n.toolTitlePrefix(tool['tool_id'].toString())),
              trailing: IconButton(
                icon: Icon(
                  Icons.delete,
                  color: Theme.of(context).colorScheme.error,
                ),
                onPressed: () {
                  ref
                      .read(mcpGatewayFormProvider(id).notifier)
                      .removeTool(index);
                },
              ),
              children: [
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      _buildStringField(ref, tool, 'tool_id', l10n.toolIdLabel),
                      _buildI18nGroup(ref, tool, l10n),
                      _buildLargeStringField(
                        ref,
                        tool,
                        'description',
                        l10n.toolDescriptionLabel,
                      ),
                      _buildJsonEditorField(
                        ref,
                        tool,
                        'input_schema',
                        l10n.jsonInputSchemaLabel,
                        l10n,
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

  Widget _buildStringField(
    WidgetRef ref,
    Map<String, dynamic> map,
    String key,
    String label,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: TextFormField(
        initialValue: map[key]?.toString() ?? '',
        decoration: InputDecoration(
          labelText: label,
          border: const OutlineInputBorder(),
        ),
        onChanged: (val) {
          map[key] =
              val; // Synchronous in-place update (Hook/TextController is also fine here)
          // If we need the title to update instantly, we can call forceRebuild()
          // but normally onSaved or normal Reactivity via onEditingComplete is used.
        },
        onSaved: (val) => map[key] = val,
      ),
    );
  }

  Widget _buildLargeStringField(
    WidgetRef ref,
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
    WidgetRef ref,
    Map<String, dynamic> map,
    String key,
    String label,
    AppLocalizations l10n,
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
            jsonDecode(val); // UI validation is fast, allowed.
            return null;
          } catch (e) {
            return l10n.invalidJsonError;
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

  Widget _buildI18nGroup(
    WidgetRef ref,
    Map<String, dynamic> tool,
    AppLocalizations l10n,
  ) {
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
        Text(
          l10n.uiDisplayNameTitle,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        Padding(
          padding: const EdgeInsets.only(bottom: 12.0),
          child: TextFormField(
            initialValue: translations['en']?.toString() ?? '',
            decoration: InputDecoration(
              labelText: l10n.englishNameLabel,
              border: const OutlineInputBorder(),
            ),
            onSaved: (val) => translations['en'] = val,
          ),
        ),
        Padding(
          padding: const EdgeInsets.only(bottom: 12.0),
          child: TextFormField(
            initialValue: translations['fi']?.toString() ?? '',
            decoration: InputDecoration(
              labelText: l10n.finnishNameLabel,
              border: const OutlineInputBorder(),
            ),
            onSaved: (val) => translations['fi'] = val,
          ),
        ),
      ],
    );
  }
}
