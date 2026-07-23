import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Build statique servi par Tauri. En dev, `tauri dev` démarre ce serveur Vite
// (port 5173, cf. `devUrl` dans src-tauri/tauri.conf.json). On EXCLUT src-tauri/**
// du watcher : sinon Vite surveille target/ (artefacts de build Rust) et plante en
// EBUSY quand cargo verrouille un .exe pendant la compilation.
export default defineConfig({
  plugins: [react()],
  build: { outDir: "dist", emptyOutDir: true, target: "es2022" },
  clearScreen: false,
  server: {
    port: 5173,
    strictPort: true,
    watch: {
      ignored: ["**/src-tauri/**"],
    },
  },
});
