import "package:go_router/go_router.dart";

import "features/dashboard/dashboard_page.dart";
import "features/onboarding/onboarding_page.dart";

/// Navigation de l'app. Étape 1 : accueil (onboarding) -> tableau de bord.
final appRouter = GoRouter(
  initialLocation: "/",
  routes: [
    GoRoute(path: "/", builder: (context, state) => const OnboardingPage()),
    GoRoute(
      path: "/dashboard",
      builder: (context, state) => const DashboardPage(),
    ),
  ],
);
