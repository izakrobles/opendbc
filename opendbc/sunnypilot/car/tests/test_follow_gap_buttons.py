"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from opendbc.car import structs
from opendbc.sunnypilot.car.follow_gap_buttons import CLOSER, CYCLE, FARTHER, PAGE_FRAMES, FollowGapButtons

ButtonType = structs.CarState.ButtonEvent.Type


def ev(t, pressed):
  return [structs.CarState.ButtonEvent(type=t, pressed=pressed)]


def tap(fgb, t):
  return fgb.update(ev(t, True)) + fgb.update(ev(t, False))


class TestFollowGapButtons:
  def test_distance_button_directions(self):
    fgb = FollowGapButtons()
    assert tap(fgb, ButtonType.gapAdjustCruise) == [CYCLE]
    assert tap(fgb, ButtonType.gapCloserCruise) == [CLOSER]
    assert tap(fgb, ButtonType.gapFartherCruise) == [FARTHER]

  def test_plus_minus_only_while_page_open(self):
    fgb = FollowGapButtons()
    assert tap(fgb, ButtonType.accelCruise) == []  # page closed: set speed, not the gap
    tap(fgb, ButtonType.gapAdjustCruise)
    assert fgb.page_open
    assert tap(fgb, ButtonType.accelCruise) == [FARTHER]
    assert tap(fgb, ButtonType.decelCruise) == [CLOSER]

  def test_page_times_out(self):
    fgb = FollowGapButtons()
    tap(fgb, ButtonType.gapAdjustCruise)
    for _ in range(PAGE_FRAMES):
      fgb.update([])
    assert not fgb.page_open
    assert tap(fgb, ButtonType.decelCruise) == []

  def test_plus_minus_keep_page_open(self):
    fgb = FollowGapButtons()
    tap(fgb, ButtonType.gapAdjustCruise)
    for _ in range(3):
      for _ in range(PAGE_FRAMES - 10):
        fgb.update([])
      assert tap(fgb, ButtonType.accelCruise) == [FARTHER]
    assert fgb.page_open

  def test_press_decided_when_it_starts(self):
    # pressed just before the page closes, released after: still the gap's, and set speed never sees it
    fgb = FollowGapButtons()
    tap(fgb, ButtonType.gapAdjustCruise)
    for _ in range(PAGE_FRAMES - 3):
      fgb.update([])
    fgb.update(ev(ButtonType.decelCruise, True))
    assert int(ButtonType.decelCruise) in fgb.page_presses
    for _ in range(50):
      fgb.update([])
    assert fgb.update(ev(ButtonType.decelCruise, False)) == [CLOSER]
    # and one that starts with the page closed belongs to the set speed even if the page opens meanwhile
    for _ in range(PAGE_FRAMES):
      fgb.update([])
    fgb.update(ev(ButtonType.accelCruise, True))
    tap(fgb, ButtonType.gapAdjustCruise)
    assert fgb.update(ev(ButtonType.accelCruise, False)) == []
