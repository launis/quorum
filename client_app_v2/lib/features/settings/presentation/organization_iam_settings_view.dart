import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/execution/views/new_execution_view.dart';
import 'package:client_app/features/settings/domain/models/tenant_secret_dto.dart';
import 'package:client_app/features/studio/models/mcp_gateway.dart';
import 'package:client_app/features/studio/models/task_brief.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/router/router.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'organization_iam_settings_view.g.dart';

@riverpod
Future<List<McpGateway>> availableMcpGateways(Ref ref) async =>
    ref.watch(studioClientProvider).getMcpGateways();

@riverpod
Future<List<TaskBrief>> organizationTaskBriefs(Ref ref) async {
  return await ref.watch(studioClientProvider).getTaskBriefs();
}

String _resolveTaskBriefLabel(I18nText text, String localeCode) {
  final primary = text.translations[localeCode];
  if (primary != null && primary.trim().isNotEmpty) {
    return primary;
  }
  final fallback = text.translations['en'];
  if (fallback != null && fallback.trim().isNotEmpty) {
    return fallback;
  }
  throw AppException.validation('Fail-Fast: Missing required translation.');
}

@riverpod
Future<List<Organization>> availableOrganizations(Ref ref) async {
  final result = await ref.watch(userRepositoryProvider).listOrganizations();
  return result.fold((err) => throw err, (list) => list);
}

@riverpod
Future<Organization> organizationProfile(Ref ref, String orgId) async {
  final result = await ref.watch(userRepositoryProvider).getOrganization(orgId);
  return result.fold((err) => throw err, (org) => org);
}

@riverpod
Future<List<ExecutionAssignmentResponseDto>> organizationAssignments(
  Ref ref,
) async {
  return await ref.watch(executionClientProvider).listAssignments();
}

@riverpod
Future<List<InvitationResponseDto>> organizationInvitations(
  Ref ref,
  String orgId,
) async {
  final result = await ref.watch(userRepositoryProvider).listInvitations(orgId);
  return result.fold((err) => throw err, (list) => list);
}

@riverpod
Future<List<User>> organizationMembers(Ref ref) async {
  final result = await ref.watch(userRepositoryProvider).listUsers();
  return result.fold((err) => throw err, (list) => list);
}

@riverpod
Future<List<TenantSecretResponseDto>> organizationSecrets(
  Ref ref,
  String orgId,
) async {
  final result = await ref.watch(userRepositoryProvider).listSecrets(orgId);
  return result.fold((err) => throw err, (list) => list);
}

class OrganizationIamSettingsView extends HookConsumerWidget {
  const OrganizationIamSettingsView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final authState = ref.watch(authControllerProvider);
    final selectedOrgId = useState<String?>(null);

    return AppErrorBoundary(
      child: Scaffold(
        appBar: AppBar(title: Text(l10n.orgIamViewTitle)),
        body: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
            child: switch (authState) {
              AsyncLoading() => const Center(
                child: CircularProgressIndicator(),
              ),
              AsyncError(:final error, :final stackTrace) => ErrorView(
                error: error,
                stackTrace: stackTrace,
              ),
              AsyncData(:final value) => () {
                if (value == null ||
                    (value.role != UserRole.manager &&
                        value.role != UserRole.admin &&
                        value.role != UserRole.root)) {
                  return Center(
                    child: Card(
                      key: const Key('org_iam_restricted_card'),
                      child: Padding(
                        padding: AppSpacing.p24,
                        child: Text(
                          l10n.errorUnauthorized,
                          style: theme.textTheme.titleMedium?.copyWith(
                            color: theme.colorScheme.error,
                          ),
                        ),
                      ),
                    ),
                  );
                }

                final defaultOrgId = value.organizationId;
                if (defaultOrgId == null || defaultOrgId.isEmpty) {
                  return Center(child: Text(l10n.errorNotFound));
                }

                final activeOrgId = value.role == UserRole.root
                    ? (selectedOrgId.value ?? defaultOrgId)
                    : defaultOrgId;

                final isAdminOrRoot =
                    value.role == UserRole.admin || value.role == UserRole.root;

                return SingleChildScrollView(
                  padding: AppSpacing.p24,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      if (value.role == UserRole.root)
                        _RootOrganizationSelectorCard(
                          activeOrgId: activeOrgId,
                          l10n: l10n,
                          onOrganizationSelected: (nextOrgId) {
                            selectedOrgId.value = nextOrgId;
                            ref.invalidate(organizationMembersProvider);
                            ref.invalidate(organizationAssignmentsProvider);
                            ref.invalidate(organizationTaskBriefsProvider);
                          },
                        ),
                      _OrganizationMetadataCard(
                        orgId: activeOrgId,
                        l10n: l10n,
                        theme: theme,
                      ),
                      _TaskAssignmentsManagementCard(l10n: l10n, theme: theme),
                      if (isAdminOrRoot) ...[
                        _InvitationsAndMembersCard(
                          orgId: activeOrgId,
                          currentUser: value,
                          l10n: l10n,
                          theme: theme,
                        ),
                        _TaskBriefsManagementCard(
                          activeOrgId: activeOrgId,
                          currentUser: value,
                          l10n: l10n,
                          theme: theme,
                        ),
                        _ByokSecretsCard(
                          orgId: activeOrgId,
                          l10n: l10n,
                          theme: theme,
                        ),
                      ],
                    ],
                  ),
                );
              }(),
            },
          ),
        ),
      ),
    );
  }
}

class _RootOrganizationSelectorCard extends ConsumerWidget {
  final String activeOrgId;
  final AppLocalizations l10n;
  final ValueChanged<String> onOrganizationSelected;

