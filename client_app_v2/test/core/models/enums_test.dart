import 'package:flutter_test/flutter_test.dart';
import 'package:client_app/core/models/enums.dart';

void main() {
  group('EngineType Enum Parity', () {
    test('contains expected execution engines including causal discovery', () {
      expect(EngineType.values, contains(EngineType.tda));
      expect(EngineType.values, contains(EngineType.synthesis));
      expect(EngineType.values, contains(EngineType.prompt));
      expect(EngineType.values, contains(EngineType.causalDiscovery));
      expect(EngineType.values.length, 4);
    });

    test('name property matches Dart camelCase identifiers', () {
      expect(EngineType.tda.name, 'tda');
      expect(EngineType.synthesis.name, 'synthesis');
      expect(EngineType.prompt.name, 'prompt');
      expect(EngineType.causalDiscovery.name, 'causalDiscovery');
    });

    test(
      'EngineType byName parses valid names and throws on invalid names (negative/boundary)',
      () {
        expect(
          EngineType.values.byName('causalDiscovery'),
          EngineType.causalDiscovery,
        );
        expect(EngineType.values.byName('tda'), EngineType.tda);
        expect(
          () => EngineType.values.byName('invalid_engine'),
          throwsArgumentError,
        );
        expect(() => EngineType.values.byName(''), throwsArgumentError);
      },
    );
  });

  group('TargetBlockType Enum Parity', () {
    test('contains executiveSummaryBlock and core SDUI block types', () {
      expect(
        TargetBlockType.values,
        contains(TargetBlockType.executiveSummaryBlock),
      );
      expect(
        TargetBlockType.values,
        contains(TargetBlockType.globalScoreBlock),
      );
      expect(
        TargetBlockType.values,
        contains(TargetBlockType.matrixGraphsBlock),
      );
    });

    test(
      'TargetBlockType byName rejects unregistered block names (negative/boundary)',
      () {
        expect(
          TargetBlockType.values.byName('executiveSummaryBlock'),
          TargetBlockType.executiveSummaryBlock,
        );
        expect(
          () => TargetBlockType.values.byName('unknown_block'),
          throwsArgumentError,
        );
        expect(
          () => TargetBlockType.values.byName('null'),
          throwsArgumentError,
        );
      },
    );
  });

  group('SystemConcurrency Enum Constants', () {
    test('enforces positive integer thresholds', () {
      expect(SystemConcurrency.maxConcurrentWorkflows.value, greaterThan(0));
      expect(SystemConcurrency.maxConcurrentLlmSteps.value, greaterThan(0));
      expect(SystemConcurrency.llmMaxRetries.value, greaterThan(0));
      expect(SystemConcurrency.llmDefaultTimeoutSeconds.value, greaterThan(0));
    });
  });

  group('TargetSpeaker Enum Parity', () {
    test('strictly defines binary USER and AI speakers', () {
      expect(TargetSpeaker.values, [TargetSpeaker.user, TargetSpeaker.ai]);
      expect(() => TargetSpeaker.values.byName('UNKNOWN'), throwsArgumentError);
    });
  });

  group('UserRole, SecretScope & InvitationStatus Parity', () {
    test(
      'UserRole.fromString parses valid tiers and throws FormatException on invalid input (negative/boundary)',
      () {
        expect(UserRole.fromString('root'), UserRole.root);
        expect(UserRole.fromString('ADMIN'), UserRole.admin);
        expect(UserRole.fromString('MANAGER'), UserRole.manager);
        expect(UserRole.fromString('MEMBER'), UserRole.member);
        expect(UserRole.fromString('VIEWER'), UserRole.viewer);
        expect(
          () => UserRole.fromString('INVALID_ROLE'),
          throwsFormatException,
        );
        expect(() => UserRole.fromString(''), throwsFormatException);
      },
    );

    test(
      'IAM, Assignment, Email, and Secret enums expose exact lowercase snake_case backend string tokens',
      () {
        // Verify canonical lowercase snake_case backendValue across all 8 aligned enums.
        expect(SecretScope.llmProvider.backendValue, 'llm_provider');
        expect(SecretScope.mcpGateway.backendValue, 'mcp_gateway');
        expect(
          SecretStorageMode.cloudSecretManager.backendValue,
          'cloud_secret_manager',
        );
        expect(SecretStorageMode.envelopeKms.backendValue, 'envelope_kms');
        expect(SubscriptionStatus.active.backendValue, 'active');
        expect(SubscriptionStatus.trial.backendValue, 'trial');
        expect(SubscriptionStatus.pastDue.backendValue, 'past_due');
        expect(SubscriptionStatus.canceled.backendValue, 'canceled');
        expect(InvitationStatus.pending.backendValue, 'pending');
        expect(InvitationStatus.accepted.backendValue, 'accepted');
        expect(InvitationStatus.expired.backendValue, 'expired');
        expect(InvitationStatus.revoked.backendValue, 'revoked');
        expect(AssignmentStatus.pending.backendValue, 'pending');
        expect(AssignmentStatus.activated.backendValue, 'activated');
        expect(AssignmentStatus.submitted.backendValue, 'submitted');
        expect(AssignmentStatus.completed.backendValue, 'completed');
        expect(AssignmentStatus.expired.backendValue, 'expired');
        expect(AssignmentStatus.revoked.backendValue, 'revoked');
        expect(
          AssignmentResultVisibility.confirmationOnly.backendValue,
          'confirmation_only',
        );
        expect(
          AssignmentResultVisibility.fullReportAccess.backendValue,
          'full_report_access',
        );
        expect(EmailTransportMode.console.backendValue, 'console');
        expect(EmailTransportMode.httpApi.backendValue, 'http_api');
        expect(EmailDeliveryStatus.pending.backendValue, 'pending');
        expect(EmailDeliveryStatus.sent.backendValue, 'sent');
        expect(EmailDeliveryStatus.failed.backendValue, 'failed');
      },
    );
  });
}
