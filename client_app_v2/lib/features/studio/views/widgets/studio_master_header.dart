import 'package:flutter/material.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// Standardized master list header for Quorum Studio master views.
/// Adheres strictly to Desktop Pro Tool UX and Studio Master Header contract freeze.
class StudioMasterHeader extends StatelessWidget {
  final String title;
  final String? subtitle;
  final String searchQuery;
  final ValueChanged<String> onSearchChanged;
  final int itemCount;
  final int totalCount;
  final String? actionLabel;
  final IconData? actionIcon;
  final VoidCallback? onAction;
  final Widget? leading;
  final Widget? bottom;

  const StudioMasterHeader({
    super.key,
    required this.title,
    this.subtitle,
    required this.searchQuery,
    required this.onSearchChanged,
    required this.itemCount,
    required this.totalCount,
    this.actionLabel,
    this.actionIcon,
    this.onAction,
    this.leading,
    this.bottom,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final l10n = AppLocalizations.of(context)!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        Row(
          children: [
            if (leading != null) ...[leading!, AppSpacing.w8],
            Expanded(
              child: Text(
                title,
                overflow: TextOverflow.ellipsis,
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            if (actionLabel != null && onAction != null) ...[
              AppSpacing.w16,
              FilledButton.icon(
                onPressed: onAction,
                icon: Icon(actionIcon ?? Icons.add),
                label: Text(actionLabel!),
              ),
            ],
          ],
        ),
        if (subtitle != null) ...[
          AppSpacing.h8,
          Text(
            subtitle!,
            overflow: TextOverflow.ellipsis,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
          ),
        ],
        AppSpacing.h16,
        Row(
          children: [
            Expanded(
              child: _SearchInputField(
                searchQuery: searchQuery,
                onSearchChanged: onSearchChanged,
                hintText: l10n.studioMasterSearchHint,
                clearTooltip: l10n.studioMasterClearSearch,
              ),
            ),
            AppSpacing.w16,
            Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppSpacing.s12,
                vertical: AppSpacing.s8,
              ),
              decoration: BoxDecoration(
                color: theme.colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(AppSpacing.s16),
              ),
              child: Text(
                l10n.studioMasterItemCount(itemCount, totalCount),
                style: theme.textTheme.labelMedium?.copyWith(
                  color: theme.colorScheme.onPrimaryContainer,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
        if (bottom != null) ...[AppSpacing.h16, bottom!],
      ],
    );
  }
}

class _SearchInputField extends StatefulWidget {
  final String searchQuery;
  final ValueChanged<String> onSearchChanged;
  final String hintText;
  final String clearTooltip;

  const _SearchInputField({
    required this.searchQuery,
    required this.onSearchChanged,
    required this.hintText,
    required this.clearTooltip,
  });

  @override
  State<_SearchInputField> createState() => _SearchInputFieldState();
}

class _SearchInputFieldState extends State<_SearchInputField> {
  late final TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController(text: widget.searchQuery);
  }

  @override
  void didUpdateWidget(covariant _SearchInputField oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.searchQuery != _controller.text) {
      _controller.text = widget.searchQuery;
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: _controller,
      onChanged: widget.onSearchChanged,
      decoration: InputDecoration(
        hintText: widget.hintText,
        prefixIcon: const Icon(Icons.search),
        suffixIcon: widget.searchQuery.isNotEmpty
            ? IconButton(
                icon: const Icon(Icons.clear),
                tooltip: widget.clearTooltip,
                onPressed: () {
                  _controller.clear();
                  widget.onSearchChanged('');
                },
              )
            : null,
        isDense: true,
        border: const OutlineInputBorder(),
      ),
    );
  }
}
