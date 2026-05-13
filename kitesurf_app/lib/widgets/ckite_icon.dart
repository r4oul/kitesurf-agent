import 'package:flutter/material.dart';
import 'dart:math' as math;

class CKiteIcon extends StatelessWidget {
  final double size;
  final Color color;

  const CKiteIcon({super.key, this.size = 28, this.color = Colors.white});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      size: Size(size, size),
      painter: _CKitePainter(color: color),
    );
  }
}

class _CKitePainter extends CustomPainter {
  final Color color;
  _CKitePainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = size.width * 0.08
      ..strokeCap = StrokeCap.round;

    final fillPaint = Paint()
      ..color = color.withOpacity(0.3)
      ..style = PaintingStyle.fill;

    final w = size.width;
    final h = size.height;

    // C-kite arc — wide leading edge across the top
    final path = Path();
    path.moveTo(w * 0.1, h * 0.55);
    path.cubicTo(
      w * 0.0, h * 0.1,   // left control
      w * 1.0, h * 0.1,   // right control
      w * 0.9, h * 0.55,  // right end
    );
    // Bottom trailing edge curves back in
    path.cubicTo(
      w * 0.85, h * 0.75,
      w * 0.15, h * 0.75,
      w * 0.1, h * 0.55,
    );
    path.close();

    canvas.drawPath(path, fillPaint);
    canvas.drawPath(path, paint);

    // Centre strut
    final strutPaint = Paint()
      ..color = color
      ..strokeWidth = size.width * 0.06
      ..strokeCap = StrokeCap.round;
    canvas.drawLine(
      Offset(w * 0.5, h * 0.2),
      Offset(w * 0.5, h * 0.72),
      strutPaint,
    );

    // Bar & lines
    final linePaint = Paint()
      ..color = color.withOpacity(0.7)
      ..strokeWidth = size.width * 0.04
      ..strokeCap = StrokeCap.round;

    // Lines from kite tips to bar
    canvas.drawLine(Offset(w * 0.1, h * 0.55), Offset(w * 0.35, h * 0.95), linePaint);
    canvas.drawLine(Offset(w * 0.9, h * 0.55), Offset(w * 0.65, h * 0.95), linePaint);

    // Bar
    canvas.drawLine(Offset(w * 0.25, h * 0.95), Offset(w * 0.75, h * 0.95), paint);
  }

  @override
  bool shouldRepaint(_CKitePainter old) => old.color != color;
}
