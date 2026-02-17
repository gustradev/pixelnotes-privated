import 'package:flutter_test/flutter_test.dart';
import 'package:pixel_notes/main.dart';

void main() {
  testWidgets('Pixel Notes app renders', (WidgetTester tester) async {
    await tester.pumpWidget(const PixelNotesApp());
    expect(find.text('Pixel Notes'), findsOneWidget);
  });
}
