use serde::Serialize;
use serde_json::Value;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::Duration;
use tauri::Manager;
use wait_timeout::ChildExt;

#[derive(Serialize)]
struct AppInfo {
    name: &'static str,
    version: &'static str,
}

/// Métadonnées réelles de l'application (aucune donnée de jeu factice).
#[tauri::command]
fn app_info() -> AppInfo {
    AppInfo { name: "Irminsul", version: env!("CARGO_PKG_VERSION") }
}

// --- Pont vers le sidecar moteur (exécutable autonome, Python non requis) --- //

const MAX_OUT: usize = 32 * 1024 * 1024; // borne la réponse
const DEFAULT_TIMEOUT: Duration = Duration::from_secs(30);

/// Résout le sidecar embarqué, à côté de l'exécutable courant (dev ET installé).
/// Ne dépend ni de la racine du dépôt ni d'un Python sur le PATH.
fn sidecar_path() -> Result<PathBuf, String> {
    let exe = std::env::current_exe().map_err(|e| e.to_string())?;
    let dir = exe.parent().ok_or_else(|| "dossier de l'exécutable introuvable".to_string())?;
    let name = if cfg!(windows) { "irminsul-sidecar.exe" } else { "irminsul-sidecar" };
    let p = dir.join(name);
    if p.exists() {
        Ok(p)
    } else {
        Err(format!("sidecar introuvable : {}", p.display()))
    }
}

/// Dossier de données de l'application (jamais le dépôt) ; créé au besoin.
fn data_root(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    let dir = app.path().app_data_dir().map_err(|e| e.to_string())?;
    std::fs::create_dir_all(&dir).map_err(|e| e.to_string())?;
    Ok(dir)
}

/// Déballe le protocole sidecar {ok, result|error}. Erreurs structurées.
fn parse_response(bytes: &[u8]) -> Result<Value, String> {
    let v: Value = serde_json::from_slice(bytes).map_err(|e| format!("réponse JSON invalide: {e}"))?;
    if v.get("ok").and_then(|b| b.as_bool()) == Some(true) {
        Ok(v.get("result").cloned().unwrap_or(Value::Null))
    } else {
        let msg = v
            .get("error")
            .and_then(|e| e.get("message"))
            .and_then(|m| m.as_str())
            .map(|s| s.to_string())
            .unwrap_or_else(|| "erreur sidecar".to_string());
        Err(msg)
    }
}

/// Exécute un appel sidecar borné : requête sur stdin, réponse JSON sur stdout,
/// timeout + kill, taille de réponse plafonnée. Aucun secret en argument.
fn run_sidecar(exe: &Path, root: &Path, req: &[u8], timeout: Duration) -> Result<Value, String> {
    use std::io::{Read, Write};
    let mut cmd = Command::new(exe);
    cmd.env("IRMINSUL_PROJECT_ROOT", root)
        .env("PYTHONUTF8", "1")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped());
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        cmd.creation_flags(0x0800_0000); // CREATE_NO_WINDOW
    }
    let mut child = cmd.spawn().map_err(|e| format!("démarrage sidecar impossible: {e}"))?;

    if let Some(mut stdin) = child.stdin.take() {
        stdin.write_all(req).map_err(|e| format!("écriture stdin: {e}"))?;
    } // stdin fermé ici

    let stdout = child.stdout.take().ok_or_else(|| "stdout indisponible".to_string())?;
    let reader = std::thread::spawn(move || {
        let mut buf = Vec::new();
        let mut limited = stdout.take((MAX_OUT + 1) as u64);
        let _ = limited.read_to_end(&mut buf);
        buf
    });

    match child.wait_timeout(timeout).map_err(|e| e.to_string())? {
        Some(status) => {
            let out = reader.join().map_err(|_| "lecture sidecar échouée".to_string())?;
            if out.len() > MAX_OUT {
                return Err("réponse sidecar trop volumineuse".to_string());
            }
            if !status.success() {
                return Err(format!("sidecar terminé en erreur (code {:?})", status.code()));
            }
            parse_response(&out)
        }
        None => {
            let _ = child.kill();
            let _ = reader.join();
            Err("délai dépassé (sidecar)".to_string())
        }
    }
}

