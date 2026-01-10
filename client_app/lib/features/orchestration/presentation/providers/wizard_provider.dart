import 'package:client_app/features/orchestration/presentation/providers/execution_controller.dart';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'wizard_provider.freezed.dart';
part 'wizard_provider.g.dart';

@freezed
abstract class WizardStateModel with _$WizardStateModel {
  const factory WizardStateModel({
    @Default(0) int currentStep,
    @Default('audit_workflow_v1') String selectedWorkflowId,
    @Default({}) Map<String, dynamic> inputs,
    @Default(false) bool isSubmitting,
    String? error,
  }) = _WizardStateModel;
}

@riverpod
class WizardState extends _$WizardState {
  @override
  WizardStateModel build() {
    return const WizardStateModel();
  }

  void setStep(int step) {
    state = state.copyWith(currentStep: step);
  }

  void selectWorkflow(String workflowId) {
    state = state.copyWith(selectedWorkflowId: workflowId);
  }

  void updateInput(String key, dynamic value) {
    final newInputs = Map<String, dynamic>.from(state.inputs);
    if (value == null || (value is String && value.isEmpty)) {
      newInputs.remove(key);
    } else {
      newInputs[key] = value;
    }
    state = state.copyWith(inputs: newInputs);
  }

  void setSubmitting(bool value) {
    state = state.copyWith(isSubmitting: value);
  }

  void setError(String? error) {
    state = state.copyWith(error: error);
  }

  bool validateInputs() {
    return state.inputs.isNotEmpty;
  }

  Future<String?> submitAnalysis() async {
    if (!validateInputs()) {
      return null;
    }

    state = state.copyWith(isSubmitting: true, error: null);

    try {
      final executionId = await ref
          .read(executionControllerProvider.notifier)
          .startAnalysis(
            workflowId: state.selectedWorkflowId,
            inputs: state.inputs,
          );
      return executionId;
    } catch (e) {
      state = state.copyWith(error: e.toString());
      return null;
    } finally {
      state = state.copyWith(isSubmitting: false);
    }
  }

  void reset() {
    state = const WizardStateModel();
  }
}
