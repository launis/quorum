import 'dart:async';
import 'dart:convert';

import 'package:client_app/core/api/execution_client.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/state/mutation.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/features/auth/data/auth_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/features/execution/models/execution_record.dart';
import 'package:client_app/features/execution/models/workflow_inputs.dart';
import 'package:client_app/features/settings/domain/models/tenant_secret_dto.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/router/router.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'task_assignment_portal_view.g.dart';

// SafeLinks-immune task assignment portal view (/task/:token).

@riverpod
Future<ExecutionAssignmentPreviewDto> taskAssignmentPreview(
  Ref ref,
  String token,
) async {
  return await ref.watch(executionClientProvider).previewAssignment(token);
}

class TaskAssignmentPortalView extends HookConsumerWidget {
  final String token;
  final Future<WorkflowInputValue?> Function(String inputKey)? onPickFile;

  const TaskAssignmentPortalView({
    super.key,
    required this.token,
    this.onPickFile,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final previewAsync = ref.watch(taskAssignmentPreviewProvider(token));
    final authState = ref.watch(authControllerProvider);

    return AppErrorBoundary(
      child: Scaffold(
        appBar: AppBar(title: Text(l10n.taskPortalTitle)),
        body: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 1200),
            child: switch (previewAsync) {
              AsyncLoading() => const Center(
                child: CircularProgressIndicator(),
              ),
              AsyncError(:final error, :final stackTrace) => ErrorView(
                error: error,
                stackTrace: stackTrace,
              ),
              AsyncData(:final value) => _TaskPortalBody(
                token: token,
                preview: value,
                authState: authState,
                l10n: l10n,
                theme: theme,
                onPickFile: onPickFile,
              ),
            },
          ),
        ),
      ),
    );
  }
}

class _TaskPortalBody extends HookConsumerWidget {
  final String token;
  final ExecutionAssignmentPreviewDto preview;
  final AsyncValue<User?> authState;
  final AppLocalizations l10n;
  final ThemeData theme;
  final Future<WorkflowInputValue?> Function(String inputKey)? onPickFile;

  const _TaskPortalBody({
    required this.token,
    required this.preview,
    required this.authState,
    required this.l10n,
    required this.theme,
    this.onPickFile,
  });

  bool _isIdentityMismatch(String userEmail, String maskedOrEmail) {
    final cleanUser = userEmail.trim().toLowerCase();
    final cleanTarget = maskedOrEmail.trim().toLowerCase();
    if (!cleanTarget.contains('*')) {
      return cleanUser != cleanTarget;
    }
    final userParts = cleanUser.split('@');
    final targetParts = cleanTarget.split('@');
    if (userParts.length != 2 || targetParts.length != 2) {
      return cleanUser != cleanTarget;
    }
    if (userParts[1] != targetParts[1]) {
      return true;
    }
    final prefix = targetParts[0].split('*').first;
    if (prefix.isNotEmpty && !userParts[0].startsWith(prefix)) {
      return true;
    }
    return false;
  }

  String _resolveLocalizedText(
    BuildContext context,
    Map<String, String> translations,
  ) {
    final langCode = Localizations.localeOf(context).languageCode;
    final activeText = translations[langCode];
    if (activeText != null && activeText.trim().isNotEmpty) {
      return activeText;
    }
    final fallbackEn = translations['en'];
    if (fallbackEn != null && fallbackEn.trim().isNotEmpty) {
      return fallbackEn;
    }
    throw AppException.validation('Fail-Fast: Missing required translation.');
  }