fn call_engine(app: &tauri::AppHandle, method: &str, params: Value) -> Result<Value, String> {
    let exe = sidecar_path()?;
    let root = data_root(app)?;
    let req = serde_json::json!({ "id": method, "method": method, "params": params });
    let bytes = serde_json::to_vec(&req).map_err(|e| e.to_string())?;
    run_sidecar(&exe, &root, &bytes, DEFAULT_TIMEOUT)
}

fn to_json_string(v: Value) -> Result<String, String> {
    serde_json::to_string(&v).map_err(|e| e.to_string())
}

#[tauri::command]
fn account_profile(app: tauri::AppHandle) -> Result<String, String> {
    call_engine(&app, "profile", serde_json::json!({})).and_then(to_json_string)
}

#[tauri::command]
fn account_overview(app: tauri::AppHandle) -> Result<String, String> {
    call_engine(&app, "overview", serde_json::json!({})).and_then(to_json_string)
}

#[tauri::command]
fn account_roster(app: tauri::AppHandle) -> Result<String, String> {
    call_engine(&app, "roster", serde_json::json!({})).and_then(to_json_string)
}

#[tauri::command]
fn account_import_good(app: tauri::AppHandle, path: String) -> Result<String, String> {
    call_engine(&app, "import-good", serde_json::json!({ "path": path })).and_then(to_json_string)
}

#[tauri::command]
fn quick_calc(app: tauri::AppHandle, params: Value) -> Result<String, String> {
    call_engine(&app, "quick-calc", params).and_then(to_json_string)
}

#[tauri::command]
fn mechanics(app: tauri::AppHandle) -> Result<String, String> {
    call_engine(&app, "mechanics", serde_json::json!({})).and_then(to_json_string)
}

#[tauri::command]
fn account_characters(app: tauri::AppHandle) -> Result<String, String> {
    call_engine(&app, "characters", serde_json::json!({})).and_then(to_json_string)
}

#[tauri::command]
fn character_stats(app: tauri::AppHandle, key: String) -> Result<String, String> {
    call_engine(&app, "character-stats", serde_json::json!({ "key": key })).and_then(to_json_string)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .invoke_handler(tauri::generate_handler![
            app_info,
            account_profile,
            account_overview,
            account_roster,
            account_import_good,
            quick_calc,
            mechanics,
            account_characters,
            character_stats
        ])
        .run(tauri::generate_context!())
        .expect("erreur au démarrage de l'application Tauri");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_ok_unwraps_result() {
        let v = parse_response(br#"{"ok":true,"result":{"status":"ok"}}"#).unwrap();
        assert_eq!(v.get("status").unwrap(), "ok");
    }

    #[test]
    fn parse_error_surfaces_message() {
        let e = parse_response(br#"{"ok":false,"error":{"type":"bad_request","message":"boom"}}"#)
            .unwrap_err();
        assert!(e.contains("boom"));
    }

    #[test]
    fn parse_invalid_json_errors() {
        assert!(parse_response(b"not json at all").is_err());
        assert!(parse_response(b"").is_err()); // réponse partielle/vide
    }

    #[test]
    fn absent_sidecar_errors() {
        let p = Path::new("definitely-missing-sidecar-xyz.exe");
        let r = run_sidecar(p, &std::env::temp_dir(), b"{}", Duration::from_secs(5));
        assert!(r.is_err());
    }

    #[test]
    fn real_sidecar_roundtrip_and_timeout() {
        let exe = Path::new(env!("CARGO_MANIFEST_DIR"))
            .join("binaries")
            .join("irminsul-sidecar-x86_64-pc-windows-msvc.exe");
        if !exe.exists() {
            return; // sauté si le sidecar n'a pas été construit
        }
        let tmp = std::env::temp_dir().join(format!("irm-sc-test-{}", std::process::id()));
        std::fs::create_dir_all(&tmp).unwrap();
        // Compte vide → réponse "empty" (jamais de donnée inventée).
        let v = run_sidecar(&exe, &tmp, br#"{"method":"profile"}"#, Duration::from_secs(30)).unwrap();
        assert_eq!(v.get("status").unwrap(), "empty");
        // Timeout déterministe (kill).
        let t = run_sidecar(&exe, &tmp, br#"{"method":"profile"}"#, Duration::from_millis(0));
        assert!(t.is_err());
        let _ = std::fs::remove_dir_all(&tmp);
    }
}
