import 'dart:async';
import 'package:client_app/core/api/studio_client.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/logging/logger_service.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/theme/app_durations.dart';
import 'package:client_app/utils/riverpod_extensions.dart';
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

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
    return await client.getOutputProfiles();
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
    OutputProfile returnData = payload;

    // 1. Optimistic Update
    switch (state) {
      case AsyncData(:final value):
        final currentList = List<OutputProfile>.from(value);
        final index = currentList.indexWhere((m) => m.id == id);

        if (index >= 0) {
          currentList[index] = payload;
        } else {
          currentList.add(payload);
        }
        state = AsyncValue.data(currentList);
      case AsyncError() || AsyncLoading():
        break;
    }

    try {
      // 2. Network Call
      final client = ref.read(studioClientProvider);
      final verifiedProfile = await client.saveOutputProfile(id, payload);

      // 3. Confirm with Actual Data
      switch (state) {
        case AsyncData(:final value):
          final currentList = List<OutputProfile>.from(value);
          final index = currentList.indexWhere((m) => m.id == id);
          if (index >= 0) {
            currentList[index] = verifiedProfile;
            state = AsyncValue.data(currentList);
          }
          returnData = verifiedProfile;
        case AsyncError() || AsyncLoading():
          break;
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

      switch (state) {
        case AsyncData(:final value):
          final currentList = List<OutputProfile>.from(value);
          currentList.removeWhere((m) => m.id == id);
          state = AsyncValue.data(currentList);
        case AsyncError() || AsyncLoading():
          break;
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
      final clonedProfile = await client.cloneOutputProfile(id);

      // 2. Update State
      switch (state) {
        case AsyncData(:final value):
          final currentList = List<OutputProfile>.from(value);
          currentList.insert(0, clonedProfile);
          state = AsyncValue.data(currentList);
        case AsyncError() || AsyncLoading():
          break;
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
      final draftProfile = await client.createOutputProfileDraft();

      switch (state) {
        case AsyncData(:final value):
          final currentList = List<OutputProfile>.from(value);
          currentList.insert(0, draftProfile);
          state = AsyncValue.data(currentList);
        case AsyncError() || AsyncLoading():
          break;
      }
      return draftProfile;
    } catch (e, st) {
      state = previousState;
      ref
          .read(loggerServiceProvider)
          .error('OutputProfilesController', 'Create draft failed', e, st);
      if (e is DioException && e.error is AppException) {
        throw e.error!;
      }
      throw AppException.unknown(e);
    }
  }
}

/// Fetches a single Output Profile natively by ID.
@riverpod
Future<OutputProfile> outputProfileById(Ref ref, String id) async {
  final client = ref.watch(studioClientProvider);
  return await client.getOutputProfile(id);
}

// --- Gold Standard Form State (Flat MVC) ---

@riverpod
class OutputProfileForm extends _$OutputProfileForm {
  @override
  FutureOr<OutputProfile> build(String configId) async {
    final profile = await ref.watch(outputProfileByIdProvider(configId).future);
    // Phase 5, Step 5.2: Operate directly on immutable Freezed OutputProfile via copyWith.
    return profile.copyWith();
  }

  void forceRebuild() {
    switch (state) {
      case AsyncData(:final value):
        // Deep copy is handled by Freezed copyWith inherently, triggering notify.
        state = AsyncData(value.copyWith());
      case AsyncError() || AsyncLoading():
        break;
    }
  }

  void updatePayload(OutputProfile payload) {
    state = AsyncData(payload);
  }

  Future<void> submit(OutputProfile updatedData) async {
    state = const AsyncLoading();

    state = await AsyncValue.guard(() async {
      final idToSave = updatedData.id.isNotEmpty ? updatedData.id : configId;
      if (idToSave.isEmpty || idToSave == 'new') {
        final error = AppException.validation('Profile ID is required');
        ref
            .read(loggerServiceProvider)
            .error(
              'OutputProfileForm',
              'Validation failed: Profile ID is required',
              error,
              StackTrace.current,
            );
        throw error;
      }

      final profileWithId = updatedData.copyWith(id: idToSave);

      // CUSTOM SCALE FAIL-FAST VALIDATION
      if (profileWithId.displayScale == DisplayScale.custom) {
        final minScale = profileWithId.customScaleMin;
        final maxScale = profileWithId.customScaleMax;
        if (minScale == null || maxScale == null) {
          final error = AppException.validation(
            'Custom Scale Min and Custom Scale Max are required when Display Scale is Custom.',
          );
          ref
              .read(loggerServiceProvider)
              .error(
                'OutputProfileForm',
                'Validation failed: missing custom scale bounds',
                error,
                StackTrace.current,
              );
          throw error;
        }
        if (maxScale <= minScale) {
          final error = AppException.validation(
            'Custom Scale Max must be strictly greater than Custom Scale Min.',
          );
          ref
              .read(loggerServiceProvider)
              .error(
                'OutputProfileForm',
                'Validation failed: customScaleMax ($maxScale) <= customScaleMin ($minScale)',
                error,
                StackTrace.current,
              );
          throw error;
        }
      }

      if (profileWithId.name.isEmpty) {
        final error = AppException.validation(
          'Profile Name (English) is required due to the English-Only Mandate.',
        );
        ref
            .read(loggerServiceProvider)
            .error(
              'OutputProfileForm',
              'Validation failed: empty profile name',
              error,
              StackTrace.current,
            );
        throw error;
      }

      final desc = profileWithId.description;
      final roleLabel = profileWithId.userRoleLabel;
      final preface = profileWithId.customPreface;
      final tone = profileWithId.toneInstruction;

      final sanitized = profileWithId.copyWith(
        description: (desc == null || desc.isEmpty) ? null : desc,
        userRoleLabel: (roleLabel == null || roleLabel.isEmpty)
            ? null
            : roleLabel,
        customPreface: (preface == null || preface.isEmpty) ? null : preface,
        toneInstruction: (tone == null || tone.isEmpty) ? null : tone,
      );

      await ref
          .read(outputProfilesControllerProvider.notifier)
          .saveProfile(idToSave, sanitized);
      return sanitized;
    });

    switch (state) {
      case AsyncError(:final error):
        throw error;
      case AsyncData() || AsyncLoading():
        break;
    }
  }
}

/// Selected section state provider for Tab 3 Master-Detail view in OutputProfileCrudView.
@riverpod
class SelectedOutputProfileConfigSection
    extends _$SelectedOutputProfileConfigSection {
  @override
  TargetBlockType? build(String profileId) => null;

  void select(TargetBlockType? section) {
    state = section;
  }
}
