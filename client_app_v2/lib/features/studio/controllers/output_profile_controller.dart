import 'package:client_app/core/utils/safe_isolate.dart';
import 'dart:async';
import 'dart:convert';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/utils/riverpod_extensions.dart';

import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/shared/models/i18n_text.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:client_app/theme/app_durations.dart';

part 'output_profile_controller.g.dart';

// --- Controllers ---

/// Controller managing Studio Output Profiles using Strict Freezed models.
/// Implements Optimistic UI principles where possible.
@riverpod
class OutputProfilesController extends _$OutputProfilesController {
  @override
  FutureOr<List<OutputProfile>> build() async {
    ref.cacheFor(AppDurations.cacheTimeout);
    return _fetchProfiles();
  }

  Future<List<OutputProfile>> _fetchProfiles() async {
    final client = ref.read(studioClientProvider);
    final rawList = await client.getOutputProfiles();
    return safeIsolateRun(
      () => rawList.map((e) => OutputProfile.fromJson(e)).toList(),
    );
  }

  /// Refreshes the profiles list from the backend.
  Future<void> refresh() async {
    state = const AsyncValue.loading();
    try {
      final newProfiles = await _fetchProfiles();
      state = AsyncValue.data(newProfiles);
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('OutputProfilesController', 'Refresh failed', e, st);
      state = AsyncValue.error(e, st);
    }
  }

