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
    // Use AppLocalizations if available, or fallbacks if translations missing
    // Generic sidebar items (English defaults per instruction "English Only" for code/comments)


    return NavigationRail(
      selectedIndex: selectedIndex,
      onDestinationSelected: onDestinationSelected,
      labelType: NavigationRailLabelType.all,
      groupAlignment: -1.0,
      destinations: const [
        NavigationRailDestination(
          icon: Icon(Icons.auto_graph_outlined),
          selectedIcon: Icon(Icons.auto_graph),
          label: Text('Studio'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.schema_outlined),
          selectedIcon: Icon(Icons.schema),
          label: Text('Registry'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.analytics_outlined),
          selectedIcon: Icon(Icons.analytics),
          label: Text('Analytics'),
        ),
        NavigationRailDestination(
          icon: Icon(Icons.admin_panel_settings_outlined),
          selectedIcon: Icon(Icons.admin_panel_settings),
          label: Text('Admin'),
        ),
      ],
    );
  }
}
