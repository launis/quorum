import 'package:client_app/core/models/enums.dart';
import 'package:client_app/features/execution/models/execution_metadata.dart';
import 'package:client_app/features/execution/models/trace_context_carrier.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('ExecutionMetadata Model Hardening Tests', () {
    test(
      'Positive 1: ExecutionMetadata roundtrips full JSON payload with nested telemetry and enum',
      () {
        final registryId = generateOpaqueUuid7('reg');
        final orgId = generateOpaqueUuid7('org');
        final initiatorId = generateOpaqueUuid7('usr');
        final rawPayload = {
          'matrix_sampling_strategy': 10,
          'workflow_version': 3,
          'global_context_vars': <String, Object?>{
            'target_locale': 'fi',
            'organization_id': orgId,
            'initiator_id': initiatorId,
            'passivity_detected': false,
          },
          'provider_override': 'vertex_ai',
          'model_registry_id': registryId,
          'telemetry': {
            'traceparent':
                '00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01',
            'tracestate': 'congo=t61rcWkgMzE',
          },
        };

        final metadata = ExecutionMetadata.fromJson(rawPayload);

        expect(metadata.matrixSamplingStrategy, equals(10));
        expect(metadata.workflowVersion, equals(3));
        expect(metadata.globalContextVars?.targetLocale, equals('fi'));
        expect(metadata.globalContextVars?.organizationId, equals(orgId));
        expect(metadata.globalContextVars?.initiatorId, equals(initiatorId));
        expect(metadata.globalContextVars?.passivityDetected, isFalse);
        expect(metadata.providerOverride, equals(LLMProvider.vertexAi));
        expect(metadata.modelRegistryId, equals(registryId));
        expect(
          metadata.telemetry,
          isA<TraceContextCarrier>().having(
            (t) => t.traceparent,
            'traceparent',
            '00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01',
          ),
        );

        final serialized = metadata.toJson();
        final roundtripped = ExecutionMetadata.fromJson(serialized);
        expect(roundtripped.matrixSamplingStrategy, equals(10));
        expect(roundtripped.workflowVersion, equals(3));
        expect(roundtripped.globalContextVars?.organizationId, equals(orgId));
        expect(
          roundtripped.globalContextVars?.initiatorId,
          equals(initiatorId),
        );
        expect(roundtripped.providerOverride, equals(LLMProvider.vertexAi));
        expect(roundtripped.modelRegistryId, equals(registryId));
        expect(
          roundtripped.telemetry?.traceparent,
          equals('00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01'),
        );
      },
    );

    test(
      'Positive 2 (Boundary): ExecutionMetadata applies default workflowVersion=1 and accepts boundary 0 sampling',
      () {
        final minimalMetadata = ExecutionMetadata.fromJson({
          'matrix_sampling_strategy': 0,
        });

        expect(minimalMetadata.matrixSamplingStrategy, equals(0));
        expect(minimalMetadata.workflowVersion, equals(1));
        expect(minimalMetadata.globalContextVars, isNull);
        expect(minimalMetadata.providerOverride, isNull);
        expect(minimalMetadata.modelRegistryId, isNull);
        expect(minimalMetadata.telemetry, isNull);
      },
    );

    test(
      'Negative 1: ExecutionMetadata and GlobalContextVarsDto reject unrecognized JSON keys via disallowUnrecognizedKeys',
      () {
        expect(
          () => ExecutionMetadata.fromJson({
            'workflow_version': 1,
            'unexpected_legacy_key': 'forbidden',
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );

        expect(
          () => GlobalContextVarsDto.fromJson({
            'target_locale': 'fi',
            'unrecognized_context_var': 'forbidden',
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );

        expect(
          () => GlobalContextVarsDto.fromJson({
            'target_locale': 'fi',
            '_sys_initiator_id': generateOpaqueUuid7('usr'),
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );
      },
    );

    test(
      'Negative 2: ExecutionMetadata rejects invalid LLMProvider enum value and wrong field types',
      () {
        expect(
          () => ExecutionMetadata.fromJson({
            'provider_override': 'invalid_provider_name',
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<ArgumentError>())),
        );

        expect(
          () => ExecutionMetadata.fromJson({
            'workflow_version': 'not_an_integer',
          }),
          throwsA(anyOf(isA<CheckedFromJsonException>(), isA<TypeError>())),
        );
      },
    );
  });
}
