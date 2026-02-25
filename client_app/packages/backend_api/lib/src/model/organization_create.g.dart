// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'organization_create.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$OrganizationCreateCWProxy {
  OrganizationCreate name(String name);

  OrganizationCreate adminEmail(String adminEmail);

  OrganizationCreate adminPassword(String adminPassword);

  OrganizationCreate adminName(String adminName);

  OrganizationCreate tpmLimit(int? tpmLimit);

  OrganizationCreate rpmLimit(int? rpmLimit);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `OrganizationCreate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// OrganizationCreate(...).copyWith(id: 12, name: "My name")
  /// ````
  OrganizationCreate call({
    String name,
    String adminEmail,
    String adminPassword,
    String adminName,
    int? tpmLimit,
    int? rpmLimit,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfOrganizationCreate.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfOrganizationCreate.copyWith.fieldName(...)`
class _$OrganizationCreateCWProxyImpl implements _$OrganizationCreateCWProxy {
  const _$OrganizationCreateCWProxyImpl(this._value);

  final OrganizationCreate _value;

  @override
  OrganizationCreate name(String name) => this(name: name);

  @override
  OrganizationCreate adminEmail(String adminEmail) =>
      this(adminEmail: adminEmail);

  @override
  OrganizationCreate adminPassword(String adminPassword) =>
      this(adminPassword: adminPassword);

  @override
  OrganizationCreate adminName(String adminName) => this(adminName: adminName);

  @override
  OrganizationCreate tpmLimit(int? tpmLimit) => this(tpmLimit: tpmLimit);

  @override
  OrganizationCreate rpmLimit(int? rpmLimit) => this(rpmLimit: rpmLimit);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `OrganizationCreate(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// OrganizationCreate(...).copyWith(id: 12, name: "My name")
  /// ````
  OrganizationCreate call({
    Object? name = const $CopyWithPlaceholder(),
    Object? adminEmail = const $CopyWithPlaceholder(),
    Object? adminPassword = const $CopyWithPlaceholder(),
    Object? adminName = const $CopyWithPlaceholder(),
    Object? tpmLimit = const $CopyWithPlaceholder(),
    Object? rpmLimit = const $CopyWithPlaceholder(),
  }) {
    return OrganizationCreate(
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
      adminEmail: adminEmail == const $CopyWithPlaceholder()
          ? _value.adminEmail
          // ignore: cast_nullable_to_non_nullable
          : adminEmail as String,
      adminPassword: adminPassword == const $CopyWithPlaceholder()
          ? _value.adminPassword
          // ignore: cast_nullable_to_non_nullable
          : adminPassword as String,
      adminName: adminName == const $CopyWithPlaceholder()
          ? _value.adminName
          // ignore: cast_nullable_to_non_nullable
          : adminName as String,
      tpmLimit: tpmLimit == const $CopyWithPlaceholder()
          ? _value.tpmLimit
          // ignore: cast_nullable_to_non_nullable
          : tpmLimit as int?,
      rpmLimit: rpmLimit == const $CopyWithPlaceholder()
          ? _value.rpmLimit
          // ignore: cast_nullable_to_non_nullable
          : rpmLimit as int?,
    );
  }
}

extension $OrganizationCreateCopyWith on OrganizationCreate {
  /// Returns a callable class that can be used as follows: `instanceOfOrganizationCreate.copyWith(...)` or like so:`instanceOfOrganizationCreate.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$OrganizationCreateCWProxy get copyWith =>
      _$OrganizationCreateCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

OrganizationCreate _$OrganizationCreateFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'OrganizationCreate',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const [
            'name',
            'admin_email',
            'admin_password',
            'admin_name',
          ],
        );
        final val = OrganizationCreate(
          name: $checkedConvert('name', (v) => v as String),
          adminEmail: $checkedConvert('admin_email', (v) => v as String),
          adminPassword: $checkedConvert('admin_password', (v) => v as String),
          adminName: $checkedConvert('admin_name', (v) => v as String),
          tpmLimit: $checkedConvert(
            'tpm_limit',
            (v) => (v as num?)?.toInt() ?? 100000,
          ),
          rpmLimit: $checkedConvert(
            'rpm_limit',
            (v) => (v as num?)?.toInt() ?? 60,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'adminEmail': 'admin_email',
        'adminPassword': 'admin_password',
        'adminName': 'admin_name',
        'tpmLimit': 'tpm_limit',
        'rpmLimit': 'rpm_limit',
      },
    );

Map<String, dynamic> _$OrganizationCreateToJson(OrganizationCreate instance) =>
    <String, dynamic>{
      'name': instance.name,
      'admin_email': instance.adminEmail,
      'admin_password': instance.adminPassword,
      'admin_name': instance.adminName,
      'tpm_limit': ?instance.tpmLimit,
      'rpm_limit': ?instance.rpmLimit,
    };
