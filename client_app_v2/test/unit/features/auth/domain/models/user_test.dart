import 'dart:convert';

import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/utils/json_converters.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:json_annotation/json_annotation.dart';

void main() {
  group('User & IAM Session DTOs Unit & ISTQB Boundary Tests', () {
    test(
      'Positive 1: User, TokenExchangeResponseDto, LogoutRequestDto, LogoutResponseDto, UserCreate, and UserUpdate serialize and deserialize roundtrip with RBAC helpers',
      () {
        final userId = generateOpaqueUuid7('usr');
        final orgId = generateOpaqueUuid7('org');
        final creatorId = generateOpaqueUuid7('usr');

        final rawExchange = <String, Object?>{
          'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.quorum_jwt',
          'token_type': 'bearer',
          'expires_in_seconds': 900,
          'user': <String, Object?>{
            'id': userId,
            'slug': 'root-admin',
            'firebase_uid': null,
            'email': 'root@quorum.ai',
            'role': 'ROOT',
            'organization_id': orgId,
            'name': 'Root Administrator',
            'created_at': '2026-11-01T10:00:00Z',
            'language': 'en',
            'theme_mode': 'dark',
            'last_login_at': '2026-11-02T12:00:00.000Z',
            'execution_count': 42,
            'is_active': true,
            'created_by': creatorId,
            'deleted_at': null,
          },
        };

        final exchange = TokenExchangeResponseDto.fromJson(rawExchange);
        expect(
          exchange.accessToken,
          equals('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.quorum_jwt'),
        );
        expect(exchange.tokenType, equals('bearer'));
        expect(exchange.expiresInSeconds, equals(900));

        final user = exchange.user;
        expect(user.id, equals(userId));
        expect(user.slug, equals('root-admin'));
        expect(user.firebaseUid, isNull);
        expect(user.email, equals('root@quorum.ai'));
        expect(user.role, equals(UserRole.root));
        expect(user.organizationId, equals(orgId));
        expect(user.name, equals('Root Administrator'));
        expect(user.createdAt, equals('2026-11-01T10:00:00Z'));
        expect(user.language, equals('en'));
        expect(user.themeMode, equals('dark'));
        expect(user.lastLoginAt, equals(DateTime.utc(2026, 11, 2, 12)));
        expect(user.executionCount, equals(42));
        expect(user.isActive, isTrue);
        expect(user.createdBy, equals(creatorId));
        expect(user.deletedAt, isNull);
        expect(user.isAdmin, isTrue);
        expect(user.canManageOrganization, isTrue);

        // Roundtrip TokenExchangeResponseDto and User (including non-null firebase_uid and deleted_at)
        final roundtrippedMap =
            jsonDecode(jsonEncode(exchange.toJson())) as Map<String, Object?>;
        final roundtripped = TokenExchangeResponseDto.fromJson(roundtrippedMap);
        expect(roundtripped.user.id, equals(userId));
        expect(roundtripped.user.executionCount, equals(42));

        final populatedUser = User.fromJson(<String, Object?>{
          'id': userId,
          'firebase_uid': 'fb_uid_root_001',
          'email': 'root@quorum.ai',
          'role': 'ROOT',
          'deleted_at': '2026-11-02T15:30:00.000Z',
        });
        expect(populatedUser.firebaseUid, equals('fb_uid_root_001'));
        expect(
          populatedUser.deletedAt,
          equals(DateTime.utc(2026, 11, 2, 15, 30)),
        );
        final populatedRoundtrip = User.fromJson(populatedUser.toJson());
        expect(populatedRoundtrip.firebaseUid, equals('fb_uid_root_001'));
        expect(
          populatedRoundtrip.deletedAt,
          equals(DateTime.utc(2026, 11, 2, 15, 30)),
        );

        // TokenExchangeRequestDto omits null fields when serialized
        final exchangeReq = TokenExchangeRequestDto(targetUserId: userId);
        final reqJson = exchangeReq.toJson();
        expect(reqJson, equals(<String, Object?>{'target_user_id': userId}));
        expect(reqJson.containsKey('firebase_token'), isFalse);
        expect(reqJson.containsKey('service_auth_secret'), isFalse);

        // LogoutRequestDto & LogoutResponseDto roundtrip
        const logoutReq = LogoutRequestDto(revokeAllSessions: true);
        expect(
          LogoutRequestDto.fromJson(logoutReq.toJson()).revokeAllSessions,
          isTrue,
        );

        final logoutResp = LogoutResponseDto.fromJson(const <String, Object?>{
          'revoked_jti': 'jti_12345',
          'all_sessions_revoked': false,
        });
        expect(logoutResp.status, equals('logged_out'));
        expect(logoutResp.revokedJti, equals('jti_12345'));
        expect(logoutResp.allSessionsRevoked, isFalse);

        // Phase 1, Step 1: UserCreate & UserUpdate roundtrip with required language and theme_mode defaults
        final userCreate = UserCreate(
          email: 'new@quorum.ai',
          organizationId: orgId,
        );
        final createJson = userCreate.toJson();
        expect(createJson['language'], equals('fi'));
        expect(createJson['theme_mode'], equals('system'));
        expect(createJson['is_active'], isTrue);
        final createdFromJson = UserCreate.fromJson(createJson);
        expect(createdFromJson.role, equals(UserRole.member));
        expect(createdFromJson.isActive, isTrue);
        expect(createdFromJson.language, equals('fi'));
        expect(createdFromJson.themeMode, equals('system'));
        expect(createdFromJson.organizationId, equals(orgId));

        final directUserCreate = UserCreate(
          email: 'direct@quorum.ai',
          name: 'Direct User',
          role: UserRole.manager,
          organizationId: orgId,
          password: 'securePassword123',
        );
        final directCreateJson = directUserCreate.toJson();
        expect(directCreateJson['name'], equals('Direct User'));
        expect(directCreateJson['password'], equals('securePassword123'));
        expect(directCreateJson['language'], equals('fi'));
        expect(directCreateJson['theme_mode'], equals('system'));

        const userUpdate = UserUpdate(
          name: 'Updated Name',
          role: UserRole.manager,
          language: 'fi',
        );
        final updateJson = userUpdate.toJson();
        expect(updateJson.containsKey('password'), isFalse);
        final updatedFromJson = UserUpdate.fromJson(updateJson);
        expect(updatedFromJson.name, equals('Updated Name'));
        expect(updatedFromJson.role, equals(UserRole.manager));
        expect(updatedFromJson.language, equals('fi'));
      },
    );

    test(
      'Positive 2 (RBAC Role Equivalence Partitions): evaluates isAdmin and canManageOrganization across all UserRole values',
      () {
        final userId = generateOpaqueUuid7('usr');

        User buildWithRole(UserRole role) =>
            User(id: userId, email: '${role.name}@quorum.ai', role: role);

        final rootUser = buildWithRole(UserRole.root);
        expect(rootUser.isAdmin, isTrue);
        expect(rootUser.canManageOrganization, isTrue);

        final adminUser = buildWithRole(UserRole.admin);
        expect(adminUser.isAdmin, isTrue);
        expect(adminUser.canManageOrganization, isTrue);

        final managerUser = buildWithRole(UserRole.manager);
        expect(managerUser.isAdmin, isFalse);
        expect(managerUser.canManageOrganization, isTrue);

        for (final nonManagerRole in [
          UserRole.member,
          UserRole.viewer,
          UserRole.unknown,
        ]) {
          final u = buildWithRole(nonManagerRole);
          expect(u.isAdmin, isFalse);
          expect(u.canManageOrganization, isFalse);
        }
      },
    );

    test(
      'Negative 1: rejects unrecognized JSON keys across User and IAM DTOs under disallowUnrecognizedKeys',
      () {
        final userId = generateOpaqueUuid7('usr');
        final orgId = generateOpaqueUuid7('org');

        expect(
          () => User.fromJson(<String, Object?>{
            'id': userId,
            'email': 'member@quorum.ai',
            'role': 'MEMBER',
            'rogue_key': 'forbidden',
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );

        expect(
          () => TokenExchangeRequestDto.fromJson(<String, Object?>{
            'target_user_id': userId,
            'extra_param': 123,
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );

        expect(
          () => UserCreate.fromJson(<String, Object?>{
            'email': 'member@quorum.ai',
            'organization_id': orgId,
            'unexpected': true,
          }),
          throwsA(
            anyOf(
              isA<UnrecognizedKeysException>(),
              isA<CheckedFromJsonException>(),
            ),
          ),
        );

        expect(
          () => UserUpdate.fromJson(<String, Object?>{
            'name': 'Alice',
            'unexpected': true,
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
      'Negative 2 (ISTQB BVA & Opaque ID Validation): rejects non-32-hex Opaque Stripe IDs (16-hex, 31-hex, 33-hex) and missing required fields',
      () {
        // 16-hex legacy ID, 31-hex (min-1), and 33-hex (max+1) must fail StrictOpaqueIdConverter with AppException
        for (final invalidId in [
          'usr_0123456789abcdef',
          'usr_0195f3a000007000800000000000000',
          'usr_0195f3a00000700080000000000000012',
          'u_0195f3a0000070008000000000000001',
        ]) {
          expect(
            () => User.fromJson(<String, Object?>{
              'id': invalidId,
              'email': 'member@quorum.ai',
              'role': 'MEMBER',
            }),
            throwsA(
              anyOf(
                isA<AppException>(),
                isA<CheckedFromJsonException>().having(
                  (e) => e.innerError,
                  'innerError',
                  isA<AppException>(),
                ),
              ),
            ),
          );
        }

        // UserCreate with invalid organization_id
        expect(
          () => UserCreate.fromJson(<String, Object?>{
            'email': 'member@quorum.ai',
            'organization_id': 'org_short',
          }),
          throwsA(
            anyOf(
              isA<AppException>(),
              isA<CheckedFromJsonException>().having(
                (e) => e.innerError,
                'innerError',
                isA<AppException>(),
              ),
            ),
          ),
        );

        // Missing required fields in TokenExchangeResponseDto
        expect(
          () => TokenExchangeResponseDto.fromJson(<String, Object?>{
            'access_token': 'jwt_token',
          }),
          throwsA(isA<CheckedFromJsonException>()),
        );
      },
    );
  });
}
