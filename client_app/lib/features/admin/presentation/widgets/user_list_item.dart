import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

/// **User List Item**
///
/// Adaptive list item for displaying user details in the Admin Panel.
/// Switches between a [ListTile] (Mobile) and a Table-row style [Row] (Desktop).
class UserListItem extends ConsumerWidget {
  const UserListItem({
    super.key,
    required this.user,
    this.onEdit,
    this.onDelete,
  });

  final User user;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Breakpoint from docs/flutterpromptohje.md
    const double mobileBreakpoint = 600.0;

    // Safety: Retrieve current user to prevent self-edit lockout
    final authState = ref.watch(authControllerProvider);
    final String? currentUserId = authState.value?.uid;

    final bool isSelf = currentUserId == user.uid;
    // Allow edit/delete only if not self and callbacks provided
    final bool canModify = !isSelf && (onEdit != null || onDelete != null);

    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth < mobileBreakpoint) {
          return _MobileLayout(
            user: user,
            canModify: canModify,
            onEdit: onEdit,
            onDelete: onDelete,
          );
        } else {
          return _DesktopLayout(
            user: user,
            canModify: canModify,
            onEdit: onEdit,
            onDelete: onDelete,
          );
        }
      },
    );
  }
}

class _MobileLayout extends StatelessWidget {
  const _MobileLayout({
    required this.user,
    required this.canModify,
    this.onEdit,
    this.onDelete,
  });

  final User user;
  final bool canModify;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);

    final formattedDate =
        user.lastLoginAt != null
            ? DateFormat.yMMMd().add_jm().format(user.lastLoginAt!)
            : '-';

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ListTile(
        title: Text(
          user.displayName ?? user.email,
          style: theme.textTheme.titleMedium,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text('${l10n.roleLabel}: ${user.role.name.toUpperCase()}'),
            Text(
              '${l10n.lastLogin}: $formattedDate',
              style: theme.textTheme.bodySmall,
            ),
          ],
        ),
        trailing:
            canModify
                ? PopupMenuButton<String>(
                  onSelected: (value) {
                    if (value == 'edit') onEdit?.call();
                    if (value == 'delete') onDelete?.call();
                  },
                  itemBuilder:
                      (context) => [
                        PopupMenuItem(
                          value: 'edit',
                          child: Text(l10n.editUser),
                        ),
                        PopupMenuItem(
                          value: 'delete',
                          child: Text(
                            l10n.deleteUser,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                        ),
                      ],
                )
                : null,
      ),
    );
  }
}

class _DesktopLayout extends StatelessWidget {
  const _DesktopLayout({
    required this.user,
    required this.canModify,
    this.onEdit,
    this.onDelete,
  });

  final User user;
  final bool canModify;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    final formattedDate =
        user.lastLoginAt != null
            ? DateFormat.yMMMd().add_jm().format(user.lastLoginAt!)
            : '-';

    // Badge color for admins
    final isPrivileged = user.isAdmin;
    final roleColor =
        isPrivileged
            ? colorScheme.tertiaryContainer
            : colorScheme.surfaceContainerHighest;
    final roleTextColor =
        isPrivileged
            ? colorScheme.onTertiaryContainer
            : colorScheme.onSurfaceVariant;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: colorScheme.outlineVariant)),
      ),
      child: Row(
        children: [
          // Name
          Expanded(
            flex: 2,
            child: Text(
              user.displayName ?? '-',
              style: theme.textTheme.bodyLarge?.copyWith(
                fontWeight: FontWeight.w500,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),

          // Email
          Expanded(
            flex: 3,
            child: Text(
              user.email,
              overflow: TextOverflow.ellipsis,
              style: theme.textTheme.bodyMedium,
            ),
          ),

          // Role
          Expanded(
            flex: 2,
            child: Align(
              alignment: Alignment.centerLeft,
              child: Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 4,
                ),
                decoration: BoxDecoration(
                  color: roleColor,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Text(
                  user.role.name.toUpperCase(),
                  style: theme.textTheme.labelMedium?.copyWith(
                    color: roleTextColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),

          // Last Login
          Expanded(
            flex: 2,
            child: Text(
              formattedDate,
              style: theme.textTheme.bodySmall,
              overflow: TextOverflow.ellipsis,
            ),
          ),

          // Actions
          SizedBox(
            width: 100, // Fixed width for actions
            child:
                canModify
                    ? Align(
                      alignment: Alignment.centerRight,
                      child: PopupMenuButton<String>(
                        tooltip: l10n.actions,
                        onSelected: (value) {
                          if (value == 'edit') onEdit?.call();
                          if (value == 'delete') onDelete?.call();
                        },
                        itemBuilder:
                            (context) => [
                              PopupMenuItem(
                                value: 'edit',
                                child: Text(l10n.editUser),
                              ),
                              PopupMenuItem(
                                value: 'delete',
                                child: Text(
                                  l10n.deleteUser,
                                  style: TextStyle(
                                    color: Theme.of(context).colorScheme.error,
                                  ),
                                ),
                              ),
                            ],
                        child: const Padding(
                          padding: EdgeInsets.all(8.0),
                          child: Icon(Icons.more_vert),
                        ),
                      ),
                    )
                    : const SizedBox.shrink(), // Empty space for alignment
          ),
        ],
      ),
    );
  }
}
