import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/auth/presentation/auth_controller.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

/// **Adaptive Navigation Scaffold**
///
/// Wraps the main application content with a responsive navigation structure.
///
/// **Behavior**:
/// - **Medium/Large Screens (>= 800dp)**: Displays a [NavigationRail] on the left.
/// - **Small Screens (< 800dp)**: Displays a [NavigationBar] at the bottom.
///
/// **Design Rationale**:
/// - Adheres to the Quorum Macro-Breakpoint standard via local [LayoutBuilder].
/// - Ensures optimal space usage on large screens (Quorum is data-heavy).
class ScaffoldWithNav extends ConsumerWidget {
  final StatefulNavigationShell navigationShell;

  const ScaffoldWithNav({super.key, required this.navigationShell});

  static const double _wideScreenBreakpoint = 800.0;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final l10n = AppLocalizations.of(context)!;

    // Evaluate Admin Role via Dart 3 pattern matching
    final authState = ref.watch(authControllerProvider);
    final isAdmin = switch (authState) {
      AsyncData(:final value) =>
        value != null &&
            (value.role == UserRole.root || value.role == UserRole.admin),
      AsyncLoading() || AsyncError() => false,
    };

    return LayoutBuilder(
      builder: (context, constraints) {
        final isWideScreen = constraints.maxWidth >= _wideScreenBreakpoint;

        return Scaffold(
          body: isWideScreen
              ? _WideScreenLayout(
                  navigationShell: navigationShell,
                  isAdmin: isAdmin,
                  onDestinationSelected: (index) =>
                      _onItemTapped(index, context, isAdmin),
                )
              : navigationShell,
          bottomNavigationBar: isWideScreen
              ? null
              : NavigationBar(
                  selectedIndex: navigationShell.currentIndex,
                  onDestinationSelected: (index) =>
                      _onItemTapped(index, context, isAdmin),
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
                    if (isAdmin)
                      NavigationDestination(
                        icon: const Icon(Icons.admin_panel_settings_outlined),
                        selectedIcon: const Icon(Icons.admin_panel_settings),
                        label: l10n.navAdmin,
                      ),
                  ],
                ),
        );
      },
    );
  }

  void _onItemTapped(int index, BuildContext context, bool isAdmin) {
    // If isAdmin is true, the Admin link is at index 3.
    if (isAdmin && index == 3) {
      context.go('/admin');
      return;
    }

    navigationShell.goBranch(
      index,
      initialLocation: index == navigationShell.currentIndex,
    );
  }
}

class _WideScreenLayout extends StatelessWidget {
  final StatefulNavigationShell navigationShell;
  final bool isAdmin;
  final ValueChanged<int> onDestinationSelected;

  const _WideScreenLayout({
    required this.navigationShell,
    required this.isAdmin,
    required this.onDestinationSelected,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Row(
      children: [
        NavigationRail(
          selectedIndex: navigationShell.currentIndex,
          onDestinationSelected: onDestinationSelected,
          labelType: NavigationRailLabelType.all,
          groupAlignment: -1.0,
          destinations: [
            NavigationRailDestination(
              icon: const Icon(Icons.dashboard_outlined),
              selectedIcon: const Icon(Icons.dashboard),
              label: Text(l10n.navDashboard, overflow: TextOverflow.ellipsis),
            ),
            NavigationRailDestination(
              icon: const Icon(Icons.add_circle_outline),
              selectedIcon: const Icon(Icons.add_circle),
              label: Text(l10n.newAnalysis, overflow: TextOverflow.ellipsis),
            ),
            NavigationRailDestination(
              icon: const Icon(Icons.settings_outlined),
              selectedIcon: const Icon(Icons.settings),
              label: Text(l10n.navSettings, overflow: TextOverflow.ellipsis),
            ),
            if (isAdmin)
              NavigationRailDestination(
                icon: const Icon(Icons.admin_panel_settings_outlined),
                selectedIcon: const Icon(Icons.admin_panel_settings),
                label: Text(l10n.navAdmin, overflow: TextOverflow.ellipsis),
              ),
          ],
        ),
        const VerticalDivider(thickness: 1, width: 1),
        Expanded(child: navigationShell),
      ],
    );
  }
}
