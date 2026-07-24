import "dart:convert";
import "dart:io";

import "package:file_picker/file_picker.dart";
import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../../i18n/strings.dart";
import "../../state/providers.dart";
import "../../theme.dart";
import "../../widgets/glass_card.dart";

class OnboardingPage extends ConsumerStatefulWidget {
  const OnboardingPage({super.key});

  @override
  ConsumerState<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends ConsumerState<OnboardingPage> {
  final _uid = TextEditingController();

  @override
  void dispose() {
    _uid.dispose();
    super.dispose();
  }

  Future<void> _importGood(L l) async {
    try {
      final res = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ["json"],
      );
      final path = res?.files.single.path;
      if (path == null) return;

      final content = await File(path).readAsString();
      final dynamic data = jsonDecode(content);
      var count = 0;
      if (data is Map && data["characters"] is List) {
        count = (data["characters"] as List).length;
      }

      ref.read(accountProvider.notifier).state = AccountSummary(
        source: "GOOD",
        label: res!.files.single.name,
        characterCount: count,
      );
      if (mounted) context.go("/dashboard");
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("${l.t("importError")}$e")),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final locale = ref.watch(localeProvider);
    final l = L(locale);

    return Scaffold(
      body: Container(
        decoration: appBackground(),
        child: SafeArea(
          child: Stack(
            children: [
              Align(
                alignment: Alignment.topRight,
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: _LangToggle(current: locale.languageCode),
                ),
              ),
              Center(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(28),
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 880),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const _Logo(),
                        const SizedBox(height: 22),
                        Text(
                          l.t("welcomeTitle"),
                          style: const TextStyle(
                            fontSize: 30,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 10),
                        Text(
                          l.t("welcomeSubtitle"),
                          style: TextStyle(
                            fontSize: 14.5,
                            color: Colors.white.withValues(alpha: 0.6),
                          ),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 28),
                        Wrap(
                          spacing: 18,
                          runSpacing: 18,
                          alignment: WrapAlignment.center,
                          children: [
                            SizedBox(
                              width: 400,
                              child: _ImportGoodCard(
                                l: l,
                                onPressed: () => _importGood(l),
                              ),
                            ),
                            SizedBox(
                              width: 400,
                              child: _ImportEnkaCard(l: l, controller: _uid),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _Logo extends StatelessWidget {
  const _Logo();

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 62,
      height: 62,
      decoration: BoxDecoration(
        gradient: const LinearGradient(colors: [kPurple, kPink]),
        borderRadius: BorderRadius.circular(18),
        boxShadow: [
          BoxShadow(
            color: kPink.withValues(alpha: 0.35),
            blurRadius: 22,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: const Center(
        child: Text("🌳", style: TextStyle(fontSize: 30)),
      ),
    );
  }
}

class _ImportGoodCard extends StatelessWidget {
  final L l;
  final VoidCallback onPressed;
  const _ImportGoodCard({required this.l, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.upload_file, color: kPurple, size: 28),
          const SizedBox(height: 14),
          Text(
            l.t("importGoodTitle"),
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            l.t("importGoodDesc"),
            style: TextStyle(
              fontSize: 13,
              color: Colors.white.withValues(alpha: 0.6),
            ),
          ),
          const SizedBox(height: 18),
          FilledButton.icon(
            onPressed: onPressed,
            icon: const Icon(Icons.folder_open, size: 18),
            label: Text(l.t("importGoodButton")),
          ),
        ],
      ),
    );
  }
}

class _ImportEnkaCard extends StatelessWidget {
  final L l;
  final TextEditingController controller;
  const _ImportEnkaCard({required this.l, required this.controller});

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.badge_outlined, color: kPink, size: 28),
          const SizedBox(height: 14),
          Text(
            l.t("importEnkaTitle"),
            style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            l.t("importEnkaDesc"),
            style: TextStyle(
              fontSize: 13,
              color: Colors.white.withValues(alpha: 0.6),
            ),
          ),
          const SizedBox(height: 18),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: controller,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    hintText: l.t("importEnkaHint"),
                    filled: true,
                    fillColor: Colors.white.withValues(alpha: 0.05),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding:
                        const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              FilledButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(l.t("enkaComingSoon"))),
                  );
                },
                child: Text(l.t("importEnkaButton")),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _LangToggle extends ConsumerWidget {
  final String current;
  const _LangToggle({required this.current});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    Widget chip(String code) {
      final active = current == code;
      return GestureDetector(
        onTap: () =>
            ref.read(localeProvider.notifier).state = Locale(code),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
          margin: const EdgeInsets.only(left: 6),
          decoration: BoxDecoration(
            gradient: active
                ? const LinearGradient(colors: [kPurple, kPink])
                : null,
            color: active ? null : Colors.white.withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            code.toUpperCase(),
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: active ? Colors.white : Colors.white70,
            ),
          ),
        ),
      );
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [chip("fr"), chip("en")],
    );
  }
}
