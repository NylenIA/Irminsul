use serde::Serialize;

#[derive(Serialize)]
struct AppInfo {
    name: &'static str,
    version: &'static str,
}

/// Métadonnées réelles de l'application (aucune donnée de jeu factice).
#[tauri::command]
fn app_info() -> AppInfo {
    AppInfo {
        name: "Irminsul",
        version: env!("CARGO_PKG_VERSION"),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![app_info])
        .run(tauri::generate_context!())
        .expect("erreur au démarrage de l'application Tauri");
}
