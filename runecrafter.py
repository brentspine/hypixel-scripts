# Written by Brentspine 2025
# Copy only with credit
import minescript # type: ignore 
import asyncio
import parse_nbt
from parse_nbt import get_clear_string_name
from message_util import print_copyable_message
import util
import time
import container_click

class RuneInfo:
    def __init__(self, name: str, count: int, slot_map: dict):
        self.name = name
        self.count = count
        self.slot_map = slot_map

    def add_slot(self, slot: int, count: int):
        if slot not in self.slot_map:
            self.slot_map[slot] = 0
        self.slot_map[slot] += count
        self.count += count

    def on_craft_use(self, slot1: int, slot2: int):
        self.slot_map[slot1] -= 1
        self.slot_map[slot2] -= 1
        minescript.echo(f"Used rune {self.name} from slots {slot1} and {slot2}")

    def get_two_slots(self):
        slots = []
        for slot, count in self.slot_map.items():
            while count > 0 and len(slots) < 2:
                slots.append(slot)
                count -= 1
            if len(slots) >= 2:
                break
        return slots if len(slots) == 2 else None
    
    def on_was_crafted(self):
        # Find the earliest slot with the result
        for slot, count in self.slot_map.items():
            if count <= 0:
                continue
            self.slot_map[slot] += 1
            
    
    def get_readable_slots_string(self):
        return ", ".join([f"Slot {slot}: {count}" for slot, count in self.slot_map.items() if count > 0])


async def main():
    await util.goto_and_wait(-37, 69, -130, tolerance=1)
    await util.natural_look_at(-37.2, 69.8, -129.5)
    time.sleep(1)
    await util.right_click_and_wait_for_container()

    while True:
        inv = minescript.player_inventory()
        rune_map = {}
        for item in inv:
            if item is None:
                continue
              
            if item.item != "minecraft:player_head":
                continue
            
            # Parse the NBT data to JSON
            nbt_data = parse_nbt.from_item(item)
            
            if "_error" in nbt_data:
                minescript.echo(f"Error parsing NBT: {nbt_data['_error']}")
                minescript.echo(f"Raw NBT: {nbt_data.get('_raw_nbt', '')[:100]}...")
                continue
            
            # Navigate to the custom name in the parsed structure
            components = nbt_data.get("components", {})
            if not isinstance(components, dict):
                minescript.echo(f"Components is not a dict: {components}")
                continue
                
            nameJson = components.get("minecraft:custom_name")
            
            if nameJson is None:
                minescript.echo(f"No custom name found. Components: {list(components.keys())}")
                continue
            if not "rune" in str(nameJson).lower():
                continue
            if "III" in str(nameJson):
                continue
            
            name = get_clear_string_name(nameJson)
            if name not in rune_map:
                rune_map[name] = RuneInfo(name, 0, {})
            rune_map[name].add_slot(item.slot, item.count)

        for rune_name, info in rune_map.items():
            # print_copyable_message(f"{rune_name}: {info.count} (In {len(info.slot_map.items())} slots)")
            minescript.echo(f"{rune_name}: {info.count} (In {len(info.slot_map.items())} slots)")
            minescript.echo(f" Slots: {info.get_readable_slots_string()}")

        had_crafts = False
        for rune_name, info in rune_map.items():
            while info.count >= 2:
                had_crafts = True
                slots = info.get_two_slots()
                if slots is None:
                    break
                slot1, slot2 = slots
                container_click.click_slot_in_player_inventory(6*9, slot1, button=0, shift=True, slot_mode="item")
                time.sleep(0.5)
                container_click.click_slot_in_player_inventory(6*9, slot2, button=0, shift=True, slot_mode="item")
                time.sleep(0.5)
                container_click.click_slot(13, button=0, shift=False) # Craft button
                info.on_craft_use(slot1, slot2)
                while True:
                    items = minescript.container_get_items()
                    rname = parse_nbt.get_clear_string_name_of_item(items[29]) # Result slot
                    if len(rname) < 2:
                        time.sleep(0.2)
                        continue
                    minescript.echo(f"Crafted {rname}!")
                    # Dont wanna bother testing, current approach works and is performant enough
                    #if rname in rune_map:
                    #    rune_map[rname].on_was_crafted()
                    break
                container_click.click_slot(31, button=0, shift=True) # Shift back
                time.sleep(1)
        if not had_crafts:
            minescript.echo("No more crafts possible, exiting")
            break


if __name__ == "__main__":
    asyncio.run(main())
