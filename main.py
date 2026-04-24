"""Entry point for the GemEdge assignment scaffold."""

from scraper.pipeline import run_pipeline


def main() -> None:
    """Run the minimal scraping pipeline."""
    run_pipeline()


if __name__ == "__main__":
    main()
