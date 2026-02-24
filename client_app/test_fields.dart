import 'dart:convert';
import 'package:http/http.dart' as http;
void main() async {
  final res = await http.get(Uri.parse('http://127.0.0.1:8000/v1/config/components'));
  if (res.statusCode == 200) {
    final list = jsonDecode(res.body) as List;
    final item = list.firstWhere((c) => c['id'] == 'ca9d9ae7-41ce-44d4-8a8f-efd2e0bd80a9');
    
    // Simulating freezed exact checks
    print('Testing: ' + item['slug'].toString());
    if (item['name'] == null) print('Error: name is null');
    if (item['content'] == null) print('Error: content is null');
    if (item['type'] == null) print('Error: type is null');
  }
}
