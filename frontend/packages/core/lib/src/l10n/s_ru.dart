// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 's.dart';

// ignore_for_file: type=lint

/// The translations for Russian (`ru`).
class SRu extends S {
  SRu([String locale = 'ru']) : super(locale);

  @override
  String get hello => 'Привет!';

  @override
  String welcome(Object name) {
    return 'Добро пожаловать, $name!';
  }
}
