import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Build statique (sera servi par Tauri en Phase 1+). Pas de serveur HTTP exposé.
export default defineConfig({
  plugins: [react()],
  build: { outDir: "dist", emptyOutDir: true, target: "es2022" },
  clearScreen: false,
});
