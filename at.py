#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uiautomator2 as u2

class AT:
    def __init__(self, serial=None):
        self.d = u2.connect(serial) if serial else u2.connect()

    def tap(self, x, y):
        self.d.click(x, y)

    def input_text(self, text, clear=False):
        self.d.send_keys(text, clear)

    def find_xpath(self, xpath):
        e = self.d.xpath(xpath)
        if e.exists:
            return e.all()
        return None

    def find_element(self, **kwargs):
        e = self.d(**kwargs)
        if e.exists:
            return e
        return None

    def click_element(self, **kwargs):
        e = self.find_element(**kwargs)
        if e:
            e.click()
            return True
        return False

    def open_url(self, url):
        self.d.open_url(url)

    def wait_for_element(self, timeout=10.0, **kwargs):
        return self.d(**kwargs).wait(timeout=timeout)

    def wait_for_click(self, timeout=10.0, **kwargs):
        if self.wait_for_element(timeout, **kwargs):
            return self.click_element(**kwargs)
        return False

    def wait_for_input(self, text, clear=False, timeout=10.0, **kwargs):
        if self.wait_for_element(timeout, **kwargs):
            self.click_element(**kwargs)
            self.input_text(text, clear)
            return True
        return False

    def press_key(self, key):
        self.d.press(key)

    def dump_hierarchy(self):
        xml = self.d.dump_hierarchy()
        return xml

    def drag(self, sx, sy, ex, ey, duration=0.1):
        self.d.drag(sx, sy, ex, ey, duration)

    def wait_for_drag_element(self, direction="right", distance=100, duration=0.1, timeout=10.0, **kwargs):
        if self.wait_for_element(timeout, **kwargs):
            element = self.find_element(**kwargs)
            if not element:
                return False
            bounds = element.bounds()
            sx = (bounds['left'] + bounds['right']) // 2
            sy = (bounds['top'] + bounds['bottom']) // 2
            if direction.lower() == "right":
                ex, ey = sx + distance, sy
            elif direction.lower() == "left":
                ex, ey = sx - distance, sy
            elif direction.lower() == "up":
                ex, ey = sx, sy - distance
            else:
                ex, ey = sx, sy + distance
            element.drag_to(ex, ey, duration=duration)
            return True
        return False

    def swipe(self, sx, sy, ex, ey, duration=0.1):
        self.d.swipe(sx, sy, ex, ey, duration)

    def screenshot(self, path=None):
        img = self.d.screenshot()
        if path:
            img.save(path)
        return img

    def back(self):
        self.d.press("back")

    def home(self):
        self.d.press("home")

    def recent(self):
        self.d.press("recent")

    def wait_activity(self, activity, timeout=10.0):
        return self.d.wait_activity(activity, timeout=timeout)

    def get_current_app(self):
        return self.d.app_current()

    def start_app(self, package, activity=None):
        self.d.app_start(package, activity, wait=True)

    def stop_app(self, package):
        self.d.app_stop(package)

    def clear_app(self, package):
        self.d.app_clear(package)

    def list_installed_apps(self):
        return self.d.app_list()

    def shell(self, cmd):
        return self.d.shell(cmd).output