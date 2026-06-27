use serde::Serialize;
use std::path::PathBuf;
use std::process::Command;

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

fn project_root() -> PathBuf {
    std::env::var("IRMINSUL_PROJECT_ROOT")
        .map(PathBuf::from)
        .unwrap_or_else(|_| std::env::current_dir().unwrap_or_else(|_| PathBuf::from(".")))
}

/// Appelle le moteur Python (service local typé) et renvoie sa sortie JSON brute.
/// En dev : python du projet (`IRMINSUL_PYTHON`) + `PYTHONPATH=src`. En prod : un
/// sidecar empaqueté remplacera l'interpréteur (à brancher ultérieurement).
/// Aucun secret n'est passé en argument de processus.
fn run_engine(args: &[&str]) -> Result<String, String> {
    let root = project_root();
    let python = std::env::var("IRMINSUL_PYTHON").unwrap_or_else(|_| "python".to_string());
    let output = Command::new(python)
        .arg("-m")
        .arg("irminsul.account_ipc")
        .args(args)
        .current_dir(&root)
        .env("PYTHONPATH", root.join("src"))
        .env("PYTHONUTF8", "1")
        .env("IRMINSUL_PROJECT_ROOT", &root)
        .output()
        .map_err(|e| format!("Moteur introuvable ou non exécutable : {e}"))?;
    if output.status.success() {
        Ok(String::from_utf8_lossy(&output.stdout).into_owned())
    } else {
        Err(String::from_utf8_lossy(&output.stderr).into_owned())
    }
}

#[tauri::command]
fn account_profile() -> Result<String, String> {
    run_engine(&["profile"])
}

#[tauri::command]
fn account_overview() -> Result<String, String> {
    run_engine(&["overview"])
}

#[tauri::command]
fn account_import_good(path: String) -> Result<String, String> {
    run_engine(&["import-good", &path])
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            app_info,
            account_profile,
            account_overview,
            account_import_good
        ])
        .run(tauri::generate_context!())
        .expect("erreur au démarrage de l'application Tauri");
}
