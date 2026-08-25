import asyncio

# Pygbag scans this entry file to preload browser-side pygame.
import pygame  # noqa: F401

from poker_game import PokerApp


async def main():
    await PokerApp().run_async()


if __name__ == "__main__":
    asyncio.run(main())
