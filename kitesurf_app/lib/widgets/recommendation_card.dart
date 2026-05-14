import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/recommendation.dart';
import '../screens/beach_forecast_screen.dart';
import '../theme.dart';

class RecommendationCard extends StatelessWidget {
  final Recommendation recommendation;
  final String riderLevel;

  const RecommendationCard({super.key, required this.recommendation, this.riderLevel = 'intermediate'});

  @override
  Widget build(BuildContext context) {
    final r = recommendation;
    return Container(
      decoration: BoxDecoration(
        color: kCardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF1E3A50), width: 1),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: GestureDetector(
                  onTap: () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (_) => BeachForecastScreen(
                        beachId: r.beachId,
                        beachName: r.beachName,
                        riderLevel: riderLevel,
                      ),
                    ),
                  ),
                  child: Row(
                    children: [
                      Text(r.beachName,
                          style: const TextStyle(
                              fontSize: 17, fontWeight: FontWeight.bold, color: kTextPrimary)),
                      const SizedBox(width: 4),
                      const Icon(Icons.chevron_right, size: 18, color: kAccent),
                    ],
                  ),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: Color(r.scoreColor).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Color(r.scoreColor), width: 1),
                ),
                child: Text(r.scoreLabel,
                    style: TextStyle(
                        color: Color(r.scoreColor),
                        fontWeight: FontWeight.bold,
                        fontSize: 13)),
              ),
            ],
          ),
          const SizedBox(height: 10),
          if (r.sewageStatus == 'discharging')
            _row('🚫', 'Sewage discharge active nearby', const Color(0xFFEF5350)),
          if (r.sewageStatus == 'offline')
            _row('📡', 'Sewage monitor offline', const Color(0xFF9E9E9E)),
          if (r.reasons.isNotEmpty)
            ...r.reasons.map((reason) => _row('✅', reason, const Color(0xFF4CAF50))),
          if (r.warnings.isNotEmpty)
            ...r.warnings.map((w) => _row('⚠️', w, const Color(0xFFFF9800))),
          if (r.hazards != null && r.hazards!.isNotEmpty) ...[
            const SizedBox(height: 6),
            _row('🚨', r.hazards!, const Color(0xFFEF5350)),
          ],
          if (r.notes != null && r.notes!.isNotEmpty) ...[
            const SizedBox(height: 6),
            _row('📝', r.notes!, kTextSecondary),
          ],
          if (r.whatsappGroups.isNotEmpty) ...[
            const SizedBox(height: 10),
            Divider(color: const Color(0xFF1E3A50)),
            const SizedBox(height: 4),
            ...r.whatsappGroups.map((group) => _whatsappButton(group)),
          ],
        ],
      ),
    );
  }

  Widget _row(String emoji, String text, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 14)),
          const SizedBox(width: 6),
          Expanded(child: Text(text, style: TextStyle(fontSize: 13, color: color))),
        ],
      ),
    );
  }

  Widget _whatsappButton(Map<String, dynamic> group) {
    return Padding(
      padding: const EdgeInsets.only(top: 6),
      child: OutlinedButton.icon(
        icon: const Text('💬', style: TextStyle(fontSize: 16)),
        label: Text(group['name'] ?? 'WhatsApp Group',
            style: const TextStyle(fontSize: 13)),
        style: OutlinedButton.styleFrom(
          foregroundColor: const Color(0xFF25D366),
          side: const BorderSide(color: Color(0xFF25D366)),
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
        onPressed: () async {
          final url = Uri.parse(group['invite_link'] ?? '');
          if (await canLaunchUrl(url)) launchUrl(url);
        },
      ),
    );
  }
}
