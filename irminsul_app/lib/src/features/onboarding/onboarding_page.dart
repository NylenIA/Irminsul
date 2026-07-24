import "dart:io";

import "package:file_picker/file_picker.dart";
import "package:flutter/material.dart";
import "package:flutter_riverpod/flutter_riverpod.dart";
import "package:go_router/go_router.dart";

import "../../i18n/strings.dart";
import "../../services/box_service.dart";
import "../../services/enka_service.dart";
import "../../state/providers.dart";
import "../../widgets/aurora_background.dart";
import "../../widgets/glass_card.dart";
import "../../widgets/irminsul_logo.dart";

class OnboardingPage extends ConsumerStatefulWidget {
  const OnboardingPage({super.key});

  @override
  ConsumerState<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends ConsumerState<OnboardingPage> {
  final _uid = TextEditingController();
  bool _enkaLoading = false;

  @override
  void dispose() {
    _uid.dispose();
    super.dispose();
  }

  Future<void> _importEnka(L l) async {
    if (_enkaLoading) return;
    setState(() => _enkaLoading = true);
    try {
      final r = await EnkaService().fetch(_uid.text);
      ref.read(accountProvider.notifier).state = AccountSummary(
        source: "Enka",
        label: "UID ${_uid.text.trim()}",
        characterCount: r.characterCount,
        playerName: r.nickname,
      );
      if (mounted) context.go("/dashboard");
    } on EnkaException catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(e.message)));
      }
    } finally {
      if (mounted) setState(() => _enkaLoading = false);
    }
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
      final name = res!.files.single.name;
      // parse complet (persos, constellations, niveaux, ER artefacts)…
      final box = BoxService.parse(content, label: name);
      // …et persistance locale : la box survit au redémarrage.
      await BoxService.save(content, name);
      ref.invalidate(boxProvider);

      ref.read(accountProvider.notifier).state = AccountSummary(
        source: "GOOD",
        label: name,
        characterCount: box.count,
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
      body: AuroraBackground(
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
                        const IrminsulLogo(size: 120),
                        const SizedBox(height: 18),
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
                              child: _ImportEnkaCard(
                                l: l,
                                controller: _uid,
                                loading: _enkaLoading,
                                onSubmit: () => _importEnka(l),
                              ),
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

class _ImportGoodCard extends StatelessWidget {
  final L l;
  final VoidCallback onPressed;
  const _ImportGoodCard({required this.l, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return GlassCard(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.upload_file, color: cs.primary, size: 28),
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
  final bool loading;
  final VoidCallback onSubmit;
  const _ImportEnkaCard({
    required this.l,
    required this.controller,
    required this.loading,
    required this.onSubmit,
  });

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return GlassCard(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.badge_outlined, color: cs.secondary, size: 28),
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
          const SizedBox(height: 4),
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
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 14,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              FilledButton(
                onPressed: loading ? null : onSubmit,
                child: loading
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : Text(l.t("importEnkaButton")),
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
    final cs = Theme.of(context).colorScheme;
    Widget chip(String code) {
      final active = current == code;
      return GestureDetector(
        onTap: () {
          ref.read(localeProvider.notifier).state = Locale(code);
          persistSetting("lang", code);
        },
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
          margin: const EdgeInsets.only(left: 6),
          decoration: BoxDecoration(
            gradient: active
                ? LinearGradient(colors: [cs.primary, cs.secondary])
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
