"""System control: volume + screen brightness (Windows).

Everything is wrapped in try/except so the app never crashes if a dependency
is missing or you're on another OS — JARVIS just reports it can't do it.
"""
from __future__ import annotations


# ---------------------------------------------------------------- volume ----
def _get_volume_iface():
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    devices = AudioUtilities.GetSpeakers()
    iface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(iface, POINTER(IAudioEndpointVolume))


def set_volume(level: int | None = None, direction: str | None = None) -> str:
    """Set volume to an absolute 0-100 level, or nudge up/down/mute/unmax."""
    try:
        vol = _get_volume_iface()
        if direction == "mute":
            vol.SetMute(1, None)
            return "Muted."
        if direction == "unmute":
            vol.SetMute(0, None)
            return "Unmuted."

        current = vol.GetMasterVolumeLevelScalar()  # 0.0 - 1.0
        if level is not None:
            target = max(0.0, min(1.0, level / 100.0))
        elif direction == "up":
            target = min(1.0, current + 0.15)
        elif direction == "down":
            target = max(0.0, current - 0.15)
        elif direction == "max":
            target = 1.0
        else:
            return f"Volume is at {round(current * 100)} percent."

        vol.SetMute(0, None)
        vol.SetMasterVolumeLevelScalar(target, None)
        return f"Volume set to {round(target * 100)} percent."
    except Exception as e:  # noqa: BLE001
        return f"Couldn't change the volume ({e.__class__.__name__})."


# ------------------------------------------------------------ brightness ----
def set_brightness(level: int | None = None, direction: str | None = None) -> str:
    """Set screen brightness to a 0-100 level, or nudge up/down."""
    try:
        import screen_brightness_control as sbc

        current = sbc.get_brightness()[0]
        if level is not None:
            target = max(0, min(100, level))
        elif direction == "up":
            target = min(100, current + 20)
        elif direction == "down":
            target = max(0, current - 20)
        else:
            return f"Brightness is at {current} percent."

        sbc.set_brightness(target)
        return f"Brightness set to {target} percent."
    except Exception as e:  # noqa: BLE001
        return f"Couldn't change brightness ({e.__class__.__name__})."
