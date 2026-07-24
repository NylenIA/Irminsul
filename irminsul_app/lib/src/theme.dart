import "package:flutter/material.dart";

/// Palette « Helios + Genshin » : sombre profond, accents violet/rose.
const kBg = Color(0xFF07070C);
const kPurple = Color(0xFFA78BFA);
const kPink = Color(0xFFEC4899);
const kSurface = Color(0xFF0E0E16);

ThemeData buildTheme() {
  final scheme = ColorScheme.fromSeed(
    seedColor: kPurple,
    brightness: Brightness.dark,
  ).copyWith(secondary: kPink, surface: kSurface);

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

/// Fond dégradé partagé (lueur violette en haut à gauche).
BoxDecoration appBackground() => const BoxDecoration(
      gradient: RadialGradient(
        center: Alignment(-0.9, -1.0),
        radius: 1.5,
        colors: [Color(0x33A78BFA), kBg],
        stops: [0.0, 0.65],
      ),
    );
