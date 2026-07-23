//! Runtime Next.js standalone embarqué — cycle de vie possédé par Tauri.
//! Port dynamique loopback, health check HTTP borné (pas de délai fixe aveugle),
//! logs fichier sans secret, kill garanti à la sortie.

use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::time::{Duration, Instant};

#[derive(Debug)]
pub struct NextServer {
    pub child: Child,
    pub url: String,
}

/// Port libre choisi par l'OS, loopback uniquement (jamais 0.0.0.0).
fn free_port() -> Result<u16, String> {
    let l = TcpListener::bind(("127.0.0.1", 0)).map_err(|e| format!("bind loopback: {e}"))?;
    Ok(l.local_addr().map_err(|e| e.to_string())?.port())
}

/// GET / minimal ; prêt si une ligne de statut HTTP revient (peu importe le code).
fn probe(port: u16) -> bool {
    let addr = format!("127.0.0.1:{port}");
    let Ok(mut s) = TcpStream::connect_timeout(
        &addr.parse().expect("addr loopback valide"),
        Duration::from_millis(500),
    ) else {
        return false;
    };
    let _ = s.set_read_timeout(Some(Duration::from_millis(1500)));
    if s.write_all(format!("GET / HTTP/1.1\r\nHost: {addr}\r\nConnection: close\r\n\r\n").as_bytes()).is_err() {
        return false;
    }
    let mut buf = [0u8; 12];
    matches!(s.read(&mut buf), Ok(n) if n >= 8 && buf.starts_with(b"HTTP/"))
}

/// Health check borné : sondes régulières jusqu'à readiness ou deadline (erreur claire).
pub fn wait_ready(port: u16, timeout: Duration) -> Result<(), String> {
    let start = Instant::now();
    while start.elapsed() < timeout {
        if probe(port) {
            return Ok(());
        }
        std::thread::sleep(Duration::from_millis(250));
    }
    Err(format!("le serveur local n'a pas répondu en {}s (port {port})", timeout.as_secs()))
}

/// Démarre `node server.js` (runtime embarqué) : HOSTNAME=127.0.0.1, PORT dynamique,
/// DATABASE_URL vers le dossier utilisateur. stdout/stderr → fichier de log (sans secret).
pub fn spawn_next(
    node: &Path,
    server_js: &Path,
    port: u16,
    database_url: &str,
    log_file: &Path,
    sidecar_exe: &Path,
    nonce: &str,
) -> Result<NextServer, String> {
    if !node.exists() {
        return Err(format!("runtime Node embarqué introuvable : {}", node.display()));
    }
    if !server_js.exists() {
        return Err(format!("serveur Next standalone introuvable : {}", server_js.display()));
    }
    let log = std::fs::File::create(log_file).map_err(|e| format!("log: {e}"))?;
    let log2 = log.try_clone().map_err(|e| e.to_string())?;
    let mut cmd = Command::new(node);
    // Arg RELATIF + cwd : un chemin absolu contenant des espaces (« IA Genshin ») est
    // tronqué par la résolution du module principal de Node sous Windows.
    cmd.arg("server.js")
        .current_dir(server_js.parent().unwrap_or(Path::new(".")))
        .env("HOSTNAME", "127.0.0.1") // loopback UNIQUEMENT — jamais exposé au LAN
        .env("PORT", port.to_string())
        .env("NODE_ENV", "production")
        .env("DATABASE_URL", database_url)
        // Desktop : les Server Actions appellent le MOTEUR GELÉ directement (pas de Python/venv).
        .env("IRMINSUL_SIDECAR_EXE", sidecar_exe)
        // Nonce éphémère (audit M3) : mutations POST refusées sans lui. Jamais loggé/persisté.
        .env("IRMINSUL_NONCE", nonce)
        .stdin(Stdio::null())
        .stdout(Stdio::from(log))
        .stderr(Stdio::from(log2));
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        cmd.creation_flags(0x0800_0000); // CREATE_NO_WINDOW
    }
    let child = cmd.spawn().map_err(|e| format!("démarrage Node: {e}"))?;
    Ok(NextServer { child, url: format!("http://127.0.0.1:{port}") })
}

/// Résolution UNIFORME dev/prod via resource_dir (les resources gardent l'arborescence).
pub fn resource_paths(resource_dir: &Path) -> (PathBuf, PathBuf, PathBuf) {
    (
        resource_dir.join("binaries").join("node-x86_64-pc-windows-msvc.exe"),
        resource_dir.join("web").join("standalone").join("apps").join("web").join("server.js"),
        resource_dir.join("web-template.db"),
    )
}

/// Prépare le dossier données utilisateur : dirs + DB copiée du template au 1er lancement.
/// Ne remplace JAMAIS une base existante (même en erreur : on la laisse pour diagnostic).
pub fn ensure_user_db(app_data: &Path, template: &Path) -> Result<String, String> {
    std::fs::create_dir_all(app_data.join("logs")).map_err(|e| format!("dossier données: {e}"))?;
    let db = app_data.join("irminsul.db");
    if !db.exists() {
        if !template.exists() {
            return Err(format!("base template absente du bundle : {}", template.display()));
        }
        std::fs::copy(template, &db).map_err(|e| format!("initialisation base: {e}"))?;
    }
    Ok(format!("file:{}", db.display().to_string().replace('\\', "/")))
}

pub fn alloc_port() -> Result<u16, String> {
    free_port()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn free_port_is_loopback_and_nonzero() {
        let p = alloc_port().unwrap();
        assert!(p > 0);
    }

    #[test]
    fn probe_false_on_closed_port() {
        let p = alloc_port().unwrap(); // alloué puis libéré : fermé
        assert!(!probe(p));
    }

    #[test]
    fn wait_ready_times_out_clearly() {
        let p = alloc_port().unwrap();
        let e = wait_ready(p, Duration::from_millis(600)).unwrap_err();
        assert!(e.contains("port"));
    }

    #[test]
    fn spawn_next_missing_resources_errors() {
        let e = spawn_next(
            Path::new("missing-node.exe"),
            Path::new("missing-server.js"),
            1,
            "file:x.db",
            &std::env::temp_dir().join("irm-next-test.log"),
            Path::new("missing-sidecar.exe"),
            "test-nonce",
        )
        .unwrap_err();
        assert!(e.contains("introuvable"));
    }

    #[test]
    fn ensure_user_db_requires_template_and_never_overwrites() {
        let tmp = std::env::temp_dir().join(format!("irm données étoile-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&tmp);
        // Template absent → erreur actionnable.
        let e = ensure_user_db(&tmp, Path::new("missing-template.db")).unwrap_err();
        assert!(e.contains("template"));
        // Template présent → copie ; base existante → JAMAIS écrasée (chemin Unicode + espaces).
        let tpl = tmp.join("tpl.db");
        std::fs::create_dir_all(&tmp).unwrap();
        std::fs::write(&tpl, b"TEMPLATE").unwrap();
        let url = ensure_user_db(&tmp, &tpl).unwrap();
        assert!(url.starts_with("file:"));
        std::fs::write(tmp.join("irminsul.db"), b"USERDATA").unwrap();
        let _ = ensure_user_db(&tmp, &tpl).unwrap();
        assert_eq!(std::fs::read(tmp.join("irminsul.db")).unwrap(), b"USERDATA");
        let _ = std::fs::remove_dir_all(&tmp);
    }
}
