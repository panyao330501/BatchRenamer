import sys
import os

# Ensure the src directory is on the import path when run as a script
sys.path.insert(0, os.path.dirname(__file__))

from app import App


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
