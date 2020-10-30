import asyncio
import pyscreenshot as ImageGrab
import threading
import colorsys
import math
import collections

from pywizlight.bulb import wizlight, PilotBuilder, discovery

MIN_SATURATION = 0.75
POLLING_RATE = 10
CHANGE_TOLERANCE = 0.2

collection = collections.deque(3*(0,0,0), 3)

def get_average_screen_color():
    image = ImageGrab.grab().convert("RGB")
    return get_average_color(image)

async def get_bulbs():
    return await discovery.find_wizlights(discovery)

def get_average_color(image):
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

def adjust_color_saturation(rgb):
    r, g, b = rgb
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    if s < MIN_SATURATION:
        r, g, b = colorsys.hls_to_rgb(h, l, MIN_SATURATION)
        return (int(r*255), int(g*255), int(b*255))
    else:
        return (r,g,b)

def get_distance(rgb1, rgb2):
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2

    return math.sqrt((r1/255 - r2/255)**2 + (g1/255 - g2/255)**2 + (b1/255 - b2/255)**2)

def should_update_lights(r,g,b):
    collection.append((r,g,b))
    if collection[0] == 0 or collection[1] == 0:
        return True
    
    distance_with_old = get_distance((r,g,b), collection[0])
    distance_between_old_prev = get_distance(collection[0], collection[1])

    if distance_between_old_prev < CHANGE_TOLERANCE:
        return False;
    else:
        if distance_with_old < CHANGE_TOLERANCE:
            return False
        else:
            return True


async def mainLoop(bulbs):
    while True:
        r, g, b = adjust_color_saturation(get_average_screen_color())
        color = PilotBuilder(rgb = (r, g, b))
        if should_update_lights(r,g,b):
            print(f'Changing {len(bulbs)} to RGB({r},{g},{b})')
            for bulb in bulbs:
                await bulb.turn_on(color)
        else:
            print('Change is within tolerance')
        await asyncio.sleep(POLLING_RATE)


async def main():
    bulbs = await get_bulbs()
    print(f'Found {len(bulbs)} bulbs')
    await mainLoop(bulbs)

loop = asyncio.new_event_loop()
loop.run_until_complete(main())