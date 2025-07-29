#!/usr/bin/env python3
"""
Python script to disable all telemetry in the Browser MCP extension
This script modifies the background.js and popup files to disable analytics
and creates a modified extension ready for Chrome installation
"""

import os
import sys
import shutil
import re
import argparse
from pathlib import Path
from typing import List, Tuple

try:
    import jsbeautifier
except ImportError:
    print("❌ jsbeautifier library not found. Please install it with:")
    print("   pip install jsbeautifier")
    sys.exit(1)


class TelemetryDisabler:
    def __init__(self, extension_path: str):
        self.extension_path = Path(extension_path)
        self.errors = []
        self.essential_files_found = False
        
    def print_status(self, message: str, color: str = "white"):
        """Print colored status messages"""
        colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "cyan": "\033[96m",
            "white": "\033[97m"
        }
        end_color = "\033[0m"
        color_code = colors.get(color, colors["white"])
        print(f"{color_code}{message}{end_color}")
    
    def rename_extension_to_prevent_updates(self) -> Path:
        """Rename extension to prevent Chrome updates"""
        parent_dir = self.extension_path.parent
        current_name = self.extension_path.name
        new_name = f"{current_name}_telemetry_disabled"
        new_path = parent_dir / new_name
        
        # Check if the new name already exists
        if new_path.exists():
            self.print_status(f"ℹ️ Extension already renamed to prevent updates: {new_name}", "yellow")
            return new_path
        
        try:
            self.print_status("🔄 Renaming extension to prevent Chrome updates...", "yellow")
            self.extension_path.rename(new_path)
            self.print_status(f"✅ Extension renamed to: {new_name}", "green")
            self.print_status("📝 This prevents Chrome from automatically updating and overwriting our changes.", "cyan")
            return new_path
        except Exception as e:
            self.print_status(f"❌ Error renaming extension: {str(e)}", "red")
            return self.extension_path
    
    def disable_analytics(self, content: str) -> str:
        """Replace analytics configurations"""
        # Replace analyticsEnabled fallback from true to false
        content = re.sub(r'analyticsEnabled.*fallback.*!0', 'analyticsEnabled",{fallback:false', content)
        
        # Replace development configuration
        content = re.sub(
            r'analytics.*enabled.*!0.*amplitudeApiKey.*bb45e733842c3732cd52d759e88826ca.*posthogApiKey.*phc_l85rVI7wMQYhw4kca0JJy8TAyztKch5WT3smy4VTEmg',
            'analytics:{enabled:false,amplitudeApiKey:"",posthogApiKey:""',
            content
        )
        
        # Replace production configuration
        content = re.sub(
            r'analytics.*enabled.*!0.*amplitudeApiKey.*10edd558159f01783d50d921d1ec4716.*posthogApiKey.*phc_KWOh1iNHba9C7csIG27O9Scq1',
            'analytics:{enabled:false,amplitudeApiKey:"",posthogApiKey:""',
            content
        )
        
        # Replace test configuration (already disabled but ensure consistency)
        content = re.sub(
            r'analytics.*enabled.*!1.*amplitudeApiKey.*"".*posthogApiKey.*""',
            'analytics:{enabled:false,amplitudeApiKey:"",posthogApiKey:""',
            content
        )
        
        return content
    
    def disable_sentry(self, content: str) -> str:
        """Disable Sentry configurations"""
        # Replace Sentry configurations to disabled
        content = re.sub(r'sentry.*enabled.*!1.*dsn.*""', 'sentry:{enabled:false,dsn:""', content)
        return content
    
    def redirect_telemetry_urls(self, content: str) -> str:
        """Redirect all telemetry URLs to localhost:9999"""
        # Amplitude URLs
        amplitude_urls = [
            (r'https://api2\.amplitude\.com/2/httpapi', 'http://localhost:9999/amplitude/api'),
            (r'https://api\.eu\.amplitude\.com/2/httpapi', 'http://localhost:9999/amplitude/eu/api'),
            (r'https://api2\.amplitude\.com/batch', 'http://localhost:9999/amplitude/batch'),
            (r'https://api\.eu\.amplitude\.com/batch', 'http://localhost:9999/amplitude/eu/batch'),
            (r'https://sr-client-cfg\.amplitude\.com/config', 'http://localhost:9999/amplitude/config'),
            (r'https://sr-client-cfg\.stag2\.amplitude\.com/config', 'http://localhost:9999/amplitude/staging/config'),
            (r'https://sr-client-cfg\.eu\.amplitude\.com/config', 'http://localhost:9999/amplitude/eu/config'),
            (r'https://app\.amplitude\.com', 'http://localhost:9999/amplitude/app'),
            (r'https://app\.eu\.amplitude\.com', 'http://localhost:9999/amplitude/eu/app'),
            (r'https://apps\.stag2\.amplitude\.com', 'http://localhost:9999/amplitude/staging/app'),
        ]
        
        # PostHog URLs
        posthog_urls = [
            (r'https://app\.posthog\.com', 'http://localhost:9999/posthog/app'),
            (r'https://us\.i\.posthog\.com', 'http://localhost:9999/posthog/us'),
            (r'https://us\.posthog\.com', 'http://localhost:9999/posthog/us/app'),
            (r'https://eu\.i\.posthog\.com', 'http://localhost:9999/posthog/eu'),
            (r'https://eu\.posthog\.com', 'http://localhost:9999/posthog/eu/app'),
            (r'https://eu-assets\.posthog\.com', 'http://localhost:9999/posthog/eu/assets'),
            (r'https://us-assets\.posthog\.com', 'http://localhost:9999/posthog/us/assets'),
        ]
        
        # Sentry URLs
        sentry_urls = [
            (r'https://o447951\.ingest\.sentry\.io', 'http://localhost:9999/sentry/ingest'),
            (r'https://ingest\.sentry\.io', 'http://localhost:9999/sentry/ingest'),
            (r'https://sentry\.io', 'http://localhost:9999/sentry'),
            (r'https://docs\.sentry\.io', 'http://localhost:9999/sentry/docs'),
        ]
        
        # Other analytics URLs
        other_urls = [
            (r'https://www\.docs\.developers\.amplitude\.com', 'http://localhost:9999/amplitude/docs'),
            (r'https://posthog\.com/docs', 'http://localhost:9999/posthog/docs'),
        ]
        
        # Apply all URL replacements
        all_urls = amplitude_urls + posthog_urls + sentry_urls + other_urls
        for pattern, replacement in all_urls:
            content = re.sub(pattern, replacement, content)
        
        return content
    
    def disable_online_features(self, content: str) -> str:
        """Disable online authentication and login features"""
        # BrowserMCP.io URLs - redirect all to localhost:9999
        content = re.sub(r'https://browsermcp\.io', 'http://localhost:9999/browsermcp', content)
        content = re.sub(r'https://app\.browsermcp\.io', 'http://localhost:9999/browsermcp/app', content)
        content = re.sub(r'https://docs\.browsermcp\.io', 'http://localhost:9999/browsermcp/docs', content)
        
        # Disable login/logout functionality by replacing with no-op functions
        content = re.sub(r'Mb\("logIn",RO\)', 'Mb("logIn",()=>{})', content)
        content = re.sub(r'Mb\("logOut",AO\)', 'Mb("logOut",()=>{})', content)
        content = re.sub(r'bR\("logIn",s8\)', 'bR("logIn",()=>{})', content)
        content = re.sub(r'bR\("logOut",a8\)', 'bR("logOut",()=>{})', content)
        
        # Disable user queries and session management
        content = re.sub(r'QT\(\)', 'null', content)
        content = re.sub(r'eI\(\)', '()=>{}', content)
        content = re.sub(r'tI\(', '()=>{}(', content)
        content = re.sub(r'nI\(', '()=>{}(', content)
        content = re.sub(r'rI\(', '()=>{}(', content)
        
        # Disable web message listeners for authentication
        content = re.sub(r'MO\("ping",async\(\)=>\{\}\)', '()=>{}', content)
        content = re.sub(r'LO\("version",async', '()=>{}(', content)
        
        return content
    
    def disable_integrity_checks(self):
        """Disable integrity checks by removing _metadata directory"""
        metadata_path = self.extension_path / "_metadata"
        if metadata_path.exists():
            try:
                shutil.rmtree(metadata_path)
                self.print_status("✅ Removed _metadata directory (disabled integrity checks)", "green")
            except Exception as e:
                self.print_status(f"❌ Error removing _metadata directory: {str(e)}", "red")
        else:
            self.print_status("ℹ️ _metadata directory not found (integrity checks already disabled)", "yellow")
    
    def beautify_js(self, content: str) -> str:
        """Beautify JavaScript code using jsbeautifier"""
        try:
            opts = jsbeautifier.default_options()
            opts.indent_size = 2
            opts.indent_char = ' '
            opts.max_preserve_newlines = 2
            opts.preserve_newlines = True
            opts.keep_array_indentation = False
            opts.break_chained_methods = False
            opts.indent_scripts = 'normal'
            opts.brace_style = 'collapse'
            opts.space_before_conditional = True
            opts.eval_code = False
            opts.unescape_strings = False
            opts.wrap_line_length = 0
            
            return jsbeautifier.beautify(content, opts)
        except Exception as e:
            self.print_status(f"⚠️ Warning: Could not beautify JS code: {str(e)}", "yellow")
            return content
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single JavaScript file"""
        try:
            if not file_path.exists():
                self.errors.append(f"{file_path.name} not found at: {file_path}")
                self.print_status(f"❌ {file_path.name} not found at: {file_path}", "red")
                return False
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply all modifications
            content = self.disable_analytics(content)
            content = self.disable_sentry(content)
            content = self.redirect_telemetry_urls(content)
            content = self.disable_online_features(content)
            
            # Beautify the JavaScript code
            content = self.beautify_js(content)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.print_status(f"✅ Modified {file_path.name}", "green")
            return True
            
        except Exception as e:
            error_msg = f"Error modifying {file_path.name}: {str(e)}"
            self.errors.append(error_msg)
            self.print_status(f"❌ {error_msg}", "red")
            return False
    
    def run(self) -> bool:
        """Main execution method"""
        self.print_status(f"🔍 Disabling telemetry in Browser MCP extension at: {self.extension_path}", "yellow")
        
        # Check if extension directory exists
        if not self.extension_path.exists():
            self.print_status(f"❌ Extension directory not found: {self.extension_path}", "red")
            self.print_status("Please provide a valid path to the Browser MCP extension directory.", "yellow")
            return False
        
        # Process background.js
        background_path = self.extension_path / "background.js"
        if self.process_file(background_path):
            self.essential_files_found = True
        
        # Process popup.js
        popup_path = self.extension_path / "chunks" / "popup-xxiXE7fj.js"
        if self.process_file(popup_path):
            self.essential_files_found = True
        
        # Process content.js if it exists (optional file)
        content_path = self.extension_path / "content-scripts" / "content.js"
        if content_path.exists():
            self.process_file(content_path)
        else:
            self.print_status(f"ℹ️ content.js not found at: {content_path} (this is normal if no telemetry URLs exist)", "yellow")
        
        # Check if any essential files were found and modified
        if not self.essential_files_found:
            self.print_status("\n❌ CRITICAL ERROR: No essential files were found or modified!", "red")
            self.print_status("The script could not find or modify any of the required files:", "yellow")
            self.print_status("  - background.js", "yellow")
            self.print_status("  - chunks/popup-xxiXE7fj.js", "yellow")
            self.print_status("\nErrors encountered:", "red")
            for err in self.errors:
                self.print_status(f"  - {err}", "red")
            self.print_status("\nPlease ensure you're pointing to a valid Browser MCP extension directory.", "yellow")
            self.print_status("The extension should contain background.js and chunks/popup-xxiXE7fj.js files.", "yellow")
            return False
        
        # Disable integrity checks to allow modified extension to work
        self.disable_integrity_checks()
        
        # Rename extension to prevent Chrome updates
        new_extension_path = self.rename_extension_to_prevent_updates()
        
        # Print success message and instructions
        self.print_status("\n🎉 Telemetry disabled and online features disabled! The extension will no longer send analytics data or connect to online services.", "green")
        self.print_status("📝 Note: You may need to reload the extension in your browser for changes to take effect.", "yellow")
        self.print_status("🔗 All telemetry URLs now point to localhost:9999 (unresolvable)", "cyan")
        self.print_status("🔒 Integrity checks disabled to allow modified extension to work", "cyan")
        self.print_status("🚫 Login/logout functionality disabled - extension works offline only", "cyan")
        self.print_status("✨ JavaScript code has been beautified for better readability", "cyan")
        
        self.print_status(f"\n📦 Modified extension folder: {new_extension_path}", "green")
        self.print_status("📝 Installation instructions:", "cyan")
        self.print_status("   1. Open Chrome and go to chrome://extensions/", "cyan")
        self.print_status("   2. Enable 'Developer mode' (toggle in top right)", "cyan")
        self.print_status("   3. Click 'Load unpacked' and select the modified extension folder:", "cyan")
        self.print_status(f"      {new_extension_path}", "yellow")
        
        self.print_status("\n🛡️ IMPORTANT: To prevent Chrome from overwriting your changes:", "yellow")
        self.print_status("1. The extension folder has been renamed to prevent automatic updates", "cyan")
        self.print_status("2. You can install the modified extension using 'Load unpacked' in Chrome's developer mode", "cyan")
        self.print_status("3. Consider disabling automatic extension updates in Chrome settings", "cyan")
        
        return True


def main():
    parser = argparse.ArgumentParser(description="Disable telemetry in Browser MCP extension")
    parser.add_argument("extension_path", help="Path to the Browser MCP extension directory")
    
    args = parser.parse_args()
    
    disabler = TelemetryDisabler(args.extension_path)
    success = disabler.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 