# -*- coding: utf-8 -*-

import pygame
from PIL import Image, ImageDraw

from pibooth import fonts
from pibooth.utils import LOGGER
from pibooth.pictures import sizing
from pibooth.language import get_translated_text


class BaseCamera(object):

    def __init__(self, resolution, delete_internal_memory):
        self._cam = None
        self._border = 50
        self._window = None
        self._captures = []
        self._overlay = None
        self._overlay_font = None  # Dynamically computed
        self.resolution = resolution
        self.delete_internal_memory = delete_internal_memory

    def _show_overlay(self, text, alpha):
        """Add an image as an overlay.
        """
        self._overlay = text

    def _hide_overlay(self):
        """Remove any existing overlay.
        """
        if self._overlay is not None:
            self._overlay = None

    def _post_process_capture(self, capture_data):
        """Rework and return a PIL Image object from capture data.
        """
        raise NotImplementedError

    def get_rect(self):
        """Return a Rect object (as defined in pygame) for resizing preview and images
        in order to fit to the defined window.
        """
        rect = self._window.get_rect()
        res = sizing.new_size_keep_aspect_ratio(self.resolution,
                                                (rect.width - 2 * self._border, rect.height - 2 * self._border))
        return pygame.Rect(rect.centerx - res[0] // 2, rect.centery - res[1] // 2, res[0], res[1])

    def build_overlay(self, size, text, alpha):
        """Return a PIL image with the given text that can be used
        as an overlay for the camera.
        """
        image = Image.new('RGBA', size)
        draw = ImageDraw.Draw(image)

        if not self._overlay_font or self._overlay_font[0] != size:
            LOGGER.debug("Compute font for countdown overlay")
            # Use the "smile" text to compute the font size, the countdown numbers
            # will have the same size to avoid font creation a each call.
            font = fonts.get_pil_font(get_translated_text('smile'),
                                      fonts.CURRENT, 0.9 * size[0], 0.9 * size[1])
            self._overlay_font = (size, font)

        txt_width, txt_height = draw.textsize(text, font=self._overlay_font[1])
        position = ((size[0] - txt_width) // 2, (size[1] - txt_height) // 2 - size[1] // 10)
        draw.text(position, text, (255, 255, 255, alpha), font=self._overlay_font[1])
        return image

    def preview(self, window, flip=True):
        """Setup the preview.
        """
        raise NotImplementedError

    def preview_countdown(self, timeout, alpha=60):
        """Show a countdown of `timeout` seconds on the preview.
        Returns when the countdown is finished.
        """
        raise NotImplementedError

    def preview_wait(self, timeout, alpha=60):
        """Wait the given time and let doing the job.
        Returns when the timeout is reached.
        """
        raise NotImplementedError

    def stop_preview(self):
        """Stop the preview.
        """
        raise NotImplementedError

    def capture(self, effect=None):
        """Capture a new picture.
        """
        raise NotImplementedError

    def get_captures(self):
        """Return all buffered captures as PIL images (buffer dropped after call).
        """
        images = []
        for data in self._captures:
            images.append(self._post_process_capture(data))
        self.drop_captures()
        return images

    def drop_captures(self):
        """Delete all buffered captures.
        """
        self._captures.clear()

    def quit(self):
        """Close the camera driver, it's definitive.
        """
        raise NotImplementedError
