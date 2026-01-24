"""
GitHub Actions script for updating stonks images.

This script is used by the GitHub Actions workflow to automatically
update the stonks images with the latest market data.
"""

from stonks import main

if __name__ == "__main__":
    # Save images for GitHub Actions (using SVG format)
    main(save=True, format='svg')
