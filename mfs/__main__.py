"""Enable running as a module: python -m mif."""

from .main import main

if __name__ == "__main__":
    raise SystemExit(main())
