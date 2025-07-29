# browserMCPShutUp
A tool to strip telemetry functions from BrowserMCP Tool

## Usage

1. Run the PowerShell script with the path to your Browser MCP extension directory:
   ```powershell
   .\disable_telemetry.ps1 -ExtensionPath "C:\path\to\your\browser-mcp-extension"
   ```

2. The script will:
   - Disable all telemetry and analytics in the extension
   - Rename the extension folder to prevent Chrome auto-updates
   - Provide clear installation instructions

## Installing the Modified Extension

After running the script, you can install the modified extension in Chrome:

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in the top right corner)
3. Click "Load unpacked" and select the modified extension folder
4. The extension will install and work without sending telemetry data

## What the Script Does

- Disables analytics (Amplitude, PostHog)
- Disables Sentry error reporting
- Redirects all telemetry URLs to localhost:9999 (unresolvable)
- Disables online authentication and login features
- Removes integrity checks to allow the modified extension to work
- Renames the extension folder to prevent Chrome from auto-updating it

## Troubleshooting

**CRX_HEADER_INVALID Error**: This error was common with the previous version that tried to create CRX files. The updated script now uses the "Load unpacked" method which avoids this issue entirely.

**Extension Updates**: The script renames the extension folder to prevent Chrome from automatically updating and overwriting your changes. Consider also disabling automatic extension updates in Chrome settings.
