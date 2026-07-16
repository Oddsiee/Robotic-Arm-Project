param(
    [string]$Model = $env:OPENROUTER_MODEL,
    [string]$Prompt = "Hello from OpenRouter via local script"
)

# Load .env from script folder if present (don't commit .env)
$envFile = Join-Path $PSScriptRoot ".env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)\s*=\s*(.+)\s*$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim().Trim("'\"")
            if (-not [string]::IsNullOrWhiteSpace($name)) { $env:$name = $value }
        }
    }
}

if (-not $env:OPENROUTER_API_KEY) {
    Write-Error "OPENROUTER_API_KEY not set. Set the environment variable or create a .env file in the script folder with OPENROUTER_API_KEY=..."
    exit 1
}

if (-not $Model) { $Model = "gpt-4o-mini" }

$body = @{ model = $Model; input = $Prompt } | ConvertTo-Json
$uri = "https://api.openrouter.ai/v1/chat/completions"

try {
    $resp = Invoke-RestMethod -Uri $uri -Method Post -Headers @{ Authorization = "Bearer $env:OPENROUTER_API_KEY" } -ContentType "application/json" -Body $body -ErrorAction Stop

    # Print a readable excerpt of the response
    if ($null -ne $resp) {
        if ($resp.output) {
            Write-Output ($resp.output | ConvertTo-Json -Depth 5)
        } elseif ($resp.choices) {
            $resp.choices | ForEach-Object {
                if ($_.message) { Write-Output ($_.message | ConvertTo-Json -Depth 5) } else { Write-Output ($_ | ConvertTo-Json -Depth 5) }
            }
        } else {
            Write-Output ($resp | ConvertTo-Json -Depth 5)
        }
    }
} catch {
    Write-Error "Request failed: $($_.Exception.Message)"
    exit 1
}
