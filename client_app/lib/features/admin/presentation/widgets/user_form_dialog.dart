import 'package:client_app/features/admin/domain/dtos/user_dtos.dart';
import 'package:client_app/features/admin/presentation/providers/user_crud_controller.dart';
import 'package:client_app/features/admin/presentation/organization_controller.dart';
import 'package:client_app/features/admin/presentation/providers/role_controller.dart';
import 'package:client_app/features/admin/domain/models/organization.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class UserFormDialog extends ConsumerStatefulWidget {
  final User? user;
  final String orgId;

  const UserFormDialog({super.key, this.user, required this.orgId});

  @override
  ConsumerState<UserFormDialog> createState() => _UserFormDialogState();
}

class _UserFormDialogState extends ConsumerState<UserFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _emailController;
  late TextEditingController _displayNameController;
  late TextEditingController _passwordController;
  late TextEditingController _orgIdController;
  late UserRole _role;

  @override
  void initState() {
    super.initState();
    _emailController = TextEditingController(text: widget.user?.email);
    _displayNameController = TextEditingController(
      text: widget.user?.displayName,
    );
    _passwordController = TextEditingController();
    _orgIdController = TextEditingController(
      text: widget.user?.organizationId ?? widget.orgId,
    );
    _role = widget.user?.role ?? UserRole.member;
  }

  @override
  void dispose() {
    _emailController.dispose();
    _displayNameController.dispose();
    _passwordController.dispose();
    _orgIdController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_formKey.currentState!.validate()) {
      Navigator.of(context).pop(); // Close dialog immediately

      // Check for ROOT permissions
      final currentUser = ref.read(authControllerProvider).value;
      final isRoot = currentUser?.role == UserRole.root;

      // Determine Org ID (Root can override, others use widget.orgId)
      final targetOrgId = isRoot ? _orgIdController.text : widget.orgId;

      if (widget.user == null) {
        // Create
        final dto = UserCreateDto(
          email: _emailController.text,
          password: _passwordController.text,
          displayName: _displayNameController.text,
          role: _role,
          organizationId: targetOrgId,
        );
        await ref
            .read(userCrudControllerProvider.notifier)
            .createUser(dto, targetOrgId);
      } else {
        // Update
        final dto = UserUpdateDto(
          displayName: _displayNameController.text,
          role: _role,
          organizationId: isRoot ? targetOrgId : null,
        );
        await ref
            .read(userCrudControllerProvider.notifier)
            .updateUser(widget.user!.uid, dto, widget.orgId);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final isEditing = widget.user != null;

    final currentUser = ref.watch(authControllerProvider).value;
    final isRoot = currentUser?.role == UserRole.root;
    final isSelf = widget.user?.uid == currentUser?.uid;

    return AlertDialog(
      title: Text(isEditing ? l10n.editUser : l10n.createUser),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Organization ID
              // Editable if ROOT and NOT Self.
              if (isRoot && !isSelf)
                ref
                    .watch(organizationListProvider)
                    .when(
                      data: (List<Organization> orgs) {
                        return DropdownButtonFormField<String>(
                          value:
                              _orgIdController.text.isNotEmpty &&
                                      orgs.any(
                                        (o) => o.id == _orgIdController.text,
                                      )
                                  ? _orgIdController.text
                                  : null,
                          decoration: InputDecoration(
                            labelText: l10n.organizationId,
                            prefixIcon: const Icon(Icons.business),
                          ),
                          items:
                              orgs.map((Organization org) {
                                return DropdownMenuItem(
                                  value: org.id,
                                  child: Text("${org.name} (${org.id})"),
                                );
                              }).toList(),
                          onChanged: (val) {
                            if (val != null) {
                              setState(() {
                                _orgIdController.text = val;
                              });
                            }
                          },
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return l10n.fieldRequired;
                            }
                            return null;
                          },
                        );
                      },
                      loading:
                          () =>
                              const Center(child: CircularProgressIndicator()),
                      error:
                          (e, s) => Text(
                            'Error loading organizations: $e',
                            style: const TextStyle(color: Colors.red),
                          ),
                    )
              else
                // Read-Only for Admins OR Self-Edit
                TextFormField(
                  initialValue:
                      _orgIdController
                          .text, // Use controller text for dynamic updates if needed, though mostly static here
                  decoration: InputDecoration(
                    labelText: l10n.organizationId,
                    prefixIcon: const Icon(Icons.business),
                  ),
                  enabled: false,
                ),

              const SizedBox(height: 16),

              // Email (Read-only if editing, usually)
              TextFormField(
                controller: _emailController,
                decoration: InputDecoration(labelText: l10n.emailLabel),
                enabled: !isEditing, // Prevent email change for now
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return l10n.fieldRequired;
                  }
                  if (!value.contains('@')) {
                    // Simple validation
                    return l10n
                        .fieldRequired; // Use a better error msg if available
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Display Name
              TextFormField(
                controller: _displayNameController,
                decoration: InputDecoration(labelText: l10n.displayNameLabel),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return l10n.fieldRequired;
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Password (Create only)
              if (!isEditing) ...[
                TextFormField(
                  controller: _passwordController,
                  decoration: InputDecoration(labelText: l10n.passwordLabel),
                  obscureText: true,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return l10n.fieldRequired;
                    }
                    if (value.length < 8) {
                      return 'Min 8 chars'; // Localization needed?
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
              ],

              // Role
              // Disabled if Self
              ref
                  .watch(assignableRolesProvider)
                  .when(
                    data: (List<UserRole> roles) {
                      // Fallback: If current role is generic/unknown but not in list (e.g. error),
                      // or if we simply need to show the current role even if not assignable?
                      // Usually standard list is fine.
                      return DropdownButtonFormField<UserRole>(
                        initialValue: _role,
                        decoration: InputDecoration(labelText: l10n.roleLabel),
                        items:
                            roles.map((UserRole role) {
                              return DropdownMenuItem(
                                value: role,
                                child: Text(role.name.toUpperCase()),
                              );
                            }).toList(),
                        onChanged:
                            isSelf
                                ? null
                                : (val) {
                                  if (val != null) setState(() => _role = val);
                                },
                        validator:
                            (val) => val == null ? l10n.fieldRequired : null,
                      );
                    },
                    loading: () => const LinearProgressIndicator(),
                    error:
                        (e, _) => Text(
                          'Error loading roles: $e',
                          style: const TextStyle(color: Colors.red),
                        ),
                  ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: Text(l10n.cancel),
        ),
        FilledButton(onPressed: _submit, child: Text(l10n.save)),
      ],
    );
  }
}
