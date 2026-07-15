"""Network Scanner - Application entry point."""
from __future__ import annotations

from ui.dashboard import Dashboard
from utils.logger import get_logger


def main() -> None:
    """Launch the Network Scanner desktop application."""
    logger = get_logger(__name__)
    logger.info("Starting Network Scanner")
    app = Dashboard()
    app.mainloop()


if __name__ == "__main__":
    main()
