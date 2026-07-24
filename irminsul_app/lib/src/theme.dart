import "package:flutter/material.dart";

/// Couleurs de base (fond). Le LOGO garde ses couleurs Irminsul (violet/cyan)
/// quel que soit le thème — seul l'accent de l'app change.
const kBg = Color(0xFF07070C);
const kSurface = Color(0xFF0E0E16);

// Couleurs « identité Irminsul » (utilisées par le logo, jamais retintées).
const kPurple = Color(0xFFA78BFA);
const kCyan = Color(0xFF22D3EE);
const kPink = Color(0xFFEC4899);

/// Palette d'accent choisie par l'utilisateur.
class AccentPalette {
  final String id;
  final String name;
  final Color primary;
  final Color secondary;
  final Color tertiary;
  const AccentPalette(
    this.id,
    this.name,
    this.primary,
    this.secondary,
    this.tertiary,
  );
}

const accentPalettes = <String, AccentPalette>{
  "irminsul": AccentPalette("irminsul", "Irminsul",
      Color(0xFFA78BFA), Color(0xFFEC4899), Color(0xFF22D3EE)),
  "sumeru": AccentPalette("sumeru", "Sumeru",
      Color(0xFF5DBB63), Color(0xFFB5E48C), Color(0xFF2DD4BF)),
  "hydro": AccentPalette("hydro", "Hydro",
      Color(0xFF3FB6FF), Color(0xFF22D3EE), Color(0xFF6366F1)),
  "pyro": AccentPalette("pyro", "Pyro",
      Color(0xFFFF6A4D), Color(0xFFF59E0B), Color(0xFFEC4899)),
  "geo": AccentPalette("geo", "Geo",
      Color(0xFFF2C14E), Color(0xFFFBBF24), Color(0xFFFDE68A)),
  "electro": AccentPalette("electro", "Electro",
      Color(0xFFB98BFF), Color(0xFF8B5CF6), Color(0xFFE879F9)),
  "sakura": AccentPalette("sakura", "Sakura",
      Color(0xFFF472B6), Color(0xFFEC4899), Color(0xFFC084FC)),
};

AccentPalette paletteOf(String id) =>
    accentPalettes[id] ?? accentPalettes["irminsul"]!;

/// Couleurs des éléments Genshin (anneaux des portraits, accents des teams).
const elementColors = <String, Color>{
  "pyro": Color(0xFFFF6A4D),
  "hydro": Color(0xFF3FB6FF),
  "electro": Color(0xFFB98BFF),
  "cryo": Color(0xFF8FE3EA),
  "anemo": Color(0xFF6FD6B6),
  "geo": Color(0xFFF2C14E),
  "dendro": Color(0xFF9AD24F),
};

Color elementColor(String e) => elementColors[e] ?? kPurple;

ThemeData buildTheme(AccentPalette p) {
  final scheme = ColorScheme.fromSeed(
    seedColor: p.primary,
    brightness: Brightness.dark,
  ).copyWith(
    primary: p.primary,
    secondary: p.secondary,
    tertiary: p.tertiary,
    surface: kSurface,
  );

  return ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: scheme,
    scaffoldBackgroundColor: kBg,
    fontFamily: "Segoe UI",
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: p.primary,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    ),
  );
}
