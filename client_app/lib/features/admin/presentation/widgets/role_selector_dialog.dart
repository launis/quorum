import 'package:client_app/features/admin/presentation/providers/admin_providers.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// **Role Selector Dialog**
///
/// A modal dialog for changing a user's role.
/// Includes logic to warn when demoting an Admin.
class RoleSelectorDialog extends ConsumerStatefulWidget {
  const RoleSelectorDialog({
    super.key,
    required this.user,
    required this.orgId,
  });

  final User user;
  final String orgId;

  @override
  ConsumerState<RoleSelectorDialog> createState() => _RoleSelectorDialogState();
}

class _RoleSelectorDialogState extends ConsumerState<RoleSelectorDialog> {
  late UserRole _selectedRole;

  @override
  void initState() {
    super.initState();
    _selectedRole = widget.user.role;
  }

  bool get _isDemotion {
    // Demotion logic: Original is Admin AND New is NOT Admin.
    return widget.user.isAdmin && !_selectedRole.isAdmin;
  }

  Future<void> _handleSave() async {
    // Close dialog immediately if no change (optional UX choice, but clearer)
    if (_selectedRole == widget.user.role) {
      Navigator.of(context).pop();
      return;
    }

    final success = await ref
        .read(userRoleControllerProvider.notifier)
        .updateRole(
          orgId: widget.orgId,
          userId: widget.user.id,
          newRole: _selectedRole,
        );

    if (mounted && success) {
      Navigator.of(context).pop();
      // Success snackbar is usually handled by the parent or a global listener,
      // but since controller returns bool, we assume error handling is done via controller state listening
      // or we rely on the controller's side effects.
      // Based on admin_providers: invalidate happens automatically.
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    // Listen to controller state for loading/error feedback
    final state = ref.watch(userRoleControllerProvider);
    final isLoading = state.isLoading;

    // Show error if one exists in the state (ephemeral)
    ref.listen(userRoleControllerProvider, (_, next) {
      if (next.hasError && !next.isLoading) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(next.error.toString()),
            backgroundColor: colorScheme.error,
          ),
        );
      }
    });

    return AlertDialog(
      title: Text(
        l10n.roleLabel,
      ), // "Role" or "Rooli" - acting as title "Role Manager"
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Role List
            // Role List
            RadioGroup<UserRole>(
              groupValue: _selectedRole,
              onChanged: (value) {
                if (!isLoading && value != null) {
                  setState(() => _selectedRole = value);
                }
              },
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children:
                    UserRole.values
                        .where((role) => role != UserRole.unknown)
                        .map((role) {
                          return RadioListTile<UserRole>(
                            title: Text(role.name.toUpperCase()),
                            value: role,
                            enabled: !isLoading,
                          );
                        })
                        .toList(),
              ),
            ),

            // Demotion Warning
            if (_isDemotion) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: colorScheme.errorContainer,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.warning_amber,
                      color: colorScheme.onErrorContainer,
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        l10n.confirmDemotion,
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: colorScheme.onErrorContainer,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
      actions: [
        // Cancel
        TextButton(
          onPressed: isLoading ? null : () => Navigator.of(context).pop(),
          child: Text(l10n.cancel), // Fallback passed via l10n gen usually
        ),

        // Save
        FilledButton.tonal(
          onPressed: isLoading ? null : _handleSave,
          child:
              isLoading
                  ? SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: colorScheme.onSecondaryContainer,
                    ),
                  )
                  : Text(l10n.save),
        ),
      ],
    );
  }
}

// Extension to help determine admin status easily
extension _UserRoleX on UserRole {
  // Assuming 'admin' and 'root' (if exists) are privileged.
  // Based on user.dart, we have: root, admin, member, unknown.
  // Assuming 'root' is also considered admin-level for demotion warnings?
  // Or is it just strictly UserRole.admin?
  // Logic: "Demoting an Admin". If I am Root, I am definitely privileged.
  // But usually RoleSelector is for choosing new role.
  // If current user is Admin, and I change to Member -> Demotion.
  // If current user is Root, and I change to Admin -> Demotion?
  // Let's stick to simplest interpretation: Is the *current* role privileged (Admin or Root)?
  bool get isAdmin => this == UserRole.admin || this == UserRole.root;
}
