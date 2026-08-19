import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:client_app/features/studio/controllers/output_profile_controller.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/views/widgets/profile/tabs/profile_general_tab.dart';
import 'package:client_app/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart';
import 'package:client_app/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart';
import 'package:client_app/core/error/app_error_boundary.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';

/// Admin Studio View for managing Output Profiles.
/// Uses the 2026 Gold Standard 3-Tab Architecture (Dumb UI Shell).
class OutputProfileCrudView extends HookConsumerWidget {
  final String id;
  const OutputProfileCrudView({super.key, required this.id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final formKey = useMemoized(() => GlobalKey<FormState>());
    final formState = ref.watch(outputProfileFormProvider(id));

    return switch (formState) {
      AsyncLoading() => Scaffold(
        appBar: AppBar(title: Text(l10n.editOutputProfileTitle)),
        body: const Center(child: CircularProgressIndicator()),
      ),
      AsyncError(:final error, :final stackTrace) => Scaffold(
        appBar: AppBar(title: Text(l10n.editOutputProfileTitle)),
        body: ErrorView(
          error: error,
          stackTrace: stackTrace,
          compact: false,
          onRetry: () => ref.invalidate(outputProfileFormProvider(id)),
        ),
      ),
      AsyncData(value: final payload) => DefaultTabController(
        length: 3,
        child: AppExceptionBoundary(
          child: Scaffold(
            appBar: AppBar(
              title: Text(l10n.editOutputProfileTitle),
              bottom: TabBar(
                tabs: [
                  Tab(text: l10n.profileTabGeneral),
                  Tab(text: l10n.profileTabScoring),
                  Tab(text: l10n.profileTabReportStructure),
                ],
              ),
              actions: [
                if (formState.isLoading)
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: AppSpacing.s16),
                    child: Center(
                      child: SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                    ),
                  )
                else ...[
                  IconButton(
                    icon: Icon(
                      Icons.delete,
                      color: Theme.of(context).colorScheme.error,
                    ),
                    onPressed: () =>
                        _deleteProfile(context, ref, l10n, payload),
                    tooltip: l10n.deleteProfileTitle,
                  ),
                  TextButton.icon(
                    onPressed: () =>
                        _saveProfile(context, ref, l10n, formKey, payload),
                    icon: const Icon(Icons.save),
                    label: Text(l10n.studioSaveButton),
                  ),
                ],
              ],
            ),
            body: Form(
              key: formKey,
              child: TabBarView(
                children: [
                  ProfileGeneralTab(id: id),
                  ProfileScoringTab(id: id),
                  ProfileLayoutsTab(id: id),
                ],
              ),
            ),
          ),
        ),
      ),
    };
  }

  Future<void> _saveProfile(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    GlobalKey<FormState> formKey,
    OutputProfile payload,
  ) async {
    if (!formKey.currentState!.validate()) return;

    try {
      final String idToSave = payload.id.trim();
      if (idToSave.isEmpty) {
        throw Exception(l10n.studioViewsProfileIdRequired);
      }

      final newPayload = payload.copyWith(
        id: idToSave,
        slug: payload.slug.trim().isNotEmpty ? payload.slug.trim() : idToSave,
      );

      final notifier = ref.read(outputProfileFormProvider(id).notifier);
      await notifier.submit(newPayload);

      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(l10n.profileSavedSuccess),
          backgroundColor: Theme.of(context).colorScheme.primary,
        ),
      );
      context.pop();
    } catch (e) {
      if (!context.mounted) return;
      ref
          .read(loggerServiceProvider)
          .error('Studio', 'Failed to save profile: $e', e);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(l10n.saveFailedError(e.toString())),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }

  Future<void> _deleteProfile(
    BuildContext context,
    WidgetRef ref,
    AppLocalizations l10n,
    OutputProfile payload,
  ) async {
    final String idToDelete = payload.id;
    if (idToDelete.isEmpty) return;

    final currentLocale = Localizations.localeOf(context).languageCode;
    final nameToDisplay =
        payload.name.translations[currentLocale] ??
        payload.name.translations['en'] ??
        idToDelete;

    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.deleteProfileTitle),
        content: Text(l10n.deleteProfileConfirmation(nameToDisplay)),
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
            .read(outputProfilesControllerProvider.notifier)
            .deleteProfile(idToDelete);
        if (context.mounted) context.pop();
      } catch (e) {
        if (!context.mounted) return;
        ref
            .read(loggerServiceProvider)
            .error('Studio', 'Failed to delete profile: $e', e);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.deleteFailedError(e.toString()))),
        );
      }
    }
  }
}
