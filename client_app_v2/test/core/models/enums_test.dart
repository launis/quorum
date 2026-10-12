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
}
