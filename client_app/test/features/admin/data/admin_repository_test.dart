import 'package:client_app/core/error/app_error.dart';
import 'package:client_app/features/admin/data/admin_repository.dart';
import 'package:client_app/features/admin/domain/models/queue_stats.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

@GenerateMocks([Dio])
import 'admin_repository_test.mocks.dart';

void main() {
  late AdminRepository repository;
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();
    repository = AdminRepository(mockDio);
  });

  group('getUsersByOrganization', () {
    const orgId = 'org-123';
    final tUser = User(
      uid: 'user-1',
      email: 'test@test.com',
      displayName: 'Test User',
      role: UserRole.member,
      organizationId: orgId,
    );
    final tList = [tUser.toJson()];

    test('should return List<User> on success', () async {
      when(mockDio.get<List<dynamic>>(any)).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          data: tList,
          statusCode: 200,
        ),
      );

      final result = await repository.getUsersByOrganization(orgId);

      expect(result.isRight(), true);
      result.fold((l) => fail('Should be Right'), (r) {
        expect(r, isA<List<User>>());
        expect(r.first.uid, 'user-1');
      });
    });

    test('should return AppError on failure', () async {
      when(mockDio.get<List<dynamic>>(any)).thenThrow(
        DioException(
          requestOptions: RequestOptions(path: ''),
          response: Response(
            requestOptions: RequestOptions(path: ''),
            statusCode: 404,
            data: {'detail': 'Not found'},
          ),
          type: DioExceptionType.badResponse,
        ),
      );

      final result = await repository.getUsersByOrganization(orgId);

      expect(result.isLeft(), true);
      result.fold(
        (l) => expect(l, isA<AppError>()),
        (r) => fail('Should be Left'),
      );
    });
  });

  group('updateUserRole', () {
    const userId = 'user-1';
    const newRole = 'ADMIN';

    test('should return Right(null) on success', () async {
      when(mockDio.put<void>(any, data: anyNamed('data'))).thenAnswer(
        (_) async =>
            Response(requestOptions: RequestOptions(path: ''), statusCode: 200),
      );

      final result = await repository.updateUserRole(userId, newRole);

      expect(result.isRight(), true);
    });

    test(
      'should map LAST_ADMIN_PROTECTION to demoteLastAdmin validation error',
      () async {
        when(mockDio.put<void>(any, data: anyNamed('data'))).thenThrow(
          DioException(
            requestOptions: RequestOptions(path: ''),
            response: Response(
              requestOptions: RequestOptions(path: ''),
              statusCode: 409,
              data: {
                'detail': {'error_code': 'LAST_ADMIN_PROTECTION'},
              },
            ),
            type: DioExceptionType.badResponse,
          ),
        );

        final result = await repository.updateUserRole(userId, newRole);

        expect(result.isLeft(), true);
        result.fold((l) {
          expect(l, isA<AppError>());
          l.maybeWhen(
            validation:
                (reason) =>
                    expect(reason, ValidationErrorReason.demoteLastAdmin),
            orElse: () => fail('Wrong error type'),
          );
        }, (r) => fail('Should be Left'));
      },
    );
  });

  group('getQueueStats', () {
    final tStats = QueueStats(queuedJobs: 1, activeJobs: 2, deadJobs: 0);

    test('should return QueueStats on success', () async {
      when(mockDio.get<Map<String, dynamic>>(any)).thenAnswer(
        (_) async => Response(
          requestOptions: RequestOptions(path: ''),
          data: tStats.toJson(),
          statusCode: 200,
        ),
      );

      final result = await repository.getQueueStats();

      expect(result.isRight(), true);
      result.fold((l) => fail('Should be Right'), (r) => expect(r, tStats));
    });
  });
}
