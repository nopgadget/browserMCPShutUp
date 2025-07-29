# PowerShell script to disable all telemetry in the Browser MCP extension
# This script modifies the background.js and popup files to disable analytics
# and creates a .crx file ready for Chrome installation

param(
    [Parameter(Mandatory=$true)]
    [string]$ExtensionPath
)

Write-Host "🔍 Disabling telemetry in Browser MCP extension at: $ExtensionPath" -ForegroundColor Yellow

# Check if extension directory exists
if (-not (Test-Path $ExtensionPath)) {
    Write-Host "❌ Extension directory not found: $ExtensionPath" -ForegroundColor Red
    Write-Host "Please provide a valid path to the Browser MCP extension directory." -ForegroundColor Yellow
    exit 1
}

# Function to rename extension to prevent updates
function Rename-ExtensionToPreventUpdates {
    param([string]$extensionPath)
    
    $parentDir = Split-Path $extensionPath -Parent
    $currentName = Split-Path $extensionPath -Leaf
    $newName = "${currentName}_telemetry_disabled"
    $newPath = Join-Path $parentDir $newName
    
    # Check if the new name already exists
    if (Test-Path $newPath) {
        Write-Host "ℹ️ Extension already renamed to prevent updates: $newName" -ForegroundColor Yellow
        return $newPath
    }
    
    try {
        Write-Host "🔄 Renaming extension to prevent Chrome updates..." -ForegroundColor Yellow
        Rename-Item $extensionPath $newName
        Write-Host "✅ Extension renamed to: $newName" -ForegroundColor Green
        Write-Host "📝 This prevents Chrome from automatically updating and overwriting our changes." -ForegroundColor Cyan
        return $newPath
    } catch {
        Write-Host "❌ Error renaming extension: $($_.Exception.Message)" -ForegroundColor Red
        return $extensionPath
    }
}

# Function to replace analytics configurations
function Disable-Analytics {
    param([string]$content)

    # Replace analyticsEnabled fallback from true to false
    $content = $content -replace 'analyticsEnabled.*fallback.*!0', 'analyticsEnabled",{fallback:false'

    # Replace development configuration
    $content = $content -replace 'analytics.*enabled.*!0.*amplitudeApiKey.*bb45e733842c3732cd52d759e88826ca.*posthogApiKey.*phc_l85rVI7wMQYhw4kca0JJy8TAyztKch5WT3smy4VTEmg', 'analytics:{enabled:false,amplitudeApiKey:"",posthogApiKey:""'

    # Replace production configuration
    $content = $content -replace 'analytics.*enabled.*!0.*amplitudeApiKey.*10edd558159f01783d50d921d1ec4716.*posthogApiKey.*phc_KWOh1iNHba9C7csIG27O9Scq1', 'analytics:{enabled:false,amplitudeApiKey:"",posthogApiKey:""'

    # Replace test configuration (already disabled but ensure consistency)
    $content = $content -replace 'analytics.*enabled.*!1.*amplitudeApiKey.*"".*posthogApiKey.*""', 'analytics:{enabled:false,amplitudeApiKey:"",posthogApiKey:""'

    return $content
}

# Function to disable Sentry
function Disable-Sentry {
    param([string]$content)

    # Replace Sentry configurations to disabled
    $content = $content -replace 'sentry.*enabled.*!1.*dsn.*""', 'sentry:{enabled:false,dsn:""'

    return $content
}

