import 'package:client_app/features/shell/presentation/widgets/admin_sidebar.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// **ScaffoldWithNav**
///
/// Responsive shell for the Admin interface.
/// Uses [AdminSidebar] for generic navigation on desktop/tablet.
/// Falls back to BottomNavigationBar for mobile.
class ScaffoldWithNav extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const ScaffoldWithNav({super.key, required this.navigationShell});

  @override
  Widget build(BuildContext context) {
    // Breakpoint: 800dp (More space for Admin dashboard)
    final isWideScreen = MediaQuery.sizeOf(context).width >= 800;
    final l10n = AppLocalizations.of(context)!;

    if (isWideScreen) {
      return Scaffold(
        body: Row(
          children: [
            AdminSidebar(
              selectedIndex: navigationShell.currentIndex,
              onDestinationSelected: (index) => _onItemTapped(context, index),
            ),
            const VerticalDivider(thickness: 1, width: 1),
            Expanded(child: navigationShell),
          ],
        ),
      );
    }

    return Scaffold(
      body: navigationShell,
      bottomNavigationBar: NavigationBar(
        selectedIndex: navigationShell.currentIndex,
        onDestinationSelected: (index) => _onItemTapped(context, index),
        destinations: [
          NavigationDestination(
            icon: const Icon(Icons.auto_graph_outlined),
            selectedIcon: const Icon(Icons.auto_graph),
            label: l10n.navStudio,
          ),
          NavigationDestination(
            icon: const Icon(Icons.schema_outlined),
            selectedIcon: const Icon(Icons.schema),
            label: l10n.navRegistry,
          ),
          NavigationDestination(
            icon: const Icon(Icons.analytics_outlined),
            selectedIcon: const Icon(Icons.analytics),
            label: l10n.navAnalytics,
          ),
          NavigationDestination(
            icon: const Icon(Icons.admin_panel_settings_outlined),
            selectedIcon: const Icon(Icons.admin_panel_settings),
            label: l10n.navAdmin,
          ),
        ],
      ),
    );
  }

  void _onItemTapped(BuildContext context, int index) {
    navigationShell.goBranch(
      index,
      initialLocation: index == navigationShell.currentIndex,
    );
  }
}
