# Per-repo fleet start config for bilibili-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'bilibili-mcp'
    BackendPort  = 11185
    FrontendPort = 11186
    HealthPath   = '/api/health'
    WebRoot      = 'webapp'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'bilibili_mcp.server:app'
        Env           = @{ WEB_PORT = '11185' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
