//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:backend_api/src/model/user.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'login_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class LoginResponse {
  /// Returns a new [LoginResponse] instance.
  LoginResponse({

    required  this.user,

    required  this.tokenValid,

     this.debugMsg,
  });

  @JsonKey(
    
    name: r'user',
    required: true,
    
  )


  final User user;



  @JsonKey(
    
    name: r'token_valid',
    required: true,
    
  )


  final bool tokenValid;



  @JsonKey(
    
    name: r'debug_msg',
    required: false,
    
  )


  final String? debugMsg;





    @override
    bool operator ==(Object other) => identical(this, other) || other is LoginResponse &&
      other.user == user &&
      other.tokenValid == tokenValid &&
      other.debugMsg == debugMsg;

    @override
    int get hashCode =>
        user.hashCode +
        tokenValid.hashCode +
        (debugMsg == null ? 0 : debugMsg.hashCode);

  factory LoginResponse.fromJson(Map<String, dynamic> json) => _$LoginResponseFromJson(json);

  Map<String, dynamic> toJson() => _$LoginResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

