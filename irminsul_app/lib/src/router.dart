import "package:flutter/material.dart";
import "package:go_router/go_router.dart";

import "features/dashboard/dashboard_page.dart";
import "features/guides/guide_detail_page.dart";
import "features/guides/guides_page.dart";
import "features/guides/leak_detail_page.dart";
import "features/onboarding/onboarding_page.dart";
import "features/placeholder/placeholder_page.dart";
import "features/settings/settings_page.dart";
import "shell/app_shell.dart";
import "widgets/data_sweep.dart";

/// Transition « Irminsul » : fondu + léger glissement, traversés par un
/// balayage de données (bande d'énergie + nœuds lumineux, couleurs du thème).
CustomTransitionPage<void> _fade(Widget child) => CustomTransitionPage<void>(
      child: child,
      transitionDuration: const Duration(milliseconds: 400),
      reverseTransitionDuration: const Duration(milliseconds: 260),
      transitionsBuilder: (context, animation, secondary, child) {
        final curved =
            CurvedAnimation(parent: animation, curve: Curves.easeOutCubic);
        return Stack(
          children: [
            FadeTransition(
              opacity: curved,
              child: SlideTransition(
                position: Tween<Offset>(
                  begin: const Offset(0.035, 0.02),
                  end: Offset.zero,
                ).animate(curved),
                child: ScaleTransition(
                  scale: Tween<double>(begin: 0.985, end: 1).animate(curved),
                  alignment: Alignment.center,
                  child: child,
                ),
              ),
            ),
            Positioned.fill(child: DataSweep(animation: animation)),
          ],
        );
      },
    );

final appRouter = GoRouter(
  initialLocation: "/",
  routes: [
    GoRoute(
      path: "/",
      pageBuilder: (context, state) => _fade(const OnboardingPage()),
    ),
    ShellRoute(
      builder: (context, state, child) =>
          AppShell(location: state.uri.path, child: child),
      routes: [
        GoRoute(
          path: "/dashboard",
          pageBuilder: (context, state) => _fade(const DashboardPage()),
        ),
        GoRoute(
          path: "/characters",
          pageBuilder: (context, state) =>
              _fade(const PlaceholderPage(tab: "characters")),
        ),
        GoRoute(
          path: "/teams",
          pageBuilder: (context, state) =>
              _fade(const PlaceholderPage(tab: "teams")),
        ),
        GoRoute(
          path: "/compare",
          pageBuilder: (context, state) =>
              _fade(const PlaceholderPage(tab: "compare")),
        ),
        GoRoute(
          path: "/guides",
          pageBuilder: (context, state) => _fade(const GuidesPage()),
        ),
        GoRoute(
          path: "/guides/leaks/:id",
          pageBuilder: (context, state) =>
              _fade(LeakDetailPage(id: state.pathParameters["id"] ?? "")),
        ),
        GoRoute(
          path: "/guides/:id",
          pageBuilder: (context, state) =>
              _fade(GuideDetailPage(id: state.pathParameters["id"] ?? "")),
        ),
        GoRoute(
          path: "/farm",
          pageBuilder: (context, state) =>
              _fade(const PlaceholderPage(tab: "farm")),
        ),
        GoRoute(
          path: "/settings",
          pageBuilder: (context, state) => _fade(const SettingsPage()),
        ),
      ],
    ),
  ],
);
