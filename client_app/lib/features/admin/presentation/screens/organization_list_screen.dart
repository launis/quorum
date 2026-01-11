import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/admin/domain/models/organization.dart';
import 'package:client_app/features/admin/presentation/organization_controller.dart';
import 'package:client_app/features/admin/presentation/widgets/organization_form_dialog.dart';
import 'package:client_app/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class OrganizationListScreen extends ConsumerWidget {
  const OrganizationListScreen({super.key});

  void _showForm(BuildContext context, [Organization? org]) {
    showDialog<void>(
      context: context,
      builder: (context) => OrganizationFormDialog(organization: org),
    );
  }

  Future<void> _deleteOrg(
    BuildContext context,
    WidgetRef ref,
    Organization org,
    AppLocalizations l10n,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text(l10n.deleteOrganization),
            content: Text(l10n.deleteOrgConfirmation(org.name)),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context, false),
                child: Text(l10n.cancel),
              ),
              FilledButton(
                onPressed: () => Navigator.pop(context, true),
                child: Text(l10n.deleteOrganization),
              ),
            ],
          ),
    );

    if (confirmed == true && context.mounted) {
      final error = await ref
          .read(organizationListProvider.notifier)
          .deleteOrganization(org.id);

      if (error != null && context.mounted) {
        // Check if error is due to existing users (409)
        bool needsForce = false;
        error.maybeWhen(
          server: (msg, code) {
            if (code == 409 && (msg?.contains('ORG_HAS_USERS') ?? false)) {
              needsForce = true;
            }
          },
          orElse: () {},
        );

        if (needsForce) {
          final forceConfirmed = await showDialog<bool>(
            context: context,
            builder:
                (context) => AlertDialog(
                  title: Text(l10n.deleteOrgHasUsersTitle),
                  content: Text(l10n.deleteOrgHasUsersMessage),
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
                      child: Text(l10n.deleteForceConfirm),
                    ),
                  ],
                ),
          );

          if (forceConfirmed == true && context.mounted) {
            await ref
                .read(organizationListProvider.notifier)
                .deleteOrganization(org.id, force: true);
          }
        } else {
          // Show other errors (e.g. 403 Forbidden) in a Snackbar
          if (context.mounted) {
            final msg = error.maybeWhen(
              server: (msg, _) => msg ?? 'Server Error',
              network: (_) => 'Network Error',
              orElse: () => 'Unknown Error',
            );
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(msg),
                backgroundColor: Theme.of(context).colorScheme.error,
              ),
            );
          }
        }
      }
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;
    final organizations = ref.watch(organizationListProvider);

    return Scaffold(
      appBar: AppBar(title: Text(l10n.organizationManagementTitle)),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: organizations.when(
            data:
                (orgs) => ListView.separated(
                  itemCount: orgs.length,
                  separatorBuilder: (context, index) => const Divider(),
                  itemBuilder: (context, index) {
                    final org = orgs[index];
                    return ListTile(
                      title: Text(org.name),
                      subtitle: Text(
                        'ID: ${org.id} • Status: ${org.status.name}',
                      ),
                      trailing: PopupMenuButton<String>(
                        onSelected: (value) {
                          if (value == 'edit') {
                            _showForm(context, org);
                          } else if (value == 'delete') {
                            _deleteOrg(context, ref, org, l10n);
                          }
                        },
                        itemBuilder:
                            (context) => [
                              PopupMenuItem(
                                value: 'edit',
                                child: Text(l10n.editOrganization),
                              ),
                              PopupMenuItem(
                                value: 'delete',
                                child: Text(
                                  l10n.deleteOrganization,
                                  style: TextStyle(
                                    color: Theme.of(context).colorScheme.error,
                                  ),
                                ),
                              ),
                            ],
                      ),
                      onTap: () => _showForm(context, org),
                    );
                  },
                ),
            error: (err, stack) => Center(child: Text('Error: $err')),
            loading: () => const Center(child: CircularProgressIndicator()),
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showForm(context),
        child: const Icon(Icons.add),
      ),
    );
  }
}