# Function to redirect all telemetry URLs to localhost:9999
function Redirect-TelemetryUrls {
    param([string]$content)

    # Amplitude URLs
    $content = $content -replace 'https://api2\.amplitude\.com/2/httpapi', 'http://localhost:9999/amplitude/api'
    $content = $content -replace 'https://api\.eu\.amplitude\.com/2/httpapi', 'http://localhost:9999/amplitude/eu/api'
    $content = $content -replace 'https://api2\.amplitude\.com/batch', 'http://localhost:9999/amplitude/batch'
    $content = $content -replace 'https://api\.eu\.amplitude\.com/batch', 'http://localhost:9999/amplitude/eu/batch'
    $content = $content -replace 'https://sr-client-cfg\.amplitude\.com/config', 'http://localhost:9999/amplitude/config'
    $content = $content -replace 'https://sr-client-cfg\.stag2\.amplitude\.com/config', 'http://localhost:9999/amplitude/staging/config'
    $content = $content -replace 'https://sr-client-cfg\.eu\.amplitude\.com/config', 'http://localhost:9999/amplitude/eu/config'
    $content = $content -replace 'https://app\.amplitude\.com', 'http://localhost:9999/amplitude/app'
    $content = $content -replace 'https://app\.eu\.amplitude\.com', 'http://localhost:9999/amplitude/eu/app'
    $content = $content -replace 'https://apps\.stag2\.amplitude\.com', 'http://localhost:9999/amplitude/staging/app'

    # PostHog URLs
    $content = $content -replace 'https://app\.posthog\.com', 'http://localhost:9999/posthog/app'
    $content = $content -replace 'https://us\.i\.posthog\.com', 'http://localhost:9999/posthog/us'
    $content = $content -replace 'https://us\.posthog\.com', 'http://localhost:9999/posthog/us/app'
    $content = $content -replace 'https://eu\.i\.posthog\.com', 'http://localhost:9999/posthog/eu'
    $content = $content -replace 'https://eu\.posthog\.com', 'http://localhost:9999/posthog/eu/app'
    $content = $content -replace 'https://eu-assets\.posthog\.com', 'http://localhost:9999/posthog/eu/assets'
    $content = $content -replace 'https://us-assets\.posthog\.com', 'http://localhost:9999/posthog/us/assets'

    # Sentry URLs
    $content = $content -replace 'https://o447951\.ingest\.sentry\.io', 'http://localhost:9999/sentry/ingest'
    $content = $content -replace 'https://ingest\.sentry\.io', 'http://localhost:9999/sentry/ingest'
    $content = $content -replace 'https://sentry\.io', 'http://localhost:9999/sentry'
    $content = $content -replace 'https://docs\.sentry\.io', 'http://localhost:9999/sentry/docs'

    # Other analytics URLs
    $content = $content -replace 'https://www\.docs\.developers\.amplitude\.com', 'http://localhost:9999/amplitude/docs'
    $content = $content -replace 'https://posthog\.com/docs', 'http://localhost:9999/posthog/docs'

    return $content
}

# Function to disable online authentication and login features
function Disable-OnlineFeatures {
    param([string]$content)

    # BrowserMCP.io URLs - redirect all to localhost:9999
    $content = $content -replace 'https://browsermcp\.io', 'http://localhost:9999/browsermcp'
    $content = $content -replace 'https://app\.browsermcp\.io', 'http://localhost:9999/browsermcp/app'
    $content = $content -replace 'https://docs\.browsermcp\.io', 'http://localhost:9999/browsermcp/docs'

    # Disable login/logout functionality by replacing with no-op functions
    $content = $content -replace 'Mb\("logIn",RO\)', 'Mb("logIn",()=>{})'
    $content = $content -replace 'Mb\("logOut",AO\)', 'Mb("logOut",()=>{})'
    $content = $content -replace 'bR\("logIn",s8\)', 'bR("logIn",()=>{})'
    $content = $content -replace 'bR\("logOut",a8\)', 'bR("logOut",()=>{})'

    # Disable user queries and session management
    $content = $content -replace 'QT\(\)', 'null'
    $content = $content -replace 'eI\(\)', '()=>{}'
    $content = $content -replace 'tI\(', '()=>{}('
    $content = $content -replace 'nI\(', '()=>{}('
    $content = $content -replace 'rI\(', '()=>{}('

    # Disable web message listeners for authentication
    $content = $content -replace 'MO\("ping",async\(\)=>\{\}\)', '()=>{}'
    $content = $content -replace 'LO\("version",async', '()=>{}('

    return $content
}

