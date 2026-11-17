"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Following gap buttons and the distance page.

Any distance button press opens the distance page for PAGE_FRAMES. While it's open, the cruise + and - buttons step
the gap (farther / closer) instead of the set speed, and each of those presses keeps it open. One implementation so
the dash page (car controller), the set speed (card) and the gap itself (selfdrived) agree on when it's open: they
all feed it the same carState.buttonEvents, one frame at a time.
"""
from opendbc.car import structs

ButtonType = structs.CarState.ButtonEvent.Type

PAGE_FRAMES = 400  # 4 s at 100 Hz, as long as the dash shows its distance page

CYCLE = 0  # step one closer, wrapping from the closest to the farthest
CLOSER = -1
FARTHER = 1

_GAP_BUTTONS = {
  int(ButtonType.gapAdjustCruise): CYCLE,
  int(ButtonType.gapCloserCruise): CLOSER,
  int(ButtonType.gapFartherCruise): FARTHER,
}
_PAGE_BUTTONS = {
  int(ButtonType.accelCruise): FARTHER,
  int(ButtonType.decelCruise): CLOSER,
}


def _raw(button_type) -> int:
  return int(getattr(button_type, 'raw', button_type))


class FollowGapButtons:
  def __init__(self):
    self.page_frames = 0
    self.page_presses: set[int] = set()  # + / - presses that began while the page was open, owned by the gap

  @property
  def page_open(self) -> bool:
    return self.page_frames > 0

  def open_page(self) -> None:
    self.page_frames = PAGE_FRAMES

  def update(self, button_events) -> list[int]:
    """Feed one frame of buttonEvents. Returns the gap steps released this frame (CYCLE, CLOSER or FARTHER)."""
    if self.page_frames > 0:
      self.page_frames -= 1

    steps = []
    for be in button_events:
      t = _raw(be.type)
      if t in _GAP_BUTTONS:
        self.open_page()
        if not be.pressed:
          steps.append(_GAP_BUTTONS[t])
      elif t in _PAGE_BUTTONS:
        if be.pressed:
          if self.page_open:
            self.page_presses.add(t)
            self.open_page()
        elif t in self.page_presses:
          self.page_presses.discard(t)
          self.open_page()
          steps.append(_PAGE_BUTTONS[t])
    return steps
