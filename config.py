"""
SaveZero - Configuration & Dynamic Selectors Module
====================================================

This module manages all runtime settings, environment variable resolution,
and cascading DOM selector heuristics for the SaveZero automation suite.

Key Components:
    - ScraperConfig: Dataclass encapsulating all timing, throttle, and session parameters.
    - Cascading Selectors: Robust, attribute-based XPath and CSS selectors decoupled from
      unstable, minified class names.
    - Anti-Detection Indicators: Keywords used to proactively detect Meta rate-limiting.

Settings can be customized via environment variables, a local `.env` file,
or command-line arguments.
"""

import os
from dataclasses import dataclass
from typing import List, Tuple
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

# Load environment variables from local .env file if present
load_dotenv()


def _get_env_float(key: str, default: float) -> float:
    """Safely retrieves a float from environment variables with fallback.

    Args:
        key: The environment variable name.
        default: The default float value if the key is missing or invalid.

    Returns:
        The resolved float value.
    """
    try:
        val = os.getenv(key)
        return float(val) if val is not None else default
    except ValueError:
        return default


def _get_env_int(key: str, default: int) -> int:
    """Safely retrieves an integer from environment variables with fallback.

    Args:
        key: The environment variable name.
        default: The default integer value if the key is missing or invalid.

    Returns:
        The resolved integer value.
    """
    try:
        val = os.getenv(key)
        return int(val) if val is not None else default
    except ValueError:
        return default


@dataclass
class ScraperConfig:
    """Runtime configuration container for the SaveZero cleanser engine.

    Attributes:
        INSTAGRAM_USERNAME: The target account's username.
        TARGET_SAVED_URL: The complete URL to the user's saved collection.
        MODE: Execution engine mode ('api' for fast in-browser requests, 'ui' for visual clicks).
        CHROME_USER_DATA_DIR: Filesystem path to the isolated Chrome automation session profile.
        CHROME_PROFILE_NAME: Profile directory name within the user data folder.
        API_MIN_DELAY: Minimum pause (seconds) between consecutive API calls.
        API_MAX_DELAY: Maximum pause (seconds) between consecutive API calls.
        MIN_ACTION_DELAY: Minimum inter-post delay (seconds) in UI mode.
        MAX_ACTION_DELAY: Maximum inter-post delay (seconds) in UI mode.
        MICRO_DELAY_MIN: Minimum pause before/after clicks in UI mode.
        MICRO_DELAY_MAX: Maximum pause before/after clicks in UI mode.
        BATCH_SIZE_BEFORE_PAUSE: Number of posts cleared before taking a micro-breather.
        BATCH_PAUSE_MIN: Minimum duration (seconds) of a micro-breather.
        BATCH_PAUSE_MAX: Maximum duration (seconds) of a micro-breather.
        PAUSE_EVERY_1000_SEC: Rest duration (seconds) after clearing 1,000 posts.
        PAUSE_EVERY_2000_SEC: Rest duration (seconds) after clearing 2,000 posts.
        MAX_POST_RETRIES: Maximum retry attempts for stubborn or transiently failed posts.
        MAX_IDLE_SCROLLS: Maximum consecutive empty scrolls before concluding collection is empty.
        SCROLL_PIXELS: Default pixel distance per scroll increment.
        MODAL_TIMEOUT: Explicit wait timeout (seconds) for dialog appearance.
        ELEMENT_TIMEOUT: Explicit wait timeout (seconds) for individual interactive elements.
    """

    # --- Account & Endpoint Targets ---
    INSTAGRAM_USERNAME: str = os.getenv("INSTAGRAM_USERNAME", "your_username")
    TARGET_SAVED_URL: str = os.getenv(
        "TARGET_SAVED_URL",
        f"https://www.instagram.com/{os.getenv('INSTAGRAM_USERNAME', 'your_username')}/saved/all-posts/",
    )

    # --- Engine Mode ---
    # 'api': In-browser asynchronous calls (~1.5s/post, recommended)
    # 'ui' : Visual modal navigation and clicking (~10s/post)
    MODE: str = os.getenv("CLEANER_MODE", "api").lower()

    # --- Browser Profile Isolation ---
    # Using an isolated profile prevents locking conflicts with daily Chrome browsers
    CHROME_USER_DATA_DIR: str = os.path.expanduser(
        os.getenv("CHROME_USER_DATA_DIR", r"~/.savezero_session")
    )
    CHROME_PROFILE_NAME: str = os.getenv("CHROME_PROFILE_NAME", "Default")

    # --- Fast API Mode Rate Limits ---
    API_MIN_DELAY: float = _get_env_float("API_MIN_DELAY", 1.2)
    API_MAX_DELAY: float = _get_env_float("API_MAX_DELAY", 2.0)

    # --- Visual UI Mode Rate Limits ---
    MIN_ACTION_DELAY: float = _get_env_float("MIN_ACTION_DELAY", 3.5)
    MAX_ACTION_DELAY: float = _get_env_float("MAX_ACTION_DELAY", 6.0)
    MICRO_DELAY_MIN: float = _get_env_float("MICRO_DELAY_MIN", 0.8)
    MICRO_DELAY_MAX: float = _get_env_float("MICRO_DELAY_MAX", 1.8)

    # --- Micro-Batch Cooldown (Every 40 posts) ---
    BATCH_SIZE_BEFORE_PAUSE: int = _get_env_int("BATCH_SIZE_BEFORE_PAUSE", 40)
    BATCH_PAUSE_MIN: float = _get_env_float("BATCH_PAUSE_MIN", 30.0)
    BATCH_PAUSE_MAX: float = _get_env_float("BATCH_PAUSE_MAX", 60.0)

    # --- Major Tiered Milestone Pauses ---
    # 1,000 posts: 15-minute cooldown
    PAUSE_EVERY_1000_SEC: float = _get_env_float("PAUSE_EVERY_1000_MINUTES", 15.0) * 60.0
    # 2,000 posts: 1-hour cooldown
    PAUSE_EVERY_2000_SEC: float = _get_env_float("PAUSE_EVERY_2000_MINUTES", 60.0) * 60.0

    # --- Bounds & Timeouts ---
    MAX_POST_RETRIES: int = _get_env_int("MAX_POST_RETRIES", 3)
    MAX_IDLE_SCROLLS: int = _get_env_int("MAX_IDLE_SCROLLS", 5)
    SCROLL_PIXELS: int = _get_env_int("SCROLL_PIXELS", 900)
    MODAL_TIMEOUT: int = _get_env_int("MODAL_TIMEOUT", 10)
    ELEMENT_TIMEOUT: int = _get_env_int("ELEMENT_TIMEOUT", 6)


