#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod backend;

// Optional: uncomment for MCP client registration (Cursor / Claude Desktop)
// mod mcp_client;

use backend::{BackendProcess, spawn_backend};
use tauri::{Emitter, Manager};

#[tauri::command]
async fn start_backend(
    app: tauri::AppHandle,
    state: tauri::State<'_, BackendProcess>,
) -> Result<String, String> {
    spawn_backend(app, &state)
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_process::init())
        .manage(BackendProcess(std::sync::Mutex::new(None)))
        .invoke_handler(tauri::generate_handler![
            start_backend,
            // Optional: uncomment for MCP client registration
            // mcp_client::get_mcp_registration_status,
            // mcp_client::register_mcp_clients
        ])
        .setup(|app| {
            // spawn_backend() is a blocking function (free_port() alone does
            // several sequential PowerShell subprocess calls, each ~0.3-0.8s
            // to spin up, up to 240s worst case) - calling it directly here
            // blocks whatever thread runs setup(), freezing the window's
            // message pump for the whole call (Windows shows this as a
            // "(Not Responding)" Ghost window until spawn_backend returns).
            // Run it on its own OS thread so setup() returns immediately.
            let handle = app.handle().clone();
            std::thread::spawn(move || {
                let state = handle.state::<BackendProcess>();
                if let Err(e) = spawn_backend(handle.clone(), state.inner()) {
                    eprintln!("Backend error: {e}");
                    let _ = handle.emit("backend-status", format!("error: {e}"));
                }
            });
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error building tauri application")
        .run(|app, event| {
            if let tauri::RunEvent::Exit = event {
                if let Some(mut child) = app.state::<BackendProcess>().0.lock().unwrap().take() {
                    let _ = child.kill();
                }
            }
        });
}