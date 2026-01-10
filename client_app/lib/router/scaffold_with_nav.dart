import 'package:client_app/l10n/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// **Adaptive Navigation Scaffold**
///
/// Wraps the main application content with a responsive navigation structure.
///
/// **Behavior**:
/// - **Wide Screens (>= 600dp)**: Displays a [NavigationRail] on the left.
/// - **Narrow Screens (< 600dp)**: Displays a [NavigationBar] at the bottom.
///
/// **Design Rationale**:
/// - Adheres to Material 3 adaptive layout guidelines.
/// - Ensures optimal space usage on large screens (Quorum is data-heavy).
class ScaffoldWithNav extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const ScaffoldWithNav({super.key, required this.navigationShell});

  @override
  Widget build(BuildContext context) {
    // Breakpoint: 600dp (Standard M3 Mobile/Tablet boundary)
    // Breakpoint: 600dp (Standard M3 Mobile/Tablet boundary)
    final isWideScreen = MediaQuery.sizeOf(context).width >= 600;
    final l10n = AppLocalizations.of(context)!;
    return Scaffold(
      body:
          isWideScreen
              ? _WideScreenLayout(navigationShell: navigationShell)
              : navigationShell,
      bottomNavigationBar:
          isWideScreen
              ? null
              : NavigationBar(
                selectedIndex: navigationShell.currentIndex,
                onDestinationSelected: (index) => _onItemTapped(index, context),
                destinations: [
                  NavigationDestination(
                    icon: const Icon(Icons.dashboard_outlined),
                    selectedIcon: const Icon(Icons.dashboard),
                    label: l10n.navDashboard,
                  ),
                  NavigationDestination(
                    icon: const Icon(Icons.add_circle_outline),
                    selectedIcon: const Icon(Icons.add_circle),
                    label: l10n.newAnalysis,
                  ),
                  NavigationDestination(
                    icon: const Icon(Icons.settings_outlined),
                    selectedIcon: const Icon(Icons.settings),
                    label: l10n.navSettings,
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

  void _onItemTapped(int index, BuildContext context) {
    navigationShell.goBranch(
      index,
      initialLocation: index == navigationShell.currentIndex,
    );
  }
}

class _WideScreenLayout extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const _WideScreenLayout({required this.navigationShell});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Row(
      children: [
        NavigationRail(
          selectedIndex: navigationShell.currentIndex,
          onDestinationSelected: (index) {
            navigationShell.goBranch(
              index,
              initialLocation: index == navigationShell.currentIndex,
            );
          },
          // Use extended label type if very wide? For now, standard 'all' labels.
          labelType: NavigationRailLabelType.all,
          groupAlignment: -1.0, // Align to top
          destinations: [
            NavigationRailDestination(
              icon: const Icon(Icons.dashboard_outlined),
              selectedIcon: const Icon(Icons.dashboard),
              label: Text(l10n.navDashboard),
            ),
            NavigationRailDestination(
              icon: const Icon(Icons.add_circle_outline),
              selectedIcon: const Icon(Icons.add_circle),
              label: Text(l10n.newAnalysis),
            ),
            NavigationRailDestination(
              icon: const Icon(Icons.settings_outlined),
              selectedIcon: const Icon(Icons.settings),
              label: Text(l10n.navSettings),
            ),
            NavigationRailDestination(
              icon: const Icon(Icons.admin_panel_settings_outlined),
              selectedIcon: const Icon(Icons.admin_panel_settings),
              label: Text(l10n.navAdmin),
            ),
          ],
        ),
        const VerticalDivider(thickness: 1, width: 1),
        Expanded(child: navigationShell),
      ],
    );
  }
}
