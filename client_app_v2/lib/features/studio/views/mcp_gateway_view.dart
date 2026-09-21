import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'dart:convert';

/// Admin Studio View for managing the MCP Gateways.
/// Uses the 2026 Gold Standard Flat MVC Architecture (Dumb UI).
class McpGatewayView extends HookConsumerWidget {
  final String id;
  const McpGatewayView({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formKey = useMemoized(() => GlobalKey<FormState>());

    final formState = ref.watch(mcpGatewayFormProvider(id));

    return switch (formState) {
      AsyncLoading() => Scaffold(
        appBar: AppBar(title: Text(l10n.studioDashboardGatewaysTitle)),
        body: const Center(child: CircularProgressIndicator()),
      ),
      AsyncError(:final error, :final stackTrace) => Scaffold(
        appBar: AppBar(title: Text(l10n.studioDashboardGatewaysTitle)),
        body: ErrorView(
          error: error,
          stackTrace: stackTrace,
          compact: false,
          onRetry: () => ref.invalidate(mcpGatewayFormProvider(id)),
        ),
      ),
      AsyncData(value: final payload) => _buildScaffold(
        context,
        ref,
        l10n,
        formKey,
        formState,
        payload,
      ),
    };
  }

  Widget _buildScaffold(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    GlobalKey<FormState> formKey,
    AsyncValue<McpGateway> formState,
    McpGateway payload,
  ) {
    final bannerMessage = useState<String?>(null);
    final isBannerError = useState<bool>(false);

    Future<void> deleteGateway() async {
      final String idToDelete = payload.id;
      if (idToDelete.isEmpty) return;

      final String nameToDisplay = payload.slug?.isNotEmpty == true
          ? payload.slug!
          : idToDelete;

      final confirm = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: Text(l10n.deleteGatewayTitle),
          content: Text(l10n.deleteGatewayConfirmation(nameToDisplay)),
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
        } catch (e, st) {
          if (!context.mounted) return;
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to delete gateway: $e', e, st);
          bannerMessage.value = l10n.deleteFailedError(e.toString());
          isBannerError.value = true;
        }
      }
    }

