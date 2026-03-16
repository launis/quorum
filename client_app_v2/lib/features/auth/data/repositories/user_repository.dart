import 'package:client_app/core/network/api_client.dart';
import 'package:client_app/features/auth/domain/models/user.dart';
import 'package:client_app/core/error/app_exception.dart';
import 'package:client_app/core/error/validation_error_reason.dart';
import 'package:dio/dio.dart';
import 'package:fpdart/fpdart.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final userRepositoryProvider = Provider<UserRepository>((ref) {
  return UserRepository(ref.watch(apiClientProvider));
});

class UserRepository {
  final Dio _client;
  UserRepository(this._client);

  Future<Either<AppException, User>> fetchCurrentUser() async {
    try {
      final response = await _client.get<Map<String, dynamic>>('/iam/users/me');
      if (response.data == null) return Left(const AppException(detail: ''));
      return Right(User.fromJson(response.data!));
    } on DioException catch (e) {
      if (e.response?.statusCode == 404)
        return Left(AppException.notFound(''));
      if (e.response?.statusCode == 401)
        return Left(AppException.unauthorized());
      return Left(AppException(detail: ''));
    } catch (e) {
      return Left(AppException.unknown());
    }
  }

  Future<Either<AppException, User>> updateProfile(
    Map<String, dynamic> data,
  ) async {
    try {
      final response = await _client.patch<Map<String, dynamic>>(
        '/iam/users/me',
        data: data,
      );
      if (response.data == null) return Left(const AppException(detail: ''));
      return Right(User.fromJson(response.data!));
    } on DioException catch (e) {
      if (e.response?.statusCode == 400)
        return Left(AppException.validation(ValidationErrorReason.unknown.toString()));
      return Left(AppException(detail: ''));
    } catch (e) {
      return Left(AppException.unknown());
    }
  }
}
