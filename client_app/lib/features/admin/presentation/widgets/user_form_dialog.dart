import 'package:client_app/features/admin/domain/dtos/user_dtos.dart';
import 'package:client_app/features/admin/presentation/providers/user_crud_controller.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
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
  late UserRole _role;

  @override
  void initState() {
    super.initState();
    _emailController = TextEditingController(text: widget.user?.email);
    _displayNameController = TextEditingController(
      text: widget.user?.displayName,
    );
    _passwordController = TextEditingController();
    _role = widget.user?.role ?? UserRole.member; // Fixed: UserRole.member
  }

  @override
  void dispose() {
    _emailController.dispose();
    _displayNameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_formKey.currentState!.validate()) {
      Navigator.of(context).pop(); // Close dialog immediately

      if (widget.user == null) {
        // Create
        final dto = UserCreateDto(
          email: _emailController.text,
          password: _passwordController.text,
          displayName: _displayNameController.text,
          role: _role,
          organizationId: widget.orgId,
        );
        await ref
            .read(userCrudControllerProvider.notifier)
            .createUser(dto, widget.orgId);
      } else {
        // Update
        final dto = UserUpdateDto(
          displayName: _displayNameController.text,
          role: _role,
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

    return AlertDialog(
      title: Text(isEditing ? l10n.editUser : l10n.createUser),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
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
              DropdownButtonFormField<UserRole>(
                initialValue: _role, // Fixed: initialValue instead of value
                decoration: InputDecoration(labelText: l10n.roleLabel),
                items:
                    UserRole.values.map((role) {
                      return DropdownMenuItem(
                        value: role,
                        child: Text(role.name.toUpperCase()),
                      );
                    }).toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _role = val);
                },
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
