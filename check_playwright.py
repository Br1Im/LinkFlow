#!/usr/bin/env python3
try:
    from playwright.async_api import async_playwright
    print("Playwright available")
except ImportError:
    print("Playwright NOT available")