  Future<WorkflowInputValue?> _defaultPickFile(String inputKey) async {
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: const ['pdf', 'txt', 'docx'],
      withData: true,
    );
    if (result == null || result.files.isEmpty) {
      return null;
    }
    final picked = result.files.first;
    final bytes = picked.bytes;
    if (bytes == null || bytes.isEmpty) {
      return null;
    }
    return WorkflowInputValue.file(
      filename: picked.name,
      contentBase64: base64Encode(bytes),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activatedAssignment = useState<ExecutionAssignmentResponseDto?>(null);
    final submittedRecord = useState<ExecutionRecord?>(null);
    final remainingSeconds = useState<int?>(preview.relativeDurationSeconds);
    final pendingOnboardingMfa = useState<MfaPendingState?>(null);
    final selectedFileInputs = useState<Map<String, WorkflowInputValue>>(
      const <String, WorkflowInputValue>{},
    );
    final onboardingEmailController = useTextEditingController(
      text: preview.assignedEmailMasked.contains('*')
          ? ''
          : preview.assignedEmailMasked,
    );
    final onboardingNameController = useTextEditingController();
    final onboardingTokenController = useTextEditingController();
    final totpCodeController = useTextEditingController();
    final inputControllers = useMemoized(
      () => <String, TextEditingController>{},
    );
    final portalMutation = useMutation<void>();

    useEffect(() {
      return () {
        for (final c in inputControllers.values) {
          c.dispose();
        }
      };
    }, const []);

    useEffect(() {
      final active = activatedAssignment.value;
      if (active == null || submittedRecord.value != null) {
        return null;
      }

      DateTime effectiveDeadline = active.hardDeadlineAt;
      if (active.activatedAt != null &&
          active.relativeDurationSeconds != null) {
        final relativeEnd = active.activatedAt!.add(
          Duration(seconds: active.relativeDurationSeconds!),
        );
        if (relativeEnd.isBefore(effectiveDeadline)) {
          effectiveDeadline = relativeEnd;
        }
      }

      void updateCountdown() {
        final diff = effectiveDeadline
            .difference(DateTime.now().toUtc())
            .inSeconds;
        remainingSeconds.value = diff > 0 ? diff : 0;
      }

      updateCountdown();
      final timer = Timer.periodic(
        const Duration(seconds: 1),
        (_) => updateCountdown(),
      );
      return timer.cancel;
    }, [activatedAssignment.value, submittedRecord.value]);

    final currentUser = switch (authState) {
      AsyncData(:final value) => value,
      AsyncLoading() || AsyncError() => null,
    };

    if (submittedRecord.value != null) {
      final record = submittedRecord.value!;
      final active = activatedAssignment.value;
      return SingleChildScrollView(
        padding: AppSpacing.p24,
        child: Card(
          key: const Key('task_portal_submitted_card'),
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSpacing.s12),
          ),
          child: Padding(
            padding: AppSpacing.p24,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.check_circle_outline,
                      size: AppSpacing.s24,
                      color: theme.colorScheme.primary,
                    ),
                    AppSpacing.w12,
                    Expanded(
                      child: Text(
                        l10n.taskPortalSubmittedTitle,
                        style: theme.textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                AppSpacing.h12,
                Text(record.id, style: theme.textTheme.bodyLarge),
                if (active != null &&
                    active.resultVisibility ==
                        AssignmentResultVisibility.fullReportAccess) ...[
                  AppSpacing.h16,
                  OutlinedButton.icon(
                    key: const Key('task_portal_view_execution_btn'),
                    onPressed: () {
                      ExecutionRoute(executionId: record.id).go(context);
                    },
                    icon: const Icon(Icons.open_in_new),
                    label: Text(l10n.orgOpenReportBtn),
                  ),
                ],
              ],
            ),
          ),
        ),
      );
    }

    if (currentUser != null &&
        _isIdentityMismatch(currentUser.email, preview.assignedEmailMasked)) {
      return SingleChildScrollView(
        padding: AppSpacing.p24,
        child: Card(
          key: const Key('task_portal_identity_mismatch_banner'),
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppSpacing.s12),
          ),
          child: Padding(
            padding: AppSpacing.p24,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(
                      Icons.warning_amber_rounded,
                      size: AppSpacing.s24,
                      color: theme.colorScheme.error,
                    ),
                    AppSpacing.w12,
                    Expanded(
                      child: Text(
                        l10n.taskPortalIdentityMismatchTitle,
                        style: theme.textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: theme.colorScheme.error,
                        ),
                      ),
                    ),
                  ],
                ),
                AppSpacing.h12,
                Text(
                  l10n.taskPortalIdentityMismatchDesc(
                    currentUser.email,
                    preview.assignedEmailMasked,
                  ),
                  style: theme.textTheme.bodyLarge,
                ),
                AppSpacing.h16,
                OutlinedButton.icon(
                  key: const Key('task_portal_switch_account_btn'),
                  onPressed: portalMutation.isLoading
                      ? null
                      : () => portalMutation.mutate(() async {
                          await ref
                              .read(authControllerProvider.notifier)
                              .signOut(revokeAllSessions: false);
                        }),
                  icon: const Icon(Icons.logout),
                  label: Text(l10n.taskPortalSwitchAccountBtn),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return SingleChildScrollView(
      padding: AppSpacing.p24,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Card(
            key: const Key('task_portal_preview_card'),
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
                          l10n.taskPortalOrgLabel(preview.organizationName),
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
                          (activatedAssignment.value?.status ?? preview.status)
                              .name
                              .toUpperCase(),
                          style: theme.textTheme.labelMedium?.copyWith(
                            color: theme.colorScheme.onPrimaryContainer,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  AppSpacing.h8,
                  Text(
                    l10n.taskPortalAssignedEmailLabel(
                      preview.assignedEmailMasked,
                    ),
                    style: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  AppSpacing.h4,
                  Text(
                    '${l10n.taskBuilderHardDeadlineLabel}: ${preview.hardDeadlineAt.toIso8601String()}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
          ),
          if ((activatedAssignment.value?.taskBrief ?? preview.taskBrief) !=
              null)
            _buildTaskBriefCard(
              context: context,
              brief:
                  (activatedAssignment.value?.taskBrief ?? preview.taskBrief)!,
            ),
          if (currentUser == null)
            Card(
              key: const Key('task_portal_jit_onboarding_card'),
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
                      l10n.taskPortalJitOnboardingTitle,
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    AppSpacing.h12,
                    TextFormField(
                      key: const Key('task_portal_onboard_email_field'),
                      controller: onboardingEmailController,
                      decoration: InputDecoration(
                        labelText: l10n.emailLabel,
                        prefixIcon: const Icon(Icons.email_outlined),
                        border: const OutlineInputBorder(),
                      ),
                    ),
                    AppSpacing.h12,
                    TextFormField(
                      key: const Key('task_portal_onboard_name_field'),
                      controller: onboardingNameController,
                      decoration: InputDecoration(
                        labelText: l10n.profileDisplayNameLabel,
                        prefixIcon: const Icon(Icons.badge_outlined),
                        border: const OutlineInputBorder(),
                      ),
                    ),
                    AppSpacing.h12,
                    TextFormField(
                      key: const Key('task_portal_onboard_token_field'),
                      controller: onboardingTokenController,
                      obscureText: true,
                      decoration: InputDecoration(
                        labelText: l10n.passwordLabel,
                        prefixIcon: const Icon(Icons.lock_outline),
                        border: const OutlineInputBorder(),
                      ),
                    ),
                    if (pendingOnboardingMfa.value?.isEnrollment == true &&
                        pendingOnboardingMfa.value?.secretKey != null) ...[
                      AppSpacing.h12,
                      Container(
                        padding: AppSpacing.p12,
                        decoration: BoxDecoration(
                          color: theme.colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(AppSpacing.s8),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              l10n.taskPortalTotpEnrollmentHint,
                              style: theme.textTheme.bodyMedium,
                            ),
                            AppSpacing.h8,
                            SelectableText(
                              pendingOnboardingMfa.value!.secretKey!,
                              key: const Key('task_portal_totp_secret_text'),
                              style: theme.textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                    AppSpacing.h12,
                    TextFormField(
                      key: const Key('task_portal_onboard_totp_field'),
                      controller: totpCodeController,
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(
                        labelText: l10n.mfaTotpCodeLabel,
                        prefixIcon: const Icon(Icons.pin_outlined),
                        border: const OutlineInputBorder(),
                      ),
                    ),
                    AppSpacing.h16,
                    if (portalMutation.hasError) ...[
                      ErrorView(error: portalMutation.error!, compact: true),
                      AppSpacing.h12,
                    ],
                    OutlinedButton.icon(
                      key: const Key('task_portal_onboard_btn'),
                      onPressed: portalMutation.isLoading
                          ? null
                          : () => portalMutation.mutate(() async {
                              final emailText = onboardingEmailController.text
                                  .trim();
                              final passwordOrTokenText =
                                  onboardingTokenController.text.trim();
                              final totpText = totpCodeController.text.trim();
                              String? resolvedIdToken;

                              if (emailText.isNotEmpty &&
                                  passwordOrTokenText.isNotEmpty) {
                                final authResult = await ref
                                    .read(authRepositoryProvider)
                                    .authenticateForTaskOnboarding(
                                      email: emailText,
                                      password: passwordOrTokenText,
                                      totpCode: totpText.isEmpty
                                          ? null
                                          : totpText,
                                    );
                                if (!context.mounted) return;
                                resolvedIdToken = authResult.fold((err) {
                                  if (err.errorCode ==
                                      'MFA_CHALLENGE_REQUIRED') {
                                    pendingOnboardingMfa.value = ref
                                        .read(authRepositoryProvider)
                                        .pendingMfaState;
                                  }
                                  throw err;
                                }, (idToken) => idToken);
                              } else if (passwordOrTokenText.isNotEmpty) {
                                resolvedIdToken = passwordOrTokenText;
                              }

                              try {
                                final exchange = await ref
                                    .read(executionClientProvider)
                                    .onboardAssignee(
                                      token: token,
                                      payload:
                                          ExecutionAssignmentOnboardingRequestDto(
                                            firebaseToken: resolvedIdToken,
                                            name:
                                                onboardingNameController.text
                                                    .trim()
                                                    .isEmpty
                                                ? null
                                                : onboardingNameController.text
                                                      .trim(),
                                          ),
                                    );
                                if (!context.mounted) return;
                                pendingOnboardingMfa.value = null;
                                await ref
                                    .read(authControllerProvider.notifier)
                                    .applyTokenExchangeResponse(exchange);
                              } on AppException catch (e) {
                                if (e.errorCode == 'MFA_REQUIRED') {
                                  final prepResult = await ref
                                      .read(authRepositoryProvider)
                                      .prepareEnrollmentForCurrentUser(
                                        fallbackEmail: emailText,
                                        reloadUser: true,
                                      );
                                  if (!context.mounted) return;
                                  prepResult.fold((_) {}, (pendingState) {
                                    pendingOnboardingMfa.value = pendingState;
                                  });
                                }
                                rethrow;
                              }
                            }),
                      icon: const Icon(Icons.verified_user_outlined),
                      label: Text(l10n.taskPortalJitCompleteBtn),
                    ),
                  ],
                ),
              ),
            )
          else if (activatedAssignment.value == null)
            Card(
              key: const Key('task_portal_activation_card'),
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
                    if (portalMutation.hasError) ...[
                      ErrorView(error: portalMutation.error!, compact: true),
                      AppSpacing.h12,
                    ],
                    OutlinedButton.icon(
                      key: const Key('task_portal_start_task_btn'),
                      onPressed: portalMutation.isLoading
                          ? null
                          : () => portalMutation.mutate(() async {
                              final activated = await ref
                                  .read(executionClientProvider)
                                  .activateAssignment(preview.id);
                              if (!context.mounted) return;
                              for (final key in activated.assigneeInputKeys) {
                                final existing =
                                    activated.draftInputs.dynamicInputs[key];
                                inputControllers[key] = TextEditingController(
                                  text: existing?.textValue ?? '',
                                );
                              }
                              activatedAssignment.value = activated;
                            }),
                      icon: const Icon(Icons.play_arrow_outlined),
                      label: Text(l10n.taskPortalStartTaskBtn),
                    ),
                  ],
                ),
              ),
            )
          else
            _buildActivatedWorkspaceCard(
              context: context,
              ref: ref,
              active: activatedAssignment.value!,
              remainingSeconds: remainingSeconds.value,
              inputControllers: inputControllers,
              selectedFileInputs: selectedFileInputs,
              portalMutation: portalMutation,
              onDraftSaved: (updated) => activatedAssignment.value = updated,
              onSubmitted: (record) => submittedRecord.value = record,
            ),
        ],
      ),
    );
  }

  Widget _buildTaskBriefCard({
    required BuildContext context,
    required TaskAssignmentBriefDto brief,
  }) {
    final localizedTitle = _resolveLocalizedText(
      context,
      brief.label.translations,
    );
    return Card(
      key: const Key('task_portal_task_brief_card'),
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
              l10n.taskPortalTaskBriefHeader,
              style: theme.textTheme.labelLarge?.copyWith(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.bold,
              ),
            ),
            AppSpacing.h4,
            Text(
              localizedTitle,
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            if (brief.instructionText != null &&
                brief.instructionText!.trim().isNotEmpty) ...[
              AppSpacing.h8,
              SelectableText(
                brief.instructionText!,
                key: const Key('task_portal_task_brief_body'),
                style: theme.textTheme.bodyMedium,
              ),
            ],
            if (brief.sourceUrl != null &&
                brief.sourceUrl!.trim().isNotEmpty) ...[
              AppSpacing.h8,
              Row(
                children: [
                  const Icon(Icons.link, size: AppSpacing.s16),
                  AppSpacing.w8,
                  Expanded(
                    child: SelectableText(
                      brief.sourceUrl!,
                      key: const Key('task_portal_task_brief_link'),
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.primary,
                      ),
                    ),
                  ),
                  IconButton(
                    key: const Key('task_portal_copy_brief_link_btn'),
                    tooltip: l10n.taskPortalCopyReferenceLinkTooltip,
                    icon: const Icon(Icons.copy_outlined, size: AppSpacing.s16),
                    onPressed: () {
                      Clipboard.setData(ClipboardData(text: brief.sourceUrl!));
                    },
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildActivatedWorkspaceCard({
    required BuildContext context,
    required WidgetRef ref,
    required ExecutionAssignmentResponseDto active,
    required int? remainingSeconds,
    required Map<String, TextEditingController> inputControllers,
    required ValueNotifier<Map<String, WorkflowInputValue>> selectedFileInputs,
    required MutationState<void> portalMutation,
    required ValueChanged<ExecutionAssignmentResponseDto> onDraftSaved,
    required ValueChanged<ExecutionRecord> onSubmitted,
  }) {
    WorkflowInputs collectCurrentInputs() {
      return WorkflowInputs(
        language: active.targetLocale,
        dynamicInputs: {
          for (final key in active.assigneeInputKeys)
            if (selectedFileInputs.value[key]?.fileValue != null)
              key: selectedFileInputs.value[key]!
            else if ((inputControllers[key]?.text.trim() ?? '').isNotEmpty)
              key: WorkflowInputValue.text(inputControllers[key]!.text.trim()),
        },
      );
    }

    return Card(
      key: const Key('task_portal_workspace_card'),
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
            if (remainingSeconds != null) ...[
              Container(
                key: const Key('task_portal_countdown_badge'),
                padding: const EdgeInsets.symmetric(
                  horizontal: AppSpacing.s12,
                  vertical: AppSpacing.s4,
                ),
                decoration: BoxDecoration(
                  color: theme.colorScheme.secondaryContainer,
                  borderRadius: BorderRadius.circular(AppSpacing.s12),
                ),
                child: Text(
                  l10n.taskPortalRemainingTimeLabel('${remainingSeconds}s'),
                  style: theme.textTheme.labelLarge?.copyWith(
                    color: theme.colorScheme.onSecondaryContainer,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              AppSpacing.h16,
            ],
            ...active.assigneeInputKeys.map((inputKey) {
              inputControllers.putIfAbsent(
                inputKey,
                () => TextEditingController(),
              );
              final attachedFile =
                  selectedFileInputs.value[inputKey]?.fileValue;
              return Padding(
                padding: const EdgeInsets.only(bottom: AppSpacing.s16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            inputKey,
                            style: theme.textTheme.labelLarge?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        OutlinedButton.icon(
                          key: Key('task_portal_upload_file_btn_$inputKey'),
                          onPressed: portalMutation.isLoading
                              ? null
                              : () async {
                                  final picker = onPickFile ?? _defaultPickFile;
                                  final picked = await picker(inputKey);
                                  if (!context.mounted || picked == null) {
                                    return;
                                  }
                                  selectedFileInputs.value =
                                      <String, WorkflowInputValue>{
                                        ...selectedFileInputs.value,
                                        inputKey: picked,
                                      };
                                },
                          icon: const Icon(Icons.upload_file_outlined),
                          label: Text(l10n.uploadFile),
                        ),
                        if (attachedFile != null) ...[
                          AppSpacing.w8,
                          Flexible(
                            child: Text(
                              attachedFile.filename,
                              key: Key(
                                'task_portal_attached_filename_$inputKey',
                              ),
                              overflow: TextOverflow.ellipsis,
                              style: theme.textTheme.bodySmall,
                            ),
                          ),
                          IconButton(
                            key: Key('task_portal_clear_file_btn_$inputKey'),
                            tooltip: l10n.delete,
                            icon: const Icon(Icons.close),
                            onPressed: () {
                              final updated =
                                  Map<String, WorkflowInputValue>.from(
                                    selectedFileInputs.value,
                                  )..remove(inputKey);
                              selectedFileInputs.value = updated;
                            },
                          ),
                        ],
                      ],
                    ),
                    AppSpacing.h8,
                    TextFormField(
                      key: Key('task_portal_input_$inputKey'),
                      controller: inputControllers[inputKey],
                      maxLines: 4,
                      decoration: InputDecoration(
                        labelText: inputKey,
                        border: const OutlineInputBorder(),
                      ),
                    ),
                  ],
                ),
              );
            }),
            if (portalMutation.hasError) ...[
              ErrorView(error: portalMutation.error!, compact: true),
              AppSpacing.h12,
            ],
            Row(
              children: [
                OutlinedButton.icon(
                  key: const Key('task_portal_save_draft_btn'),
                  onPressed: portalMutation.isLoading
                      ? null
                      : () => portalMutation.mutate(() async {
                          final updated = await ref
                              .read(executionClientProvider)
                              .saveAssignmentDraft(
                                assignmentId: active.id,
                                payload: ExecutionAssignmentDraftDto(
                                  draftInputs: collectCurrentInputs(),
                                ),
                              );
                          if (!context.mounted) return;
                          onDraftSaved(updated);
                        }),
                  icon: const Icon(Icons.save_outlined),
                  label: Text(l10n.taskPortalSaveDraftBtn),
                ),
                AppSpacing.w12,
                OutlinedButton.icon(
                  key: const Key('task_portal_submit_btn'),
                  onPressed: portalMutation.isLoading
                      ? null
                      : () => portalMutation.mutate(() async {
                          final record = await ref
                              .read(executionClientProvider)
                              .submitAssignment(
                                assignmentId: active.id,
                                payload: ExecutionAssignmentSubmitDto(
                                  submittedInputs: collectCurrentInputs(),
                                ),
                              );
                          if (!context.mounted) return;
                          onSubmitted(record);
                        }),
                  icon: const Icon(Icons.send_outlined),
                  label: Text(l10n.taskPortalSubmitTaskBtn),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
