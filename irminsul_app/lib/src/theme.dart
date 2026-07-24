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

/// Thèmes par NATION (DA moodboards) + identité Irminsul.
const accentPalettes = <String, AccentPalette>{
  "irminsul": AccentPalette("irminsul", "Irminsul",
      Color(0xFFA78BFA), Color(0xFFEC4899), Color(0xFF22D3EE)),
  "mondstadt": AccentPalette("mondstadt", "Mondstadt · Liberté",
      Color(0xFF57C7B8), Color(0xFF9BE8D2), Color(0xFF3FB6FF)),
  "liyue": AccentPalette("liyue", "Liyue · Contrat",
      Color(0xFFF2A93B), Color(0xFFE8833A), Color(0xFFFFD9A0)),
  "inazuma": AccentPalette("inazuma", "Inazuma · Éternité",
      Color(0xFF9C7BFF), Color(0xFFF4A7C8), Color(0xFFC4B5FD)),
  "sumeru": AccentPalette("sumeru", "Sumeru · Sagesse",
      Color(0xFF5DBB63), Color(0xFFB5E48C), Color(0xFF2DD4BF)),
  "fontaine": AccentPalette("fontaine", "Fontaine · Justice",
      Color(0xFF3FA9F5), Color(0xFF22D3EE), Color(0xFFF2C14E)),
  "natlan": AccentPalette("natlan", "Natlan · Guerre",
      Color(0xFFFF6A3D), Color(0xFFFFB13D), Color(0xFFEC4899)),
  "nodkrai": AccentPalette("nodkrai", "Nod-Krai · Lune",
      Color(0xFF5C6BC0), Color(0xFFB8C4F0), Color(0xFF8FD8EA)),
  "snezhnaya": AccentPalette("snezhnaya", "Snezhnaya · Amour",
      Color(0xFF8FD8EA), Color(0xFFF6D27A), Color(0xFFDDF7FA)),
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
