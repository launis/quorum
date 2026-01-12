import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/core/error/app_error_ext.dart';
import 'package:client_app/features/admin/presentation/providers/admin_providers.dart';
import 'package:client_app/features/admin/presentation/providers/user_crud_controller.dart';
import 'package:client_app/features/admin/presentation/widgets/user_form_dialog.dart';
import 'package:client_app/features/admin/presentation/widgets/user_list_item.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// **User Management Screen**
///
/// Displays a list of users for the current organization and allows role management.
/// Uses [CustomScrollView] for performance and adheres to the max-width constraint.
class UserManagementScreen extends ConsumerWidget {
  const UserManagementScreen({super.key});

  void _showUserDialog(BuildContext context, String orgId, [User? user]) {
    showDialog<void>(
      context: context,
      builder: (context) => UserFormDialog(user: user, orgId: orgId),
    );
  }

  Future<void> _deleteUser(
    BuildContext context,
    WidgetRef ref,
    User user,
    String orgId,
  ) async {
    final l10n = AppLocalizations.of(context)!;
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(l10n.deleteUser),
            content: Text(
              l10n.deleteUserConfirmation(user.displayName ?? user.email),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: Text(l10n.cancel),
              ),
              FilledButton(
                style: FilledButton.styleFrom(
                  backgroundColor: Theme.of(context).colorScheme.error,
                ),
                onPressed: () => Navigator.pop(context, true),
                child: Text(l10n.deleteUser),
              ),
            ],
          ),
    );

    if (confirmed == true && context.mounted) {
      await ref
          .read(userCrudControllerProvider.notifier)
          .deleteUser(user.uid, orgId);
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    // 1. Get Current User (to determine Org ID)
    final authState = ref.watch(authControllerProvider);

    // Listen for CRUD errors/success
    ref.listen(userCrudControllerProvider, (previous, next) {
      next.whenOrNull(
        error: (error, stack) {
          if (error is AppError) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(
                  error.message(l10n),
                ), // Assuming AppError has message(l10n) helper or similar
                backgroundColor: colorScheme.error,
              ),
            );
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(error.toString()),
                backgroundColor: colorScheme.error,
              ),
            );
          }
        },
      );
    });

    return Scaffold(
      body: Align(
        alignment: Alignment.topCenter,
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: authState.when(
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (err, stack) => Center(child: Text('Error: $err')),
            data: (currentUser) {
              if (currentUser == null) {
                return Center(child: Text(l10n.loginRequired));
              }

              final orgId = currentUser.organizationId;
              if (orgId == null || orgId.isEmpty) {
                return Center(child: Text(l10n.errorNotFound));
              }

              final orgUsersValue = ref.watch(orgUsersProvider(orgId));

              return RefreshIndicator(
                onRefresh: () async {
                  return ref.refresh(orgUsersProvider(orgId).future);
                },
                child: CustomScrollView(
                  slivers: [
                    // Header
                    SliverToBoxAdapter(
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              l10n.organizationMembers,
                              style: theme.textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.refresh),
                              onPressed: () {
                                ref.invalidate(orgUsersProvider(orgId));
                              },
                              tooltip: l10n.refresh,
                            ),
                          ],
                        ),
                      ),
                    ),

                    // User List state
                    orgUsersValue.when(
                      loading:
                          () => const SliverFillRemaining(
                            child: Center(child: CircularProgressIndicator()),
                          ),
                      error:
                          (err, stack) => SliverFillRemaining(
                            child: Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.error_outline,
                                    size: 48,
                                    color: colorScheme.error,
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    err.toString(),
                                    style: TextStyle(color: colorScheme.error),
                                    textAlign: TextAlign.center,
                                  ),
                                  const SizedBox(height: 16),
                                  FilledButton.tonal(
                                    onPressed: () {
                                      ref.invalidate(orgUsersProvider(orgId));
                                    },
                                    child: Text(l10n.retry),
                                  ),
                                ],
                              ),
                            ),
                          ),
                      data: (users) {
                        if (users.isEmpty) {
                          return SliverFillRemaining(
                            child: Center(
                              child: Text(
                                l10n.noUsersFound,
                                style: theme.textTheme.bodyLarge,
                              ),
                            ),
                          );
                        }

                        return SliverList(
                          delegate: SliverChildBuilderDelegate((
                            context,
                            index,
                          ) {
                            final user = users[index];
                            return UserListItem(
                              user: user,
                              onEdit:
                                  () => _showUserDialog(context, orgId, user),
                              onDelete:
                                  () => _deleteUser(context, ref, user, orgId),
                            );
                          }, childCount: users.length),
                        );
                      },
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ),
      floatingActionButton:
          authState.value?.organizationId != null
              ? FloatingActionButton(
                onPressed:
                    () => _showUserDialog(
                      context,
                      authState.value!.organizationId!,
                    ),
                child: const Icon(Icons.add),
              )
              : null,
    );
  }
}
