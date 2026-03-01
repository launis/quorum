import 'dart:convert';
import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shared_preferences/shared_preferences.dart';

part 'reflection_form_controller.freezed.dart';
part 'reflection_form_controller.g.dart';

enum ReflectionInputMode { guided, text, file }

@freezed
abstract class ReflectionFormState with _$ReflectionFormState {
  const factory ReflectionFormState({
    @Default(ReflectionInputMode.guided) ReflectionInputMode inputMode,
    @Default('') String q1Goal,
    @Default('') String q2Falsification,
    @Default('') String q3Synthesis,
    @Default('') String q4Argumentation,
    @Default('') String freeText,
  }) = _ReflectionFormState;

  factory ReflectionFormState.fromJson(Map<String, dynamic> json) =>
      _$ReflectionFormStateFromJson(json);
}

@riverpod
class ReflectionFormController extends _$ReflectionFormController {
  static const _prefsKey = 'autosave_reflection_form_state';
  final _prefs = SharedPreferencesAsync();

  @override
  FutureOr<ReflectionFormState> build() async {
    return _loadState();
  }

  Future<ReflectionFormState> _loadState() async {
    try {
      final savedStr = await _prefs.getString(_prefsKey);
      if (savedStr != null) {
        final json = jsonDecode(savedStr) as Map<String, dynamic>;
        return ReflectionFormState.fromJson(json);
      }
    } catch (e) {
      // Ignore parsing errors and return default
    }
    return const ReflectionFormState();
  }

  void setMode(ReflectionInputMode mode) {
    if (state.value?.inputMode == mode) return;
    state = AsyncValue.data(state.value!.copyWith(inputMode: mode));
    _autosave();
  }

  void setQ1Goal(String valueStr) {
    state = AsyncValue.data(state.value!.copyWith(q1Goal: valueStr));
    _autosave();
  }

  void setQ2Falsification(String valueStr) {
    state = AsyncValue.data(state.value!.copyWith(q2Falsification: valueStr));
    _autosave();
  }

  void setQ3Synthesis(String valueStr) {
    state = AsyncValue.data(state.value!.copyWith(q3Synthesis: valueStr));
    _autosave();
  }

  void setQ4Argumentation(String valueStr) {
    state = AsyncValue.data(state.value!.copyWith(q4Argumentation: valueStr));
    _autosave();
  }

  void setFreeText(String valueStr) {
    state = AsyncValue.data(state.value!.copyWith(freeText: valueStr));
    _autosave();
  }

  Future<void> _autosave() async {
    final currentState = state.value;
    if (currentState == null) return;
    try {
      final jsonStr = jsonEncode(currentState.toJson());
      await _prefs.setString(_prefsKey, jsonStr);
    } catch (e) {
      // Ignore autosave errors
    }
  }

  Future<void> clear() async {
    state = const AsyncValue.data(ReflectionFormState());
    await _prefs.remove(_prefsKey);
  }
}
