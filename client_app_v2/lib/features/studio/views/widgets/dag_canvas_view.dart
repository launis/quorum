import 'package:flutter/material.dart';
import 'package:client_app/utils/safe_cast.dart';

/// InteractiveViewer 2D Canvas for Workflow DAGs
class DagCanvasView extends StatefulWidget {
  final Map<String, dynamic> workflow;
  final Function(String stepId) onNodeSelected;
  final Function(Map<String, dynamic> updatedWorkflow) onWorkflowUpdated;

  const DagCanvasView({
    super.key,
    required this.workflow,
    required this.onNodeSelected,
    required this.onWorkflowUpdated,
  });

  @override
  State<DagCanvasView> createState() => _DagCanvasViewState();
}

class _DagCanvasViewState extends State<DagCanvasView> {
  final TransformationController _transformationController =
      TransformationController();

  Map<String, dynamic> get _workflow => widget.workflow;

  void _updateNodePosition(String stepId, double x, double y) {
    final steps = SafeCast.safeList(_workflow['steps']);
    for (int i = 0; i < steps.length; i++) {
      final step = SafeCast.safeMap(steps[i]);
      if (step['id'] == stepId) {
        step['ui_pos_x'] = x;
        step['ui_pos_y'] = y;
        steps[i] = step;
        break;
      }
    }

    final updated = Map<String, dynamic>.from(_workflow);
    updated['steps'] = steps;
    widget.onWorkflowUpdated(updated);
  }

  @override
  Widget build(BuildContext context) {
    final steps = SafeCast.safeList(_workflow['steps']);

    return LayoutBuilder(
      builder: (context, constraints) {
        return Scaffold(
          body: InteractiveViewer(
            transformationController: _transformationController,
            constrained: false, // Infinite Canvas
            minScale: 0.1,
            maxScale: 2.0,
            boundaryMargin: const EdgeInsets.all(4000), // Very large boundary
            child: SizedBox(
              width: 8000,
              height: 8000,
              child: Stack(
                clipBehavior: Clip.none,
                children: [
                  // TODO: Draw Edges (CustomPaint) based on depends_on

                  // Draw Nodes
                  ...steps.map((rawStep) {
                    final step = SafeCast.safeMap(rawStep);
                    final stepId = SafeCast.safeString(step['id']);
                    final double posX = SafeCast.safeDouble(
                      step['ui_pos_x'],
                      4000.0,
                    );
                    final double posY = SafeCast.safeDouble(
                      step['ui_pos_y'],
                      4000.0,
                    );

                    return Positioned(
                      left: posX,
                      top: posY,
                      child: GestureDetector(
                        onTap: () => widget.onNodeSelected(stepId),
                        onPanUpdate: (details) {
                          _updateNodePosition(
                            stepId,
                            posX + details.delta.dx,
                            posY + details.delta.dy,
                          );
                        },
                        child: _DagNodeWidget(
                          stepId: stepId,
                          blueprintId: SafeCast.safeString(
                            step['task_blueprint'],
                          ),
                        ),
                      ),
                    );
                  }),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

class _DagNodeWidget extends StatelessWidget {
  final String stepId;
  final String blueprintId;

  const _DagNodeWidget({required this.stepId, required this.blueprintId});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 200,
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Theme.of(context).colorScheme.outline),
        boxShadow: [
          BoxShadow(
            color: Theme.of(context).colorScheme.surfaceContainer,
            blurRadius: 10,
            offset: Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.hub,
                size: 16,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  stepId,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Blueprint: ${blueprintId.isNotEmpty ? blueprintId : "Unassigned"}',
            style: TextStyle(
              fontSize: 12,
              color: Theme.of(context).colorScheme.onSurfaceVariant,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