# Function to disable integrity checks by removing _metadata directory
function Disable-IntegrityChecks {
    $metadataPath = Join-Path $ExtensionPath "_metadata"
    if (Test-Path $metadataPath) {
        try {
            Remove-Item $metadataPath -Recurse -Force
            Write-Host "✅ Removed _metadata directory (disabled integrity checks)" -ForegroundColor Green
        } catch {
            Write-Host "❌ Error removing _metadata directory: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "ℹ️ _metadata directory not found (integrity checks already disabled)" -ForegroundColor Yellow
    }
}

# Track if any essential files were found and modified
$essentialFilesFound = $false
$errors = @()

# Process background.js
try {
    $backgroundPath = Join-Path $ExtensionPath "background.js"
    if (Test-Path $backgroundPath) {
        $content = Get-Content $backgroundPath -Raw -Encoding UTF8
        $content = Disable-Analytics $content
        $content = Disable-Sentry $content
        $content = Redirect-TelemetryUrls $content
        $content = Disable-OnlineFeatures $content
        Set-Content $backgroundPath $content -Encoding UTF8
        Write-Host "✅ Modified background.js" -ForegroundColor Green
        $essentialFilesFound = $true
    } else {
        $errors += "background.js not found at: $backgroundPath"
        Write-Host "❌ background.js not found at: $backgroundPath" -ForegroundColor Red
    }
} catch {
    $errors += "Error modifying background.js: $($_.Exception.Message)"
    Write-Host "❌ Error modifying background.js: $($_.Exception.Message)" -ForegroundColor Red
}

# Process popup.js
try {
    $popupPath = Join-Path $ExtensionPath "chunks\popup-xxiXE7fj.js"
    if (Test-Path $popupPath) {
        $content = Get-Content $popupPath -Raw -Encoding UTF8
        $content = Disable-Analytics $content
        $content = Disable-Sentry $content
        $content = Redirect-TelemetryUrls $content
        $content = Disable-OnlineFeatures $content
        Set-Content $popupPath $content -Encoding UTF8
        Write-Host "✅ Modified popup-xxiXE7fj.js" -ForegroundColor Green
        $essentialFilesFound = $true
    } else {
        $errors += "popup-xxiXE7fj.js not found at: $popupPath"
        Write-Host "❌ popup-xxiXE7fj.js not found at: $popupPath" -ForegroundColor Red
    }
} catch {
    $errors += "Error modifying popup-xxiXE7fj.js: $($_.Exception.Message)"
    Write-Host "❌ Error modifying popup-xxiXE7fj.js: $($_.Exception.Message)" -ForegroundColor Red
}

# Process content.js if it exists (optional file)
try {
    $contentPath = Join-Path $ExtensionPath "content-scripts\content.js"
    if (Test-Path $contentPath) {
        $content = Get-Content $contentPath -Raw -Encoding UTF8
        $content = Redirect-TelemetryUrls $content
        $content = Disable-OnlineFeatures $content
        Set-Content $contentPath $content -Encoding UTF8
        Write-Host "✅ Modified content.js" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ content.js not found at: $contentPath (this is normal if no telemetry URLs exist)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error modifying content.js: $($_.Exception.Message)" -ForegroundColor Red
}

# Check if any essential files were found and modified
if (-not $essentialFilesFound) {
    Write-Host "`n❌ CRITICAL ERROR: No essential files were found or modified!" -ForegroundColor Red
    Write-Host "The script could not find or modify any of the required files:" -ForegroundColor Yellow
    Write-Host "  - background.js" -ForegroundColor Yellow
    Write-Host "  - chunks\popup-xxiXE7fj.js" -ForegroundColor Yellow
    Write-Host "`nErrors encountered:" -ForegroundColor Red
    foreach ($err in $errors) {
        Write-Host "  - $err" -ForegroundColor Red
    }
    Write-Host "`nPlease ensure you're pointing to a valid Browser MCP extension directory." -ForegroundColor Yellow
    Write-Host "The extension should contain background.js and chunks\popup-xxiXE7fj.js files." -ForegroundColor Yellow
    exit 1
}

# Disable integrity checks to allow modified extension to work
Disable-IntegrityChecks

# Rename extension to prevent Chrome updates
$newExtensionPath = Rename-ExtensionToPreventUpdates $ExtensionPath

# Create .crx file from the modified extension
# $zipFilePath = Create-CrxFile $newExtensionPath # This line is removed

Write-Host "`n🎉 Telemetry disabled and online features disabled! The extension will no longer send analytics data or connect to online services." -ForegroundColor Green
Write-Host "📝 Note: You may need to reload the extension in your browser for changes to take effect." -ForegroundColor Yellow
Write-Host "🔗 All telemetry URLs now point to localhost:9999 (unresolvable)" -ForegroundColor Cyan
Write-Host "🔒 Integrity checks disabled to allow modified extension to work" -ForegroundColor Cyan
Write-Host "🚫 Login/logout functionality disabled - extension works offline only" -ForegroundColor Cyan

Write-Host "`n📦 Modified extension folder: $newExtensionPath" -ForegroundColor Green
Write-Host "📝 Installation instructions:" -ForegroundColor Cyan
Write-Host "   1. Open Chrome and go to chrome://extensions/" -ForegroundColor Cyan
Write-Host "   2. Enable 'Developer mode' (toggle in top right)" -ForegroundColor Cyan
Write-Host "   3. Click 'Load unpacked' and select the modified extension folder:" -ForegroundColor Cyan
Write-Host "      $newExtensionPath" -ForegroundColor Yellow

Write-Host "`n🛡️ IMPORTANT: To prevent Chrome from overwriting your changes:" -ForegroundColor Yellow
Write-Host "1. The extension folder has been renamed to prevent automatic updates" -ForegroundColor Cyan
Write-Host "2. You can install the modified extension using 'Load unpacked' in Chrome's developer mode" -ForegroundColor Cyan
Write-Host "3. Consider disabling automatic extension updates in Chrome settings" -ForegroundColor Cyan