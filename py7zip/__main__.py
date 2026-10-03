"""Enable ``python -m py7zip`` as a synonym for the console script."""

from .cli import main

raise SystemExit(main())