  const _RootOrganizationSelectorCard({
    required this.activeOrgId,
    required this.l10n,
    required this.onOrganizationSelected,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final orgsAsync = ref.watch(availableOrganizationsProvider);

    return Card(
      key: const Key('org_root_selector_card'),
      elevation: 2,
      margin: const EdgeInsets.only(bottom: AppSpacing.s16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p16,
        child: switch (orgsAsync) {
          AsyncLoading() => const Center(child: CircularProgressIndicator()),
          AsyncError(:final error, :final stackTrace) => ErrorView(
            error: error,
            stackTrace: stackTrace,
            compact: true,
          ),
          AsyncData(value: final orgs) =>
            !orgs.any((o) => o.id == activeOrgId)
                ? ErrorView(
                    error: AppException.notFound(l10n.errorNotFound),
                    compact: true,
                  )
                : DropdownButtonFormField<String>(
                    key: const Key('org_root_selector_dropdown'),
                    isExpanded: true,
                    initialValue: activeOrgId,
                    decoration: InputDecoration(
                      labelText: l10n.orgSelectOrganizationLabel,
                      prefixIcon: const Icon(Icons.domain_outlined),
                      border: const OutlineInputBorder(),
                    ),
                    items: [
                      for (final org in orgs)
                        DropdownMenuItem(
                          value: org.id,
                          child: Text(
                            org.name,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                    ],
                    onChanged: (nextOrgId) {
                      if (nextOrgId != null && nextOrgId != activeOrgId) {
                        onOrganizationSelected(nextOrgId);
                      }
                    },
                  ),
        },
      ),
    );
  }
}

class _OrganizationMetadataCard extends HookConsumerWidget {
  final String orgId;
  final AppLocalizations l10n;
  final ThemeData theme;

  const _OrganizationMetadataCard({
    required this.orgId,
    required this.l10n,
    required this.theme,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final orgAsync = ref.watch(organizationProfileProvider(orgId));
    final saveMutation = useMutation<void>();

    return Card(
      key: const Key('org_metadata_card'),
      elevation: 2,
      margin: const EdgeInsets.only(bottom: AppSpacing.s16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p16,
        child: switch (orgAsync) {
          AsyncLoading() => const Center(child: CircularProgressIndicator()),
          AsyncError(:final error, :final stackTrace) => ErrorView(
            error: error,
            stackTrace: stackTrace,
            compact: true,
          ),
          AsyncData(:final value) => _OrganizationMetadataForm(
            org: value,
            saveMutation: saveMutation,
            l10n: l10n,
            theme: theme,
          ),
        },
      ),
    );
  }
}

class _OrganizationMetadataForm extends HookConsumerWidget {
  final Organization org;
  final MutationState<void> saveMutation;
  final AppLocalizations l10n;
  final ThemeData theme;

  const _OrganizationMetadataForm({
    required this.org,
    required this.saveMutation,
    required this.l10n,
    required this.theme,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nameController = useTextEditingController(text: org.name);
    final contactEmailController = useTextEditingController(
      text: org.contactEmail ?? '',
    );
    final quotaController = useTextEditingController(
      text: org.quotaLimit.toStringAsFixed(2),
    );
    final tpmController = useTextEditingController(
      text: org.tpmLimit.toString(),
    );
    final rpmController = useTextEditingController(
      text: org.rpmLimit.toString(),
    );

    useEffect(
      () {
        nameController.text = org.name;
        contactEmailController.text = org.contactEmail ?? '';
        quotaController.text = org.quotaLimit.toStringAsFixed(2);
        tpmController.text = org.tpmLimit.toString();
        rpmController.text = org.rpmLimit.toString();
        return null;
      },
      [
        org.id,
        org.name,
        org.contactEmail,
        org.quotaLimit,
        org.tpmLimit,
        org.rpmLimit,
      ],
    );

    Future<void> saveOrg() async {
      final nextName = nameController.text.trim();
      final nextEmail = contactEmailController.text.trim();
      await saveMutation.mutate(() async {
        final result = await ref
            .read(userRepositoryProvider)
            .updateOrganization(
              org.id,
              OrganizationUpdateDto(
                name: nextName.isEmpty ? null : nextName,
                contactEmail: nextEmail.isEmpty ? null : nextEmail,
              ),
            );
        result.fold((err) => throw err, (_) {
          ref.invalidate(organizationProfileProvider(org.id));
          if (context.mounted) {
            ScaffoldMessenger.of(
              context,
            ).showSnackBar(SnackBar(content: Text(l10n.profileUpdatedSuccess)));
          }
        });
      });
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                l10n.orgProfileCardTitle,
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.s12,
                vertical: AppSpacing.s4,
              ),
              decoration: BoxDecoration(
                color: theme.colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(AppSpacing.s12),
              ),
              child: Text(
                org.subscriptionStatus.name.toUpperCase(),
                style: theme.textTheme.labelMedium?.copyWith(
                  color: theme.colorScheme.onPrimaryContainer,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
        AppSpacing.h16,
        Row(
          children: [
            Expanded(
              child: TextFormField(
                key: const Key('org_quota_limit_readonly_field'),
                controller: quotaController,
                readOnly: true,
                decoration: InputDecoration(
                  labelText: l10n.orgQuotaLimitLabel,
                  border: const OutlineInputBorder(),
                ),
              ),
            ),
            AppSpacing.w12,
            Expanded(
              child: TextFormField(
                key: const Key('org_tpm_limit_readonly_field'),
                controller: tpmController,
                readOnly: true,
                decoration: InputDecoration(
                  labelText: l10n.orgTpmLimitLabel,
                  border: const OutlineInputBorder(),
                ),
              ),
            ),
            AppSpacing.w12,
            Expanded(
              child: TextFormField(
                key: const Key('org_rpm_limit_readonly_field'),
                controller: rpmController,
                readOnly: true,
                decoration: InputDecoration(
                  labelText: l10n.orgRpmLimitLabel,
                  border: const OutlineInputBorder(),
                ),
              ),
            ),
          ],
        ),
        AppSpacing.h16,
        TextFormField(
          key: const Key('org_name_field'),
          controller: nameController,
          decoration: InputDecoration(
            labelText: l10n.orgNameLabel,
            prefixIcon: const Icon(Icons.business_outlined),
            border: const OutlineInputBorder(),
          ),
        ),
        AppSpacing.h12,
        TextFormField(
          key: const Key('org_contact_email_field'),
          controller: contactEmailController,
          decoration: InputDecoration(
            labelText: l10n.orgContactEmailLabel,
            prefixIcon: const Icon(Icons.alternate_email),
            border: const OutlineInputBorder(),
          ),
        ),
        AppSpacing.h16,
        if (saveMutation.hasError) ...[
          ErrorView(error: saveMutation.error!, compact: true),
          AppSpacing.h12,
        ],
        OutlinedButton.icon(
          key: const Key('org_save_metadata_btn'),
          onPressed: saveMutation.isLoading ? null : saveOrg,
          icon: const Icon(Icons.save_outlined),
          label: Text(l10n.orgSaveProfileBtn),
        ),
      ],
    );
  }
}

class _TaskAssignmentsManagementCard extends HookConsumerWidget {
  final AppLocalizations l10n;
  final ThemeData theme;

  const _TaskAssignmentsManagementCard({
    required this.l10n,
    required this.theme,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final assignmentsAsync = ref.watch(organizationAssignmentsProvider);
    final actionMutation = useMutation<void>();

    return Card(
      key: const Key('org_assignments_card'),
      elevation: 2,
      margin: const EdgeInsets.only(bottom: AppSpacing.s16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    l10n.orgTaskAssignmentsCardTitle,
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                IconButton(
                  key: const Key('org_refresh_assignments_btn'),
                  tooltip: l10n.refresh,
                  onPressed: () =>
                      ref.invalidate(organizationAssignmentsProvider),
                  icon: const Icon(Icons.refresh),
                ),
                AppSpacing.w8,
                OutlinedButton.icon(
                  key: const Key('org_new_task_assignment_btn'),
                  onPressed: () async {
                    final localeCode = Localizations.localeOf(
                      context,
                    ).languageCode;
                    await showDialog<void>(
                      context: context,
                      builder: (dialogContext) =>
                          TaskAssignmentConfigDialog(targetLocale: localeCode),
                    );
                    if (!context.mounted) return;
                    ref.invalidate(organizationAssignmentsProvider);
                  },
                  icon: const Icon(Icons.add_task_outlined),
                  label: Text(l10n.orgNewTaskAssignmentBtn),
                ),
              ],
            ),
            AppSpacing.h16,
            if (actionMutation.hasError) ...[
              ErrorView(error: actionMutation.error!, compact: true),
              AppSpacing.h12,
            ],
            switch (assignmentsAsync) {
              AsyncLoading() => const Center(
                child: CircularProgressIndicator(),
              ),
              AsyncError(:final error, :final stackTrace) => ErrorView(
                error: error,
                stackTrace: stackTrace,
                compact: true,
              ),
              AsyncData(:final value) =>
                value.isEmpty
                    ? Text(
                        l10n.noWorkflowsAvailable,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      )
                    : Column(
                        children: value.map((assignment) {
                          return Container(
                            margin: const EdgeInsets.only(
                              bottom: AppSpacing.s12,
                            ),
                            padding: AppSpacing.p12,
                            decoration: BoxDecoration(
                              border: Border.all(
                                color: theme.colorScheme.outlineVariant,
                              ),
                              borderRadius: BorderRadius.circular(
                                AppSpacing.s12,
                              ),
                            ),
                            child: Row(
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        assignment.assignedEmail,
                                        style: theme.textTheme.titleSmall
                                            ?.copyWith(
                                              fontWeight: FontWeight.bold,
                                            ),
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      AppSpacing.h4,
                                      Wrap(
                                        spacing: AppSpacing.s8,
                                        runSpacing: AppSpacing.s4,
                                        children: [
                                          Container(
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: AppSpacing.s8,
                                              vertical: AppSpacing.s2,
                                            ),
                                            decoration: BoxDecoration(
                                              color: theme
                                                  .colorScheme
                                                  .primaryContainer,
                                              borderRadius:
                                                  BorderRadius.circular(
                                                    AppSpacing.s12,
                                                  ),
                                            ),
                                            child: Text(
                                              assignment.status.name
                                                  .toUpperCase(),
                                              style: theme.textTheme.labelSmall,
                                            ),
                                          ),
                                          Container(
                                            padding: const EdgeInsets.symmetric(
                                              horizontal: AppSpacing.s8,
                                              vertical: AppSpacing.s2,
                                            ),
                                            decoration: BoxDecoration(
                                              color: theme
                                                  .colorScheme
                                                  .secondaryContainer,
                                              borderRadius:
                                                  BorderRadius.circular(
                                                    AppSpacing.s12,
                                                  ),
                                            ),
                                            child: Text(
                                              assignment
                                                  .emailDeliveryStatus
                                                  .name
                                                  .toUpperCase(),
                                              style: theme.textTheme.labelSmall,
                                            ),
                                          ),
                                          if (assignment.batchId != null)
                                            Container(
                                              padding:
                                                  const EdgeInsets.symmetric(
                                                    horizontal: AppSpacing.s8,
                                                    vertical: AppSpacing.s2,
                                                  ),
                                              decoration: BoxDecoration(
                                                color: theme
                                                    .colorScheme
                                                    .tertiaryContainer,
                                                borderRadius:
                                                    BorderRadius.circular(
                                                      AppSpacing.s12,
                                                    ),
                                              ),
                                              child: Text(
                                                assignment.batchId!,
                                                style:
                                                    theme.textTheme.labelSmall,
                                              ),
                                            ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                                AppSpacing.w8,
                                if (assignment.status ==
                                        AssignmentStatus.pending ||
                                    assignment.status ==
                                        AssignmentStatus.activated)
                                  OutlinedButton.icon(
                                    onPressed: actionMutation.isLoading
                                        ? null
                                        : () => actionMutation.mutate(() async {
                                            await ref
                                                .read(executionClientProvider)
                                                .resendAssignmentEmail(
                                                  assignment.id,
                                                );
                                            ref.invalidate(
                                              organizationAssignmentsProvider,
                                            );
                                          }),
                                    icon: const Icon(Icons.mark_email_unread),
                                    label: Text(l10n.orgResendEmailBtn),
                                  ),
                                if (assignment.executionId != null) ...[
                                  AppSpacing.w8,
                                  OutlinedButton.icon(
                                    onPressed: () {
                                      ExecutionReportRoute(
                                        executionId: assignment.executionId!,
                                      ).go(context);
                                    },
                                    icon: const Icon(Icons.assessment_outlined),
                                    label: Text(l10n.orgOpenReportBtn),
                                  ),
                                ],
                              ],
                            ),
                          );
                        }).toList(),
                      ),
            },
          ],
        ),
      ),
    );
  }
}

class _TaskBriefsManagementCard extends HookConsumerWidget {
  final String activeOrgId;
  final User currentUser;
  final AppLocalizations l10n;
  final ThemeData theme;

  const _TaskBriefsManagementCard({
    required this.activeOrgId,
    required this.currentUser,
    required this.l10n,
    required this.theme,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final briefsAsync = ref.watch(organizationTaskBriefsProvider);
    final mutation = useMutation<void>();
    final localeCode = Localizations.localeOf(context).languageCode;

    return Card(
      key: const Key('org_task_briefs_card'),
      elevation: 2,
      margin: const EdgeInsets.only(bottom: AppSpacing.s16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    l10n.orgTaskBriefsCardTitle,
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                OutlinedButton.icon(
                  key: const Key('org_create_task_brief_btn'),
                  onPressed: mutation.isLoading
                      ? null
                      : () => mutation.mutate(() async {
                          await ref
                              .read(studioClientProvider)
                              .createTaskBriefDraft();
                          if (!context.mounted) return;
                          ref.invalidate(organizationTaskBriefsProvider);
                          ref.invalidate(availableTaskBriefsProvider);
                        }),
                  icon: const Icon(Icons.note_add_outlined),
                  label: Text(l10n.orgCreateTaskBriefBtn),
                ),
              ],
            ),
            AppSpacing.h16,
            if (mutation.hasError) ...[
              ErrorView(error: mutation.error!, compact: true),
              AppSpacing.h12,
            ],
            switch (briefsAsync) {
              AsyncLoading() => const Center(
                child: CircularProgressIndicator(),
              ),
              AsyncError(:final error, :final stackTrace) => ErrorView(
                error: error,
                stackTrace: stackTrace,
                compact: true,
              ),
              AsyncData(value: final briefs) => () {
                if (briefs.isEmpty) {
                  return Text(
                    l10n.orgTaskBriefEmptyState,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  );
                }
                return Column(
                  children: briefs.map((brief) {
                    final canModify =
                        currentUser.role == UserRole.root ||
                        brief.organizationId == activeOrgId;
                    final title = _resolveTaskBriefLabel(
                      brief.label,
                      localeCode,
                    );
                    final sourceUrl = brief.sourceUrl;
                    final bodyText = brief.instructionText;
                    return Container(
                      key: Key('org_task_brief_row_${brief.id}'),
                      margin: const EdgeInsets.only(bottom: AppSpacing.s12),
                      padding: AppSpacing.p12,
                      decoration: BoxDecoration(
                        border: Border.all(
                          color: theme.colorScheme.outlineVariant,
                        ),
                        borderRadius: BorderRadius.circular(AppSpacing.s12),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  title,
                                  style: theme.textTheme.titleSmall?.copyWith(
                                    fontWeight: FontWeight.bold,
                                  ),
                                  overflow: TextOverflow.ellipsis,
                                ),
                                if (sourceUrl != null &&
                                    sourceUrl.trim().isNotEmpty) ...[
                                  AppSpacing.h4,
                                  Text(
                                    sourceUrl,
                                    style: theme.textTheme.bodySmall?.copyWith(
                                      color: theme.colorScheme.primary,
                                    ),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ],
                                if (bodyText != null &&
                                    bodyText.trim().isNotEmpty) ...[
                                  AppSpacing.h4,
                                  Text(
                                    bodyText,
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                    style: theme.textTheme.bodySmall?.copyWith(
                                      color: theme.colorScheme.onSurfaceVariant,
                                    ),
                                  ),
                                ],
                              ],
                            ),
                          ),
                          IconButton(
                            key: Key('org_clone_task_brief_btn_${brief.id}'),
                            tooltip: l10n.tooltipDuplicate,
                            icon: const Icon(Icons.copy_outlined),
                            onPressed: mutation.isLoading
                                ? null
                                : () => mutation.mutate(() async {
                                    await ref
                                        .read(studioClientProvider)
                                        .cloneTaskBrief(brief.id);
                                    if (!context.mounted) return;
                                    ref.invalidate(
                                      organizationTaskBriefsProvider,
                                    );
                                    ref.invalidate(availableTaskBriefsProvider);
                                  }),
                          ),
                          IconButton(
                            key: Key('org_edit_task_brief_btn_${brief.id}'),
                            tooltip: l10n.orgEditTaskBriefTooltip,
                            icon: const Icon(Icons.edit_outlined),
                            onPressed: (!canModify || mutation.isLoading)
                                ? null
                                : () async {
                                    await showDialog<void>(
                                      context: context,
                                      builder: (dialogContext) =>
                                          _EditTaskBriefDialog(
                                            brief: brief,
                                            l10n: l10n,
                                          ),
                                    );
                                    if (!context.mounted) return;
                                    ref.invalidate(
                                      organizationTaskBriefsProvider,
                                    );
                                    ref.invalidate(availableTaskBriefsProvider);
                                  },
                          ),
                          IconButton(
                            key: Key('org_delete_task_brief_btn_${brief.id}'),
                            tooltip: l10n.delete,
                            color: theme.colorScheme.error,
                            icon: const Icon(Icons.delete_outline),
                            onPressed: (!canModify || mutation.isLoading)
                                ? null
                                : () => mutation.mutate(() async {
                                    await ref
                                        .read(studioClientProvider)
                                        .deleteTaskBrief(brief.id);
                                    if (!context.mounted) return;
                                    ref.invalidate(
                                      organizationTaskBriefsProvider,
                                    );
                                    ref.invalidate(availableTaskBriefsProvider);
                                  }),
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                );
              }(),
            },
          ],
        ),
      ),
    );
  }
}

class _EditTaskBriefDialog extends HookConsumerWidget {
  final TaskBrief brief;
  final AppLocalizations l10n;

  const _EditTaskBriefDialog({required this.brief, required this.l10n});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final localeCode = Localizations.localeOf(context).languageCode;
    final titleController = useTextEditingController(
      text: _resolveTaskBriefLabel(brief.label, localeCode),
    );
    final urlController = useTextEditingController(text: brief.sourceUrl ?? '');
    final bodyController = useTextEditingController(
      text: brief.instructionText ?? '',
    );
    final saveMutation = useMutation<void>();

    Future<void> saveBrief() async {
      final nextTitle = titleController.text.trim();
      final nextUrl = urlController.text.trim();
      final nextBody = bodyController.text.trim();

      await saveMutation.mutate(() async {
        if (nextTitle.isEmpty) {
          throw AppException.validation(l10n.errorValidation);
        }
        final updatedBrief = brief.copyWith(
          label: I18nText(
            translations: <String, String>{
              ...brief.label.translations,
              'en': nextTitle,
              'fi': nextTitle,
            },
          ),
          instructionText: nextBody.isEmpty ? null : nextBody,
          sourceUrl: nextUrl.isEmpty ? null : nextUrl,
        );
        await ref
            .read(studioClientProvider)
            .saveTaskBrief(brief.id, updatedBrief);
        if (!context.mounted) return;
        Navigator.of(context).pop();
      });
    }

    return AlertDialog(
      key: const Key('org_edit_task_brief_dialog'),
      title: Text(l10n.orgEditTaskBriefDialogTitle),
      content: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 600),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextField(
                key: const Key('org_edit_task_brief_title_field'),
                controller: titleController,
                decoration: InputDecoration(
                  labelText: l10n.orgTaskBriefTitleLabel,
                  border: const OutlineInputBorder(),
                ),
              ),
              AppSpacing.h12,
              TextField(
                key: const Key('org_edit_task_brief_url_field'),
                controller: urlController,
                decoration: InputDecoration(
                  labelText: l10n.orgTaskBriefUrlLabel,
                  border: const OutlineInputBorder(),
                ),
              ),
              AppSpacing.h12,
              TextField(
                key: const Key('org_edit_task_brief_body_field'),
                controller: bodyController,
                minLines: 4,
                maxLines: 8,
                decoration: InputDecoration(
                  labelText: l10n.orgTaskBriefBodyLabel,
                  border: const OutlineInputBorder(),
                ),
              ),
              if (saveMutation.hasError) ...[
                AppSpacing.h12,
                ErrorView(error: saveMutation.error!, compact: true),
              ],
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(l10n.cancel),
        ),
        OutlinedButton.icon(
          key: const Key('org_edit_task_brief_save_btn'),
          onPressed: saveMutation.isLoading ? null : saveBrief,
          icon: const Icon(Icons.save_outlined),
          label: Text(l10n.save),
        ),
      ],
    );
  }
}

