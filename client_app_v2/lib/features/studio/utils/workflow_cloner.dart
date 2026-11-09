import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/studio/models/output_profile.dart';
import 'package:client_app/features/studio/models/workflow.dart';
import 'package:client_app/shared/models/sdui_block_dto.dart';
import 'package:client_app/utils/json_converters.dart';

/// **WorkflowCloner (The Routing Logic Engine)**
///
/// Handles the complex deep-cloning of a Workflow DAG.
/// Enforces 100% Freezed model domain cloning (`cloneWorkflow`) and strict
/// Fail-Fast validation (Zero-Fallback, 32-hex RFC 9562 UUIDv7 IDs via
/// `generateOpaqueUuid7`, and DAG dependency / causal source verification).
class WorkflowCloner {
  /// Clones a strongly-typed [Workflow] domain model with newly generated
  /// 32-hex RFC 9562 UUIDv7 identifiers (`wf_`, `sr_`, `op_`) and remapped
  /// DAG dependency, input mapping, causal source, and output profile references.
  ///
  /// Throws [AppException] if any dependency or `causalSourceStepId` points to
  /// a missing or unmapped step.
  static Workflow cloneWorkflow(Workflow original) {
    final newWorkflowId = generateOpaqueUuid7('wf');
    final newSlug = original.slug.isNotEmpty
        ? '${original.slug}_copy'
        : newWorkflowId;

    // 1. Build 1:1 StepRule ID mapping using 32-hex RFC 9562 UUIDv7 ('sr_')
    final idMap = <String, String>{};
    for (final step in original.steps) {
      if (step.id.isEmpty) {
        throw const AppException(
          type: 'https://api.quorum.fi/errors/workflow-clone-failed',
          title: 'Clone Failed',
          status: 400,
          detail: 'Step ID cannot be empty during workflow clone.',
          extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
        );
      }
      idMap[step.id] = generateOpaqueUuid7('sr');
    }

    final validNewIds = idMap.values.toSet();

    // 2. Remap StepRule instances and enforce Fail-Fast topological invariants
    final clonedSteps = <StepRule>[];
    for (final step in original.steps) {
      final newStepId = idMap[step.id]!;

      final newDependsOn = <String>[];
      for (final oldDep in step.dependsOn) {
        final mappedDep = idMap[oldDep];
        if (mappedDep == null || !validNewIds.contains(mappedDep)) {
          throw const AppException(
            type: 'https://api.quorum.fi/errors/workflow-clone-failed',
            title: 'Clone Failed',
            status: 400,
            detail: 'Dependency points to a missing/invalid step.',
            extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
          );
        }
        newDependsOn.add(mappedDep);
      }

      final newMappings = <String, String>{};
      for (final entry in step.inputMappings.entries) {
        newMappings[entry.key] = _remapStepBindingString(entry.value, idMap);
      }

      String? newCausalSource;
      final oldCausalSource = step.causalSourceStepId;
      if (oldCausalSource != null && oldCausalSource.isNotEmpty) {
        final mappedCausal = idMap[oldCausalSource];
        if (mappedCausal == null || !validNewIds.contains(mappedCausal)) {
          throw const AppException(
            type: 'https://api.quorum.fi/errors/workflow-clone-failed',
            title: 'Clone Failed',
            status: 400,
            detail: 'Causal source step ID could not be remapped.',
            extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
          );
        }
        if (!newDependsOn.contains(mappedCausal)) {
          throw const AppException(
            type: 'https://api.quorum.fi/errors/workflow-clone-failed',
            title: 'Clone Failed',
            status: 400,
            detail:
                'Causal source step ID must exist in valid new steps and depends_on.',
            extensions: {'error_code': 'WORKFLOW_CLONE_FAILED'},
          );
        }
        newCausalSource = mappedCausal;
      }

      clonedSteps.add(
        step.copyWith(
          id: newStepId,
          dependsOn: newDependsOn,
          inputMappings: newMappings,
          causalSourceStepId: newCausalSource,
        ),
      );
    }

    // 3. Remap attached OutputProfiles and their content block bindings
    final profileIdMap = <String, String>{};
    final clonedProfiles = <String, OutputProfile>{};
    for (final entry in original.outputProfiles.entries) {
      final oldProfile = entry.value;
      final newProfileId = generateOpaqueUuid7('op');
      profileIdMap[entry.key] = newProfileId;
      profileIdMap[oldProfile.id] = newProfileId;

      final remappedBlocks = oldProfile.contentBlocks
          .map((block) => _remapSduiBlock(block, idMap))
          .toList(growable: false);

      clonedProfiles[newProfileId] = oldProfile.copyWith(
        id: newProfileId,
        workflowId: newWorkflowId,
        contentBlocks: remappedBlocks,
      );
    }

    final newDefaultProfileId =
        profileIdMap[original.defaultProfileId] ?? original.defaultProfileId;

    return original.copyWith(
      id: newWorkflowId,
      slug: newSlug,
      version: 1,
      steps: clonedSteps,
      outputProfiles: clonedProfiles,
      defaultProfileId: newDefaultProfileId,
    );
  }

