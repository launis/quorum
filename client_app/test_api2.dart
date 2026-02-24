import 'dart:convert';
import 'package:http/http.dart' as http;
void main() async {
  final res1 = await http.get(Uri.parse('http://127.0.0.1:8000/v1/config/agents'));
  print('Agents: \');
  final res2 = await http.get(Uri.parse('http://127.0.0.1:8000/v1/config/outputs'));
  print('Outputs: \');
}
