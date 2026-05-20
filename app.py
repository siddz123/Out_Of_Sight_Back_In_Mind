import os
import subprocess
from urllib.parse import urlparse

import rumps
from AppKit import (
    NSWorkspace, NSAttributedString, NSColor, NSFont,
    NSForegroundColorAttributeName, NSFontAttributeName,
)

DISTRACTION_BLACKLIST = ['Discord', 'Spotify', 'Twitter', 'Facebook', 'Terminal']
DOMAIN_BLACKLIST = [
    'youtube.com', 'x.com', 'twitter.com', 'reddit.com',
    'instagram.com', 'tiktok.com', 'facebook.com', 'netflix.com',
]
BROWSER_SCRIPTS = {
    'Google Chrome': 'tell application "Google Chrome" to get URL of active tab of front window',
    'Brave Browser': 'tell application "Brave Browser" to get URL of active tab of front window',
    'Arc':           'tell application "Arc" to get URL of active tab of front window',
    'Safari':        'tell application "Safari" to get URL of current tab of front window',
}
DEFAULT_TITLE = "🎯 Set Focus"
DISTRACTION_THRESHOLD = 5
FLASH_INTERVAL = 0.7


def get_browser_domain(app_name):
    script = BROWSER_SCRIPTS.get(app_name)
    if not script:
        return None
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True, text=True, timeout=2,
        )
    except subprocess.TimeoutExpired:
        return None
    url = result.stdout.strip()
    if not url:
        return None
    host = urlparse(url).netloc.lower()
    if host.startswith('www.'):
        host = host[4:]
    return host


def is_distraction(active_name):
    if active_name in DISTRACTION_BLACKLIST:
        return True
    domain = get_browser_domain(active_name)
    if domain and any(domain == d or domain.endswith('.' + d) for d in DOMAIN_BLACKLIST):
        return True
    return False


class FocusGhost(rumps.App):
    def __init__(self):
        super().__init__(DEFAULT_TITLE)
        self.goal = None
        self.distraction_count = 0
        self.is_warning = False
        self._flash_on = False

        self.complete_item = rumps.MenuItem("✅ Mark as Complete", callback=self.mark_complete)
        self.complete_item.set_callback(None)
        self.change_item = rumps.MenuItem("🔄 Change Focus Goal", callback=self.change_goal)

        self.menu = [self.complete_item, self.change_item]

    def _display_text(self):
        return self.goal if len(self.goal) <= 20 else self.goal[:19] + "…"

    def _status_button(self):
        try:
            return self._nsapp.nsstatusitem.button()
        except AttributeError:
            return None

    def _apply_warning_title(self, red_on):
        text = f"⚠️ {self._display_text()}"
        color = NSColor.systemRedColor() if red_on else NSColor.labelColor()
        attrs = {
            NSForegroundColorAttributeName: color,
            NSFontAttributeName: NSFont.menuBarFontOfSize_(0),
        }
        attr_str = NSAttributedString.alloc().initWithString_attributes_(text, attrs)
        button = self._status_button()
        if button is not None:
            button.setAttributedTitle_(attr_str)
        else:
            self.title = text

    def _clear_attributed_title(self):
        button = self._status_button()
        if button is not None:
            empty = NSAttributedString.alloc().initWithString_("")
            button.setAttributedTitle_(empty)

    def _set_active_title(self):
        if self.is_warning:
            self._flash_on = True
            self._apply_warning_title(True)
        else:
            self._clear_attributed_title()
            self.title = f"🟢 {self._display_text()}"

    def _prompt_goal(self):
        window = rumps.Window(
            title="FocusGhost",
            message="What's your focus goal right now?",
            default_text=self.goal or "",
            ok="Set Goal",
            cancel="Cancel",
            dimensions=(320, 60),
        )
        response = window.run()
        if response.clicked and response.text.strip():
            self.goal = response.text.strip()
            self.distraction_count = 0
            self.is_warning = False
            self.complete_item.set_callback(self.mark_complete)
            self._set_active_title()

    def change_goal(self, _):
        self._prompt_goal()

    def mark_complete(self, _):
        os.system('afplay /System/Library/Sounds/Glass.aiff &')
        rumps.notification(
            title="Task Smashed!",
            subtitle="FocusGhost cleared.",
            message="",
        )
        self.goal = None
        self.distraction_count = 0
        self.is_warning = False
        self.complete_item.set_callback(None)
        self._clear_attributed_title()
        self.title = DEFAULT_TITLE

    @rumps.timer(FLASH_INTERVAL)
    def flash_warning(self, _):
        if not self.is_warning:
            return
        self._flash_on = not self._flash_on
        self._apply_warning_title(self._flash_on)

    @rumps.timer(60)
    def monitor_focus(self, _):
        if not self.goal:
            return

        active_app = NSWorkspace.sharedWorkspace().activeApplication()
        if not active_app:
            return
        active_name = active_app.get('NSApplicationName', '')

        if is_distraction(active_name):
            self.distraction_count += 1
            if self.distraction_count >= DISTRACTION_THRESHOLD and not self.is_warning:
                self.is_warning = True
                self._set_active_title()
        else:
            if self.distraction_count > 0 or self.is_warning:
                self.distraction_count = 0
                if self.is_warning:
                    self.is_warning = False
                    self._set_active_title()


if __name__ == "__main__":
    FocusGhost().run()
