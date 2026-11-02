import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/settings/domain/models/tenant_secret_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/router/router.dart';
import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'organization_iam_settings_view.g.dart';

// Phase 6, Step 6.2: Role-Segregated Organization IAM, Task Assignments & BYOK Secrets Studio UI (/organization).

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

                final orgId = value.organizationId;
                if (orgId == null || orgId.isEmpty) {
                  return Center(child: Text(l10n.errorNotFound));
                }

                final isAdminOrRoot =
                    value.role == UserRole.admin || value.role == UserRole.root;

                return SingleChildScrollView(
                  padding: AppSpacing.p24,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      _OrganizationMetadataCard(
                        orgId: orgId,
                        l10n: l10n,
                        theme: theme,
                      ),
                      _TaskAssignmentsManagementCard(l10n: l10n, theme: theme),
                      if (isAdminOrRoot) ...[
                        _InvitationsAndMembersCard(
                          orgId: orgId,
                          currentUser: value,
                          l10n: l10n,
                          theme: theme,
                        ),
                        _ByokSecretsCard(
                          orgId: orgId,
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
                OutlinedButton.icon(
                  onPressed: () =>
                      ref.invalidate(organizationAssignmentsProvider),
                  icon: const Icon(Icons.refresh),
                  label: Text(l10n.orgNewTaskAssignmentBtn),
                ),
              ],
            ),
            AppSpacing.h16,
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
    final selectedRole = useState<UserRole>(UserRole.member);
    final isBatchMode = useState<bool>(false);
    final mutation = useMutation<void>();

    Future<void> sendInvite() async {
      await mutation.mutate(() async {
        if (isBatchMode.value) {
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
              children: [
                ChoiceChip(
                  label: Text(l10n.orgSendInvitationBtn),
                  selected: !isBatchMode.value,
                  onSelected: (_) => isBatchMode.value = false,
                ),
                ChoiceChip(
                  label: Text(l10n.orgSendBatchInvitationBtn),
                  selected: isBatchMode.value,
                  onSelected: (_) => isBatchMode.value = true,
                ),
              ],
            ),
            AppSpacing.h12,
            if (!isBatchMode.value)
              TextFormField(
                key: const Key('org_invite_email_field'),
                controller: emailController,
                decoration: InputDecoration(
                  labelText: l10n.orgInviteEmailLabel,
                  prefixIcon: const Icon(Icons.mail_outline),
                  border: const OutlineInputBorder(),
                ),
              )
            else
              TextFormField(
                key: const Key('org_batch_invite_emails_field'),
                controller: batchEmailsController,
                maxLines: 3,
                decoration: InputDecoration(
                  labelText: l10n.orgBatchInviteHint,
                  border: const OutlineInputBorder(),
                ),
              ),
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
                for (final role in const [
                  UserRole.viewer,
                  UserRole.member,
                  UserRole.manager,
                  UserRole.admin,
                ])
                  DropdownMenuItem(
                    value: role,
                    child: Text(role.name.toUpperCase()),
                  ),
              ],
              onChanged: (val) {
                if (val != null) selectedRole.value = val;
              },
            ),
            AppSpacing.h12,
            OutlinedButton.icon(
              key: const Key('org_send_invite_btn'),
              onPressed: mutation.isLoading ? null : sendInvite,
              icon: const Icon(Icons.send_outlined),
              label: Text(
                isBatchMode.value
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
                              await ref
                                  .read(userRepositoryProvider)
                                  .revokeInvitation(orgId, inv.id);
                              ref.invalidate(
                                organizationInvitationsProvider(orgId),
                              );
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
                children: value.map((member) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: AppSpacing.s8),
                    child: Row(
                      children: [
                        Expanded(
                          flex: 2,
                          child: Text(
                            member.email,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        AppSpacing.w8,
                        Expanded(
                          flex: 1,
                          child: DropdownButtonFormField<UserRole>(
                            isExpanded: true,
                            initialValue: member.role,
                            decoration: const InputDecoration(
                              border: OutlineInputBorder(),
                              isDense: true,
                            ),
                            items: [
                              for (final role in UserRole.values)
                                DropdownMenuItem(
                                  value: role,
                                  child: Text(role.name.toUpperCase()),
                                ),
                            ],
                            onChanged: (newRole) {
                              if (newRole != null && newRole != member.role) {
                                mutation.mutate(() async {
                                  await ref
                                      .read(userRepositoryProvider)
                                      .updateUser(
                                        member.id,
                                        UserUpdate(role: newRole),
                                      );
                                  ref.invalidate(organizationMembersProvider);
                                });
                              }
                            },
                          ),
                        ),
                        AppSpacing.w8,
                        if (member.id != currentUser.id)
                          IconButton(
                            tooltip: l10n.orgGdprDeleteUserBtn,
                            color: theme.colorScheme.error,
                            icon: const Icon(Icons.person_remove_outlined),
                            onPressed: () => mutation.mutate(() async {
                              await ref
                                  .read(userRepositoryProvider)
                                  .deleteUser(member.id);
                              ref.invalidate(organizationMembersProvider);
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

class _ByokSecretsCard extends HookConsumerWidget {
  final String orgId;
  final AppLocalizations l10n;
  final ThemeData theme;

  const _ByokSecretsCard({
    required this.orgId,
    required this.l10n,
    required this.theme,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final secretsAsync = ref.watch(organizationSecretsProvider(orgId));
    final selectedScope = useState<SecretScope>(SecretScope.llmProvider);
    final selectedStorageMode = useState<SecretStorageMode>(
      SecretStorageMode.envelopeKms,
    );
    final targetController = useTextEditingController();
    final secretValueController = useTextEditingController();
    final mutation = useMutation<void>();

    Future<void> saveSecret() async {
      final target = targetController.text.trim();
      final plaintext = secretValueController.text.trim();
      if (target.isEmpty || plaintext.isEmpty) return;

      await mutation.mutate(() async {
        final result = await ref
            .read(userRepositoryProvider)
            .upsertSecret(
              orgId,
              TenantSecretCreateDto(
                scope: selectedScope.value,
                targetIdentifier: target,
                plaintextSecret: plaintext,
              ),
            );
        result.fold((err) => throw err, (_) {
          targetController.clear();
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
                    initialValue: selectedScope.value,
                    decoration: InputDecoration(
                      labelText: l10n.orgSecretScopeLabel,
                      border: const OutlineInputBorder(),
                    ),
                    items: [
                      for (final scope in SecretScope.values)
                        DropdownMenuItem(
                          value: scope,
                          child: Text(
                            scope.name,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                    ],
                    onChanged: (val) {
                      if (val != null) selectedScope.value = val;
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
            TextFormField(
              key: const Key('org_secret_target_field'),
              controller: targetController,
              decoration: InputDecoration(
                labelText: l10n.orgSecretTargetIdentifierLabel,
                prefixIcon: const Icon(Icons.hub_outlined),
                border: const OutlineInputBorder(),
              ),
            ),
            AppSpacing.h12,
            TextFormField(
              key: const Key('org_secret_value_field'),
              controller: secretValueController,
              obscureText: true,
              decoration: InputDecoration(
                labelText: l10n.orgSecretPlaintextLabel,
                prefixIcon: const Icon(Icons.key_outlined),
                border: const OutlineInputBorder(),
              ),
            ),
            AppSpacing.h12,
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
                                secret.targetIdentifier,
                                style: theme.textTheme.titleSmall?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                              AppSpacing.h4,
                              Wrap(
                                spacing: AppSpacing.s8,
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
                            await ref
                                .read(userRepositoryProvider)
                                .deleteSecret(orgId, secret.id);
                            ref.invalidate(organizationSecretsProvider(orgId));
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