    Future<void> saveGateway() async {
      if (formKey.currentState!.validate()) {
        formKey.currentState!.save();
        try {
          final current = ref.read(mcpGatewayFormProvider(id)).value ?? payload;
          final notifier = ref.read(mcpGatewayFormProvider(id).notifier);
          await notifier.submit(current);
          bannerMessage.value = l10n.gatewaySavedSuccess;
          isBannerError.value = false;
        } catch (e, st) {
          if (!context.mounted) return;
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to save gateway: $e', e, st);
          bannerMessage.value = l10n.saveFailedError(e.toString());
          isBannerError.value = true;
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
                padding: EdgeInsets.only(right: AppSpacing.s16),
                child: SizedBox(
                  width: AppSpacing.s16,
                  height: AppSpacing.s16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
            ),
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
            onPressed: formState.isLoading ? null : saveGateway,
          ),
          AppSpacing.w16,
        ],
      ),
      body: Form(
        key: formKey,
        child: ListView(
          padding: AppSpacing.p16,
          children: [
            if (bannerMessage.value != null) ...[
              MaterialBanner(
                content: Text(bannerMessage.value!),
                backgroundColor: isBannerError.value
                    ? Theme.of(context).colorScheme.errorContainer
                    : Theme.of(context).colorScheme.primaryContainer,
                actions: [
                  TextButton(
                    onPressed: () => bannerMessage.value = null,
                    child: Text(l10n.cancelButton),
                  ),
                ],
              ),
              AppSpacing.h16,
            ],
            _buildSystemAttributes(l10n, payload, ref),
            AppSpacing.h24,
            _buildToolsSection(context, ref, l10n, payload),
          ],
        ),
      ),
    );
  }

  Widget _buildSystemAttributes(
    AppLocalizations l10n,
    McpGateway data,
    WidgetRef ref,
  ) {
    return Card(
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.gatewayMetadataTitle,
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
            ),
            AppSpacing.h16,
            TextFormField(
              initialValue: data.id,
              decoration: InputDecoration(labelText: l10n.configIdLabel),
              readOnly: true,
            ),
            AppSpacing.h8,
            TextFormField(
              initialValue: data.slug ?? '',
              decoration: InputDecoration(labelText: l10n.slugLabel),
              onSaved: (val) {
                final current = ref.read(mcpGatewayFormProvider(id)).value;
                if (current != null) {
                  ref
                      .read(mcpGatewayFormProvider(id).notifier)
                      .forceRebuild(
                        current.copyWith(
                          slug: val != null && val.trim().isNotEmpty
                              ? val.trim()
                              : null,
                        ),
                      );
                }
              },
            ),
            AppSpacing.h8,
            TextFormField(
              initialValue: data.type,
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
    McpGateway data,
  ) {
    final tools = data.tools;

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
        AppSpacing.h16,
        if (tools.isEmpty) Text(l10n.noToolsDefinedGateway),
        ...tools.asMap().entries.map((entry) {
          final index = entry.key;
          final tool = entry.value;

          return Card(
            margin: const EdgeInsets.only(bottom: AppSpacing.s16),
            child: ExpansionTile(
              initiallyExpanded: true,
              title: Text(l10n.toolTitlePrefix(tool.toolId)),
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
                  padding: AppSpacing.p16,
                  child: Column(
                    children: [
                      Padding(
                        padding: const EdgeInsets.only(bottom: AppSpacing.s16),
                        child: TextFormField(
                          initialValue: tool.toolId,
                          decoration: InputDecoration(
                            labelText: l10n.toolIdLabel,
                            border: const OutlineInputBorder(),
                          ),
                          onSaved: (val) {
                            _updateTool(
                              ref,
                              index,
                              (t) => t.copyWith(toolId: val ?? ''),
                            );
                          },
                        ),
                      ),
                      _buildI18nGroup(ref, index, tool, l10n),
                      Padding(
                        padding: const EdgeInsets.only(bottom: AppSpacing.s16),
                        child: TextFormField(
                          initialValue: tool.description,
                          maxLines: 3,
                          decoration: InputDecoration(
                            labelText: l10n.toolDescriptionLabel,
                            border: const OutlineInputBorder(),
                          ),
                          onSaved: (val) {
                            _updateTool(
                              ref,
                              index,
                              (t) => t.copyWith(description: val ?? ''),
                            );
                          },
                        ),
                      ),
                      _buildJsonEditorField(ref, index, tool, l10n),
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

  void _updateTool(
    WidgetRef ref,
    int index,
    AllowedMcpTool Function(AllowedMcpTool) update,
  ) {
    final current = ref.read(mcpGatewayFormProvider(id)).value;
    if (current == null) return;
    final updatedTools = List<AllowedMcpTool>.from(current.tools);
    if (index >= 0 && index < updatedTools.length) {
      updatedTools[index] = update(updatedTools[index]);
      ref
          .read(mcpGatewayFormProvider(id).notifier)
          .forceRebuild(current.copyWith(tools: updatedTools));
    }
  }

  Widget _buildJsonEditorField(
    WidgetRef ref,
    int toolIndex,
    AllowedMcpTool tool,
    AppLocalizations l10n,
  ) {
    final currentStr = const JsonEncoder.withIndent(
      '  ',
    ).convert(tool.inputSchema);

    return Padding(
      padding: const EdgeInsets.only(bottom: AppSpacing.s16),
      child: TextFormField(
        initialValue: currentStr,
        maxLines: 5,
        style: const TextStyle(fontFamily: 'monospace'),
        decoration: InputDecoration(
          labelText: l10n.jsonInputSchemaLabel,
          border: const OutlineInputBorder(),
        ),
        validator: (val) {
          if (val == null || val.trim().isEmpty) return null;
          try {
            jsonDecode(val);
            return null;
          } catch (e) {
            return l10n.invalidJsonError;
          }
        },
        onSaved: (val) {
          Map<String, dynamic> schema = {};
          if (val != null && val.trim().isNotEmpty) {
            try {
              schema = jsonDecode(val) as Map<String, dynamic>;
            } catch (_) {}
          }
          _updateTool(ref, toolIndex, (t) => t.copyWith(inputSchema: schema));
        },
      ),
    );
  }

  Widget _buildI18nGroup(
    WidgetRef ref,
    int toolIndex,
    AllowedMcpTool tool,
    AppLocalizations l10n,
  ) {
    final translations = Map<String, String>.from(tool.name.translations);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.uiDisplayNameTitle,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        AppSpacing.h8,
        Padding(
          padding: const EdgeInsets.only(bottom: AppSpacing.s16),
          child: TextFormField(
            initialValue: translations['en'] ?? '',
            decoration: InputDecoration(
              labelText: l10n.englishNameLabel,
              border: const OutlineInputBorder(),
            ),
            onSaved: (val) {
              translations['en'] = val ?? '';
              _updateTool(
                ref,
                toolIndex,
                (t) => t.copyWith(name: I18nText(translations: translations)),
              );
            },
          ),
        ),
        Padding(
          padding: const EdgeInsets.only(bottom: AppSpacing.s16),
          child: TextFormField(
            initialValue: translations['fi'] ?? '',
            decoration: InputDecoration(
              labelText: l10n.finnishNameLabel,
              border: const OutlineInputBorder(),
            ),
            onSaved: (val) {
              translations['fi'] = val ?? '';
              _updateTool(
                ref,
                toolIndex,
                (t) => t.copyWith(name: I18nText(translations: translations)),
              );
            },
          ),
        ),
      ],
    );
  }
}
