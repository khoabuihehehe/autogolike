#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rich.table import Table
from rich.live import Live
import time
import shutil
import threading

class UI:
    def __init__(self, devices):
        self.share_data = {}
        self.row_id = len(devices)
        self.lock = threading.Lock()

    def create_table(self):
        title = "[yellow]===[/yellow]   [white]Danh sách luồng GOLIKE[/white]   [yellow]===[/yellow]"
        tab = Table(title=title, show_header=True)
        widths = {'STT': 5, 'USER': 18, 'DEVICE': 20, 'TIME': 10, 'DONE': 10, 'SKIP': 10, 'EARN': 10}
        terminal_size = shutil.get_terminal_size()
        terminal_width = terminal_size.columns
        total_width = sum(widths.values())
        border_padding = len(widths) + 1
        massage_with = max(3, terminal_width - total_width - border_padding)
        for header, width in widths.items():
            tab.add_column(header, justify="center", width=width)
        tab.add_column("MESSAGE", justify="center", width=massage_with)
        return tab

    def update_table(self, live):
        while True:
            tab = self.create_table()
            with self.lock:
                for i in range(1, self.row_id + 1):
                    if i in self.share_data.keys():
                        row = self.share_data[i]
                        tab.add_row(
                            row['STT'],
                            row['USER'],
                            row['DEVICE'],
                            row['TIME'],
                            row['DONE'],
                            row['SKIP'],
                            row['EARN'],
                            row['MESSAGE'],
                            end_section=True
                        )
            live.update(tab)

    def update_row(self, row, user, serial, done, skip, earn, mess):
        with self.lock:
            self.share_data[row] = {
                'STT': str(row),
                'USER': str(user),
                'DEVICE': str(serial),
                'TIME': time.strftime("%H:%M:%S"),
                'DONE': str(done),
                'SKIP': str(skip),
                'EARN': str(earn),
                'MESSAGE': str(mess),
            }