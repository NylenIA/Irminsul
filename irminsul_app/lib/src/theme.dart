import "package:flutter/material.dart";

/// Palette « Irminsul » : sombre profond, arbre-monde de données.
/// Violet/rose (accent) + cyan (le « côté informatique » / data-tree).
const kBg = Color(0xFF07070C);
const kPurple = Color(0xFFA78BFA);
const kPink = Color(0xFFEC4899);
const kCyan = Color(0xFF22D3EE);
const kSurface = Color(0xFF0E0E16);

ThemeData buildTheme() {
  final scheme = ColorScheme.fromSeed(
    seedColor: kPurple,
    brightness: Brightness.dark,
  ).copyWith(secondary: kPink, tertiary: kCyan, surface: kSurface);

  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: scheme,
    scaffoldBackgroundColor: kBg,
    fontFamily: "Segoe UI",
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: kPurple,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
  );
}
