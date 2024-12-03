class DuniteException(Exception):
    """Base exception for all Dunite related errors."""

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
