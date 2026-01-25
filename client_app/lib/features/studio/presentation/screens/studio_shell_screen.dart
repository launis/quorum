import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

/// **Studio Shell Screen**
///
/// The dedicated layout shell for the "Cognitive Studio" (Admin Workspace).
/// Provides navigation between:
/// - Workflows (/studio/workflows)
/// - Prompts (/studio/prompts)
/// - Ontology (/studio/ontology)
///
/// **Design**:
/// - Distinctive 'Surface Variant' background or subtle tint to differentiate from the Main App.
/// - NavigationRail (Desktop) / NavigationBar (Mobile).
class StudioShellScreen extends StatelessWidget {
  final Widget child;

  const StudioShellScreen({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    // Destinations
    final destinations = [
      (
        icon: Icons.schema_outlined,
        selectedIcon: Icons.schema,
        label: 'Workflows',
        path: '/studio/workflows',
      ),
      (
        icon: Icons.chat_bubble_outline,
        selectedIcon: Icons.chat_bubble,
        label: 'Prompts',
        path: '/studio/prompts',
      ),
      (
        icon: Icons.category_outlined,
        selectedIcon: Icons.category,
        label: 'Ontology',
        path: '/studio/ontology',
      ),
    ];

    // Calculate selected index
    final String location = GoRouterState.of(context).uri.toString();
    int selectedIndex = destinations.indexWhere(
      (d) => location.startsWith(d.path),
    );

    // Fallback/Default
    if (selectedIndex == -1) {
      if (location == '/studio') {
        selectedIndex = 0; // Default to Workflows
      } else {
        selectedIndex = 0;
      }
    }

    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth >= 600;
        final theme = Theme.of(context);

        // Studio Branding: Use a slightly tinted background or surface
        final backgroundColor = theme.colorScheme.surfaceContainerLow;

        if (isWide) {
          return Scaffold(
            backgroundColor: backgroundColor,
            body: Row(
              children: [
                NavigationRail(
                  backgroundColor: theme.colorScheme.surface,
                  selectedIndex: selectedIndex,
                  onDestinationSelected:
                      (index) => context.go(destinations[index].path),
                  labelType: NavigationRailLabelType.all,
                  destinations:
                      destinations.map((d) {
                        return NavigationRailDestination(
                          icon: Icon(d.icon),
                          selectedIcon: Icon(d.selectedIcon),
                          label: Text(d.label),
                        );
                      }).toList(),
                  // Add a "Back to App" or Logo header if needed
                  leading: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 24.0),
                    child: Icon(
                      Icons.auto_awesome,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                ),
                VerticalDivider(
                  thickness: 1,
                  width: 1,
                  color: theme.colorScheme.outlineVariant,
                ),
                Expanded(
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 1400),
                      child: child,
                    ),
                  ),
                ),
              ],
            ),
          );
        } else {
          return Scaffold(
            backgroundColor: backgroundColor,
            body: SafeArea(child: child),
            bottomNavigationBar: NavigationBar(
              selectedIndex: selectedIndex,
              onDestinationSelected:
                  (index) => context.go(destinations[index].path),
              destinations:
                  destinations.map((d) {
                    return NavigationDestination(
                      icon: Icon(d.icon),
                      selectedIcon: Icon(d.selectedIcon),
                      label: d.label,
                    );
                  }).toList(),
            ),
          );
        }
      },
    );
  }
}
