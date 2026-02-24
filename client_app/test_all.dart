import 'dart:convert';
import 'package:http/http.dart' as http;
import 'lib/features/studio/domain/models/component_def.dart';

void main() async {
  print('Testing agents');
  var r1 = await http.get(Uri.parse('http://127.0.0.1:8000/v1/config/agents'));
  for (var i in jsonDecode(r1.body)) {
    try { StudioComponentDef.fromJson(i); } catch (e) { print('Agent Fail: \ -> '); }
  }
  print('Testing outputs');
  var r2 = await http.get(Uri.parse('http://127.0.0.1:8000/v1/config/outputs'));
  for (var i in jsonDecode(r2.body)) {
    try { StudioComponentDef.fromJson(i); } catch (e) { print('Output Fail: \ -> '); }
  }
  print('Done.');
}
