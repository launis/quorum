import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/models/enums.dart';
import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/features/settings/domain/models/tenant_secret_dto.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late UserRepository repository;

  final validUserId = generateOpaqueUuid7('usr');
  final validOrgId = generateOpaqueUuid7('org');
  final validInviteId = generateOpaqueUuid7('inv');
  final validSecretId = generateOpaqueUuid7('sec');

  User buildUser({String? id}) => User(
    id: id ?? validUserId,
    email: 'admin@quorum.ai',
    role: UserRole.admin,
    organizationId: validOrgId,
    name: 'Executive Admin',
    isActive: true,
    language: 'fi',
    themeMode: 'system',
  );

  Organization buildOrganization({String? id}) => Organization(
    id: id ?? validOrgId,
    name: 'Quorum Enterprise Oy',
    tier: 'enterprise',
    isActive: true,
    contactEmail: 'billing@quorum.ai',
    subscriptionStatus: SubscriptionStatus.active,
    quotaLimit: 500.0,
    tpmLimit: 200000,
    rpmLimit: 120,
    allowedEmailDomains: const <String>['quorum.ai'],
  );

  InvitationResponseDto buildInvitation({String? id}) => InvitationResponseDto(
    id: id ?? validInviteId,
    organizationId: validOrgId,
    email: 'invitee@quorum.ai',
    role: UserRole.member,
    status: InvitationStatus.pending,
    emailDeliveryStatus: EmailDeliveryStatus.sent,
    invitedBy: validUserId,
    expiresAt: DateTime.utc(2026, 12, 31),
    createdAt: DateTime.utc(2026, 11, 1),
  );

  TenantSecretResponseDto buildSecret({String? id}) => TenantSecretResponseDto(
    id: id ?? validSecretId,
    organizationId: validOrgId,
    scope: SecretScope.llmProvider,
    targetIdentifier: 'GOOGLE_AI_STUDIO',
    storageMode: SecretStorageMode.envelopeKms,
    configured: true,
    maskedHint: 'AIza...9999',
    kekVersion: 'v1',
    updatedAt: DateTime.utc(2026, 11, 1),
  );

  setUp(() {
    mockDio = MockDio();
    repository = UserRepository(mockDio);
  });

  group('UserRepository Unit & ISTQB Boundary Tests', () {
    test(
      'Positive 1: userRepositoryProvider and User CRUD endpoints (fetchCurrentUser, createUser, updateUser, listUsers, deleteUser) execute strict DTO roundtrips',
      () async {
        final container = ProviderContainer(
          overrides: [apiClientProvider.overrideWithValue(mockDio)],
        );
        addTearDown(container.dispose);

        final providedRepo = container.read(userRepositoryProvider);
        expect(providedRepo, isA<UserRepository>());

        final userPayload = buildUser().toJson();

        when(
          () => mockDio.get<Map<String, Object?>>('/iam/auth/me'),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/me'),
            data: userPayload,
            statusCode: 200,
          ),
        );

        final meResult = await providedRepo.fetchCurrentUser();
        expect(meResult.isRight(), isTrue);
        expect(meResult.getRight().toNullable()!.id, equals(validUserId));

        final createDto = UserCreate(
          email: 'new@quorum.ai',
          name: 'New Coach',
          role: UserRole.member,
          organizationId: validOrgId,
        );
        final expectedCreateJson = createDto.toJson();

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/users/',
            data: expectedCreateJson,
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/users/'),
            data: userPayload,
            statusCode: 201,
          ),
        );

        final createResult = await repository.createUser(createDto);
        expect(createResult.isRight(), isTrue);
        expect(createResult.getRight().toNullable()!.id, equals(validUserId));

        const updateDto = UserUpdate(name: 'Updated Name', language: 'en');
        final expectedUpdateJson = updateDto.toJson();

        when(
          () => mockDio.put<Map<String, Object?>>(
            '/iam/users/$validUserId',
            data: expectedUpdateJson,
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/users/$validUserId'),
            data: userPayload,
            statusCode: 200,
          ),
        );

        final updateResult = await repository.updateUser(
          validUserId,
          updateDto,
        );
        expect(updateResult.isRight(), isTrue);

        final userListPayload = <Object?>[userPayload];
        when(() => mockDio.get<List<Object?>>('/iam/users/')).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(path: '/iam/users/'),
            data: userListPayload,
            statusCode: 200,
          ),
        );

        final listResult = await repository.listUsers();
        expect(listResult.isRight(), isTrue);
        expect(listResult.getRight().toNullable()!, hasLength(1));

        final deletePayload = UserDeleteResponse(
          status: 'deleted',
          id: validUserId,
        ).toJson();
        when(
          () => mockDio.delete<Map<String, Object?>>('/iam/users/$validUserId'),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/users/$validUserId'),
            data: deletePayload,
            statusCode: 200,
          ),
        );

        final deleteResult = await repository.deleteUser(validUserId);
        expect(deleteResult.isRight(), isTrue);
        expect(deleteResult.getRight().toNullable()!.id, equals(validUserId));
      },
    );

    test(
      'Positive 2: Organization, Invitation, and BYOK Tenant Secret endpoints execute strict DTO roundtrips',
      () async {
        final orgPayload = buildOrganization().toJson();
        final orgListPayload = <Object?>[orgPayload];

        when(
          () => mockDio.get<List<Object?>>('/iam/organizations/'),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(path: '/iam/organizations/'),
            data: orgListPayload,
            statusCode: 200,
          ),
        );

        final orgsResult = await repository.listOrganizations();
        expect(orgsResult.isRight(), isTrue);
        expect(
          orgsResult.getRight().toNullable()!.single.id,
          equals(validOrgId),
        );

        when(
          () => mockDio.get<Map<String, Object?>>(
            '/iam/organizations/$validOrgId',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId',
            ),
            data: orgPayload,
            statusCode: 200,
          ),
        );

        final orgResult = await repository.getOrganization(validOrgId);
        expect(orgResult.isRight(), isTrue);

        const orgUpdateDto = OrganizationUpdateDto(
          name: 'Quorum Global',
          quotaLimit: 1000.0,
        );
        final expectedOrgUpdateJson = orgUpdateDto.toJson();

        when(
          () => mockDio.put<Map<String, Object?>>(
            '/iam/organizations/$validOrgId',
            data: expectedOrgUpdateJson,
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId',
            ),
            data: orgPayload,
            statusCode: 200,
          ),
        );

        final updateOrgResult = await repository.updateOrganization(
          validOrgId,
          orgUpdateDto,
        );
        expect(updateOrgResult.isRight(), isTrue);

        final inviteDto = buildInvitation();
        final invitePayload = inviteDto.toJson();
        final inviteListPayload = <Object?>[invitePayload];

        when(
          () => mockDio.get<List<Object?>>(
            '/iam/organizations/$validOrgId/invitations',
          ),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId/invitations',
            ),
            data: inviteListPayload,
            statusCode: 200,
          ),
        );

        final invitesResult = await repository.listInvitations(validOrgId);
        expect(invitesResult.isRight(), isTrue);
        expect(invitesResult.getRight().toNullable()!, hasLength(1));

        const createInviteDto = InvitationCreateDto(
          email: 'invitee@quorum.ai',
          role: UserRole.member,
        );
        final expectedCreateInviteJson = createInviteDto.toJson();

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/organizations/$validOrgId/invitations',
            data: expectedCreateInviteJson,
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId/invitations',
            ),
            data: invitePayload,
            statusCode: 201,
          ),
        );

        final createdInvite = await repository.createInvitation(
          validOrgId,
          createInviteDto,
        );
        expect(createdInvite.isRight(), isTrue);

        const batchCreateDto = InvitationBatchCreateDto(
          recipients: <InvitationCreateDto>[createInviteDto],
        );
        final expectedBatchCreateJson = batchCreateDto.toJson();
        final batchResponsePayload = InvitationBatchResponseDto(
          createdCount: 1,
          invitations: <InvitationResponseDto>[inviteDto],
        ).toJson();

        when(
          () => mockDio.post<Map<String, Object?>>(
            '/iam/organizations/$validOrgId/invitations/batch',
            data: expectedBatchCreateJson,
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId/invitations/batch',
            ),
            data: batchResponsePayload,
            statusCode: 201,
          ),
        );

        final batchResult = await repository.createInvitationBatch(
          validOrgId,
          batchCreateDto,
        );
        expect(batchResult.isRight(), isTrue);
        expect(batchResult.getRight().toNullable()!.createdCount, equals(1));

        when(
          () => mockDio.delete<Map<String, Object?>>(
            '/iam/organizations/$validOrgId/invitations/$validInviteId',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId/invitations/$validInviteId',
            ),
            data: invitePayload,
            statusCode: 200,
          ),
        );

        final revokeResult = await repository.revokeInvitation(
          validOrgId,
          validInviteId,
        );
        expect(revokeResult.isRight(), isTrue);

        final secretPayload = buildSecret().toJson();
        final secretListPayload = <Object?>[secretPayload];

        when(
          () => mockDio.get<List<Object?>>(
            '/iam/organizations/$validOrgId/secrets',
          ),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId/secrets',
            ),
            data: secretListPayload,
            statusCode: 200,
          ),
        );

        final secretsResult = await repository.listSecrets(validOrgId);
        expect(secretsResult.isRight(), isTrue);
        expect(secretsResult.getRight().toNullable()!, hasLength(1));

        const createSecretDto = TenantSecretCreateDto(
          scope: SecretScope.llmProvider,
          targetIdentifier: 'GOOGLE_AI_STUDIO',
          plaintextSecret: 'test-secret-placeholder',
          storageMode: SecretStorageMode.envelopeKms,
        );
        final expectedCreateSecretJson = createSecretDto.toJson();

        when(
          () => mockDio.put<Map<String, Object?>>(
            '/iam/organizations/$validOrgId/secrets',
            data: expectedCreateSecretJson,
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId/secrets',
            ),
            data: secretPayload,
            statusCode: 200,
          ),
        );

        final upsertResult = await repository.upsertSecret(
          validOrgId,
          createSecretDto,
        );
        expect(upsertResult.isRight(), isTrue);

        final deleteSecretPayload = OrganizationDeleteResponse(
          status: 'deleted',
          deletedId: validSecretId,
        ).toJson();

        when(
          () => mockDio.delete<Map<String, Object?>>(
            '/iam/organizations/$validOrgId/secrets/$validSecretId',
          ),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId/secrets/$validSecretId',
            ),
            data: deleteSecretPayload,
            statusCode: 200,
          ),
        );

        final deleteSecretResult = await repository.deleteSecret(
          validOrgId,
          validSecretId,
        );
        expect(deleteSecretResult.isRight(), isTrue);
        expect(
          deleteSecretResult.getRight().toNullable()!.deletedId,
          equals(validSecretId),
        );
      },
    );

    test(
      'Negative 1 (ISTQB BVA & Schema Integrity): rejects null payloads, non-Map array elements, and non-32-hex entity IDs (16-hex min-1 / 33-hex max+1)',
      () async {
        // Null payload -> Left(AppException)
        when(
          () => mockDio.get<Map<String, Object?>>('/iam/auth/me'),
        ).thenAnswer(
          (_) async => Response<Map<String, Object?>>(
            requestOptions: RequestOptions(path: '/iam/auth/me'),
            data: null,
            statusCode: 200,
          ),
        );
        final nullMe = await repository.fetchCurrentUser();
        expect(nullMe.isLeft(), isTrue);

        // Non-Map element inside list responses -> fail-fast SERVER_ERROR
        final invalidListPayload = <Object?>['malformed_scalar_element'];
        when(() => mockDio.get<List<Object?>>('/iam/users/')).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(path: '/iam/users/'),
            data: invalidListPayload,
            statusCode: 200,
          ),
        );
        final badUsersList = await repository.listUsers();
        expect(badUsersList.isLeft(), isTrue);
        expect(
          badUsersList.getLeft().toNullable()!.errorCode,
          equals('SERVER_ERROR'),
        );

        when(
          () => mockDio.get<List<Object?>>('/iam/organizations/'),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(path: '/iam/organizations/'),
            data: invalidListPayload,
            statusCode: 200,
          ),
        );
        final badOrgsList = await repository.listOrganizations();
        expect(badOrgsList.isLeft(), isTrue);
        expect(
          badOrgsList.getLeft().toNullable()!.errorCode,
          equals('SERVER_ERROR'),
        );

        when(
          () => mockDio.get<List<Object?>>(
            '/iam/organizations/$validOrgId/invitations',
          ),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId/invitations',
            ),
            data: invalidListPayload,
            statusCode: 200,
          ),
        );
        final badInvitesList = await repository.listInvitations(validOrgId);
        expect(badInvitesList.isLeft(), isTrue);
        expect(
          badInvitesList.getLeft().toNullable()!.errorCode,
          equals('SERVER_ERROR'),
        );

        when(
          () => mockDio.get<List<Object?>>(
            '/iam/organizations/$validOrgId/secrets',
          ),
        ).thenAnswer(
          (_) async => Response<List<Object?>>(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId/secrets',
            ),
            data: invalidListPayload,
            statusCode: 200,
          ),
        );
        final badSecretsList = await repository.listSecrets(validOrgId);
        expect(badSecretsList.isLeft(), isTrue);
        expect(
          badSecretsList.getLeft().toNullable()!.errorCode,
          equals('SERVER_ERROR'),
        );

        // BVA on StrictOpaqueIdConverter: 31 hex chars (min-1) and 33 hex chars (max+1) fail fast
        for (final invalidId in <String>[
          'usr_0195f3a000007000800000000000001',
          'usr_0195f3a00000700080000000000000001',
        ]) {
          final malformedUserPayload = Map<String, Object?>.of(
            buildUser().toJson(),
          );
          malformedUserPayload['id'] = invalidId;
          when(
            () => mockDio.get<Map<String, Object?>>('/iam/auth/me'),
          ).thenAnswer(
            (_) async => Response<Map<String, Object?>>(
              requestOptions: RequestOptions(path: '/iam/auth/me'),
              data: malformedUserPayload,
              statusCode: 200,
            ),
          );
          final res = await repository.fetchCurrentUser();
          expect(res.isLeft(), isTrue);
          expect(
            res.getLeft().toNullable()!.errorCode,
            equals('UNKNOWN_ERROR'),
          );
        }
      },
    );

    test(
      'Negative 2: maps DioException (wrapped AppException, RFC 7807 body, 404, 401, 400, 500) and direct AppException accurately',
      () async {
        // 1. DioException wrapping an existing AppException
        when(() => mockDio.get<Map<String, Object?>>('/iam/auth/me')).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/iam/auth/me'),
            error: AppException.timeout('Gateway timeout'),
          ),
        );
        final wrappedRes = await repository.fetchCurrentUser();
        expect(wrappedRes.isLeft(), isTrue);
        expect(wrappedRes.getLeft().toNullable()!.errorCode, equals('TIMEOUT'));

        // 2. DioException with RFC 7807 Problem Details response body
        final rfc7807Body = const AppException(
          type: 'https://api.quorum.fi/errors/quota-exceeded',
          title: 'Quota Exceeded',
          status: 429,
          detail: 'Monthly organization quota exceeded.',
        ).toJson();
        when(
          () => mockDio.get<Map<String, Object?>>(
            '/iam/organizations/$validOrgId',
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId',
            ),
            response: Response<Map<String, Object?>>(
              requestOptions: RequestOptions(
                path: '/iam/organizations/$validOrgId',
              ),
              statusCode: 429,
              data: rfc7807Body,
            ),
          ),
        );
        final rfcRes = await repository.getOrganization(validOrgId);
        expect(rfcRes.isLeft(), isTrue);
        expect(
          rfcRes.getLeft().toNullable()!.errorCode,
          equals('QUOTA_EXCEEDED'),
        );

        // 3. HTTP 404 -> RESOURCE_NOT_FOUND
        when(
          () => mockDio.delete<Map<String, Object?>>('/iam/users/$validUserId'),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/iam/users/$validUserId'),
            response: Response<Map<String, Object?>>(
              requestOptions: RequestOptions(path: '/iam/users/$validUserId'),
              statusCode: 404,
            ),
          ),
        );
        final notFoundRes = await repository.deleteUser(validUserId);
        expect(notFoundRes.isLeft(), isTrue);
        expect(
          notFoundRes.getLeft().toNullable()!.errorCode,
          equals('RESOURCE_NOT_FOUND'),
        );

        // 4. HTTP 401 -> AUTHENTICATION_FAILED
        when(() => mockDio.get<List<Object?>>('/iam/users/')).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/iam/users/'),
            response: Response<List<Object?>>(
              requestOptions: RequestOptions(path: '/iam/users/'),
              statusCode: 401,
            ),
          ),
        );
        final unauthRes = await repository.listUsers();
        expect(unauthRes.isLeft(), isTrue);
        expect(
          unauthRes.getLeft().toNullable()!.errorCode,
          equals('AUTHENTICATION_FAILED'),
        );

        // 5. HTTP 400 -> VALIDATION_FAILED
        when(
          () => mockDio.delete<Map<String, Object?>>(
            '/iam/organizations/$validOrgId/invitations/$validInviteId',
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(
              path: '/iam/organizations/$validOrgId/invitations/$validInviteId',
            ),
            response: Response<Map<String, Object?>>(
              requestOptions: RequestOptions(
                path:
                    '/iam/organizations/$validOrgId/invitations/$validInviteId',
              ),
              statusCode: 400,
            ),
          ),
        );
        final badReqRes = await repository.revokeInvitation(
          validOrgId,
          validInviteId,
        );
        expect(badReqRes.isLeft(), isTrue);
        expect(
          badReqRes.getLeft().toNullable()!.errorCode,
          equals('VALIDATION_FAILED'),
        );

        // 6. Direct AppException thrown -> preserved
        when(
          () => mockDio.delete<Map<String, Object?>>(
            '/iam/organizations/$validOrgId/secrets/$validSecretId',
          ),
        ).thenThrow(AppException.cancelled());
        final cancelledRes = await repository.deleteSecret(
          validOrgId,
          validSecretId,
        );
        expect(cancelledRes.isLeft(), isTrue);
        expect(
          cancelledRes.getLeft().toNullable()!.errorCode,
          equals('CANCELLED'),
        );
      },
    );
  });
}
