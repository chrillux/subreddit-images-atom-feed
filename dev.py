import asyncio
import json

import src.app as app


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.main())


if __name__ == "__main__":
    main()