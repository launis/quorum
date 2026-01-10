import 'package:flutter/material.dart';
import 'package:client_app/l10n/app_localizations.dart';

class OrganizationListScreen extends StatelessWidget {
  const OrganizationListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      appBar: AppBar(title: Text(l10n.organizationManagementTitle)),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1000),
          child: Text(l10n.organizationListPlaceholder),
        ),
      ),
    );
  }
}
