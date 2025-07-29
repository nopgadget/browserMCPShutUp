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
   - Create a `.crx` file ready for Chrome installation

## Installing the Modified Extension

After running the script, you can install the modified extension in Chrome:

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in the top right corner)
3. Drag and drop the generated `.crx` file onto the extensions page
4. Click "Add extension" when prompted

The modified extension will now work without sending any telemetry data to external services.

## What the Script Does

- Disables analytics (Amplitude, PostHog)
- Disables Sentry error reporting
- Redirects all telemetry URLs to localhost:9999 (unresolvable)
- Disables online authentication and login features
- Removes integrity checks to allow the modified extension to work
- Renames the extension folder to prevent Chrome from auto-updating it
