//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/subscription_status.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'organization_update.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class OrganizationUpdate {
  /// Returns a new [OrganizationUpdate] instance.
  OrganizationUpdate({

     this.name,

     this.tier,

     this.contactEmail,

     this.billingId,

     this.subscriptionStatus,

     this.quotaLimit,

     this.tpmLimit,

     this.rpmLimit,

     this.settingsOverride,
  });

  @JsonKey(
    
    name: r'name',
    required: false,
    
  )


  final String? name;



  @JsonKey(
    
    name: r'tier',
    required: false,
    
  )


  final String? tier;



  @JsonKey(
    
    name: r'contact_email',
    required: false,
    
  )


  final String? contactEmail;



  @JsonKey(
    
    name: r'billing_id',
    required: false,
    
  )


  final String? billingId;



  @JsonKey(
    
    name: r'subscription_status',
    required: false,
    
  )


  final SubscriptionStatus? subscriptionStatus;



  @JsonKey(
    
    name: r'quota_limit',
    required: false,
    
  )


  final num? quotaLimit;



  @JsonKey(
    
    name: r'tpm_limit',
    required: false,
    
  )


  final int? tpmLimit;



  @JsonKey(
    
    name: r'rpm_limit',
    required: false,
    
  )


  final int? rpmLimit;



  @JsonKey(
    
    name: r'settings_override',
    required: false,
    
  )


  final Map<String, Object>? settingsOverride;





    @override
    bool operator ==(Object other) => identical(this, other) || other is OrganizationUpdate &&
      other.name == name &&
      other.tier == tier &&
      other.contactEmail == contactEmail &&
      other.billingId == billingId &&
      other.subscriptionStatus == subscriptionStatus &&
      other.quotaLimit == quotaLimit &&
      other.tpmLimit == tpmLimit &&
      other.rpmLimit == rpmLimit &&
      other.settingsOverride == settingsOverride;

    @override
    int get hashCode =>
        (name == null ? 0 : name.hashCode) +
        (tier == null ? 0 : tier.hashCode) +
        (contactEmail == null ? 0 : contactEmail.hashCode) +
        (billingId == null ? 0 : billingId.hashCode) +
        (subscriptionStatus == null ? 0 : subscriptionStatus.hashCode) +
        (quotaLimit == null ? 0 : quotaLimit.hashCode) +
        (tpmLimit == null ? 0 : tpmLimit.hashCode) +
        (rpmLimit == null ? 0 : rpmLimit.hashCode) +
        (settingsOverride == null ? 0 : settingsOverride.hashCode);

  factory OrganizationUpdate.fromJson(Map<String, dynamic> json) => _$OrganizationUpdateFromJson(json);

  Map<String, dynamic> toJson() => _$OrganizationUpdateToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

