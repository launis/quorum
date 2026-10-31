import 'package:client_app/features/shell/presentation/widgets/admin_sidebar.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// **ScaffoldWithNav**
///
/// Responsive shell for the Admin interface.
/// Uses [AdminSidebar] for generic navigation on desktop/tablet (>= 800dp).
/// Renders [NavigationBar] on narrow viewports (< 800dp).
class ScaffoldWithNav extends StatelessWidget {
  final StatefulNavigationShell navigationShell;

  const ScaffoldWithNav({super.key, required this.navigationShell});

  static const double _wideScreenBreakpoint = 800.0;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return LayoutBuilder(
      builder: (context, constraints) {
        final isWideScreen = constraints.maxWidth >= _wideScreenBreakpoint;

        if (isWideScreen) {
          return Scaffold(
            body: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                AdminSidebar(
                  selectedIndex: navigationShell.currentIndex,
                  onDestinationSelected: (index) =>
                      _onItemTapped(context, index),
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
              NavigationDestination(
                icon: const Icon(Icons.api_outlined),
                selectedIcon: const Icon(Icons.api),
                label: l10n.navSystemInspector,
              ),
            ],
          ),
        );
      },
    );
  }

  void _onItemTapped(BuildContext context, int index) {
    navigationShell.goBranch(
      index,
      initialLocation: index == navigationShell.currentIndex,
    );
  }
}
