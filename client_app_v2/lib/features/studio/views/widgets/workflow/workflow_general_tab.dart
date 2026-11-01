import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/features/studio/models/model_config.dart';
import '../../../../../l10n/gen/app_localizations.dart';
import '../i18n_text_field.dart';
import '../../../controllers/output_profile_controller.dart';
import '../../../controllers/mcp_gateways_controller.dart';
import '../../../controllers/model_registry_controller.dart';

/// **WorkflowGeneralTab**
///
/// Componentized UI widget representing Tab 1 of the Workflow Builder.
/// Handles high-level metadata and the default output profile routing.
class WorkflowGeneralTab extends HookConsumerWidget {
  final Workflow workflow;
  final TextEditingController idController;
  final TextEditingController slugController;
  final ValueChanged<Workflow> onChanged;

  const WorkflowGeneralTab({
    super.key,
    required this.workflow,
    required this.idController,
    required this.slugController,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final currentLocale = Localizations.localeOf(context).languageCode;
    final descTranslations = workflow.description.translations;

    final descEnController = useTextEditingController(
      text: descTranslations['en'] ?? '',
    );
    final descFiController = useTextEditingController(
      text: descTranslations['fi'] ?? '',
    );
    final syncedWorkflowId = useRef<String?>(null);

    useEffect(() {
      final nextEn = descTranslations['en'] ?? '';
      final nextFi = descTranslations['fi'] ?? '';
      if (syncedWorkflowId.value != workflow.id) {
        descEnController.text = nextEn;
        descFiController.text = nextFi;
        syncedWorkflowId.value = workflow.id;
      } else {
        if (descEnController.text != nextEn) {
          descEnController.value = descEnController.value.copyWith(
            text: nextEn,
            selection: TextSelection.collapsed(offset: nextEn.length),
          );
        }
        if (descFiController.text != nextFi) {
          descFiController.value = descFiController.value.copyWith(
            text: nextFi,
            selection: TextSelection.collapsed(offset: nextFi.length),
          );
        }
      }
      return null;
    }, [workflow.id, descTranslations['en'], descTranslations['fi']]);

    return SingleChildScrollView(
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: idController,
                    decoration: InputDecoration(
                      labelText: l10n.studioWorkflowIdOpaque,
                      prefixIcon: const Icon(Icons.fingerprint),
                    ),
                    readOnly: true, // Opaque Stripe ID mandate
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
                AppSpacing.w16,
                Expanded(
                  child: TextField(
                    controller: slugController,
                    decoration: InputDecoration(
                      labelText: l10n.studioWorkflowSlugSemantic,
                      prefixIcon: const Icon(Icons.link),
                    ),
                    onChanged: (val) {
                      onChanged(workflow.copyWith(slug: val));
                    },
                  ),
                ),
              ],
            ),
            AppSpacing.h16,
            Card(
              elevation: 2,
              child: Padding(
                padding: AppSpacing.p16,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      l10n.studioWorkflowIdentity,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    AppSpacing.h16,
                    I18nTextField(
                      label: l10n.studioWorkflowNameLabel,
                      initialData: workflow.name,
                      onChanged: (val) {
                        onChanged(workflow.copyWith(name: val));
                      },
                    ),
                    AppSpacing.h16,
                    TextField(
                      controller: descEnController,
                      maxLines: 2,
                      decoration: InputDecoration(
                        labelText: l10n.studioWorkflowDescEnLabel,
                        border: const OutlineInputBorder(),
                      ),
                      onChanged: (val) {
                        final newMap = Map<String, String>.from(
                          descTranslations,
                        );
                        newMap['en'] = val;
                        onChanged(
                          workflow.copyWith(
                            description: workflow.description.copyWith(
                              translations: newMap,
                            ),
                          ),
                        );
                      },
                    ),
                    AppSpacing.h16,
                    TextField(
                      controller: descFiController,
                      maxLines: 2,
                      decoration: InputDecoration(
                        labelText: l10n.studioWorkflowDescFiLabel,
                        border: const OutlineInputBorder(),
                      ),
                      onChanged: (val) {
                        final newMap = Map<String, String>.from(
                          descTranslations,
                        );
                        newMap['fi'] = val;
                        onChanged(
                          workflow.copyWith(
                            description: workflow.description.copyWith(
                              translations: newMap,
                            ),
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),
            ),
            AppSpacing.h16,
            Card(
              elevation: 2,
              child: Padding(
                padding: AppSpacing.p16,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      l10n.studioWorkflowGlobalSettings,
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    AppSpacing.h16,
                    Builder(
                      builder: (context) {
                        final globalProfilesAsync = ref.watch(
                          outputProfilesControllerProvider,
                        );
                        final globalProfiles = switch (globalProfilesAsync) {
                          AsyncData(:final value) => value,
                          _ => const <OutputProfile>[],
                        };
                        final applicableProfiles = globalProfiles
                            .where((p) => p.workflowId == workflow.id)
                            .toList();

                        final profileIds = applicableProfiles
                            .map((p) => p.id)
                            .toList();
                        final fallbackId = workflow.defaultProfileId.isNotEmpty
                            ? workflow.defaultProfileId
                            : 'default';
                        if (profileIds.isEmpty) profileIds.add(fallbackId);

                        final currentDefault = workflow.defaultProfileId;
                        final safeDefault = profileIds.contains(currentDefault)
                            ? currentDefault
                            : profileIds.first;

                        return DropdownButtonFormField<String>(
                          key: ValueKey(profileIds.join(':')),
                          initialValue: safeDefault == '' ? null : safeDefault,
                          isExpanded: true,
                          decoration: InputDecoration(
                            labelText: l10n.studioWorkflowDefaultProfile,
                            border: const OutlineInputBorder(),
                            isDense: true,
                          ),
                          items: profileIds.map((key) {
                            final profileData = applicableProfiles
                                .where((p) => p.id == key)
                                .firstOrNull;
                            final title =
                                (profileData != null &&
                                    profileData.name.isNotEmpty)
                                ? profileData.name.get(currentLocale)
                                : key;
                            final displayLabel = [title, '($key)'].join(' ');
                            return DropdownMenuItem(
                              value: key,
                              child: Text(
                                displayLabel,
                                overflow: TextOverflow.ellipsis,
                              ),
                            );
                          }).toList(),
                          onChanged: (val) {
                            if (val != null) {
                              onChanged(
                                workflow.copyWith(defaultProfileId: val),
                              );
                            }
                          },
                        );
                      },
                    ),
                    AppSpacing.h16,
                    Builder(
                      builder: (context) {
                        final mcpGatewaysAsync = ref.watch(
                          mcpGatewaysControllerProvider,
                        );
                        final gateways = switch (mcpGatewaysAsync) {
                          AsyncData(:final value) => value,
                          _ => const <McpGateway>[],
                        };
                        final currentGatewayId = workflow.mcpGatewayId;
                        final hasCurrentGw =
                            currentGatewayId == null ||
                            gateways.any((gw) => gw.id == currentGatewayId);
                        final safeGatewayId = hasCurrentGw
                            ? currentGatewayId
                            : null;

                        return DropdownButtonFormField<String?>(
                          key: ValueKey(
                            'mcp_gw_${gateways.length}_$safeGatewayId',
                          ),
                          initialValue: safeGatewayId,
                          isExpanded: true,
                          decoration: InputDecoration(
                            labelText: l10n.studioWorkflowMcpGateway,
                            border: const OutlineInputBorder(),
                            isDense: true,
                          ),
                          items: [
                            DropdownMenuItem<String?>(
                              value: null,
                              child: Text(
                                l10n.studioWorkflowMcpGatewayNone,
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            ...gateways.map((gw) {
                              final id = gw.id;
                              final toolsCount = gw.tools.length;
                              final displayLabel = [
                                id,
                                '($toolsCount)',
                              ].join(' ');
                              return DropdownMenuItem<String?>(
                                value: id,
                                child: Text(
                                  displayLabel,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              );
                            }),
                          ],
                          onChanged: (val) {
                            onChanged(workflow.copyWith(mcpGatewayId: val));
                          },
                        );
                      },
                    ),
                    AppSpacing.h16,
                    Builder(
                      builder: (context) {
                        final registriesAsync = ref.watch(
                          modelRegistryControllerProvider,
                        );
                        final registries = switch (registriesAsync) {
                          AsyncData(:final value) => value,
                          _ => const <ModelConfig>[],
                        };
                        final currentRegistryId = workflow.modelRegistryId;

                        final hasCurrent = registries.any(
                          (r) => r.id == currentRegistryId,
                        );

                        return DropdownButtonFormField<String>(
                          key: ValueKey(
                            'model_registry_${registries.length}_$currentRegistryId',
                          ),
                          initialValue: currentRegistryId.isNotEmpty
                              ? currentRegistryId
                              : (registries.isNotEmpty
                                    ? registries.first.id
                                    : null),
                          isExpanded: true,
                          decoration: InputDecoration(
                            labelText: l10n.studioWorkflowModelRegistry,
                            helperText:
                                l10n.studioWorkflowModelRegistrySubtitle,
                            border: const OutlineInputBorder(),
                            isDense: true,
                          ),
                          items: [
                            if (!hasCurrent && currentRegistryId.isNotEmpty)
                              DropdownMenuItem<String>(
                                value: currentRegistryId,
                                child: Text(
                                  currentRegistryId,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ...registries.map((r) {
                              final name = r.name.isNotEmpty ? r.name : r.id;
                              final provider = r.defaultProvider.toUpperCase();
                              final displayLabel = [
                                name,
                                '($provider)',
                              ].join(' ');
                              return DropdownMenuItem<String>(
                                value: r.id,
                                child: Text(
                                  displayLabel,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              );
                            }),
                          ],
                          onChanged: (val) {
                            if (val != null) {
                              onChanged(
                                workflow.copyWith(modelRegistryId: val),
                              );
                            }
                          },
                        );
                      },
                    ),
                    AppSpacing.h16,
                    SwitchListTile(
                      title: Text(l10n.enableContextualOverridesLabel),
                      subtitle: Text(l10n.enableContextualOverridesDescription),
                      value: workflow.enableContextualOverrides,
                      onChanged: (val) {
                        onChanged(
                          workflow.copyWith(enableContextualOverrides: val),
                        );
                      },
                      contentPadding: EdgeInsets.zero,
                    ),
                    AppSpacing.h16,
                    SwitchListTile(
                      title: Text(l10n.systemAuditTrailLabel),
                      subtitle: Text(l10n.systemAuditTrailDescription),
                      value: workflow.systemAuditTrail,
                      onChanged: (val) {
                        onChanged(workflow.copyWith(systemAuditTrail: val));
                      },
                      contentPadding: EdgeInsets.zero,
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
