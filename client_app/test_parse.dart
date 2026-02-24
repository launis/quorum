import 'dart:convert';
import 'package:http/http.dart' as http;
import 'lib/features/studio/domain/models/component_def.dart';

void main() async {
  final res = await http.get(Uri.parse('http://127.0.0.1:8000/v1/config/components'));
  if (res.statusCode == 200) {
    final list = jsonDecode(res.body) as List;
    final Map<String, dynamic>? globalCtx = list.firstWhere(
        (c) => c['id'] == 'ca9d9ae7-41ce-44d4-8a8f-efd2e0bd80a9', 
        orElse: () => null
    );
    if (globalCtx != null) {
      if (globalCtx['name'] == null) globalCtx['name'] = globalCtx['id'];
      try {
        final comp = StudioComponentDef.fromJson(globalCtx);
        print('Parsed successfully: ' + (comp.slug ?? ''));
      } catch (e) {
        print('Failed simulated parse: ' + e.toString());
      }
    }
  }
}
