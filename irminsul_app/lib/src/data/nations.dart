import "package:flutter/material.dart";

import "../theme.dart";

/// Identité visuelle d'une nation de Teyvat : couleurs et principe (idéal).
/// Base de la DA « chaque nation, son ambiance » (moodboards 2026-07-24).
class NationStyle {
  final String id;
  final String name;
  final String principle; // idéal de l'Archon / thème de la région
  final Color a; // couleur dominante
  final Color b; // couleur secondaire
  const NationStyle(this.id, this.name, this.principle, this.a, this.b);
}

const nations = <String, NationStyle>{
  "Mondstadt": NationStyle("mondstadt", "Mondstadt", "Liberté",
      Color(0xFF57C7B8), Color(0xFF9BE8D2)),
  "Liyue": NationStyle(
      "liyue", "Liyue", "Contrat", Color(0xFFF2A93B), Color(0xFFFFD9A0)),
  "Inazuma": NationStyle("inazuma", "Inazuma", "Éternité",
      Color(0xFF9C7BFF), Color(0xFFF4A7C8)),
  "Sumeru": NationStyle(
      "sumeru", "Sumeru", "Sagesse", Color(0xFF5DBB63), Color(0xFF2DD4BF)),
  "Fontaine": NationStyle("fontaine", "Fontaine", "Justice",
      Color(0xFF3FA9F5), Color(0xFFF2C14E)),
  "Natlan": NationStyle(
      "natlan", "Natlan", "Guerre", Color(0xFFFF6A3D), Color(0xFFFFB13D)),
  "Nod-Krai": NationStyle("nodkrai", "Nod-Krai", "Lune",
      Color(0xFF5C6BC0), Color(0xFFB8C4F0)),
  "Snezhnaya": NationStyle("snezhnaya", "Snezhnaya", "Amour",
      Color(0xFF8FD8EA), Color(0xFFF6D27A)),
};

const _fallbackNation =
    NationStyle("teyvat", "Teyvat", "Irminsul", kPurple, kCyan);

/// Style de nation depuis le champ `region` des données du jeu
/// ('' pour les Voyageurs/inclassés → identité Irminsul neutre).
NationStyle nationOf(String region) => nations[region] ?? _fallbackNation;