enum _UserProvisioningMode { singleInvite, batchInvite, directCreate }

class _InvitationsAndMembersCard extends HookConsumerWidget {
  final String orgId;
  final User currentUser;
  final AppLocalizations l10n;
  final ThemeData theme;

  const _InvitationsAndMembersCard({
    required this.orgId,
    required this.currentUser,
    required this.l10n,
    required this.theme,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final invitationsAsync = ref.watch(organizationInvitationsProvider(orgId));
    final membersAsync = ref.watch(organizationMembersProvider);
    final emailController = useTextEditingController();
    final batchEmailsController = useTextEditingController();
    final createEmailController = useTextEditingController();
    final createNameController = useTextEditingController();
    final createPasswordController = useTextEditingController();
    final selectedRole = useState<UserRole>(UserRole.member);
    final provisioningMode = useState<_UserProvisioningMode>(
      _UserProvisioningMode.singleInvite,
    );
    final mutation = useMutation<void>();

    final assignableRoles = <UserRole>[
      UserRole.viewer,
      UserRole.member,
      UserRole.manager,
      UserRole.admin,
      if (currentUser.role == UserRole.root) UserRole.root,
    ];

    Future<void> sendInvite() async {
      await mutation.mutate(() async {
        if (provisioningMode.value == _UserProvisioningMode.batchInvite) {
          final lines = batchEmailsController.text
              .split(RegExp(r'[\r\n,;]+'))
              .map((s) => s.trim())
              .where((s) => s.contains('@'))
              .toList();
          if (lines.isEmpty) return;
          final recipients = lines
              .map(
                (email) =>
                    InvitationCreateDto(email: email, role: selectedRole.value),
              )
              .toList();
          final res = await ref
              .read(userRepositoryProvider)
              .createInvitationBatch(
                orgId,
                InvitationBatchCreateDto(recipients: recipients),
              );
          res.fold((err) => throw err, (_) {
            batchEmailsController.clear();
            ref.invalidate(organizationInvitationsProvider(orgId));
          });
        } else {
          final email = emailController.text.trim();
          if (email.isEmpty) return;
          final res = await ref
              .read(userRepositoryProvider)
              .createInvitation(
                orgId,
                InvitationCreateDto(email: email, role: selectedRole.value),
              );
          res.fold((err) => throw err, (_) {
            emailController.clear();
            ref.invalidate(organizationInvitationsProvider(orgId));
          });
        }
      });
    }

    Future<void> createDirectUser() async {
      await mutation.mutate(() async {
        final email = createEmailController.text.trim();
        final name = createNameController.text.trim();
        final password = createPasswordController.text;
        if (email.isEmpty || !email.contains('@') || password.length < 6) {
          throw AppException.validation(l10n.orgCreateUserPasswordHint);
        }
        final res = await ref
            .read(userRepositoryProvider)
            .createUser(
              UserCreate(
                email: email,
                name: name.isEmpty ? null : name,
                role: selectedRole.value,
                organizationId: orgId,
                password: password,
              ),
            );
        res.fold((err) => throw err, (_) {
          createEmailController.clear();
          createNameController.clear();
          createPasswordController.clear();
          ref.invalidate(organizationMembersProvider);
          if (context.mounted) {
            ScaffoldMessenger.of(
              context,
            ).showSnackBar(SnackBar(content: Text(l10n.orgCreateUserSuccess)));
          }
        });
      });
    }

    return Card(
      key: const Key('org_invitations_card'),
      elevation: 2,
      margin: const EdgeInsets.only(bottom: AppSpacing.s16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.orgInvitationsCardTitle,
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            AppSpacing.h12,
            Wrap(
              spacing: AppSpacing.s8,
              runSpacing: AppSpacing.s8,
              children: [
                ChoiceChip(
                  label: Text(l10n.orgSendInvitationBtn),
                  selected:
                      provisioningMode.value ==
                      _UserProvisioningMode.singleInvite,
                  onSelected: (_) => provisioningMode.value =
                      _UserProvisioningMode.singleInvite,
                ),
                ChoiceChip(
                  label: Text(l10n.orgSendBatchInvitationBtn),
                  selected:
                      provisioningMode.value ==
                      _UserProvisioningMode.batchInvite,
                  onSelected: (_) => provisioningMode.value =
                      _UserProvisioningMode.batchInvite,
                ),
                ChoiceChip(
                  key: const Key('org_create_user_mode_chip'),
                  label: Text(l10n.orgCreateUserDirectBtn),
                  selected:
                      provisioningMode.value ==
                      _UserProvisioningMode.directCreate,
                  onSelected: (_) => provisioningMode.value =
                      _UserProvisioningMode.directCreate,
                ),
              ],
            ),
            AppSpacing.h12,
            switch (provisioningMode.value) {
              _UserProvisioningMode.singleInvite => TextFormField(
                key: const Key('org_invite_email_field'),
                controller: emailController,
                decoration: InputDecoration(
                  labelText: l10n.orgInviteEmailLabel,
                  prefixIcon: const Icon(Icons.mail_outline),
                  border: const OutlineInputBorder(),
                ),
              ),
              _UserProvisioningMode.batchInvite => TextFormField(
                key: const Key('org_batch_invite_emails_field'),
                controller: batchEmailsController,
                maxLines: 3,
                decoration: InputDecoration(
                  labelText: l10n.orgBatchInviteHint,
                  border: const OutlineInputBorder(),
                ),
              ),
              _UserProvisioningMode.directCreate => Column(
                children: [
                  TextFormField(
                    key: const Key('org_create_user_email_field'),
                    controller: createEmailController,
                    decoration: InputDecoration(
                      labelText: l10n.profileEmailLabel,
                      prefixIcon: const Icon(Icons.mail_outline),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  AppSpacing.h12,
                  TextFormField(
                    key: const Key('org_create_user_name_field'),
                    controller: createNameController,
                    decoration: InputDecoration(
                      labelText: l10n.profileDisplayNameLabel,
                      prefixIcon: const Icon(Icons.badge_outlined),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  AppSpacing.h12,
                  TextFormField(
                    key: const Key('org_create_user_password_field'),
                    controller: createPasswordController,
                    obscureText: true,
                    decoration: InputDecoration(
                      labelText: l10n.orgCreateUserPasswordLabel,
                      hintText: l10n.orgCreateUserPasswordHint,
                      prefixIcon: const Icon(Icons.lock_outline),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                ],
              ),
            },
            AppSpacing.h12,
            DropdownButtonFormField<UserRole>(
              key: const Key('org_invite_role_dropdown'),
              isExpanded: true,
              initialValue: selectedRole.value,
              decoration: InputDecoration(
                labelText: l10n.orgInviteRoleLabel,
                border: const OutlineInputBorder(),
              ),
              items: [
                for (final role in assignableRoles)
                  DropdownMenuItem(
                    value: role,
                    child: Text(
                      role.name.toUpperCase(),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
              ],
              onChanged: (val) {
                if (val != null) selectedRole.value = val;
              },
            ),
            AppSpacing.h12,
            if (mutation.hasError) ...[
              ErrorView(error: mutation.error!, compact: true),
              AppSpacing.h12,
            ],
            if (provisioningMode.value == _UserProvisioningMode.directCreate)
              OutlinedButton.icon(
                key: const Key('org_create_user_submit_btn'),
                onPressed: mutation.isLoading ? null : createDirectUser,
                icon: const Icon(Icons.person_add_alt_1_outlined),
                label: Text(l10n.orgCreateUserDirectBtn),
              )
            else
              OutlinedButton.icon(
                key: const Key('org_send_invite_btn'),
                onPressed: mutation.isLoading ? null : sendInvite,
                icon: const Icon(Icons.send_outlined),
                label: Text(
                  provisioningMode.value == _UserProvisioningMode.batchInvite
                      ? l10n.orgSendBatchInvitationBtn
                      : l10n.orgSendInvitationBtn,
                ),
              ),
            AppSpacing.h16,
            switch (invitationsAsync) {
              AsyncLoading() => const Center(
                child: CircularProgressIndicator(),
              ),
              AsyncError(:final error, :final stackTrace) => ErrorView(
                error: error,
                stackTrace: stackTrace,
                compact: true,
              ),
              AsyncData(:final value) => Column(
                children: value.map((inv) {
                  return ListTile(
                    contentPadding: EdgeInsets.zero,
                    title: Text(inv.email, overflow: TextOverflow.ellipsis),
                    subtitle: Text(
                      '${inv.role.name.toUpperCase()} • ${inv.status.name.toUpperCase()}',
                      overflow: TextOverflow.ellipsis,
                    ),
                    trailing: inv.status == InvitationStatus.pending
                        ? IconButton(
                            tooltip: l10n.orgRevokeInvitationBtn,
                            color: theme.colorScheme.error,
                            icon: const Icon(Icons.delete_outline),
                            onPressed: () => mutation.mutate(() async {
                              final res = await ref
                                  .read(userRepositoryProvider)
                                  .revokeInvitation(orgId, inv.id);
                              res.fold((err) => throw err, (_) {
                                ref.invalidate(
                                  organizationInvitationsProvider(orgId),
                                );
                              });
                            }),
                          )
                        : null,
                  );
                }).toList(),
              ),
            },
            const Divider(),
            AppSpacing.h12,
            Text(
              l10n.orgMembersHeader,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            AppSpacing.h12,
            switch (membersAsync) {
              AsyncLoading() => const Center(
                child: CircularProgressIndicator(),
              ),
              AsyncError(:final error, :final stackTrace) => ErrorView(
                error: error,
                stackTrace: stackTrace,
                compact: true,
              ),
              AsyncData(:final value) => Column(
                children: value
                    .where((member) => member.organizationId == orgId)
                    .map((member) {
                      final memberRoleOptions = <UserRole>[
                        UserRole.viewer,
                        UserRole.member,
                        UserRole.manager,
                        UserRole.admin,
                        if (currentUser.role == UserRole.root ||
                            member.role == UserRole.root)
                          UserRole.root,
                      ];
                      final canChangeMemberRole =
                          currentUser.role == UserRole.root ||
                          (member.role != UserRole.root &&
                              member.id != currentUser.id);
                      final canModifyMember =
                          currentUser.role == UserRole.root ||
                          member.role != UserRole.root;

                      return Padding(
                        padding: const EdgeInsets.only(bottom: AppSpacing.s8),
                        child: Row(
                          children: [
                            Expanded(
                              flex: 2,
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    member.email,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  if (member.name != null &&
                                      member.name!.isNotEmpty)
                                    Text(
                                      member.name!,
                                      style: theme.textTheme.bodySmall
                                          ?.copyWith(
                                            color: theme
                                                .colorScheme
                                                .onSurfaceVariant,
                                          ),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                ],
                              ),
                            ),
                            AppSpacing.w8,
                            Expanded(
                              flex: 1,
                              child: DropdownButtonFormField<UserRole>(
                                key: Key(
                                  'org_member_role_dropdown_${member.id}',
                                ),
                                isExpanded: true,
                                initialValue: member.role,
                                decoration: const InputDecoration(
                                  border: OutlineInputBorder(),
                                  isDense: true,
                                ),
                                items: [
                                  for (final role in memberRoleOptions)
                                    DropdownMenuItem(
                                      value: role,
                                      child: Text(
                                        role.name.toUpperCase(),
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                ],
                                onChanged:
                                    (!canChangeMemberRole || mutation.isLoading)
                                    ? null
                                    : (newRole) {
                                        if (newRole != null &&
                                            newRole != member.role) {
                                          mutation.mutate(() async {
                                            final res = await ref
                                                .read(userRepositoryProvider)
                                                .updateUser(
                                                  member.id,
                                                  UserUpdate(role: newRole),
                                                );
                                            res.fold((err) => throw err, (_) {
                                              ref.invalidate(
                                                organizationMembersProvider,
                                              );
                                            });
                                          });
                                        }
                                      },
                              ),
                            ),
                            AppSpacing.w8,
                            if (canModifyMember)
                              IconButton(
                                key: Key('org_edit_member_btn_${member.id}'),
                                tooltip: l10n.orgEditMemberTooltip,
                                icon: const Icon(Icons.edit_outlined),
                                onPressed: mutation.isLoading
                                    ? null
                                    : () {
                                        showDialog<void>(
                                          context: context,
                                          builder: (dialogContext) =>
                                              _EditMemberDialog(
                                                member: member,
                                                currentUser: currentUser,
                                                currentOrgId: orgId,
                                                l10n: l10n,
                                              ),
                                        );
                                      },
                              ),
                            if (member.id != currentUser.id && canModifyMember)
                              IconButton(
                                key: Key('org_delete_member_btn_${member.id}'),
                                tooltip: l10n.orgGdprDeleteUserBtn,
                                color: theme.colorScheme.error,
                                icon: const Icon(Icons.person_remove_outlined),
                                onPressed: mutation.isLoading
                                    ? null
                                    : () => mutation.mutate(() async {
                                        final res = await ref
                                            .read(userRepositoryProvider)
                                            .deleteUser(member.id);
                                        res.fold((err) => throw err, (_) {
                                          ref.invalidate(
                                            organizationMembersProvider,
                                          );
                                        });
                                      }),
                              ),
                          ],
                        ),
                      );
                    })
                    .toList(),
              ),
            },
          ],
        ),
      ),
    );
  }
}

class _EditMemberDialog extends HookConsumerWidget {
  final User member;
  final User currentUser;
  final String currentOrgId;
  final AppLocalizations l10n;

  const _EditMemberDialog({
    required this.member,
    required this.currentUser,
    required this.currentOrgId,
    required this.l10n,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final nameController = useTextEditingController(text: member.name ?? '');
    final isActive = useState<bool>(member.isActive ?? true);
    final selectedOrgId = useState<String>(
      member.organizationId ?? currentOrgId,
    );
    final dialogMutation = useMutation<void>();

    final canToggleActive =
        currentUser.role == UserRole.root || member.id != currentUser.id;

    return AlertDialog(
      key: const Key('org_edit_member_dialog'),
      title: Text(l10n.orgEditMemberDialogTitle),
      content: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 480),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                key: const Key('org_edit_member_name_field'),
                controller: nameController,
                decoration: InputDecoration(
                  labelText: l10n.profileDisplayNameLabel,
                  prefixIcon: const Icon(Icons.badge_outlined),
                  border: const OutlineInputBorder(),
                ),
              ),
              AppSpacing.h12,
              SwitchListTile(
                key: const Key('org_edit_member_active_switch'),
                contentPadding: EdgeInsets.zero,
                title: Text(l10n.orgMemberActiveStatusLabel),
                value: isActive.value,
                onChanged: canToggleActive
                    ? (val) => isActive.value = val
                    : null,
              ),
              if (currentUser.role == UserRole.root) ...[
                AppSpacing.h12,
                switch (ref.watch(availableOrganizationsProvider)) {
                  AsyncLoading() => const Center(
                    child: CircularProgressIndicator(),
                  ),
                  AsyncError(:final error, :final stackTrace) => ErrorView(
                    error: error,
                    stackTrace: stackTrace,
                    compact: true,
                  ),
                  AsyncData(value: final orgs) =>
                    DropdownButtonFormField<String>(
                      key: const Key('org_edit_member_org_dropdown'),
                      isExpanded: true,
                      initialValue: selectedOrgId.value,
                      decoration: InputDecoration(
                        labelText: l10n.profileOrganizationIdLabel,
                        prefixIcon: const Icon(Icons.domain_outlined),
                        border: const OutlineInputBorder(),
                      ),
                      items: [
                        for (final org in orgs)
                          DropdownMenuItem(
                            value: org.id,
                            child: Text(
                              org.name,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                      ],
                      onChanged: (val) {
                        if (val != null) selectedOrgId.value = val;
                      },
                    ),
                },
              ],
              if (dialogMutation.hasError) ...[
                AppSpacing.h12,
                ErrorView(error: dialogMutation.error!, compact: true),
              ],
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(l10n.cancel),
        ),
        OutlinedButton.icon(
          key: const Key('org_edit_member_save_btn'),
          onPressed: dialogMutation.isLoading
              ? null
              : () async {
                  final nextName = nameController.text.trim();
                  await dialogMutation.mutate(() async {
                    final res = await ref
                        .read(userRepositoryProvider)
                        .updateUser(
                          member.id,
                          UserUpdate(
                            name: nextName.isEmpty ? null : nextName,
                            isActive: isActive.value,
                            organizationId: currentUser.role == UserRole.root
                                ? selectedOrgId.value
                                : null,
                          ),
                        );
                    res.fold((err) => throw err, (_) {
                      ref.invalidate(organizationMembersProvider);
                      if (context.mounted) {
                        Navigator.of(context).pop();
                      }
                    });
                  });
                },
          icon: const Icon(Icons.save_outlined),
          label: Text(l10n.save),
        ),
      ],
    );
  }
}

class _ByokSecretsCard extends HookConsumerWidget {
  final String orgId;
  final AppLocalizations l10n;
  final ThemeData theme;

  const _ByokSecretsCard({
    required this.orgId,
    required this.l10n,
    required this.theme,
  });

  static const String _rootSystemOrgId = 'org_0195f3a0000070008000000000000001';

  static List<McpGateway> _visibleGatewaysForOrg(
    List<McpGateway> gateways,
    String orgId,
    UserRole? role,
  ) {
    if (role == UserRole.root) {
      return gateways;
    }
    return [
      for (final gw in gateways)
        if (gw.organizationId == orgId || gw.organizationId == _rootSystemOrgId)
          gw,
    ];
  }

  static String _llmProviderBackendValue(LLMProvider provider) =>
      switch (provider) {
        LLMProvider.vertexAi => 'vertex_ai',
        LLMProvider.aiStudio => 'ai_studio',
        LLMProvider.openai => 'openai',
        LLMProvider.anthropic => 'anthropic',
        LLMProvider.azureOpenai => 'azure_openai',
        LLMProvider.local => 'local',
      };

  static String _formatSecretTarget(
    TenantSecretResponseDto secret,
    AsyncValue<List<McpGateway>> gatewaysAsync,
  ) => switch (secret.scope) {
    SecretScope.llmProvider => secret.targetIdentifier,
    SecretScope.telemetry => secret.targetIdentifier,
    SecretScope.mcpGateway => switch (gatewaysAsync) {
      AsyncData(:final value) => () {
        for (final gw in value) {
          if (gw.id == secret.targetIdentifier) {
            return '${gw.name} (${secret.targetIdentifier})';
          }
        }
        return secret.targetIdentifier;
      }(),
      _ => secret.targetIdentifier,
    },
  };

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    const telemetryTargets = <String>['logfire', 'logfire_read'];
    final currentUser = switch (ref.watch(authControllerProvider)) {
      AsyncData(:final value) => value,
      _ => null,
    };
    final canManageTelemetry =
        currentUser?.role == UserRole.root && orgId == _rootSystemOrgId;
    final availableScopes = <SecretScope>[
      for (final scope in SecretScope.values)
        if (scope != SecretScope.telemetry || canManageTelemetry) scope,
    ];
    final secretsAsync = ref.watch(organizationSecretsProvider(orgId));
    final gatewaysAsync = ref.watch(availableMcpGatewaysProvider);
    final selectedScope = useState<SecretScope>(SecretScope.llmProvider);
    final effectiveScope = availableScopes.contains(selectedScope.value)
        ? selectedScope.value
        : SecretScope.llmProvider;
    final selectedStorageMode = useState<SecretStorageMode>(
      SecretStorageMode.envelopeKms,
    );
    final selectedTarget = useState<String?>(
      _llmProviderBackendValue(LLMProvider.openai),
    );
    final obscureSecret = useState<bool>(true);
    final secretValueController = useTextEditingController();
    final mutation = useMutation<void>();

    final String? effectiveTarget = switch (effectiveScope) {
      SecretScope.llmProvider =>
        LLMProvider.values.any(
              (p) => _llmProviderBackendValue(p) == selectedTarget.value,
            )
            ? selectedTarget.value
            : _llmProviderBackendValue(LLMProvider.openai),
      SecretScope.mcpGateway => switch (gatewaysAsync) {
        AsyncData(:final value) => () {
          final visibleGateways = _visibleGatewaysForOrg(
            value,
            orgId,
            currentUser?.role,
          );
          return visibleGateways.any((gw) => gw.id == selectedTarget.value)
              ? selectedTarget.value
              : (visibleGateways.isNotEmpty ? visibleGateways.first.id : null);
        }(),
        _ => null,
      },
      SecretScope.telemetry =>
        telemetryTargets.contains(selectedTarget.value)
            ? selectedTarget.value
            : telemetryTargets.first,
    };

    Future<void> saveSecret() async {
      final target = (effectiveTarget ?? '').trim();
      final plaintext = secretValueController.text.trim();

      await mutation.mutate(() async {
        if (target.isEmpty || plaintext.isEmpty) {
          throw AppException.validation(l10n.errorValidation);
        }
        final result = await ref
            .read(userRepositoryProvider)
            .upsertSecret(
              orgId,
              TenantSecretCreateDto(
                scope: effectiveScope,
                targetIdentifier: target,
                plaintextSecret: plaintext,
                storageMode: selectedStorageMode.value,
              ),
            );
        result.fold((err) => throw err, (_) {
          secretValueController.clear();
          ref.invalidate(organizationSecretsProvider(orgId));
        });
      });
    }

    return Card(
      key: const Key('org_byok_secrets_card'),
      elevation: 2,
      margin: const EdgeInsets.only(bottom: AppSpacing.s16),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppSpacing.s12),
      ),
      child: Padding(
        padding: AppSpacing.p16,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              l10n.orgByokSecretsCardTitle,
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            AppSpacing.h16,
            Row(
              children: [
                Expanded(
                  child: DropdownButtonFormField<SecretScope>(
                    key: const Key('org_secret_scope_dropdown'),
                    isExpanded: true,
                    initialValue: effectiveScope,
                    decoration: InputDecoration(
                      labelText: l10n.orgSecretScopeLabel,
                      border: const OutlineInputBorder(),
                    ),
                    items: [
                      for (final scope in availableScopes)
                        DropdownMenuItem(
                          value: scope,
                          child: Text(
                            scope.name,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                    ],
                    onChanged: (val) {
                      if (val != null) {
                        selectedScope.value = val;
                        switch (val) {
                          case SecretScope.llmProvider:
                            selectedTarget.value = _llmProviderBackendValue(
                              LLMProvider.openai,
                            );
                          case SecretScope.mcpGateway:
                            selectedTarget.value = switch (gatewaysAsync) {
                              AsyncData(:final value) => () {
                                final visibleGateways = _visibleGatewaysForOrg(
                                  value,
                                  orgId,
                                  currentUser?.role,
                                );
                                return visibleGateways.isNotEmpty
                                    ? visibleGateways.first.id
                                    : null;
                              }(),
                              _ => null,
                            };
                          case SecretScope.telemetry:
                            selectedTarget.value = telemetryTargets.first;
                        }
                      }
                    },
                  ),
                ),
                AppSpacing.w12,
                Expanded(
                  child: DropdownButtonFormField<SecretStorageMode>(
                    key: const Key('org_secret_storage_mode_dropdown'),
                    isExpanded: true,
                    initialValue: selectedStorageMode.value,
                    decoration: InputDecoration(
                      labelText: l10n.orgSecretStorageModeLabel,
                      border: const OutlineInputBorder(),
                    ),
                    items: [
                      for (final mode in SecretStorageMode.values)
                        DropdownMenuItem(
                          value: mode,
                          child: Text(
                            mode.name,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                    ],
                    onChanged: (val) {
                      if (val != null) selectedStorageMode.value = val;
                    },
                  ),
                ),
              ],
            ),
            AppSpacing.h12,
            switch (effectiveScope) {
              SecretScope.llmProvider => KeyedSubtree(
                key: const ValueKey<String>('scope_llm_target_subtree'),
                child: DropdownButtonFormField<String>(
                  key: const ValueKey<String>('org_secret_target_dropdown'),
                  isExpanded: true,
                  initialValue: effectiveTarget,
                  decoration: InputDecoration(
                    labelText: l10n.orgSecretTargetIdentifierLabel,
                    prefixIcon: const Icon(Icons.hub_outlined),
                    border: const OutlineInputBorder(),
                  ),
                  items: [
                    for (final provider in LLMProvider.values)
                      DropdownMenuItem<String>(
                        value: _llmProviderBackendValue(provider),
                        child: Text(
                          _llmProviderBackendValue(provider),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                  ],
                  onChanged: (val) {
                    selectedTarget.value = val;
                  },
                ),
              ),
              SecretScope.mcpGateway => KeyedSubtree(
                key: const ValueKey<String>('scope_mcp_target_subtree'),
                child: switch (gatewaysAsync) {
                  AsyncLoading() => const Center(
                    child: CircularProgressIndicator(),
                  ),
                  AsyncError(:final error, :final stackTrace) => ErrorView(
                    error: error,
                    stackTrace: stackTrace,
                    compact: true,
                  ),
                  AsyncData(:final value) => () {
                    final visibleGateways = _visibleGatewaysForOrg(
                      value,
                      orgId,
                      currentUser?.role,
                    );
                    return DropdownButtonFormField<String>(
                      key: const ValueKey<String>('org_secret_target_dropdown'),
                      isExpanded: true,
                      initialValue: effectiveTarget,
                      decoration: InputDecoration(
                        labelText: l10n.orgSecretTargetIdentifierLabel,
                        prefixIcon: const Icon(Icons.hub_outlined),
                        border: const OutlineInputBorder(),
                      ),
                      items: [
                        for (final gw in visibleGateways)
                          DropdownMenuItem<String>(
                            value: gw.id,
                            child: Text(
                              '${gw.name} (${gw.id})',
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                      ],
                      onChanged: (val) {
                        selectedTarget.value = val;
                      },
                    );
                  }(),
                },
              ),
              SecretScope.telemetry => KeyedSubtree(
                key: const ValueKey<String>('scope_telemetry_target_subtree'),
                child: DropdownButtonFormField<String>(
                  key: const ValueKey<String>('org_secret_target_dropdown'),
                  isExpanded: true,
                  initialValue: effectiveTarget,
                  decoration: InputDecoration(
                    labelText: l10n.orgSecretTargetIdentifierLabel,
                    prefixIcon: const Icon(Icons.hub_outlined),
                    border: const OutlineInputBorder(),
                  ),
                  items: [
                    for (final target in telemetryTargets)
                      DropdownMenuItem<String>(
                        value: target,
                        child: Text(target, overflow: TextOverflow.ellipsis),
                      ),
                  ],
                  onChanged: (val) {
                    selectedTarget.value = val;
                  },
                ),
              ),
            },
            AppSpacing.h12,
            TextFormField(
              key: const Key('org_secret_value_field'),
              controller: secretValueController,
              obscureText: obscureSecret.value,
              minLines: 1,
              maxLines: obscureSecret.value ? 1 : 6,
              decoration: InputDecoration(
                labelText: l10n.orgSecretPlaintextLabel,
                prefixIcon: const Icon(Icons.key_outlined),
                suffixIcon: IconButton(
                  key: const Key('org_secret_visibility_toggle_btn'),
                  icon: Icon(
                    obscureSecret.value
                        ? Icons.visibility_outlined
                        : Icons.visibility_off_outlined,
                  ),
                  onPressed: () {
                    obscureSecret.value = !obscureSecret.value;
                  },
                ),
                border: const OutlineInputBorder(),
              ),
            ),
            AppSpacing.h12,
            if (mutation.hasError) ...[
              ErrorView(error: mutation.error!, compact: true),
              AppSpacing.h12,
            ],
            OutlinedButton.icon(
              key: const Key('org_save_secret_btn'),
              onPressed: mutation.isLoading ? null : saveSecret,
              icon: const Icon(Icons.enhanced_encryption_outlined),
              label: Text(l10n.orgSaveSecretBtn),
            ),
            AppSpacing.h16,
            switch (secretsAsync) {
              AsyncLoading() => const Center(
                child: CircularProgressIndicator(),
              ),
              AsyncError(:final error, :final stackTrace) => ErrorView(
                error: error,
                stackTrace: stackTrace,
                compact: true,
              ),
              AsyncData(:final value) => Column(
                children: value.map((secret) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: AppSpacing.s8),
                    padding: AppSpacing.p12,
                    decoration: BoxDecoration(
                      border: Border.all(
                        color: theme.colorScheme.outlineVariant,
                      ),
                      borderRadius: BorderRadius.circular(AppSpacing.s12),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _formatSecretTarget(secret, gatewaysAsync),
                                style: theme.textTheme.titleSmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                              AppSpacing.h4,
                              Wrap(
                                spacing: AppSpacing.s8,
                                runSpacing: AppSpacing.s4,
                                children: [
                                  if (secret.configured)
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                        horizontal: AppSpacing.s8,
                                        vertical: AppSpacing.s2,
                                      ),
                                      decoration: BoxDecoration(
                                        color:
                                            theme.colorScheme.primaryContainer,
                                        borderRadius: BorderRadius.circular(
                                          AppSpacing.s12,
                                        ),
                                      ),
                                      child: Text(
                                        l10n.orgSecretConfiguredBadge,
                                        style: theme.textTheme.labelSmall,
                                      ),
                                    ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: AppSpacing.s8,
                                      vertical: AppSpacing.s2,
                                    ),
                                    decoration: BoxDecoration(
                                      color: theme
                                          .colorScheme
                                          .surfaceContainerHighest,
                                      borderRadius: BorderRadius.circular(
                                        AppSpacing.s12,
                                      ),
                                    ),
                                    child: Text(
                                      secret.scope.name,
                                      style: theme.textTheme.labelSmall,
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: AppSpacing.s8,
                                      vertical: AppSpacing.s2,
                                    ),
                                    decoration: BoxDecoration(
                                      color:
                                          theme.colorScheme.tertiaryContainer,
                                      borderRadius: BorderRadius.circular(
                                        AppSpacing.s12,
                                      ),
                                    ),
                                    child: Text(
                                      secret.storageMode.name,
                                      style: theme.textTheme.labelSmall,
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: AppSpacing.s8,
                                      vertical: AppSpacing.s2,
                                    ),
                                    decoration: BoxDecoration(
                                      color:
                                          theme.colorScheme.secondaryContainer,
                                      borderRadius: BorderRadius.circular(
                                        AppSpacing.s12,
                                      ),
                                    ),
                                    child: Text(
                                      secret.maskedHint,
                                      style: theme.textTheme.labelSmall,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                        IconButton(
                          tooltip: l10n.delete,
                          color: theme.colorScheme.error,
                          icon: const Icon(Icons.delete_outline),
                          onPressed: () => mutation.mutate(() async {
                            final res = await ref
                                .read(userRepositoryProvider)
                                .deleteSecret(orgId, secret.id);
                            res.fold((err) => throw err, (_) {
                              ref.invalidate(
                                organizationSecretsProvider(orgId),
                              );
                            });
                          }),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            },
          ],
        ),
      ),
    );
  }
}
