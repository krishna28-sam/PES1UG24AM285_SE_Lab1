import math
import random
from array import array

import pygame

MASTER_VOLUME = 0.35  # 0.0 - 1.0, keeps the generated sounds from being harsh


class SoundManager:
    """Builds simple sound effects in code and plays them.

    If audio can't be initialised, `enabled` is False and play() does nothing,
    so the rest of the game never has to care.
    """

    def __init__(self):
        self.enabled = False
        self._sounds = {}
        self._rng = random.Random(1234)  # private RNG; doesn't touch the game's random state

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            init = pygame.mixer.get_init()
            if init is None:
                return
            self._rate, fmt, self._channels = init
            if fmt != -16:  # we only generate signed 16-bit samples
                return

            self._sounds = {
                "fire": self._make(self._fire_samples()),
                "explosion": self._make(self._explosion_samples()),
                "game_over": self._make(self._game_over_samples()),
            }
            self.enabled = True
        except Exception:
            self.enabled = False
            self._sounds = {}

    # ---------- public API ----------

    def play(self, name):
        if not self.enabled:
            return
        try:
            self._sounds[name].play()
        except Exception:
            pass  # never let audio problems crash the game

    # ---------- sample generation ----------

    def _make(self, samples):
        """Turn a list of floats in [-1, 1] into a pygame Sound."""
        data = array("h")
        for s in samples:
            value = int(max(-1.0, min(1.0, s)) * MASTER_VOLUME * 32767)
            for _ in range(self._channels):  # duplicate for stereo mixers
                data.append(value)
        return pygame.mixer.Sound(buffer=data.tobytes())

    def _envelope(self, i, n, attack=0.005, release_power=1.5):
        """Short fade-in (avoids clicks) and a decaying tail."""
        t = i / self._rate
        attack_gain = min(1.0, t / attack) if attack > 0 else 1.0
        tail_gain = (1.0 - i / n) ** release_power
        return attack_gain * tail_gain

    def _sweep(self, f_start, f_end, duration, square_mix=0.0):
        """Tone gliding from f_start to f_end Hz; square_mix adds a buzzier edge."""
        n = int(self._rate * duration)
        phase = 0.0
        out = []
        for i in range(n):
            freq = f_start + (f_end - f_start) * (i / n)
            phase += 2 * math.pi * freq / self._rate
            sine = math.sin(phase)
            square = 1.0 if sine >= 0 else -1.0
            wave = sine * (1 - square_mix) + square * square_mix
            out.append(wave * self._envelope(i, n))
        return out

    def _fire_samples(self):
        # Quick descending "pew"
        return self._sweep(900, 300, 0.12, square_mix=0.4)

    def _explosion_samples(self):
        # Noise burst plus a low falling thump
        duration = 0.25
        n = int(self._rate * duration)
        thump = self._sweep(160, 50, duration)
        out = []
        for i in range(n):
            noise = self._rng.uniform(-1.0, 1.0) * self._envelope(i, n, release_power=2.0)
            out.append(noise * 0.7 + thump[i] * 0.6)
        return out

    def _game_over_samples(self):
        # Four descending notes, slightly buzzy
        out = []
        for freq in (440, 370, 311, 220):
            out.extend(self._sweep(freq, freq * 0.97, 0.22, square_mix=0.3))
        return out
