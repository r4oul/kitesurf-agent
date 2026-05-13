import 'package:flutter/material.dart';

// ── DARK THEME (current) ──────────────────────────────────────────────────
// To revert to light theme, swap the const below to kLightTheme

const kAppBarColor       = Color(0xFF0D1B2A);  // deep navy
const kAppBarBottom      = Color(0xFF0A1520);  // darker navy
const kBackground        = Color(0xFF0D1B2A);  // page background
const kCardColor         = Color(0xFF132236);  // card surface
const kAccent            = Color(0xFF00D4FF);  // electric cyan
const kAccentText        = Color(0xFF0D1B2A);  // text on cyan buttons
const kTextPrimary       = Colors.white;
const kTextSecondary     = Color(0xFFB0BEC5);
const kChipSelected      = kAccent;
const kChipSelectedText  = kAppBarColor;
const kChipUnselected    = Color(0xFF1E3A50);
const kNavBar            = Color(0xFF0A1520);
const kNavSelected       = kAccent;

// ── LIGHT THEME (original) ───────────────────────────────────────────────
// const kAppBarColor      = Color(0xFF0077B6);
// const kAppBarBottom     = Color(0xFF005F92);
// const kBackground       = Color(0xFFF0F4F8);
// const kCardColor        = Colors.white;
// const kAccent           = Color(0xFF0077B6);
// const kAccentText       = Colors.white;
// const kTextPrimary      = Color(0xFF1A202C);
// const kTextSecondary    = Color(0xFF718096);
// const kChipSelected     = Colors.white;
// const kChipSelectedText = Color(0xFF0077B6);
// const kChipUnselected   = Color(0x40FFFFFF);  // white24
// const kNavBar           = Colors.white;
// const kNavSelected      = Color(0xFF0077B6);

ThemeData buildTheme() {
  return ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.dark(
      primary: kAccent,
      surface: kCardColor,
      onSurface: kTextPrimary,
    ),
    scaffoldBackgroundColor: kBackground,
    cardTheme: CardThemeData(
      color: kCardColor,
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
    navigationBarTheme: NavigationBarThemeData(
      backgroundColor: kNavBar,
      indicatorColor: kAccent.withOpacity(0.2),
      iconTheme: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const IconThemeData(color: kAccent);
        }
        return const IconThemeData(color: Color(0xFF607D8B));
      }),
      labelTextStyle: WidgetStateProperty.resolveWith((states) {
        if (states.contains(WidgetState.selected)) {
          return const TextStyle(color: kAccent, fontWeight: FontWeight.bold, fontSize: 12);
        }
        return const TextStyle(color: Color(0xFF607D8B), fontSize: 12);
      }),
    ),
    dividerColor: const Color(0xFF1E3A50),
  );
}
