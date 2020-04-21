def hello(*, name: str) -> None:
    """hello message"""
    pass


if __name__ == "__main__":
    from gogen.cli import describe

    describe(__name__)