# =============================================================================
# Cascading DOM Selectors
# =============================================================================
# Instagram frequently re-compiles and obfuscates CSS class names (e.g., ._aagw, .x1lliihq).
# To ensure resilience, selectors rely on semantic attributes (href, role, aria-label)
# and structural heuristics arranged in priority cascades.

GRID_POST_SELECTORS: List[Tuple[str, str]] = [
    # 1. Links inside main content matching post or reel shortcode pattern
    (By.XPATH, "//main//a[contains(@href, '/p/') or contains(@href, '/reel/')]"),
    # 2. General anchor attribute matching
    (By.CSS_SELECTOR, "a[href*='/p/'], a[href*='/reel/']"),
    # 3. Article container anchors
    (By.XPATH, "//article//a[contains(@href, '/p/')]"),
]

MODAL_DIALOG_SELECTORS: List[Tuple[str, str]] = [
    # 1. Semantic dialog role
    (By.XPATH, "//div[@role='dialog']"),
    # 2. CSS role selector
    (By.CSS_SELECTOR, "div[role='dialog']"),
    # 3. Top-layer modal overlay with article child
    (By.XPATH, "//div[contains(@style, 'z-index') and descendant::article]"),
]

# Saved / Bookmark toggle button within the open modal dialog:
# When currently SAVED   : aria-label is "Remove", "Saved", or "Unsave"
# When currently UNSAVED : aria-label toggles to "Save"
BOOKMARK_REMOVE_SELECTORS: List[Tuple[str, str]] = [
    # 1. Button containing an element with 'Remove', 'Unsave', or 'Saved' label
    (By.XPATH, "//div[@role='dialog']//button[descendant::*[@aria-label='Remove' or @aria-label='Unsave' or @aria-label='Saved']]"),
    # 2. Any interactive wrapper around the target label
    (By.XPATH, "//div[@role='dialog']//*[@aria-label='Remove' or @aria-label='Unsave' or @aria-label='Saved']/ancestor-or-self::*[@role='button' or self::button]"),
    # 3. Direct SVG with matching aria-label
    (By.XPATH, "//div[@role='dialog']//*[local-name()='svg' and (@aria-label='Remove' or @aria-label='Unsave' or @aria-label='Saved')]"),
    # 4. Action bar position heuristic: bookmark button is typically the last button in the action section
    (By.XPATH, "//div[@role='dialog']//section//div[contains(@class, '')]//button[last()]"),
]

# Verification selector to confirm the post transitioned to unsaved ("Save") state
BOOKMARK_ALREADY_UNSAVED_SELECTORS: List[Tuple[str, str]] = [
    (By.XPATH, "//div[@role='dialog']//button[descendant::*[@aria-label='Save']]"),
    (By.XPATH, "//div[@role='dialog']//*[@aria-label='Save']/ancestor-or-self::*[@role='button' or self::button]"),
]

# Modal close button fallback selectors (used if Keys.ESCAPE fails)
MODAL_CLOSE_SELECTORS: List[Tuple[str, str]] = [
    (By.XPATH, "//div[@role='dialog']//button[descendant::*[@aria-label='Close']]"),
    (By.XPATH, "//*[@aria-label='Close']/ancestor-or-self::button"),
    (By.CSS_SELECTOR, "svg[aria-label='Close']"),
]

# Text triggers indicating Meta velocity blocks or account challenges
ACTION_BLOCK_INDICATORS: List[str] = [
    "Try Again Later",
    "Action Blocked",
    "We restrict certain activity",
    "Something went wrong",
    "Please wait a few minutes before you try again",
]
