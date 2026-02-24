void main() {
  final Map<String, dynamic> data = {'id': 'my-id', 'content': 'hello'};
  if (data['name'] == null) {
    data['name'] = data['id'];
  }
  print('Result: ' + data['name'].toString());
}
