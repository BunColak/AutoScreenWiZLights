import asyncio
import pyscreenshot as ImageGrab
import threading

from pywizlight.bulb import wizlight, PilotBuilder, discovery

def get_average_screen_color():
    image = ImageGrab.grab().convert("RGB")
    return get_average_color((24,290), 50, image)

async def get_bulbs():
    return await discovery.find_wizlights(discovery)

def get_average_color(xy, n, image):
    r, g, b = 0, 0, 0
    count = 0
    for s in range(image.width):
        for t in range(image.height):
            pixlr, pixlg, pixlb = image.getpixel((s,t))
            r += pixlr
            g += pixlg
            b += pixlb
            count += 1
    return (int(r/count), int(g/count), int(b/count))

async def mainLoop(bulbs):
    while True:
        r, g, b = get_average_screen_color()
        color = PilotBuilder(rgb = (r, g, b))
        print(f'Changing {len(bulbs)} to RGB({r},{g},{b})')
        for bulb in bulbs:
            await bulb.turn_on(color)
        await asyncio.sleep(30)


async def main():
    bulbs = await get_bulbs()
    print(f'Found {len(bulbs)} bulbs')
    await mainLoop(bulbs)

loop = asyncio.new_event_loop()
loop.run_until_complete(main())