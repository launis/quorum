import 'package:firebase_auth/firebase_auth.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'firebase_instance_provider.g.dart';

@Riverpod(keepAlive: true)
FirebaseAuth firebaseAuthInstance(Ref ref) {
  return FirebaseAuth.instance;
}
