import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/features/studio/controllers/mcp_gateways_controller.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';

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

    return AppErrorBoundary(
      child: switch (formState) {
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
      },
    );
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

      final String nameToDisplay = payload.slug.isNotEmpty
          ? payload.slug
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
          if (!context.mounted) return;
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

    Future<void> discoverTools() async {
      if (formKey.currentState!.validate()) {
        formKey.currentState!.save();
        try {
          final current = ref.read(mcpGatewayFormProvider(id)).value ?? payload;
          final notifier = ref.read(mcpGatewayFormProvider(id).notifier);
          await notifier.discoverTools(current);
          if (!context.mounted) return;
          final updated = ref.read(mcpGatewayFormProvider(id)).value;
          final count = updated?.tools.length ?? 0;
          bannerMessage.value = l10n.mcpToolsDiscoveredSuccess(count);
          isBannerError.value = false;
        } catch (e, st) {
          if (!context.mounted) return;
          ref
              .read(loggerServiceProvider)
              .error('Studio', 'Failed to discover MCP tools: $e', e, st);
          bannerMessage.value = l10n.mcpDiscoverToolsFailed(e.toString());
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
        // Phase 4, Step 4.2: Wrap form ListView in 1200px ConstrainedBox
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
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
                _buildSystemAttributes(context, l10n, payload, ref),
                AppSpacing.h16,
                _buildConnectionCard(
                  context,
                  ref,
                  l10n,
                  payload,
                  formState.isLoading,
                  discoverTools,
                ),
                AppSpacing.h24,
                _buildToolsSection(context, ref, l10n, payload),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _updateGateway(WidgetRef ref, McpGateway Function(McpGateway) update) {
    final current = ref.read(mcpGatewayFormProvider(id)).value;
    if (current != null) {
      ref
          .read(mcpGatewayFormProvider(id).notifier)
          .forceRebuild(update(current));
    }
  }

  Widget _buildSystemAttributes(
    BuildContext context,
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
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontSize: 20,
                fontWeight: FontWeight.w600,
              ),
            ),
            AppSpacing.h16,
            TextFormField(
              initialValue: data.id,
              decoration: InputDecoration(labelText: l10n.configIdLabel),
              readOnly: true,
            ),
            AppSpacing.h8,
            TextFormField(
              initialValue: data.slug,
              decoration: InputDecoration(labelText: l10n.slugLabel),
              onSaved: (val) {
                _updateGateway(
                  ref,
                  (current) => current.copyWith(
                    slug: val != null && val.trim().isNotEmpty
                        ? val.trim()
                        : 'default_mcp_gateway',
                  ),
                );
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

  Widget _buildConnectionCard(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    McpGateway data,
    bool isLoading,
    Future<void> Function() onDiscoverTools,
  ) {
    // Phase 4, Step 4.2: Connection & Authentication Card with live discovery trigger
    return Card(
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    l10n.mcpConnectionCardTitle,
                    overflow: TextOverflow.ellipsis,
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontSize: 20,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                AppSpacing.w16,
                FilledButton.icon(
                  onPressed: isLoading ? null : onDiscoverTools,
                  icon: const Icon(Icons.sync),
                  label: Text(l10n.mcpDiscoverToolsButton),
                ),
              ],
            ),
            AppSpacing.h16,
            TextFormField(
              initialValue: data.endpointUrl,
              decoration: InputDecoration(
                labelText: l10n.mcpEndpointUrlLabel,
                border: const OutlineInputBorder(),
              ),
              onSaved: (val) {
                _updateGateway(
                  ref,
                  (gw) => gw.copyWith(endpointUrl: val?.trim() ?? ''),
                );
              },
            ),
            AppSpacing.h16,
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<McpTransportType>(
                    isExpanded: true,
                    initialValue: data.transportType,
                    decoration: InputDecoration(
                      labelText: l10n.mcpTransportTypeLabel,
                      border: const OutlineInputBorder(),
                    ),
                    items: McpTransportType.values.map((t) {
                      final label = switch (t) {
                        McpTransportType.streamableHttp =>
                          l10n.mcpTransportStreamableHttp,
                        McpTransportType.sse => l10n.mcpTransportSse,
                      };
                      return DropdownMenuItem(
                        value: t,
                        child: Text(label, overflow: TextOverflow.ellipsis),
                      );
                    }).toList(),
                    onChanged: (val) {
                      if (val != null) {
                        _updateGateway(
                          ref,
                          (gw) => gw.copyWith(transportType: val),
                        );
                      }
                    },
                  ),
                ),
                AppSpacing.w16,
                Expanded(
                  child: DropdownButtonFormField<McpAuthType>(
                    isExpanded: true,
                    initialValue: data.authType,
                    decoration: InputDecoration(
                      labelText: l10n.mcpAuthTypeLabel,
                      border: const OutlineInputBorder(),
                    ),
                    items: McpAuthType.values.map((a) {
                      final label = switch (a) {
                        McpAuthType.none => l10n.mcpAuthNone,
                        McpAuthType.bearer => l10n.mcpAuthBearer,
                        McpAuthType.apiKeyHeader => l10n.mcpAuthApiKeyHeader,
                      };
                      return DropdownMenuItem(
                        value: a,
                        child: Text(label, overflow: TextOverflow.ellipsis),
                      );
                    }).toList(),
                    onChanged: (val) {
                      if (val != null) {
                        _updateGateway(ref, (gw) => gw.copyWith(authType: val));
                      }
                    },
                  ),
                ),
              ],
            ),
            if (data.authType == McpAuthType.apiKeyHeader) ...[
              AppSpacing.h16,
              TextFormField(
                initialValue: data.authHeaderName ?? '',
                decoration: InputDecoration(
                  labelText: l10n.mcpAuthHeaderNameLabel,
                  border: const OutlineInputBorder(),
                ),
                onSaved: (val) {
                  _updateGateway(
                    ref,
                    (gw) => gw.copyWith(
                      authHeaderName: val != null && val.trim().isNotEmpty
                          ? val.trim()
                          : null,
                    ),
                  );
                },
              ),
            ],
            if (data.authType != McpAuthType.none) ...[
              AppSpacing.h16,
              TextFormField(
                initialValue: data.authEnvVar ?? '',
                decoration: InputDecoration(
                  labelText: l10n.mcpAuthEnvVarLabel,
                  border: const OutlineInputBorder(),
                ),
                onSaved: (val) {
                  _updateGateway(
                    ref,
                    (gw) => gw.copyWith(
                      authEnvVar: val != null && val.trim().isNotEmpty
                          ? val.trim()
                          : null,
                    ),
                  );
                },
              ),
            ],
            AppSpacing.h16,
            TextFormField(
              initialValue: data.timeoutSeconds.toString(),
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: l10n.mcpTimeoutSecondsLabel,
                border: const OutlineInputBorder(),
              ),
              validator: (val) {
                if (val == null || val.trim().isEmpty) {
                  return l10n.invalidJsonError;
                }
                final parsed = int.tryParse(val.trim());
                if (parsed == null || parsed < 1) {
                  return l10n.invalidJsonError;
                }
                return null;
              },
              onSaved: (val) {
                final parsed = int.tryParse(val?.trim() ?? '');
                if (parsed != null && parsed >= 1) {
                  _updateGateway(
                    ref,
                    (gw) => gw.copyWith(timeoutSeconds: parsed),
                  );
                }
              },
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
            Expanded(
              child: Row(
                children: [
                  Flexible(
                    child: Text(
                      l10n.allowedMcpToolsTitle,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontSize: 20,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  AppSpacing.w8,
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: AppSpacing.s8,
                      vertical: AppSpacing.s2,
                    ),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.primaryContainer,
                      borderRadius: BorderRadius.circular(AppSpacing.s12),
                    ),
                    child: Text(
                      l10n.mcpDiscoveredToolsCountBadge(tools.length),
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: Theme.of(context).colorScheme.onPrimaryContainer,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            AppSpacing.w16,
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
              title: Text(
                l10n.toolTitlePrefix(tool.toolId),
                overflow: TextOverflow.ellipsis,
              ),
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
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      SwitchListTile(
                        contentPadding: EdgeInsets.zero,
                        title: Text(
                          l10n.mcpToolEnabledLabel,
                          overflow: TextOverflow.ellipsis,
                          style: Theme.of(context).textTheme.bodyMedium
                              ?.copyWith(fontWeight: FontWeight.w600),
                        ),
                        value: tool.enabled,
                        onChanged: (bool val) {
                          _updateTool(
                            ref,
                            index,
                            (t) => t.copyWith(enabled: val),
                          );
                        },
                      ),
                      AppSpacing.h8,
                      Padding(
                        padding: const EdgeInsets.only(bottom: AppSpacing.s16),
                        child: TextFormField(
                          initialValue: tool.toolId,
                          decoration: InputDecoration(
                            labelText: l10n.toolIdLabel,
                            border: const OutlineInputBorder(),
                          ),
                          validator: (val) {
                            if (val == null || val.trim().isEmpty) {
                              return l10n.invalidJsonError;
                            }
                            return null;
                          },
                          onSaved: (val) {
                            _updateTool(
                              ref,
                              index,
                              (t) => t.copyWith(toolId: val?.trim() ?? ''),
                            );
                          },
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.only(bottom: AppSpacing.s16),
                        child: DropdownButtonFormField<ToolCapability>(
                          isExpanded: true,
                          initialValue: tool.capability,
                          decoration: InputDecoration(
                            labelText: l10n.mcpToolCapabilityLabel,
                            border: const OutlineInputBorder(),
                          ),
                          items: ToolCapability.values.map((cap) {
                            final capLabel = switch (cap) {
                              ToolCapability.search => l10n.mcpCapabilitySearch,
                              ToolCapability.documentReader =>
                                l10n.mcpCapabilityDocumentReader,
                              ToolCapability.action => l10n.mcpCapabilityAction,
                              ToolCapability.general =>
                                l10n.mcpCapabilityGeneral,
                            };
                            return DropdownMenuItem(
                              value: cap,
                              child: Text(
                                capLabel,
                                overflow: TextOverflow.ellipsis,
                              ),
                            );
                          }).toList(),
                          onChanged: (val) {
                            if (val != null) {
                              _updateTool(
                                ref,
                                index,
                                (t) => t.copyWith(capability: val),
                              );
                            }
                          },
                        ),
                      ),
                      _buildI18nGroup(context, ref, index, tool, l10n),
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
                      _buildParametersTable(context, tool, l10n),
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

  Widget _buildParametersTable(
    BuildContext context,
    AllowedMcpTool tool,
    AppLocalizations l10n,
  ) {
    // Phase 4, Step 4.2: Structured read-only parameter preview DataTable
    final properties = tool.inputSchema.properties;
    final requiredSet = tool.inputSchema.requiredFields.toSet();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          l10n.mcpParametersTableTitle,
          style: Theme.of(
            context,
          ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold),
        ),
        AppSpacing.h8,
        if (properties.isEmpty)
          Text(
            l10n.mcpNoParametersDefined,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
          )
        else
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              columns: [
                DataColumn(label: Text(l10n.mcpParamColName)),
                DataColumn(label: Text(l10n.mcpParamColType)),
                DataColumn(label: Text(l10n.mcpParamColRequired)),
                DataColumn(label: Text(l10n.mcpParamColDescription)),
              ],
              rows: properties.entries.map((propEntry) {
                final propName = propEntry.key;
                final propDef = propEntry.value;
                final isRequired = requiredSet.contains(propName);

                return DataRow(
                  cells: [
                    DataCell(
                      Text(
                        propName,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          fontFamily: 'monospace',
                        ),
                      ),
                    ),
                    DataCell(Text(propDef.type.name)),
                    DataCell(
                      Text(
                        isRequired
                            ? l10n.mcpParamRequiredYes
                            : l10n.mcpParamRequiredNo,
                      ),
                    ),
                    DataCell(
                      ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 350),
                        child: Text(
                          propDef.description,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ),
                  ],
                );
              }).toList(),
            ),
          ),
      ],
    );
  }

  Widget _buildI18nGroup(
    BuildContext context,
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
          style: Theme.of(
            context,
          ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold),
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
