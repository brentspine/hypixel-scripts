# Written by Brentspine 2025
# Copy only with credit
import minescript # type: ignore
from java import JavaClass # type: ignore
import datetime
from enum import Enum

class _MC:
    Minecraft = None
    ClickType = None
    
class EntityType(Enum):
    ARMOR_STAND = "entity.minecraft.armor_stand"
    PLAYER = "entity.minecraft.player"

def _ensure_classes_loaded():
    if _MC.Minecraft is None:
        _MC.Minecraft = JavaClass("net.minecraft.client.Minecraft")
    if _MC.ClickType is None:
        _MC.ClickType = JavaClass("net.minecraft.world.inventory.ClickType")
    return True

def _ctx():
    _ensure_classes_loaded()
    mc = _MC.Minecraft.getInstance()
    if mc is None:
        return None
    player = mc.player
    if player is None:
        return None
    menu = player.containerMenu
    if menu is None:
        return None
    return (mc, player, menu)

def click_slot(slot, button=0, shift=False):
    """
    Click a slot in the currently open container GUI.

    slot: index to click
    button: 0=left, 1=right, 2=middle
    shift: True => shift-click (QUICK_MOVE), False => normal click (PICKUP)
    index_mode: "absolute" | "container" | "player"
    """
    ctx = _ctx()
    if ctx is None:
        return False
    #minescript.log(f"Got context {datetime.datetime.now()}")
    mc, player, menu = ctx
    abs_index = slot

    click_type = _MC.ClickType.QUICK_MOVE if shift else _MC.ClickType.PICKUP
    #minescript.log(f"Executing click {datetime.datetime.now()}")
    mc.gameMode.handleInventoryMouseClick(menu.containerId, abs_index, button, click_type, player)
    # minescript.echo(f"Click done! Slot {slot}")
    return True

def click_slot_in_player_inventory(container_size, slot, button=0, shift=False, slot_mode="normal"):
    """
    Click a slot in the player's inventory.

    slot: index to click (0-35)
    button: 0=left, 1=right, 2=middle
    shift: True => shift-click (QUICK_MOVE), False => normal click (PICKUP)
    """
    # open_container = minescript.container_get_items()
    # Hotbar 0-8, then starting from top left 9-35
    if slot_mode == "item":
        column = (slot % 9)
        row = (slot // 9)+1
        # minescript.echo(f"Column: {column}, Row: {row}, Slot: {slot}")
        # slot = (4-row)*9 + column 
        if row == 1:
            slot = 3*9 + column 
        else:
            slot = slot - 9
        # minescript.echo(f"Converted to container slot: {slot}")
    return click_slot(slot+container_size, button=button, shift=shift)
