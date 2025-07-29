# browserMCPShutUp

A Python tool to completely disable telemetry and online features in the BrowserMCP extension, making it work offline without sending any analytics data.

## Features

- **Complete Telemetry Disabling**: Disables all analytics (Amplitude, PostHog) and error reporting (Sentry)
- **URL Redirection**: Redirects all telemetry URLs to localhost:9999 (unresolvable)
- **Offline Mode**: Disables online authentication and login features
- **Code Beautification**: Beautifies JavaScript code for better readability using jsbeautifier
- **Update Prevention**: Renames extension folder to prevent Chrome auto-updates
- **Integrity Check Removal**: Disables integrity checks to allow modified extension to work
- **Colored Output**: Provides clear, colored status messages during execution

## Installation

1. Clone or download this repository
2. Install the required Python dependency:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the Python script with the path to your Browser MCP extension directory:

```bash
python disable_telemetry.py "C:\path\to\your\browser-mcp-extension"
```

### Example:
```bash
python disable_telemetry.py "C:\Users\username\Downloads\browser-mcp-extension"
```

## What the Script Does

The script performs the following modifications to the Browser MCP extension:

### Analytics Disabling
- Disables Amplitude analytics (development and production configurations)
- Disables PostHog analytics
- Sets all analytics fallbacks to `false`

### Error Reporting Disabling
- Disables Sentry error reporting
- Removes all Sentry DSN configurations

### URL Redirection
- Redirects all Amplitude URLs to `localhost:9999`
- Redirects all PostHog URLs to `localhost:9999`
- Redirects all Sentry URLs to `localhost:9999`
- Redirects BrowserMCP.io URLs to `localhost:9999`

### Online Features Disabling
- Disables login/logout functionality
- Disables user session management
- Disables web message listeners for authentication
- Makes the extension work in offline mode only

### Code Enhancement
- Beautifies JavaScript code using jsbeautifier library
- Improves code readability with proper formatting
- Maintains functionality while making code more maintainable

### Extension Protection
- Renames the extension folder to prevent Chrome auto-updates
- Removes `_metadata` directory to disable integrity checks
- Ensures modified extension can be installed without issues

## Installing the Modified Extension

After running the script, install the modified extension in Chrome:

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in the top right corner)
3. Click "Load unpacked" and select the modified extension folder
4. The extension will install and work without sending any telemetry data

## File Structure

The script modifies these key files in the extension:
- `background.js` - Main extension background script
- `chunks/popup-xxiXE7fj.js` - Extension popup interface
- `content-scripts/content.js` - Content scripts (if present)

## Troubleshooting

### Common Issues

**Import Error for jsbeautifier**:
```bash
pip install jsbeautifier
```

**Extension Directory Not Found**:
- Ensure you're pointing to the correct Browser MCP extension directory
- The directory should contain `background.js` and `chunks/popup-xxiXE7fj.js` files

**No Essential Files Modified**:
- Verify the extension path is correct
- Check that the extension contains the expected file structure
- Ensure you have read/write permissions for the extension directory

### Extension Updates

The script automatically renames the extension folder to prevent Chrome from automatically updating and overwriting your changes. You can also:

1. Disable automatic extension updates in Chrome settings
2. Use the renamed extension folder for installation
3. Keep a backup of the modified extension

### CRX_HEADER_INVALID Error

This error was common with older versions that tried to create CRX files. The current Python version uses the "Load unpacked" method which avoids this issue entirely.

## Requirements

- Python 3.6 or higher
- jsbeautifier library (automatically installed via requirements.txt)

## Security Note

This tool modifies the Browser MCP extension to disable telemetry and online features. The modified extension will:
- Not send any analytics data
- Not connect to online services
- Work in offline mode only
- Have disabled integrity checks

Use this tool responsibly and ensure you understand the implications of modifying browser extensions.
