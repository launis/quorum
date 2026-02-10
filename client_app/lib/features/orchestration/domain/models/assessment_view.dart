import 'package:freezed_annotation/freezed_annotation.dart';

part 'assessment_view.freezed.dart';
part 'assessment_view.g.dart';

@freezed
abstract class AssessmentView with _$AssessmentView {
  const factory AssessmentView({
    required String sessionId,
    required String statusLabel,      // e.g. "Analysoidaan..."
    required String uiVariant,        // "default", "warning", "error"
    required String statusMessage,    // Contextual help text
    required bool showWarningBanner,  // Toggle for warning UI
    @Default([]) List<StepProgressItem> steps, // Progress indicators
    int? finalScore,                  // Nullable
  }) = _AssessmentView;

  factory AssessmentView.fromJson(Map<String, dynamic> json) => _$AssessmentViewFromJson(json);
}

@freezed
abstract class StepProgressItem with _$StepProgressItem {
  const factory StepProgressItem({
    required String id,
    required String label,
    required String status, // "pending", "running", "completed", "failed"
  }) = _StepProgressItem;

  factory StepProgressItem.fromJson(Map<String, dynamic> json) => _$StepProgressItemFromJson(json);
}