  /// Saves a profile utilizing Optimistic Updates.
  Future<OutputProfile> saveProfile(String id, OutputProfile payload) async {
    final previousState = state;
    OutputProfile returnData =
        payload; // Assuming payload already has ID initialized or preserved

    // 1. Optimistic Update
    if (state.hasValue && state.value != null) {
      final currentList = List<OutputProfile>.from(state.value!);
      final index = currentList.indexWhere((m) => m.id == id);

      if (index >= 0) {
        currentList[index] = payload;
      } else {
        currentList.add(payload);
      }
      state = AsyncValue.data(currentList);
    }

    try {
      // 2. Network Call
      final client = ref.read(studioClientProvider);
      final rawResponse = await client.saveOutputProfile(id, payload.toJson());
      final verifiedProfile = await safeIsolateRun(
        () => OutputProfile.fromJson(rawResponse),
      );

      // 3. Confirm with Actual Data
      if (state.hasValue && state.value != null) {
        final currentList = List<OutputProfile>.from(state.value!);
        final index = currentList.indexWhere((m) => m.id == id);
        if (index >= 0) {
          currentList[index] = verifiedProfile;
          state = AsyncValue.data(currentList);
        }
        returnData = verifiedProfile;
      }
      return returnData;
    } catch (e, st) {
      // 4. Rollback on Failure
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('OutputProfilesController', 'Save failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Deletes a profile.
  Future<void> deleteProfile(String id) async {
    try {
      final client = ref.read(studioClientProvider);
      await client.deleteOutputProfile(id);

      if (state.hasValue && state.value != null) {
        final currentList = List<OutputProfile>.from(state.value!);
        currentList.removeWhere((m) => m.id == id);
        state = AsyncValue.data(currentList);
      }
    } catch (e, st) {
      ref
          .read(loggerServiceProvider)
          .error('OutputProfilesController', 'Delete failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Clones an Output Profile utilizing Optimistic UI.
  Future<OutputProfile> cloneProfile(String id) async {
    final previousState = state;
    try {
      // 1. Network Call
      final client = ref.read(studioClientProvider);
      final rawProfile = await client.cloneOutputProfile(id);
      final clonedProfile = await safeIsolateRun(
        () => OutputProfile.fromJson(rawProfile),
      );

      // 2. Update State
      if (state.hasValue && state.value != null) {
        final currentList = List<OutputProfile>.from(state.value!);
        currentList.insert(0, clonedProfile); // prepend for visibility
        state = AsyncValue.data(currentList);
      }
      return clonedProfile;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('OutputProfilesController', 'Clone failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }

  /// Creates a draft Output Profile via the SSoT backend.
  Future<OutputProfile> createOutputProfileDraft() async {
    final previousState = state;
    try {
      final client = ref.read(studioClientProvider);
      final rawProfile = await client.createOutputProfileDraft();
      final draftProfile = await safeIsolateRun(
        () => OutputProfile.fromJson(rawProfile),
      );

      if (state.hasValue && state.value != null) {
        final currentList = List<OutputProfile>.from(state.value!);
        currentList.insert(0, draftProfile);
        state = AsyncValue.data(currentList);
      }
      return draftProfile;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('OutputProfilesController', 'Create draft failed', e, st);
      if (e is DioException && e.error is AppException) throw e.error!;
      throw AppException.unknown(e);
    }
  }
}

/// Fetches a single Output Profile natively by ID
@riverpod
Future<OutputProfile> outputProfileById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  final rawData = await client.getOutputProfile(id);
  return safeIsolateRun(() => OutputProfile.fromJson(rawData));
}

// --- Gold Standard Form State (Flat MVC) ---

@riverpod
class OutputProfileForm extends _$OutputProfileForm {
  @override
  FutureOr<OutputProfile> build(String configId) async {
    final profile = await ref.watch(outputProfileByIdProvider(configId).future);
    final str = jsonEncode(profile.toJson());
    return safeIsolateRun(() => OutputProfile.fromJson(jsonDecode(str)));
  }

  void forceRebuild() {
    final payload = state.value;
    if (payload != null) {
      // Deep copy is handled by Freezed copyWith inherently, but we trigger notify
      state = AsyncData(payload.copyWith());
    }
  }

  void updatePayload(OutputProfile payload) {
    state = AsyncData(payload);
  }

  Future<void> submit(OutputProfile updatedData) async {
    state = const AsyncLoading();

    state = await AsyncValue.guard(() async {
      final idToSave = updatedData.id.isNotEmpty ? updatedData.id : configId;
      if (idToSave.isEmpty || idToSave == 'new')
        throw AppException.validation("Profile ID is required");

      final profileWithId = updatedData.copyWith(id: idToSave);

      // RIGOROUS DTO SANITIZATION (Flatten empty I18nTexts to null to satisfy strict backend extra='forbid' & English-Only Mandate)
      bool isEmptyI18n(I18nText? text) {
        if (text == null) return true;
        if (text.translations.isEmpty) return true;
        if (text.translations.values.every((v) => v.trim().isEmpty))
          return true;
        return false;
      }

      if (isEmptyI18n(profileWithId.name)) {
        throw AppException.validation(
          "Profile Name (English) is required due to the English-Only Mandate.",
        );
      }

      Map<String, I18nText> sanitizeMap(Map<String, I18nText> map) {
        final sanitizedMap = <String, I18nText>{};
        map.forEach((k, v) {
          if (!isEmptyI18n(v)) sanitizedMap[k] = v;
        });
        return sanitizedMap;
      }

      final sanitized = profileWithId.copyWith(
        description: isEmptyI18n(profileWithId.description)
            ? null
            : profileWithId.description,
        userRoleLabel: isEmptyI18n(profileWithId.userRoleLabel)
            ? null
            : profileWithId.userRoleLabel,
        customPreface: isEmptyI18n(profileWithId.customPreface)
            ? null
            : profileWithId.customPreface,
        toneInstruction: isEmptyI18n(profileWithId.toneInstruction)
            ? null
            : profileWithId.toneInstruction,
        userRoleMappings: sanitizeMap(profileWithId.userRoleMappings),
        extensionLabels: sanitizeMap(profileWithId.extensionLabels),
        synthesis: profileWithId.synthesis == null
            ? null
            : profileWithId.synthesis!.copyWith(
                preambleText: isEmptyI18n(profileWithId.synthesis!.preambleText)
                    ? null
                    : profileWithId.synthesis!.preambleText,
                toneInstruction:
                    isEmptyI18n(profileWithId.synthesis!.toneInstruction)
                    ? null
                    : profileWithId.synthesis!.toneInstruction,
              ),
        layouts: profileWithId.layouts.map((l) {
          return l.copyWith(
            title: isEmptyI18n(l.title) ? null : l.title,
            description: isEmptyI18n(l.description) ? null : l.description,
            matrixColumnLabels: sanitizeMap(l.matrixColumnLabels),
          );
        }).toList(),
      );

      await ref
          .read(outputProfilesControllerProvider.notifier)
          .saveProfile(idToSave, sanitized);
      return sanitized;
    });
  }
}
