import 'package:client_app/features/studio/presentation/screens/workflow_studio_screen.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class StudioRoute extends GoRouteData {
  const StudioRoute();

  @override
  Widget build(BuildContext context, GoRouterState state) =>
      const WorkflowStudioScreen();
}
