"""
Root entry point.

pygbag requires the served entry file to be `main.py` in the packaged folder
with a top-level asyncio.run() call. Also works on desktop: `python main.py`.
"""

import asyncio

from src.main import main

asyncio.run(main())
