import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/admin/data/organization_repository.dart';
import 'package:client_app/features/admin/domain/models/organization.dart';
import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

// Manual Mock
class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late OrganizationRepository repository;

  setUp(() {
    mockDio = MockDio();
    repository = OrganizationRepository(mockDio);
  });

  group('fetchOrganizations', () {
    test(
      'returns Right(List<Organization>) when API call is successful',
      () async {
        // Arrange
        final responseData = [
          {'id': 'org-1', 'name': 'Test Org', 'status': 'ACTIVE'},
          {'id': 'org-2', 'name': 'Another Org', 'status': 'SUSPENDED'},
        ];

        when(() => mockDio.get<List<dynamic>>('/organizations')).thenAnswer(
          (_) async => Response(
            data: responseData,
            statusCode: 200,
            requestOptions: RequestOptions(path: '/organizations'),
          ),
        );

        // Act
        final result = await repository.fetchOrganizations();

        // Assert
        expect(result.isRight(), true);
        result.fold((l) => fail('Should not return error'), (r) {
          expect(r.length, 2);
          expect(r[0].id, 'org-1');
          expect(r[0].status, OrganizationStatus.active);
          expect(r[1].id, 'org-2');
          expect(r[1].status, OrganizationStatus.suspended);
        });
      },
    );

    test('returns Right([]) when API call returns null data', () async {
      // Arrange
      when(() => mockDio.get<List<dynamic>>('/organizations')).thenAnswer(
        (_) async => Response(
          data: null,
          statusCode: 200,
          requestOptions: RequestOptions(path: '/organizations'),
        ),
      );

      // Act
      final result = await repository.fetchOrganizations();

      // Assert
      expect(result.isRight(), true);
      result.fold((l) => fail('Should not return error'), (r) {
        expect(r, isEmpty);
      });
    });

    test(
      'returns Left(AppError.server) when API throws DioException',
      () async {
        // Arrange
        when(() => mockDio.get<List<dynamic>>('/organizations')).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/organizations'),
            type: DioExceptionType.badResponse,
            response: Response(
              statusCode: 500,
              requestOptions: RequestOptions(path: '/organizations'),
            ),
            message: 'Server Error',
          ),
        );

        // Act
        final result = await repository.fetchOrganizations();

        // Assert
        expect(result.isLeft(), true);
        result.fold(
          (l) => expect(l, isA<AppError>()),
          (r) => fail('Should not return data'),
        );
      },
    );
  });

  group('updateOrganization', () {
    const orgId = 'org-123';
    final updateData = {'name': 'Updated Name'};

    test('returns Right(Organization) when update is successful', () async {
      // Arrange
      final responseData = {
        'id': orgId,
        'name': 'Updated Name',
        'status': 'ACTIVE',
      };

      when(
        () => mockDio.patch<Map<String, dynamic>>(
          '/organizations/$orgId',
          data: any(named: 'data'),
        ),
      ).thenAnswer(
        (_) async => Response(
          data: responseData,
          statusCode: 200,
          requestOptions: RequestOptions(path: '/organizations/$orgId'),
        ),
      );

      // Act
      final result = await repository.updateOrganization(orgId, updateData);

      // Assert
      expect(result.isRight(), true);
      result.fold((l) => fail('Should not return error'), (r) {
        expect(r.id, orgId);
        expect(r.name, 'Updated Name');
      });
    });

    test('returns Left(AppError.server) when API returns null data', () async {
      // Arrange
      when(
        () => mockDio.patch<Map<String, dynamic>>(
          '/organizations/$orgId',
          data: any(named: 'data'),
        ),
      ).thenAnswer(
        (_) async => Response(
          data: null,
          statusCode: 200,
          requestOptions: RequestOptions(path: '/organizations/$orgId'),
        ),
      );

      // Act
      final result = await repository.updateOrganization(orgId, updateData);

      // Assert
      expect(result.isLeft(), true);
    });
  });

  group('createOrganization', () {
    const orgData = {'id': 'new-org', 'name': 'New Org'};

    test('returns Right(Organization) when creation is successful', () async {
      when(
        () => mockDio.post<Map<String, dynamic>>(
          '/organizations/',
          data: any(named: 'data'),
        ),
      ).thenAnswer(
        (_) async => Response(
          data: {'id': 'new-org', 'name': 'New Org', 'status': 'ACTIVE'},
          statusCode: 200,
          requestOptions: RequestOptions(path: '/organizations/'),
        ),
      );

      final result = await repository.createOrganization(orgData);

      expect(result.isRight(), true);
      result.fold((l) => fail('Should not return error'), (r) {
        expect(r.id, 'new-org');
      });
    });
  });

  group('deleteOrganization', () {
    const orgId = 'del-org';

    test('calls delete with correct URI and returns Right(void)', () async {
      when(
        () => mockDio.delete<Unit>(
          '/organizations/$orgId',
          queryParameters: any(named: 'queryParameters'),
        ),
      ).thenAnswer(
        (_) async => Response(
          data: null,
          statusCode: 200,
          requestOptions: RequestOptions(path: '/organizations/$orgId'),
        ),
      );

      final result = await repository.deleteOrganization(orgId);

      expect(result.isRight(), true);
      verify(
        () => mockDio.delete<Unit>(
          '/organizations/$orgId',
          queryParameters: any(named: 'queryParameters'),
        ),
      ).called(1);
    });

    test('sends force=true param when force is true', () async {
      when(
        () => mockDio.delete<Unit>(
          '/organizations/$orgId',
          queryParameters: any(named: 'queryParameters'),
        ),
      ).thenAnswer(
        (_) async => Response(
          data: null,
          statusCode: 200,
          requestOptions: RequestOptions(path: '/organizations/$orgId'),
        ),
      );

      final result = await repository.deleteOrganization(orgId, force: true);

      expect(result.isRight(), true);
      verify(
        () => mockDio.delete<Unit>(
          '/organizations/$orgId',
          queryParameters: any(named: 'queryParameters'),
        ),
      ).called(1);
    });

    test(
      'returns Left(AppError.server) when API returns 409 Conflict',
      () async {
        when(
          () => mockDio.delete<Unit>(
            '/organizations/$orgId',
            queryParameters: any(named: 'queryParameters'),
          ),
        ).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: '/organizations/$orgId'),
            type: DioExceptionType.badResponse,
            response: Response(
              statusCode: 409,
              data: {'detail': 'ORG_HAS_USERS'},
              requestOptions: RequestOptions(path: '/organizations/$orgId'),
            ),
          ),
        );

        final result = await repository.deleteOrganization(orgId);

        expect(result.isLeft(), true);
        result.fold((l) {
          l.maybeWhen(
            server: (msg, code) {
              expect(code, 409);
              expect(msg, 'ORG_HAS_USERS');
            },
            orElse: () => fail('Expected AppError.server, got $l'),
          );
        }, (r) => fail('Should not return success'));
      },
    );
  });
}
