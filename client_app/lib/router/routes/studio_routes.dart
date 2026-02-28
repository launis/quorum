import 'package:client_app/features/studio/presentation/screens/workflow_studio_screen.dart';
import 'package:client_app/features/knowledge_base/view/ingestion_view.dart';
import 'package:client_app/features/studio/presentation/screens/studio_dashboard_screen.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

part 'studio_routes.g.dart';

@TypedGoRoute<StudioDashboardRoute>(
  path: '/studio',
  routes: [
    TypedGoRoute<StudioWorkflowsRoute>(path: 'workflows'),
    TypedGoRoute<StudioMatricesRoute>(path: 'matrices'),
    TypedGoRoute<StudioStepsRoute>(path: 'steps'),
    TypedGoRoute<StudioComponentsRoute>(path: 'components'),
    TypedGoRoute<StudioKnowledgeRoute>(path: 'knowledge'),
  ],
)
class StudioDashboardRoute extends GoRouteData with $StudioDashboardRoute {
  const StudioDashboardRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) {
    return const StudioDashboardScreen();
  }
}

class StudioWorkflowsRoute extends GoRouteData with $StudioWorkflowsRoute {
  const StudioWorkflowsRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const WorkflowStudioScreen(initialTabIndex: 0);
}

class StudioMatricesRoute extends GoRouteData with $StudioMatricesRoute {
  const StudioMatricesRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const WorkflowStudioScreen(initialTabIndex: 1);
}

class StudioStepsRoute extends GoRouteData with $StudioStepsRoute {
  const StudioStepsRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const WorkflowStudioScreen(initialTabIndex: 2);
}

class StudioComponentsRoute extends GoRouteData with $StudioComponentsRoute {
  const StudioComponentsRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const WorkflowStudioScreen(initialTabIndex: 3);
}

class StudioKnowledgeRoute extends GoRouteData with $StudioKnowledgeRoute {
  const StudioKnowledgeRoute();
  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const IngestionView();
}
