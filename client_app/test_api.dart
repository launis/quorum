import 'dart:convert';
import 'package:http/http.dart' as http;

void main() async {
  final res = await http.get(Uri.parse('http://127.0.0.1:8000/v1/config/components'));
  if (res.statusCode == 200) {
    final list = jsonDecode(res.body) as List;
    final Map<String, dynamic>? globalCtx = list.firstWhere(
        (c) => c['id'] == 'ca9d9ae7-41ce-44d4-8a8f-efd2e0bd80a9', 
        orElse: () => null
    );
    if (globalCtx != null) {
      print('Found globalCtx: \');
      
      try {
        if (globalCtx['name'] == null) globalCtx['name'] = globalCtx['id'];
        
        final id = globalCtx['id'];
        final slug = globalCtx['slug'];
        final name = globalCtx['name'];
        final type = globalCtx['type'];
        final content = globalCtx['content'];
        
        if (id == null) throw Exception('id null');
        if (name == null) throw Exception('name null');
        if (type == null) throw Exception('type null');
        // if content is missing, it will throw in freezed.
        print('All required fields present natively');
      } catch (e) {
        print('Failed simulated parse: \');
      }
    } else {
      print('GLOBAL_CONTEXT not found in API response');
    }
  }
}
