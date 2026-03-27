import 'package:flutter/material.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

class AdminSidebar extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onDestinationSelected;

  const AdminSidebar({
    super.key,
    required this.selectedIndex,
    required this.onDestinationSelected,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return NavigationRail(
      selectedIndex: selectedIndex,
      onDestinationSelected: onDestinationSelected,
      labelType: NavigationRailLabelType.all,
      groupAlignment: -1.0,
      destinations: [
        NavigationRailDestination(
          icon: const Icon(Icons.auto_graph_outlined),
          selectedIcon: const Icon(Icons.auto_graph),
          label: Text(l10n.navStudio),
        ),
        NavigationRailDestination(
          icon: const Icon(Icons.schema_outlined),
          selectedIcon: const Icon(Icons.schema),
          label: Text(l10n.navRegistry),
        ),
        NavigationRailDestination(
          icon: const Icon(Icons.analytics_outlined),
          selectedIcon: const Icon(Icons.analytics),
          label: Text(l10n.navAnalytics),
        ),
        NavigationRailDestination(
          icon: const Icon(Icons.admin_panel_settings_outlined),
          selectedIcon: const Icon(Icons.admin_panel_settings),
          label: Text(l10n.navAdmin),
        ),
        NavigationRailDestination(
          icon: const Icon(Icons.api_outlined),
          selectedIcon: const Icon(Icons.api),
          label: Text(l10n.navSystemInspector),
        ),
      ],
    );
  }
}
