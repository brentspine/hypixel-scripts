import asyncio
from enum import Enum
import random
from container_click import click_slot
import minescript # type: ignore
from minescript import ItemStack # type: ignore 
from datetime import datetime
import sys

async def goto_and_wait(target_x: float, target_y: float, target_z: float, tolerance: float = 0.7, timeout: float = 0, announce_timeout: bool = True) -> bool:
    start_time = datetime.now().timestamp() if timeout > 0 else sys.maxsize
    # Tell baritone to move
    minescript.chat(f"#goto {target_x} {target_y} {target_z}")
    
    while True:
        if datetime.now().timestamp() - start_time > timeout:
            if announce_timeout:
                minescript.echo(f"Timeout waiting for position arrival ({target_x}, {target_y}, {target_z})")
            return False
        player_x, player_y, player_z = minescript.player().position

        # Check each axis independently
        close_x = abs(player_x - target_x) <= tolerance
        close_y = abs(player_y - target_y) <= tolerance
        close_z = abs(player_z - target_z) <= tolerance

        if close_x and close_y and close_z:
            break
        if random.randint(1,20) == 1: # In case we bug out
            minescript.chat(f"#goto {target_x} {target_y} {target_z}")
        await asyncio.sleep(0.2)
    minescript.chat("#stop")
    print(f"Arrived near ({target_x}, {target_y}, {target_z}) at ({player_x:.2f}, {player_y:.2f}, {player_z:.2f})")
    return True

async def goto_and_wait_with_yp(target_x: float, target_y: float, target_z: float, yaw: float, pitch: float, tolerance: float = 0.7):
    await goto_and_wait(target_x, target_y, target_z, tolerance)
    minescript.player_set_orientation(yaw, pitch)
  
async def wait_until_container(is_open: bool):
    while True:
        container = minescript.container_get_items()

        if container is None and not is_open:
            break
        if container is not None and is_open:
            break

        await asyncio.sleep(0.2)
        
async def wait_till_container_change(old_items: ItemStack, timeout: float = 0.0):
    start_time = datetime.now().timestamp() if timeout > 0 else sys.maxsize
    while True:
        if datetime.now().timestamp() - start_time > timeout:
            minescript.echo("Timeout waiting for container change")
            return False
        new_items = minescript.container_get_items()
        if new_items is None:
            return
        for i in range(len(old_items)):
            if old_items[i].slot != new_items[i].slot:
                minescript.echo(f"Slot change")
                return True
            if old_items[i].count != new_items[i].count:
                minescript.echo(f"Count change")
                return True
            if old_items[i].nbt != new_items[i].nbt:
                minescript.echo(f"nbt change")
                return True
        await asyncio.sleep(0.2)

async def click_and_wait_for_change(slot, button=0, shift=False, index_mode="container"):
    old_items = minescript.container_get_items()
    clicked = click_slot(slot, button=0, shift=False, index_mode="container")
    await time.sleep(0.2) # So the click doesnt count as change
    await wait_till_container_change(old_items)
    return clicked

async def right_click_and_wait_for_container():
    old_container = minescript.container_get_items()
    minescript.player_press_use(True)
    await time.sleep(0.2)
    minescript.player_press_use(False)
    await wait_until_container(True)
    return

class SmoothLookType(Enum):
    INSTANT = 1
    LINEAR = 2

# Not implemented yet
async def natural_look_at(target_x: float, target_y: float, target_z: float):
    # Do instant for now
    minescript.player_look_at(target_x, target_y, target_z)
    minescript.echo(f"Looked at ({target_x}, {target_y}, {target_z}) naturally")

# Used in advertise script
def random_chars(length: int) -> str:
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(random.choice(chars) for _ in range(length))
