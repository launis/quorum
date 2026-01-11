import 'package:client_app/features/admin/domain/models/organization.dart';
import 'package:client_app/features/admin/presentation/organization_controller.dart';
import 'package:client_app/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

class OrganizationFormDialog extends ConsumerStatefulWidget {
  final Organization? organization;

  const OrganizationFormDialog({super.key, this.organization});

  @override
  ConsumerState<OrganizationFormDialog> createState() =>
      _OrganizationFormDialogState();
}

class _OrganizationFormDialogState
    extends ConsumerState<OrganizationFormDialog> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _contactEmailController;
  late String _tier;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.organization?.name);
    _contactEmailController = TextEditingController(
      text: widget.organization?.contactEmail,
    );
    _tier = widget.organization?.tier ?? 'standard';
  }

  @override
  void dispose() {
    _nameController.dispose();
    _contactEmailController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_formKey.currentState!.validate()) {
      Navigator.of(context).pop(); // Close dialog immediately

      final data = {
        'name': _nameController.text,
        'contact_email': _contactEmailController.text,
        'tier': _tier,
      };

      if (widget.organization == null) {
        await ref.read(organizationListProvider.notifier).addOrganization(data);
      } else {
        await ref
            .read(organizationListProvider.notifier)
            .updateOrganization(widget.organization!.id, data);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final isEditing = widget.organization != null;

    return AlertDialog(
      title: Text(isEditing ? l10n.editOrganization : l10n.createOrganization),
      content: SingleChildScrollView(
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: InputDecoration(labelText: l10n.orgNameLabel),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return l10n.fieldRequired;
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _contactEmailController,
                decoration: InputDecoration(labelText: l10n.contactEmailLabel),
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                initialValue: _tier,
                decoration: InputDecoration(labelText: l10n.orgTierLabel),
                items: [
                  DropdownMenuItem(
                    value: 'standard',
                    child: Text(l10n.basicTier),
                  ),
                  DropdownMenuItem(
                    value: 'premium',
                    child: Text(l10n.premiumTier),
                  ),
                  DropdownMenuItem(
                    value: 'enterprise',
                    child: Text(l10n.enterpriseTier),
                  ),
                ],
                onChanged: (val) {
                  if (val != null) setState(() => _tier = val);
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
