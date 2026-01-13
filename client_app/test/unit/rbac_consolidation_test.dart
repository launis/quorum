import 'package:client_app/features/admin/data/admin_repository.dart';
import 'package:client_app/features/admin/data/organization_repository.dart';
import 'package:client_app/features/admin/domain/dtos/user_dtos.dart';
import 'package:client_app/features/auth/data/repositories/user_repository.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

// --- Mocks ---
class MockDio extends Mock implements Dio {}

void main() {
  group('RBAC & User Management Automated Tests', () {
    late MockDio mockDio;
    late UserRepository userRepository;
    late AdminRepository adminRepository;
    late OrganizationRepository organizationRepository;

    setUp(() {
      mockDio = MockDio();
      userRepository = UserRepository(mockDio);
      adminRepository = AdminRepository(mockDio);
      organizationRepository = OrganizationRepository(mockDio);

      registerFallbackValue(RequestOptions(path: ''));
    });

    // 1. SELF-SERVICE: Update Own Profile
    test('Self-Update: updateCurrentUser sends correct PUT request', () async {
      // Arrange
      const uid = 'mem1';
      const updates = {'display_name': 'New Name'};
      final responseData = {
        'uid': uid,
        'email': 'mem@test.com',
        'role': 'MEMBER',
        'display_name': 'New Name',
        'organization_id': 'org1',
      };

      when(
        () =>
            mockDio.put<Map<String, dynamic>>(any(), data: any(named: 'data')),
      ).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          data: responseData,
          statusCode: 200,
        ),
      );

      // Act
      final result = await userRepository.updateCurrentUser(uid, updates);

      // Assert
      expect(result.isRight(), true);
      verify(
        () => mockDio.put<Map<String, dynamic>>(
          '/admin/users/$uid',
          data: updates,
        ),
      ).called(1);
    });

    // 2. ADMIN: Update Other User (Org Admin Scenario)
    test(
      'Admin-Update: updateUser sends correct PATCH request with DTO',
      () async {
        // Arrange
        const targetUid = 'target1';
        const updatesDto = UserUpdateDto(
          displayName: 'Updated Name',
          role: UserRole.member,
        );

        // AdminRepository.updateUser is async void (Right(null))
        when(
          () => mockDio.patch<void>(any(), data: any(named: 'data')),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(path: ''),
            data: null,
            statusCode: 200,
          ),
        );

        // Act
        final result = await adminRepository.updateUser(
          userId: targetUid,
          data: updatesDto,
        );

        // Assert
        expect(result.isRight(), true);

        verify(
          () => mockDio.patch<void>(
            '/admin/users/$targetUid',
            data: updatesDto.toJson(),
          ),
        ).called(1);
      },
    );

    // 3. ROOT: Create Organization (Root Capability)
    test(
      'Root-Action: createOrganization sends correct POST request',
      () async {
        // Arrange
        final orgData = {
          'name': 'New Org',
          'admin_email': 'admin@new.com',
          'admin_password': 'password',
          'admin_name': 'Admin Name',
        };

        final responseData = {
          'id': 'new_org_id',
          'name': 'New Org',
          'created_at': '2024-01-01',
          'is_active': true,
          'tier': 'standard',
        };

        when(
          () => mockDio.post<Map<String, dynamic>>(
            any(),
            data: any(named: 'data'),
          ),
        ).thenAnswer(
          (_) async => Response(
            requestOptions: RequestOptions(path: ''),
            data: responseData,
            statusCode: 200,
          ),
        );

        // Act
        final result = await organizationRepository.createOrganization(orgData);

        // Assert
        expect(result.isRight(), true);
        verify(
          () => mockDio.post<Map<String, dynamic>>(
            '/organizations/',
            data: orgData,
          ),
        ).called(1);
      },
    );
  });
}
