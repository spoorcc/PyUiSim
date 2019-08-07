
from collections import OrderedDict
from copy import deepcopy
from PIL import Image, ImageTk
from random import randint
import logging
import os
import queue
import threading
import time
import tkinter as tk
import xml.etree.ElementTree as ET
logging.basicConfig(level=logging.INFO)

class UiElement:

    def __init__(self, path):
        self._image = Image.open(path).convert("RGBA")
        self.visible = True

    def image(self):
        return self._image

    def merge(self, other):
        self._image.paste(other.image(), (0,0), other.image())

    def create_photo(self):
        return ImageTk.PhotoImage(self._image)

class Images:
    def __init__(self, window, queue, img_dir, update=50):
        self._update_time = update
        self._window = window
        self._queue = queue

        self.images = OrderedDict()
        for image in os.listdir(img_dir):
            path = os.path.join(img_dir, image)
            logging.info('Adding %s from %s', image, path)
            self.images[image] = UiElement(path)

        photo = self.compose()
        self._label = tk.Label(window, image=photo)
        self._label.image = photo 
        self._label.pack(fill=tk.BOTH, expand=tk.YES)
        self.update()

    def compose(self):
        images = iter(self.images.values())
        first_image = deepcopy(next(images))
        for img in images:
            if img.visible:
                first_image.merge(img)
        return first_image.create_photo()

    def update(self):
        while not self._queue.empty():
            cmd = self._queue.get()
            try:
                self.images[cmd[0]].visible = cmd[1]
            except KeyError:
                pass

        photo = self.compose()
        self._label.configure(image=photo)
        self._label.image = photo
        self._window.after(self._update_time, self.update)


class ElementProxy(object):

    def __init__(self, name):
        self._name = name

    def __set__(self, obj, val):
        obj.set_visibility(self._name, val)

class WorkerThread(threading.Thread):
    ''' A WorkerThread in a separate thread that can handle commands '''

    def __init__(self, img_dir):
        self.output_queue = queue.Queue()
        super().__init__()

        for image in os.listdir(img_dir):
            setattr(WorkerThread, image.split('.')[0], ElementProxy(image))

        self.start()

    def do_work(self):
        pass

    def run(self):
        ''' Do Work'''
        while self._should_run():
            self.do_work()

    def _should_run(self):
        return getattr(self, "_do_run", True)

    def stop(self):
        self._do_run = False
        self.join()

    def set_visibility(self, img, boolean):
        self.output_queue.put( (img, boolean))


class ExampleUiSim(WorkerThread):

    def __init__(self):
        super().__init__('images/output')

    def do_work(self):
        self.bcd_digit7 = False
        time.sleep(0.1)
        self.bcd_digit7 = True
        time.sleep(0.1)

window = tk.Tk()
window.title("Welcome to PyUiSim")

worker = ExampleUiSim()
images = Images(window, worker.output_queue, 'images/output', 10)

window.mainloop()

worker.stop()