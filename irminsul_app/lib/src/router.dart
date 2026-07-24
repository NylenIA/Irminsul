import "package:flutter/material.dart";
import "package:go_router/go_router.dart";

import "features/dashboard/dashboard_page.dart";
import "features/onboarding/onboarding_page.dart";
import "features/placeholder/placeholder_page.dart";
import "features/settings/settings_page.dart";
import "shell/app_shell.dart";

/// Transition douce (fondu + léger glissement) — fluidité demandée.
CustomTransitionPage<void> _fade(Widget child) => CustomTransitionPage<void>(
      child: child,
      transitionDuration: const Duration(milliseconds: 380),
      reverseTransitionDuration: const Duration(milliseconds: 260),
      transitionsBuilder: (context, animation, secondary, child) {
        final curved =
            CurvedAnimation(parent: animation, curve: Curves.easeOutCubic);
        return FadeTransition(
          opacity: curved,
          child: SlideTransition(
            position: Tween<Offset>(
              begin: const Offset(0, 0.03),
              end: Offset.zero,
            ).animate(curved),
            child: child,
          ),
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
          pageBuilder: (context, state) =>
              _fade(const PlaceholderPage(tab: "guides")),
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
