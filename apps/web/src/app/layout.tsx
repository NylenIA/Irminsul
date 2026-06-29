import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Irminsul — Archive astrale",
  description: "Observatoire tactique Genshin — version web (en construction).",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  );
}
