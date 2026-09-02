import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/controllers/studio_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/views/widgets/i18n_text_field.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Tab 1: Profile identity, URL slug, workflow binding, and rich text preface.
class ProfileGeneralTab extends ConsumerWidget {
  final String id;
  const ProfileGeneralTab({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formState = ref.watch(outputProfileFormProvider(id));
    final workflowsState = ref.watch(workflowsControllerProvider);

    final payload = formState.value;
    if (payload == null) {
      throw StateError(
        'Profile payload must not be null when rendering ProfileGeneralTab',
      );
    }

    void updatePayload(OutputProfile p) {
      ref.read(outputProfileFormProvider(id).notifier).updatePayload(p);
    }

    return ListView(
      padding: AppSpacing.p16,
      children: [
        Card(
          child: Padding(
            padding: AppSpacing.p16,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                TextFormField(
                  initialValue: payload.id,
                  decoration: InputDecoration(
                    labelText: l10n.profileIdLabel,
                    border: const OutlineInputBorder(),
                  ),
                  readOnly: true,
                ),
                AppSpacing.h16,
                TextFormField(
                  initialValue: payload.slug,
                  decoration: InputDecoration(
                    labelText: l10n.urlSlugLabel,
                    border: const OutlineInputBorder(),
                  ),
                  onChanged: (val) {
                    updatePayload(payload.copyWith(slug: val.trim()));
                  },
                ),
                AppSpacing.h16,
                switch (workflowsState) {
                  AsyncData(value: final rawWorkflows) => Builder(
                    builder: (context) {
                      final workflows = rawWorkflows.cast<Workflow>();
                      String? currentValue = payload.workflowId.isNotEmpty
                          ? payload.workflowId
                          : null;
                      final bool hasValidValue =
                          currentValue != null &&
                          (workflows.any((w) => w.id == currentValue) ||
                              currentValue == '');
                      return DropdownButtonFormField<String>(
                        initialValue: hasValidValue ? currentValue : null,
                        isExpanded: true,
                        decoration: InputDecoration(
                          labelText: l10n.workflowIdBindingLabel,
                          border: const OutlineInputBorder(),
                        ),
                        hint: Text(l10n.selectWorkflowHint),
                        items: [
                          DropdownMenuItem(
                            value: '',
                            child: Text(
                              l10n.noneDefaultLabel,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          ...workflows.map((flow) {
                            final flowId = flow.id;
                            final localeCode = Localizations.localeOf(
                              context,
                            ).languageCode;
                            final displayName = flow.name.get(localeCode);
                            return DropdownMenuItem(
                              value: flowId,
                              child: Text(
                                '$displayName ($flowId)',
                                overflow: TextOverflow.ellipsis,
                              ),
                            );
                          }),
                        ],
                        onChanged: (val) {
                          if (val != null) {
                            updatePayload(payload.copyWith(workflowId: val));
                          }
                        },
                      );
                    },
                  ),
                  AsyncLoading() => const Center(
                    child: CircularProgressIndicator(),
                  ),
                  AsyncError(:final error) => Text(
                    l10n.studioViewsErrorLoadingWorkflows(error.toString()),
                  ),
                },
                AppSpacing.h16,
                I18nTextField(
                  label: l10n.profileDisplayNameLabel,
                  initialData: payload.name,
                  onChanged: (val) {
                    updatePayload(payload.copyWith(name: val));
                  },
                ),
                AppSpacing.h16,
                I18nTextField(
                  label: l10n.profileDescriptionLabel,
                  initialData: payload.description,
                  onChanged: (val) {
                    final isEmpty =
                        val.translations.isEmpty ||
                        val.translations.values.every((v) => v.trim().isEmpty);
                    updatePayload(
                      payload.copyWith(description: isEmpty ? null : val),
                    );
                  },
                ),
                AppSpacing.h16,
                I18nTextField(
                  label: l10n.customPrefaceLabel,
                  initialData: payload.customPreface,
                  onChanged: (val) {
                    final isEmpty =
                        val.translations.isEmpty ||
                        val.translations.values.every((v) => v.trim().isEmpty);
                    updatePayload(
                      payload.copyWith(customPreface: isEmpty ? null : val),
                    );
                  },
                ),
                AppSpacing.h16,
                InputDecorator(
                  decoration: InputDecoration(
                    labelText: l10n.profileLanguageLabel,
                    isDense: true,
                    border: const OutlineInputBorder(),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<SystemLocale?>(
                      value: payload.language,
                      isDense: true,
                      isExpanded: true,
                      items: [
                        DropdownMenuItem<SystemLocale?>(
                          value: null,
                          child: Text(
                            l10n.profileLanguageDefault,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        ...SystemLocale.values.map((locale) {
                          return DropdownMenuItem<SystemLocale?>(
                            value: locale,
                            child: Text(switch (locale) {
                              SystemLocale.fi => l10n.profileLanguageFi,
                              SystemLocale.en => l10n.profileLanguageEn,
                            }, overflow: TextOverflow.ellipsis),
                          );
                        }),
                      ],
                      onChanged: (val) {
                        updatePayload(payload.copyWith(language: val));
                      },
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
