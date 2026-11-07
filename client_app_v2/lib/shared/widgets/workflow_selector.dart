import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/core/ui/error_view.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

@immutable
class WorkflowSelectorItem {
  final String id;
  final I18nText? localizedName;
  final String? directName;

  const WorkflowSelectorItem({
    required this.id,
    this.localizedName,
    this.directName,
  });
}

class WorkflowSelector extends ConsumerWidget {
  final List<WorkflowSelectorItem> workflows;
  final String? selectedId;
  final ValueChanged<String?> onChanged;
  final bool isLoading;

  const WorkflowSelector({
    super.key,
    required this.workflows,
    required this.selectedId,
    required this.onChanged,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final locale = Localizations.localeOf(context).languageCode;

    try {
      if (selectedId != null && selectedId!.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: WorkflowSelector selectedId cannot be an empty string.',
        );
      }

      final seenIds = <String>{};
      final items = <DropdownMenuItem<String>>[];

      for (final wf in workflows) {
        final idRaw = wf.id;
        if (idRaw.trim().isEmpty) {
          throw AppException.validation(
            'Fail-Fast: Workflow entry is missing a valid non-empty String "id".',
          );
        }
        if (!seenIds.add(idRaw)) {
          throw AppException.validation(
            'Fail-Fast: Duplicate workflow id "$idRaw" in WorkflowSelector.',
          );
        }

        final String nameStr;
        if (wf.localizedName != null) {
          nameStr = wf.localizedName!.get(locale);
        } else if (wf.directName != null && wf.directName!.trim().isNotEmpty) {
          nameStr = wf.directName!;
        } else {
          throw AppException.validation(
            'Fail-Fast: Workflow "$idRaw" is missing a valid localized "name".',
          );
        }

        items.add(
          DropdownMenuItem<String>(
            value: idRaw,
            child: Text(nameStr, maxLines: 1, overflow: TextOverflow.ellipsis),
          ),
        );
      }

      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (isLoading) const LinearProgressIndicator(),
          InputDecorator(
            decoration: InputDecoration(
              labelText: l10n.chooseAnalysisType,
              border: const OutlineInputBorder(),
              prefixIcon: const Icon(Icons.settings_applications),
              contentPadding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.s12,
                vertical: AppSpacing.s4,
              ),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: selectedId != null && seenIds.contains(selectedId)
                    ? selectedId
                    : null,
                items: items,
                onChanged: onChanged,
                isExpanded: true,
              ),
            ),
          ),
        ],
      );
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error(
            'WorkflowSelector',
            'VALIDATION_FAILED: Failed to render WorkflowSelector',
            e,
            st,
          );
      return ErrorView(error: e, stackTrace: st, compact: true);
    }
  }
}
