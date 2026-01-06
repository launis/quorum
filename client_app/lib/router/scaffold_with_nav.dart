import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// **Adaptive Navigation Scaffold**
///
/// Wraps the main application content with a responsive navigation structure.
///
/// **Behavior**:
/// - **Desktop (> 900px)**: Displays a [NavigationRail] on the left.
/// - **Mobile (< 900px)**: Displays a [BottomNavigationBar].
///
/// **Design Rationale**:
/// - Adheres to Material 3 adaptive layout guidelines.
/// - Ensures optimal space usage on large screens (Quorum is data-heavy).
class ScaffoldWithNav extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const ScaffoldWithNav({super.key, required this.navigationShell});

  @override
  Widget build(BuildContext context) {
    // Breakpoint: 900px (Tablet/Desktop boundary)
    final isDesktop = MediaQuery.of(context).size.width > 900;

    return Scaffold(
      body:
          isDesktop
              ? _DesktopLayout(navigationShell: navigationShell)
              : navigationShell,
      bottomNavigationBar:
          isDesktop
              ? null
              : NavigationBar(
                selectedIndex: navigationShell.currentIndex,
                onDestinationSelected: (index) => _onItemTapped(index, context),
                destinations: const [
                  NavigationDestination(
                    icon: Icon(Icons.dashboard_outlined),
                    selectedIcon: Icon(Icons.dashboard),
                    label: 'Dashboard',
                  ),
                  NavigationDestination(
                    icon: Icon(Icons.admin_panel_settings_outlined),
                    selectedIcon: Icon(Icons.admin_panel_settings),
                    label: 'Admin',
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

class _DesktopLayout extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const _DesktopLayout({required this.navigationShell});

  @override
  Widget build(BuildContext context) {
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
          labelType: NavigationRailLabelType.all,
          destinations: const [
            NavigationRailDestination(
              icon: Icon(Icons.dashboard_outlined),
              selectedIcon: Icon(Icons.dashboard),
              label: Text('Dashboard'),
            ),
            NavigationRailDestination(
              icon: Icon(Icons.admin_panel_settings_outlined),
              selectedIcon: Icon(Icons.admin_panel_settings),
              label: Text('Admin'),
            ),
          ],
        ),
        const VerticalDivider(thickness: 1, width: 1),
        Expanded(child: navigationShell),
      ],
    );
  }
}
