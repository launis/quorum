import 'package:flutter/material.dart';
import 'package:client_app/features/sdui/models/sdui_render_payload.dart';
import 'package:client_app/features/sdui/utils/sdui_translator.dart';

/// Render a dynamic 1D gauge component calculating percentage visually.
class Gauge1DWidget extends StatelessWidget {
  final SduiComponent component;

  const Gauge1DWidget({super.key, required this.component});

  @override
  Widget build(BuildContext context) {
    // Zero-Math constraints: we compute exactly how much width to fill securely
    final maxVal = component.scaleMax > 0 ? component.scaleMax : 100.0;
    final double raw = component.value;
    final double pct = (raw / maxVal).clamp(0.0, 1.0);

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              component.title.isNotEmpty ? SduiTranslator.translate(context, component.title) : 'Gauge',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: Color(0xFF2C3E50),
              ),
            ),
            const SizedBox(height: 15),
            Center(
              child: Column(
                children: [
                  Text(
                    '${raw.toStringAsFixed(1)} / ${maxVal.toStringAsFixed(1)}',
                    style: const TextStyle(
                      fontSize: 52,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF1E88E5), // Matches PDF V6
                    ),
                  ),
                  if (component.scaleText.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.only(top: 8.0),
                      child: Text(
                        component.scaleText,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: Color(0xFF555555),
                        ),
                      ),
                    ),
                ],
              ),
            ),
            const SizedBox(height: 25),
            
            // The Gauge Bar
            Container(
              height: 32,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(12),
                boxShadow: const [
                  BoxShadow(
                    color: Colors.black12,
                    blurRadius: 4,
                    offset: Offset(0, 2),
                    blurStyle: BlurStyle.inner,
                  )
                ],
              ),
              clipBehavior: Clip.antiAlias,
              child: Stack(
                children: [
                  FractionallySizedBox(
                    widthFactor: pct,
                    heightFactor: 1.0,
                    child: Container(
                      decoration: const BoxDecoration(
                        gradient: LinearGradient(
                          colors: [Color(0xFF2196F3), Color(0xFF4CAF50)],
                          begin: Alignment.centerLeft,
                          end: Alignment.centerRight,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
