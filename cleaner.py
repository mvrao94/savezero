"""
SaveZero - Automated Saved Collection Cleanser
==============================================

A self-healing Python automation tool designed to programmatically traverse and unsave
large Instagram saved collections while pacing requests and detecting common browser
or action-block failures. It cannot guarantee that Instagram will not restrict an account.

Architecture:
    1. Dynamic Selector Resolution:
       Bypasses fragile, obfuscated CSS classes by utilizing relative XPaths, semantic ARIA
       attributes, and self-healing selector priority caching.
    2. Dual Execution Engines:
       - In-Browser API Mode (Default): Direct asynchronous fetch calls from the active
         authenticated browser session (~1.5s/post, ~2,000+ posts/hour).
       - Visual UI Mode: Full DOM traversal, modal lifecycle validation, and simulated clicks.
    3. Tiered Milestone Throttling:
       - Micro-breathers: Randomized 30s to 60s pauses every 40 posts.
       - Hourly rest: 15-minute cooldown every 1,000 posts.
       - Multi-hour rest: 1-hour cooldown every 2,000 posts.
    4. Self-Healing Browser Recovery:
       Automatically catches dropped DevTools connections, system sleep interruptions, or
       renderer crashes, relaunching Chrome and seamlessly resuming without losing progress.

Usage:
    # Direct execution after installing the package dependencies:
    python cleaner.py

    # Override options via CLI:
    python cleaner.py --username your_username --mode api
"""

import argparse
import logging
import os
import random
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from config import (
    ACTION_BLOCK_INDICATORS,
    BOOKMARK_ALREADY_UNSAVED_SELECTORS,
    BOOKMARK_REMOVE_SELECTORS,
    GRID_POST_SELECTORS,
    MODAL_CLOSE_SELECTORS,
    MODAL_DIALOG_SELECTORS,
    ScraperConfig,
)

