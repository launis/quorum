import 'package:flutter/material.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/theme/app_spacing.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/l10n/gen/app_localizations.dart';

const double _kCanvasDimension = 8000.0;
const double _kCanvasDefaultCoord = 4000.0;
const double _kMinScale = 0.1;
const double _kMaxScale = 2.0;
const double _kNodeWidth = 200.0;
const double _kNodeEstimatedHeight = 72.0;
const double _kNodeIconSize = 16.0;
const double _kNodeBlurRadius = 10.0;
const double _kEdgeStrokeWidth = 2.0;
const EdgeInsets _kCanvasBoundaryMargin = EdgeInsets.all(_kCanvasDefaultCoord);

/// Interactive 2D canvas for visualizing and positioning Workflow DAG step nodes.
class DagCanvasView extends StatefulWidget {
  final Workflow workflow;
  final ValueChanged<String> onNodeSelected;
  final ValueChanged<Workflow> onWorkflowUpdated;

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

  Workflow get _workflow => widget.workflow;

  @override
  void dispose() {
    _transformationController.dispose();
    super.dispose();
  }

  static double _resolveCoord(double rawCoord) {
    return rawCoord == 0.0 ? _kCanvasDefaultCoord : rawCoord;
  }

  void _updateNodePosition(String stepId, double x, double y) {
    const double maxAllowedCoord = _kCanvasDimension - _kNodeWidth;
    final double clampedX = x.clamp(0.0, maxAllowedCoord);
    final double clampedY = y.clamp(0.0, maxAllowedCoord);

    final List<StepRule> updatedSteps = _workflow.steps.map((StepRule step) {
      if (step.id == stepId) {
        return step.copyWith(uiPosX: clampedX, uiPosY: clampedY);
      }
      return step;
    }).toList();

    widget.onWorkflowUpdated(_workflow.copyWith(steps: updatedSteps));
  }

  void _validateWorkflowInvariants(Workflow workflow) {
    if (workflow.id.trim().isEmpty) {
      throw AppException.validation(
        'Fail-Fast: Workflow ID cannot be empty in DagCanvasView.',
      );
    }
    for (final StepRule step in workflow.steps) {
      if (step.id.trim().isEmpty) {
        throw AppException.validation(
          'Fail-Fast: Step ID cannot be empty in DagCanvasView.',
        );
      }
      if (!step.uiPosX.isFinite ||
          !step.uiPosY.isFinite ||
          step.uiPosX < 0.0 ||
          step.uiPosY < 0.0 ||
          step.uiPosX > _kCanvasDimension ||
          step.uiPosY > _kCanvasDimension) {
        throw AppException.validation(
          'Fail-Fast: Step ${step.id} has out-of-bounds or non-finite canvas coordinates (${step.uiPosX}, ${step.uiPosY}).',
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    _validateWorkflowInvariants(_workflow);

    final List<StepRule> steps = _workflow.steps;
    final ThemeData theme = Theme.of(context);

    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints constraints) {
        return Scaffold(
          body: InteractiveViewer(
            transformationController: _transformationController,
            constrained: false,
            minScale: _kMinScale,
            maxScale: _kMaxScale,
            boundaryMargin: _kCanvasBoundaryMargin,
            child: SizedBox(
              width: _kCanvasDimension,
              height: _kCanvasDimension,
              child: Stack(
                clipBehavior: Clip.none,
                children: <Widget>[
                  Positioned.fill(
                    child: CustomPaint(
                      painter: _DagEdgesPainter(
                        steps: steps,
                        edgeColor: theme.colorScheme.outlineVariant,
                      ),
                    ),
                  ),
                  ...steps.map((StepRule step) {
                    final String stepId = step.id;
                    final double posX = _resolveCoord(step.uiPosX);
                    final double posY = _resolveCoord(step.uiPosY);

                    return Positioned(
                      key: ValueKey<String>('dag_node_pos_$stepId'),
                      left: posX,
                      top: posY,
                      child: FocusableActionDetector(
                        key: ValueKey<String>('dag_node_focus_$stepId'),
                        mouseCursor: SystemMouseCursors.click,
                        actions: <Type, Action<Intent>>{
                          ActivateIntent: CallbackAction<ActivateIntent>(
                            onInvoke: (ActivateIntent intent) {
                              widget.onNodeSelected(stepId);
                              return null;
                            },
                          ),
                        },
                        child: GestureDetector(
                          key: ValueKey<String>('dag_node_gesture_$stepId'),
                          onTap: () => widget.onNodeSelected(stepId),
                          onPanUpdate: (DragUpdateDetails details) {
                            _updateNodePosition(
                              stepId,
                              posX + details.delta.dx,
                              posY + details.delta.dy,
                            );
                          },
                          child: _DagNodeWidget(
                            stepId: stepId,
                            blueprintId: step.taskBlueprint,
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

class _DagEdgesPainter extends CustomPainter {
  final List<StepRule> steps;
  final Color edgeColor;

  const _DagEdgesPainter({required this.steps, required this.edgeColor});

  @override
  void paint(Canvas canvas, Size size) {
    if (steps.length < 2) {
      return;
    }

    final Map<String, Offset> nodeCenters = <String, Offset>{
      for (final StepRule step in steps)
        step.id: Offset(
          _DagCanvasViewState._resolveCoord(step.uiPosX) + (_kNodeWidth / 2.0),
          _DagCanvasViewState._resolveCoord(step.uiPosY) +
              (_kNodeEstimatedHeight / 2.0),
        ),
    };

    final Paint paint = Paint()
      ..color = edgeColor
      ..strokeWidth = _kEdgeStrokeWidth
      ..style = PaintingStyle.stroke;

    for (final StepRule step in steps) {
      final Offset? targetCenter = nodeCenters[step.id];
      if (targetCenter == null) {
        continue;
      }
      for (final String depId in step.dependsOn) {
        final Offset? sourceCenter = nodeCenters[depId];
        if (sourceCenter != null) {
          canvas.drawLine(sourceCenter, targetCenter, paint);
        }
      }
    }
  }

  @override
  bool shouldRepaint(covariant _DagEdgesPainter oldDelegate) {
    return oldDelegate.edgeColor != edgeColor || oldDelegate.steps != steps;
  }
}

class _DagNodeWidget extends StatelessWidget {
  final String stepId;
  final String blueprintId;

  const _DagNodeWidget({required this.stepId, required this.blueprintId});

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    final AppLocalizations l10n = AppLocalizations.of(context)!;
    final String resolvedBlueprint = blueprintId.trim().isNotEmpty
        ? blueprintId
        : l10n.studioViewsNone;
    final String blueprintLabel =
        '${l10n.studioWorkflowTaskProfileTitle}: $resolvedBlueprint';

    return Container(
      width: _kNodeWidth,
      padding: AppSpacing.p12,
      decoration: BoxDecoration(
        color: theme.cardColor,
        borderRadius: BorderRadius.circular(AppSpacing.s12),
        border: Border.all(color: theme.colorScheme.outline),
        boxShadow: <BoxShadow>[
          BoxShadow(
            color: theme.colorScheme.surfaceContainer,
            blurRadius: _kNodeBlurRadius,
            offset: const Offset(0, AppSpacing.s4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Row(
            children: <Widget>[
              Icon(
                Icons.hub,
                size: _kNodeIconSize,
                color: theme.colorScheme.onSurfaceVariant,
              ),
              AppSpacing.w8,
              Expanded(
                child: Text(
                  stepId,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
          AppSpacing.h8,
          Text(
            blueprintLabel,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.onSurfaceVariant,
            ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ),
    );
  }
}