  // Operate exclusively on typed Freezed SduiBlockDTO variants via Dart 3 switch.
  static SduiBlockDTO _remapSduiBlock(
    SduiBlockDTO block,
    Map<String, String> idMap,
  ) {
    return switch (block) {
      SduiParagraphBlock(:final text) => block.copyWith(
        text: _remapStepBindingString(text, idMap),
      ),
      SduiBulletListBlock(:final items) => block.copyWith(
        items: items
            .map(
              (item) => item.copyWith(
                text: _remapStepBindingString(item.text, idMap),
              ),
            )
            .toList(growable: false),
      ),
      SduiAccordionBlock(:final title, :final children) => block.copyWith(
        title: _remapStepBindingString(title, idMap),
        children: children
            .map((child) => _remapSduiBlock(child, idMap))
            .toList(growable: false),
      ),
      SduiAlertBoxBlock(:final text) => block.copyWith(
        text: _remapStepBindingString(text, idMap),
      ),
      SduiHeroInsightBlock(:final text) => block.copyWith(
        text: _remapStepBindingString(text, idMap),
      ),
      SduiMarkdownBlock(:final text) => block.copyWith(
        text: _remapStepBindingString(text, idMap),
      ),
      SduiQuoteCardBlock(:final quote) => block.copyWith(
        quote: _remapStepBindingString(quote, idMap),
      ),
      SduiWarningCardBlock(:final message, :final quoteText) => block.copyWith(
        message: _remapStepBindingString(message, idMap),
        quoteText: quoteText != null
            ? _remapStepBindingString(quoteText, idMap)
            : null,
      ),
      SduiNACardBlock(:final message) => block.copyWith(
        message: _remapStepBindingString(message, idMap),
      ),
      SduiGridBlock(:final items) => block.copyWith(
        items: items
            .map((item) => _remapSduiBlock(item, idMap))
            .toList(growable: false),
      ),
      SduiMetadataBlock(:final title, :final metadataLines) => block.copyWith(
        title: _remapStepBindingString(title, idMap),
        metadataLines: metadataLines
            .map((line) => _remapStepBindingString(line, idMap))
            .toList(growable: false),
      ),
      SduiScoreCardBlock() ||
      SduiAuditTrailBlock() ||
      SduiRadarChartBlock() ||
      SduiScatterPlotBlock() ||
      SduiQuadrantMatrixBlock() ||
      SduiMetrics1DBlock() ||
      SduiMatrixTableBlock() ||
      SduiCausalGraphBlock() => block,
    };
  }

  static String _remapStepBindingString(
    String value,
    Map<String, String> idMap,
  ) {
    String updated = value;
    for (final entry in idMap.entries) {
      final oldId = entry.key;
      final newId = entry.value;

      final stepsPrefix = '\$steps.$oldId.';
      if (updated.contains(stepsPrefix)) {
        updated = updated.replaceFirst(stepsPrefix, '\$steps.$newId.');
      }

      final resultsPrefix = '\$results.$oldId.';
      if (updated.contains(resultsPrefix)) {
        updated = updated.replaceFirst(resultsPrefix, '\$results.$newId.');
      }
    }
    return updated;
  }
}
