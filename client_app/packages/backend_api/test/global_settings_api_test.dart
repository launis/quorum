import 'package:test/test.dart';
import 'package:backend_api/backend_api.dart';

/// tests for GlobalSettingsApi
void main() {
  final instance = BackendApi().getGlobalSettingsApi();

  group(GlobalSettingsApi, () {
    // Get Settings
    //
    // Retrieves the current global system connection settings.
    //
    //Future<SystemSettings> getSettingsSettingsGet() async
    test('test getSettingsSettingsGet', () async {
      // TODO
    });

    // Update Settings
    //
    // Updates global system settings.  Requires ROOT.
    //
    //Future<SystemSettings> updateSettingsSettingsPatch(SystemSettings systemSettings, { String authorization }) async
    test('test updateSettingsSettingsPatch', () async {
      // TODO
    });
  });
}