# -----------------------------------------------------------------------------
# Structured Logging Setup
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("instagram_cleaner.log", mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger("SaveZero")


class ActionBlockedException(Exception):
    """Raised when Instagram serves an action block, rate-limit, or challenge dialog."""

    pass


class SelectorEngine:
    """Self-healing DOM selector manager with dynamic caching.

    Instead of querying every fallback selector sequentially on every post, the
    SelectorEngine caches the most recently successful selector for each element
    category and tries it first in subsequent iterations, minimizing DOM overhead.

    Attributes:
        cached_selectors: Dictionary mapping category names to their last successful
            (By, selector_string) tuple.
    """

    def __init__(self) -> None:
        """Initializes an empty selector cache."""
        self.cached_selectors: Dict[str, Tuple[str, str]] = {}

    def find_element(
        self,
        driver_or_parent: Any,
        selectors: List[Tuple[str, str]],
        category_name: str,
        timeout: int = 5,
    ) -> Optional[WebElement]:
        """Resolves an element by testing candidate selectors in prioritized order.

        Prioritizes the cached winner from previous successful queries, updating the
        cache whenever a new working selector is discovered.

        Args:
            driver_or_parent: WebDriver instance or parent WebElement.
            selectors: Ordered list of (By, selector_string) candidate tuples.
            category_name: Identifier for the element role (e.g. 'bookmark_remove').
            timeout: Maximum seconds to wait for presence of each candidate.

        Returns:
            The resolved WebElement if visible and found; None if all candidates fail.
        """
        # Place the cached winner at the head of the evaluation list
        candidate_list = list(selectors)
        if category_name in self.cached_selectors:
            cached = self.cached_selectors[category_name]
            if cached in candidate_list:
                candidate_list.remove(cached)
                candidate_list.insert(0, cached)

        wait = WebDriverWait(driver_or_parent, timeout)

        for by_type, selector_str in candidate_list:
            try:
                element = wait.until(EC.presence_of_element_located((by_type, selector_str)))
                if element and element.is_displayed():
                    self.cached_selectors[category_name] = (by_type, selector_str)
                    return element
            except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
                continue

        logger.debug(f"Selector resolution exhausted for category '{category_name}'.")
        return None

    def find_all_elements(
        self,
        driver_or_parent: Any,
        selectors: List[Tuple[str, str]],
    ) -> List[WebElement]:
        """Finds all matching elements across a selector cascade.

        Args:
            driver_or_parent: WebDriver instance or parent WebElement.
            selectors: Ordered list of (By, selector_string) candidate tuples.

        Returns:
            A list of WebElements matching the first valid selector in the cascade.
        """
        for by_type, selector_str in selectors:
            try:
                elements = driver_or_parent.find_elements(by_type, selector_str)
                if elements:
                    return elements
            except (NoSuchElementException, StaleElementReferenceException):
                continue
        return []


class SaveZeroCleanser:
    """Main orchestration controller for traversing and unsaving Instagram posts.

    Attributes:
        config: ScraperConfig dataclass holding runtime options and rate limits.
        driver: Active Selenium Chrome WebDriver instance.
        selector_engine: SelectorEngine instance managing dynamic fallback locators.
        processed_shortcodes: Set tracking visited post shortcodes to prevent re-processing.
        cleared_count: Total posts successfully unsaved in the current session.
        skipped_count: Total posts skipped (already unsaved or deleted).
        failed_count: Total posts that failed after maximum retry attempts.
    """

    def __init__(self, config: Optional[ScraperConfig] = None) -> None:
        """Initializes cleanser state, metrics, and selector engine.

        Args:
            config: Optional custom ScraperConfig. If omitted, uses default ScraperConfig.
        """
        self.config: ScraperConfig = config or ScraperConfig()
        self.driver: Optional[webdriver.Chrome] = None
        self.selector_engine: SelectorEngine = SelectorEngine()
        self.processed_shortcodes: Set[str] = set()
        self.attempt_counts: Dict[str, int] = {}
        self.cleared_count: int = 0
        self.skipped_count: int = 0
        self.failed_count: int = 0

    # -------------------------------------------------------------------------
    # Driver Lifecycle & Anti-Fingerprinting
    # -------------------------------------------------------------------------
    def init_driver(self, use_user_profile: bool = True) -> webdriver.Chrome:
        """Configures and launches Chrome with stealth flags and session persistence.

        Includes flags to prevent Chrome from background-throttling or discarding tabs
        during long-running automated runs. Patches navigator.webdriver via CDP.

        Args:
            use_user_profile: If True, uses the dedicated automation profile directory
                to retain cookies and 2FA authentication state across runs.

        Returns:
            An active, configured webdriver.Chrome instance.
        """
        logger.info("Initializing Selenium WebDriver...")
        service = Service(ChromeDriverManager().install())

        def build_options(user_dir: Optional[str], profile_name: Optional[str]) -> Options:
            opts = Options()
            # Disable automation detection banners and flags
            opts.add_argument("--disable-blink-features=AutomationControlled")
            opts.add_argument("--start-maximized")
            opts.add_argument("--disable-infobars")
            opts.add_argument("--disable-notifications")

            # Prevent Windows power saving and Chrome memory-saver from killing background DevTools
            opts.add_argument("--disable-background-timer-throttling")
            opts.add_argument("--disable-backgrounding-occluded-windows")
            opts.add_argument("--disable-renderer-backgrounding")
            opts.add_argument("--disable-features=CalculateNativeWinOcclusion")
            opts.add_argument("--disable-hang-monitor")

            opts.add_experimental_option("excludeSwitches", ["enable-automation"])
            opts.add_experimental_option("useAutomationExtension", False)

            if user_dir:
                opts.add_argument(f"--user-data-dir={user_dir}")
                if profile_name:
                    opts.add_argument(f"--profile-directory={profile_name}")
            return opts

        # Launch using dedicated automation profile
        if use_user_profile and self.config.CHROME_USER_DATA_DIR:
            os.makedirs(self.config.CHROME_USER_DATA_DIR, exist_ok=True)
            logger.info(f"Using Chrome automation profile: {self.config.CHROME_USER_DATA_DIR}")
            options = build_options(
                self.config.CHROME_USER_DATA_DIR, self.config.CHROME_PROFILE_NAME
            )
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            options = build_options(None, None)
            self.driver = webdriver.Chrome(service=service, options=options)

        # Remove navigator.webdriver attribute via Chrome DevTools Protocol (CDP)
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """},
        )
        return self.driver

    # -------------------------------------------------------------------------
    # Rate Limiting & Cooldown Management
    # -------------------------------------------------------------------------
    def jitter_sleep(self, min_sec: float, max_sec: float, context: str = "") -> None:
        """Sleeps for a randomized duration to evade behavioral fingerprinting.

        Args:
            min_sec: Lower bound of sleep interval.
            max_sec: Upper bound of sleep interval.
            context: Informative label describing the action being paced.
        """
        duration = round(random.uniform(min_sec, max_sec), 2)
        if context:
            logger.debug(f"Pacing delay ({context}): {duration}s")
        time.sleep(duration)

    def action_cooldown(self) -> None:
        """Applies standard randomized inter-action delay in UI mode."""
        self.jitter_sleep(
            self.config.MIN_ACTION_DELAY,
            self.config.MAX_ACTION_DELAY,
            context="Inter-action Throttle",
        )

    def countdown_sleep(self, total_seconds: float, label: str) -> None:
        """Sleeps with periodic countdown logging so the console stays active and informative.

        Args:
            total_seconds: Total sleep duration in seconds.
            label: Descriptive name for the cooldown milestone.
        """
        end_time = time.time() + total_seconds
        while True:
            remaining = end_time - time.time()
            if remaining <= 0:
                break
            rem_min = int(remaining // 60)
            rem_sec = int(remaining % 60)
            if remaining > 60:
                logger.info(
                    f"[{label}] Cooling down... {rem_min}m {rem_sec}s remaining until resume."
                )
                time.sleep(min(60, remaining))
            else:
                logger.info(f"[{label}] Resuming in {int(remaining)}s...")
                time.sleep(remaining)
                break
        logger.info(f"[{label}] Rest interval complete! Resuming work...")

    def check_batch_pause(self) -> None:
        """Enforces tiered cooldown pauses to safeguard the account from Meta rate limits.

        Tier 1 (Multi-Hour): Every 2,000 posts -> 1 hour rest.
        Tier 2 (Hourly):     Every 1,000 posts -> 15 minutes rest.
        Tier 3 (Velocity):   Every 40 posts    -> Randomized 30s to 60s micro-breather.
        """
        if self.cleared_count <= 0:
            return

        # 2,000-post milestone: 1-hour rest
        if self.cleared_count % 2000 == 0:
            logger.info("=" * 60)
            logger.info(f"🏆 [MILESTONE: {self.cleared_count} POSTS CLEARED]")
            logger.info("Resting for 1 HOUR to completely reset Instagram velocity limits...")
            logger.info("=" * 60)
            self.countdown_sleep(self.config.PAUSE_EVERY_2000_SEC, "1-Hour Milestone Rest")
            return

        # 1,000-post milestone: 15-minute rest
        if self.cleared_count % 1000 == 0:
            logger.info("=" * 60)
            logger.info(f"🎖️ [MILESTONE: {self.cleared_count} POSTS CLEARED]")
            logger.info("Resting for 15 MINUTES to safeguard your account against action limits...")
            logger.info("=" * 60)
            self.countdown_sleep(self.config.PAUSE_EVERY_1000_SEC, "15-Minute Milestone Rest")
            return

        # Micro-batch breather: every 40 posts (randomized 30s to 60s)
        if self.cleared_count % self.config.BATCH_SIZE_BEFORE_PAUSE == 0:
            pause_time = round(
                random.uniform(self.config.BATCH_PAUSE_MIN, self.config.BATCH_PAUSE_MAX), 1
            )
            logger.info(
                f"[Batch Rest] Cleared {self.cleared_count} posts. "
                f"Taking a quick breather of {pause_time}s..."
            )
            time.sleep(pause_time)

    # -------------------------------------------------------------------------
    # State Inspection & Action Block Detection
    # -------------------------------------------------------------------------
    def detect_action_block(self) -> None:
        """Scans page source for known Meta rate-limit, challenge, or action block warnings.

        Raises:
            ActionBlockedException: If any action-block keyword signature is detected.
        """
        try:
            page_text = self.driver.page_source.lower()
            for indicator in ACTION_BLOCK_INDICATORS:
                if indicator.lower() in page_text:
                    raise ActionBlockedException(
                        f"Instagram Action Block detected containing text: '{indicator}'"
                    )
        except ActionBlockedException:
            raise
        except Exception as e:
            logger.debug(f"Action block scan error (non-fatal): {e}")

    def safe_click(self, element: WebElement, description: str = "element") -> None:
        """Clicks an element, automatically falling back to JavaScript click if intercepted.

        Args:
            element: The WebElement to click.
            description: Human-readable name of the element for diagnostic logging.
        """
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                element,
            )
            self.jitter_sleep(0.3, 0.6)
            element.click()
        except ElementClickInterceptedException:
            logger.warning(f"Click intercepted on {description}; executing JS click fallback.")
            self.driver.execute_script("arguments[0].click();", element)
        except StaleElementReferenceException:
            raise

    # -------------------------------------------------------------------------
    # UI Mode: Modal Lifecycle Management
    # -------------------------------------------------------------------------
    def wait_for_modal_open(self) -> WebElement:
        """Verifies that the post detail modal dialog has fully mounted in the DOM.

        Returns:
            The resolved dialog WebElement.

        Raises:
            TimeoutException: If the modal does not mount within MODAL_TIMEOUT.
        """
        modal = self.selector_engine.find_element(
            self.driver,
            MODAL_DIALOG_SELECTORS,
            category_name="modal_dialog",
            timeout=self.config.MODAL_TIMEOUT,
        )
        if not modal:
            raise TimeoutException("Post modal dialog did not mount within expected timeout.")
        return modal

    def close_modal(self) -> bool:
        """Dismisses the open modal cleanly, verifying its disappearance from the DOM.

        Priority 1: Dispatches Keys.ESCAPE to the active element (least DOM-fragile).
        Priority 2: Locates and clicks the modal close button.
        Priority 3: Falls back to history back navigation.

        Returns:
            True if the modal was successfully dismissed; False otherwise.
        """
        try:
            active_el = self.driver.switch_to.active_element
            active_el.send_keys(Keys.ESCAPE)
            self.jitter_sleep(self.config.MICRO_DELAY_MIN, self.config.MICRO_DELAY_MAX)

            if not self.is_modal_present():
                return True

            close_btn = self.selector_engine.find_element(
                self.driver,
                MODAL_CLOSE_SELECTORS,
                category_name="modal_close",
                timeout=2,
            )
            if close_btn:
                self.safe_click(close_btn, description="Modal Close Button")

            WebDriverWait(self.driver, 4).until(lambda d: not self.is_modal_present())
            return True
        except Exception as e:
            logger.warning(f"Modal close issue: {e}. Executing fallback history back.")
            try:
                if "/p/" in self.driver.current_url:
                    self.driver.back()
                    self.jitter_sleep(1.5, 2.5)
            except Exception:
                pass
            return not self.is_modal_present()

    def is_modal_present(self) -> bool:
        """Checks whether any modal dialog currently exists and is displayed in the DOM.

        Returns:
            True if an active modal dialog is present; False otherwise.
        """
        for by_type, selector in MODAL_DIALOG_SELECTORS:
            elements = self.driver.find_elements(by_type, selector)
            if any(el.is_displayed() for el in elements):
                return True
        return False

    def process_post_modal(self, post_url: str) -> bool:
        """Executes the full UI unsave sequence on an individual post modal.

        Sequence:
            1. Verify modal opened.
            2. Idempotency check: Skip if already showing 'Save' (already unsaved).
            3. Locate active 'Remove' / 'Saved' bookmark button via fallback cascade.
            4. Click unsave button.
            5. State verification: Confirm button state flips to 'Save'.
            6. Dismiss modal cleanly.

        Args:
            post_url: Direct URL of the post being processed.

        Returns:
            True if the post was successfully unsaved or already unsaved; False on error.
        """
        try:
            self.wait_for_modal_open()
        except TimeoutException:
            logger.warning(f"Modal failed to open for {post_url}. Skipping.")
            return False

        self.jitter_sleep(
            self.config.MICRO_DELAY_MIN,
            self.config.MICRO_DELAY_MAX,
            context="Pre-click introspection",
        )

        # Idempotency check
        already_unsaved = self.selector_engine.find_element(
            self.driver,
            BOOKMARK_ALREADY_UNSAVED_SELECTORS,
            category_name="already_unsaved",
            timeout=2,
        )
        if already_unsaved:
            logger.info(f"Post {post_url} is already unsaved. Skipping click.")
            self.skipped_count += 1
            self.close_modal()
            return True

        # Locate active bookmark removal button
        remove_button = self.selector_engine.find_element(
            self.driver,
            BOOKMARK_REMOVE_SELECTORS,
            category_name="bookmark_remove",
            timeout=self.config.ELEMENT_TIMEOUT,
        )
        if not remove_button:
            logger.warning(f"Could not locate active bookmark button for {post_url}.")
            self.close_modal()
            return False

        self.safe_click(remove_button, description="Remove Bookmark Button")
        self.jitter_sleep(
            self.config.MICRO_DELAY_MIN,
            self.config.MICRO_DELAY_MAX,
            context="Post-click state sync",
        )

        # State toggle verification
        try:
            WebDriverWait(self.driver, 4).until(
                lambda d: self.selector_engine.find_element(
                    d,
                    BOOKMARK_ALREADY_UNSAVED_SELECTORS,
                    category_name="already_unsaved",
                    timeout=1,
                )
                is not None
            )
            self.cleared_count += 1
        except TimeoutException:
            logger.warning(f"Bookmark state did not confirm unsaved for {post_url}.")
            self.close_modal()
            return False

        self.close_modal()
        return True

    # -------------------------------------------------------------------------
    # Infinite Scrolling & Navigation
    # -------------------------------------------------------------------------
    def smooth_scroll_down(self) -> None:
        """Scrolls directly to document bottom to trigger Instagram's GraphQL infinite scroll."""
        logger.info("Scrolling to bottom of viewport to trigger Instagram infinite scroll...")
        scroll_script = """
            window.scrollTo({
                top: document.body.scrollHeight,
                left: 0,
                behavior: 'smooth'
            });
        """
        self.driver.execute_script(scroll_script)
        self.jitter_sleep(2.5, 4.0, context="Infinite Scroll Hydration")

    def extract_shortcode(self, href: str) -> Optional[str]:
        """Extracts the unique alphanumeric shortcode from an Instagram post/reel URL.

        Args:
            href: Full URL string (e.g. 'https://www.instagram.com/p/C7kX8s0.../').

        Returns:
            The isolated shortcode string (e.g. 'C7kX8s0...'), or the raw href on fallback.
        """
        try:
            path_segments = [seg for seg in urlparse(href).path.split("/") if seg]
            for index, segment in enumerate(path_segments[:-1]):
                if segment in ("p", "reel"):
                    return path_segments[index + 1]
        except Exception:
            pass
        return href

    def get_unprocessed_grid_links(self) -> List[Tuple[WebElement, str, str]]:
        """Scans current DOM for post links and filters out shortcodes already processed.

        Returns:
            List of tuples: (WebElement, full_href, shortcode).
        """
        grid_elements = self.selector_engine.find_all_elements(self.driver, GRID_POST_SELECTORS)
        unprocessed = []
        for elem in grid_elements:
            try:
                href = elem.get_attribute("href")
                if not href:
                    continue
                shortcode = self.extract_shortcode(href)
                if shortcode and shortcode not in self.processed_shortcodes:
                    unprocessed.append((elem, href, shortcode))
            except StaleElementReferenceException:
                continue
        return unprocessed

    # -------------------------------------------------------------------------
    # Authentication Gate
    # -------------------------------------------------------------------------
    def is_login_page(self) -> bool:
        """Determines if the browser is currently resting on an unauthenticated login page.

        Note: Inspects urlparse path specifically to avoid false-positives from query
        parameters like '?__coig_login=1' attached after successful redirects.

        Returns:
            True if currently unauthenticated on a login page; False otherwise.
        """
        try:
            parsed = urlparse(self.driver.current_url.lower())
            if "/saved/" in parsed.path:
                return False
            if "/accounts/login" in parsed.path or parsed.path == "/login":
                return True
            if len(self.driver.find_elements(By.NAME, "username")) > 0:
                return True
        except Exception:
            pass
        return False

    def ensure_authenticated(self, target_url: str) -> None:
        """Verifies active login session, pausing and prompting the user if authentication is needed.

        Args:
            target_url: Destination URL to navigate to once login is detected.

        Raises:
            TimeoutException: If login is not completed within 5 minutes.
        """
        if self.is_login_page():
            logger.info("=" * 60)
            logger.warning("[AUTHENTICATION REQUIRED]")
            logger.warning("Instagram requires authentication.")
            logger.warning(
                "Please log into your account and complete 2FA in the opened Chrome window."
            )
            logger.warning("SaveZero will automatically detect your login and continue...")
            logger.info("=" * 60)

            timeout = 300  # 5 minutes
            start_wait = time.time()
            while time.time() - start_wait < timeout:
                time.sleep(2)
                if not self.is_login_page():
                    logger.info("Authentication detected! Proceeding to saved collection...")
                    if "/saved/" not in self.driver.current_url.lower():
                        self.driver.get(target_url)
                    self.jitter_sleep(3.5, 5.5, context="Post-login collection load")
                    return
            raise TimeoutException("Authentication timed out after 5 minutes.")

    # -------------------------------------------------------------------------
    # Fast In-Browser API Mode
    # -------------------------------------------------------------------------
    def shortcode_to_media_id(self, shortcode: str) -> int:
        """Converts an Instagram Base64 URL shortcode into its 64-bit integer media_id.

        Instagram shortcodes are custom Base64 representations of the underlying 64-bit
        database primary key. This function decodes the shortcode locally with zero network calls.

        Args:
            shortcode: The post shortcode string (e.g. 'C7kX8s0...').

        Returns:
            The 64-bit integer media_id required by Instagram's unsave API endpoint.
        """
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        media_id = 0
        for char in shortcode:
            media_id = media_id * 64 + alphabet.index(char)
        return media_id

    def api_unsave_media(self, media_id: int) -> Dict[str, Any]:
        """Dispatches an asynchronous in-browser POST request to Instagram's unsave endpoint.

        Executes within the authenticated browser context, inheriting official session
        cookies (csrftoken, sessionid) and headers (x-ig-app-id) without DOM interaction lags.

        Args:
            media_id: The 64-bit integer ID of the media to unsave.

        Returns:
            A dictionary containing HTTP status_code and response payload.
        """
        script = """
        const callback = arguments[arguments.length - 1];
        const mediaId = arguments[0];
        const getCookie = (name) => {
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if (parts.length === 2) return parts.pop().split(';').shift();
            return '';
        };
        const csrfToken = getCookie('csrftoken');
        fetch(`https://www.instagram.com/api/v1/web/save/${mediaId}/unsave/`, {
            method: 'POST',
            headers: {
                'x-csrftoken': csrfToken,
                'x-ig-app-id': '936619743392459',
                'x-requested-with': 'XMLHttpRequest',
                'content-type': 'application/x-www-form-urlencoded',
                'x-asbd-id': '129477'
            },
            credentials: 'include'
        })
        .then(async (res) => {
            const text = await res.text();
            try {
                return callback({ status_code: res.status, json: JSON.parse(text) });
            } catch(e) {
                return callback({ status_code: res.status, raw: text });
            }
        })
        .catch((err) => callback({ status_code: 0, error: err.toString() }));
        """
        return self.driver.execute_async_script(script, str(media_id))

    def run_api_mode(self, target_url: str) -> None:
        """Executes fast in-browser API clearing with self-healing DevTools auto-recovery.

        Args:
            target_url: Destination URL of the saved collection.
        """
        idle_scroll_count = 0
        start_time = time.time()
        logger.info(
            "⚡ Fast In-Browser API Mode active: Unsaving at ~1.5s per post (no modal rendering lag)."
        )

        max_session_reconnects = 5
        reconnect_attempts = 0

        while reconnect_attempts < max_session_reconnects:
            try:
                while True:
                    self.detect_action_block()
                    candidates = self.get_unprocessed_grid_links()

                    if not candidates:
                        idle_scroll_count += 1
                        logger.info(
                            f"Scanning viewport for more posts (attempt {idle_scroll_count}/{self.config.MAX_IDLE_SCROLLS})..."
                        )
                        if idle_scroll_count in (2, 4):
                            # Auto-refresh: Since prior posts were unsaved in the database,
                            # reloading the page immediately brings the next batch of 24-36 items to top
                            logger.info(
                                "Refreshing page to load freshly surfaced saved posts into view..."
                            )
                            self.driver.refresh()
                            self.jitter_sleep(4.0, 6.0, context="Post-refresh Hydration")
                            continue
                        elif idle_scroll_count >= self.config.MAX_IDLE_SCROLLS:
                            logger.info(
                                "No more saved posts detected. Collection clearing complete!"
                            )
                            return

                        self.smooth_scroll_down()
                        continue

                    idle_scroll_count = 0

                    for elem, href, shortcode in candidates:
                        attempt = self.attempt_counts.get(shortcode, 0) + 1
                        self.attempt_counts[shortcode] = attempt
                        try:
                            media_id = self.shortcode_to_media_id(shortcode)
                        except Exception:
                            media_id = None

                        if not media_id:
                            logger.warning(
                                f"Could not calculate media ID for {shortcode}. Marking as failed."
                            )
                            self.failed_count += 1
                            self.processed_shortcodes.add(shortcode)
                            continue

                        logger.info(
                            f"[{self.cleared_count + 1}] Fast Unsave -> {shortcode} (Media ID: {media_id})"
                        )
                        resp = self.api_unsave_media(media_id)
                        status_code = resp.get("status_code", 0)

                        if status_code == 200:
                            self.cleared_count += 1
                            self.processed_shortcodes.add(shortcode)
                            self.attempt_counts.pop(shortcode, None)
                        elif status_code == 400 and "checkpoint_required" in str(resp):
                            raise ActionBlockedException("Instagram checkpoint challenge required.")
                        elif status_code == 429:
                            raise ActionBlockedException("Rate limit 429 received from Instagram.")
                        elif status_code in (400, 404):
                            logger.info(
                                f"Post {shortcode} was already unsaved or is unavailable. Skipping."
                            )
                            self.skipped_count += 1
                            self.processed_shortcodes.add(shortcode)
                            self.attempt_counts.pop(shortcode, None)
                        else:
                            logger.warning(
                                f"Unsave failed for {shortcode} with status {status_code} "
                                f"(attempt {attempt}/{self.config.MAX_POST_RETRIES})."
                            )
                            logger.debug(f"API response for {shortcode}: {resp}")
                            if attempt >= self.config.MAX_POST_RETRIES:
                                self.failed_count += 1
                                self.processed_shortcodes.add(shortcode)
                                self.attempt_counts.pop(shortcode, None)

                        reconnect_attempts = 0

                        # Fast API delay (1.2s - 2.0s)
                        duration = round(
                            random.uniform(self.config.API_MIN_DELAY, self.config.API_MAX_DELAY), 2
                        )
                        time.sleep(duration)

                        # Check tiered milestone and micro-breather cooldowns
                        self.check_batch_pause()

            except KeyboardInterrupt:
                logger.info("Script manually interrupted by user (Ctrl+C). Cleaning up...")
                break
            except ActionBlockedException as abe:
                logger.critical(
                    f"\n[CRITICAL WARNING] {abe}\nExecution halted to safeguard your account."
                )
                break
            except (WebDriverException, Exception) as e:
                err_str = str(e).lower()
                if (
                    "invalid session id" in err_str
                    or "disconnected" in err_str
                    or "not connected to devtools" in err_str
                    or "no such window" in err_str
                ):
                    reconnect_attempts += 1
                    logger.warning(
                        f"\n[SELF-HEALING RECOVERY] Chrome connection dropped ({getattr(e, 'msg', e)})."
                        f"\nAuto-restarting Chrome and resuming cleanly (attempt {reconnect_attempts}/{max_session_reconnects})...\n"
                    )
                    try:
                        self.cleanup()
                    except Exception:
                        pass
                    time.sleep(4)
                    self.init_driver()
                    self.driver.get(target_url)
                    self.jitter_sleep(4.0, 6.0)
                    self.ensure_authenticated(target_url)
                    idle_scroll_count = 0
                    continue
                else:
                    logger.exception(f"Unexpected error in API mode: {e}")
                    break
            finally:
                if reconnect_attempts == 0 or reconnect_attempts >= max_session_reconnects:
                    elapsed = round(time.time() - start_time, 1)
                    self.print_summary(elapsed)
                    self.cleanup()

    # -------------------------------------------------------------------------
    # Main Engine Entrypoint & UI Mode Loop
    # -------------------------------------------------------------------------
    def run(self, saved_url: Optional[str] = None) -> None:
        """Main execution entrypoint for SaveZero.

        Initializes driver, verifies authentication, routes to selected engine mode (api/ui),
        and orchestrates error recovery and progress tracking.

        Args:
            saved_url: Optional override destination URL. Defaults to config.TARGET_SAVED_URL.
        """
        target_url = saved_url or self.config.TARGET_SAVED_URL

        if not self.driver:
            self.init_driver()

        logger.info(f"Navigating to Instagram Saved Posts: {target_url}")
        self.driver.get(target_url)
        self.jitter_sleep(4.0, 6.0, context="Initial page load")
        self.ensure_authenticated(target_url)

        # Route to high-speed API engine if selected
        if self.config.MODE == "api":
            self.run_api_mode(target_url)
            return

        # Fallback: Visual UI Interaction Engine
        idle_scroll_count = 0
        start_time = time.time()
        max_session_reconnects = 5
        reconnect_attempts = 0

        while reconnect_attempts < max_session_reconnects:
            try:
                while True:
                    self.detect_action_block()
                    candidates = self.get_unprocessed_grid_links()

                    if not candidates:
                        idle_scroll_count += 1
                        logger.info(
                            f"No new unvisited posts in viewport (attempt {idle_scroll_count}/{self.config.MAX_IDLE_SCROLLS})."
                        )
                        if idle_scroll_count in (2, 4):
                            logger.info(
                                "Refreshing page to pull freshly surfaced saved posts into view..."
                            )
                            self.driver.refresh()
                            self.jitter_sleep(4.0, 6.0, context="Post-refresh Hydration")
                            continue
                        elif idle_scroll_count >= self.config.MAX_IDLE_SCROLLS:
                            logger.info(
                                "Max idle scrolls reached. No additional posts found in grid. Work complete!"
                            )
                            return

                        self.smooth_scroll_down()
                        continue

                    idle_scroll_count = 0

                    for elem, href, shortcode in candidates:
                        logger.info(f"[{self.cleared_count + 1}] Processing post: {href}")

                        retries = 0
                        success = False

                        while retries < self.config.MAX_POST_RETRIES and not success:
                            try:
                                self.safe_click(elem, description=f"Post thumbnail ({shortcode})")
                                success = self.process_post_modal(href)
                            except StaleElementReferenceException:
                                logger.warning(
                                    f"Stale element on thumbnail {shortcode}. Re-querying..."
                                )
                                try:
                                    refreshed = self.driver.find_element(
                                        By.XPATH, f"//a[contains(@href, '{shortcode}')]"
                                    )
                                    self.safe_click(refreshed, description="Refreshed thumbnail")
                                    success = self.process_post_modal(href)
                                except Exception:
                                    break
                            except TimeoutException as te:
                                logger.warning(f"Timeout on {shortcode}: {te}")
                                self.close_modal()
                            except Exception as e:
                                logger.warning(f"Hiccup on post {shortcode}: {e}")
                                self.close_modal()

                            retries += 1

                        if not success:
                            self.failed_count += 1
                            self.processed_shortcodes.add(shortcode)
                            logger.error(
                                f"Failed to clear post {shortcode} after {retries} retries. Continuing."
                            )
                        else:
                            self.processed_shortcodes.add(shortcode)

                        reconnect_attempts = 0
                        self.action_cooldown()
                        self.check_batch_pause()

            except KeyboardInterrupt:
                logger.info("Script manually interrupted by user (Ctrl+C). Cleaning up...")
                break
            except ActionBlockedException as abe:
                logger.critical(
                    f"\n[CRITICAL WARNING] {abe}\nExecution halted to safeguard your account."
                )
                break
            except (WebDriverException, Exception) as e:
                err_str = str(e).lower()
                if (
                    "invalid session id" in err_str
                    or "disconnected" in err_str
                    or "not connected to devtools" in err_str
                    or "no such window" in err_str
                ):
                    reconnect_attempts += 1
                    logger.warning(
                        f"\n[SELF-HEALING RECOVERY] Chrome connection dropped ({getattr(e, 'msg', e)})."
                        f"\nAuto-restarting Chrome and resuming cleanly (attempt {reconnect_attempts}/{max_session_reconnects})...\n"
                    )
                    try:
                        self.cleanup()
                    except Exception:
                        pass
                    time.sleep(4)
                    self.init_driver()
                    self.driver.get(target_url)
                    self.jitter_sleep(4.0, 6.0)
                    self.ensure_authenticated(target_url)
                    idle_scroll_count = 0
                    continue
                else:
                    logger.exception(f"Unexpected fatal error encountered: {e}")
                    break
            finally:
                if reconnect_attempts == 0 or reconnect_attempts >= max_session_reconnects:
                    elapsed = round(time.time() - start_time, 1)
                    self.print_summary(elapsed)
                    self.cleanup()

    def print_summary(self, elapsed_seconds: float) -> None:
        """Displays formatted execution metrics upon script completion or interruption.

        Args:
            elapsed_seconds: Total execution duration in seconds.
        """
        logger.info("=" * 60)
        logger.info(" SAVEZERO - EXECUTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f" Total Elapsed Time:      {elapsed_seconds} seconds")
        logger.info(f" Successfully Cleared:    {self.cleared_count}")
        logger.info(f" Already Unsaved/Skipped: {self.skipped_count}")
        logger.info(f" Failed / Retried Out:    {self.failed_count}")
        logger.info(f" Unique Posts Handled:    {len(self.processed_shortcodes)}")
        logger.info("=" * 60)

    def cleanup(self) -> None:
        """Safely terminates the active Chrome browser session."""
        if self.driver:
            logger.info("Closing browser session...")
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None


def main() -> None:
    """Parse command-line options and launch the cleanser."""
    parser = argparse.ArgumentParser(
        description="SaveZero - Programmatically traverse and unsave thousands of Instagram saved posts.",
        epilog=(
            "Examples:\n"
            "  python cleaner.py --username your_instagram_username\n"
            "  run.bat --username your_instagram_username\n"
            "  ./run.sh --username your_instagram_username\n"
            "  savezero --username your_instagram_username\n"
            "  savezero --url https://www.instagram.com/your_username/saved/all-posts/\n"
            "\n"
            "If --username is omitted, INSTAGRAM_USERNAME is read from .env; "
            "otherwise SaveZero prompts for it.\n"
            "The run.bat and run.sh launchers create a project environment and install "
            "missing dependencies automatically."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-u", "--username", type=str, help="Instagram username to clear saved posts for."
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=["api", "ui"],
        help="Clearing engine mode: 'api' (fast in-browser API ~1.5s/post) or 'ui' (visual modal clicks).",
    )
    parser.add_argument(
        "--url", type=str, help="Direct custom URL for a specific saved collection."
    )
    args = parser.parse_args()

    # Instantiate runtime configuration
    config = ScraperConfig()
    if args.mode:
        config.MODE = args.mode.lower()
    if args.username:
        config.INSTAGRAM_USERNAME = args.username
        config.TARGET_SAVED_URL = f"https://www.instagram.com/{args.username}/saved/all-posts/"
    if args.url:
        config.TARGET_SAVED_URL = args.url

    # Interactive prompt if username is unspecified
    if (
        config.INSTAGRAM_USERNAME in ("your_username", "your_username_here", "", None)
        and not args.url
    ):
        print("\n" + "=" * 60)
        print(" SAVEZERO - INSTAGRAM SAVED POSTS CLEANSER")
        print("=" * 60)
        entered_user = input("Please enter your Instagram username (without @): ").strip()
        if entered_user:
            config.INSTAGRAM_USERNAME = entered_user
            config.TARGET_SAVED_URL = f"https://www.instagram.com/{entered_user}/saved/all-posts/"
        else:
            print("No username provided. Exiting.")
            sys.exit(1)

    # Launch cleanser
    cleanser = SaveZeroCleanser(config=config)
    cleanser.run()


# -----------------------------------------------------------------------------
# CLI Entrypoint
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
