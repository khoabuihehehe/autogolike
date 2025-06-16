#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rich.live import Live
from gl import GL
from at import AT
from cl import CL
from ui import UI
import os
import time
import adbutils
import threading

def run(gl: GL, ui: UI, row, serial):
    os.system('cls' if os.name == 'nt' else 'clear')
    done, skip, earn, fail = [0] * 4
    ui.update_row(row, "null", serial, done, skip, earn, "[bold bright_green]Đang khởi động máy chủ.[/bold bright_green]")
    cl = CL()
    at = AT(serial)
    acc = gl.get_accounts()
    ui.update_row(row, "null", serial, done, skip, earn, f"[bold bright_green]Đang mở ứng dụng TikTok.[/bold bright_green]")
    at.start_app("com.ss.android.ugc.trill", "com.ss.android.ugc.aweme.splash.SplashActivity")
    ui.update_row(row, "null", serial, done, skip, earn, f"[bold bright_green]Đang chuyển qua trang Profile.[/bold bright_green]")
    at.wait_for_click(500, text="Hồ sơ")
    user = next(e.text.lstrip("@") for e in at.find_xpath("//*") if e.text and e.text.startswith("@"))
    acc_id = next((a['id'] for a in acc if a['unique_username'] == user), None)
    if not acc_id:
        ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_green]Tài khoản [bold bright_yellow]['{user}'][/bold bright_yellow] chưa thêm vào GOLIKE.[/bold bright_green]")
        return
    ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_green]Lấy tài khoản [bold bright_yellow]['{user}'][/bold bright_yellow] thành công.[/bold bright_green]")
    while True:
        if fail >= 10:
            ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_green]Tài khoản [bold bright_yellow]['{user}'][/bold bright_yellow] gặp sự cố.[/bold bright_green]")
            break
        ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_green]Đang tìm kiếm nhiệm vụ.[/bold bright_green]")
        job = gl.get_jobs(acc_id)
        print(job)
        if job['status'] != 200:
            for i in range(10, -1, -1):
                ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_white][[bold bright_yellow]{i}[/bold bright_yellow]][/bold bright_white] [bold bright_green]Không tìm thấy nhiệm vụ.[/bold bright_green]")
                time.sleep(1)
            continue
        ads_id = job['data']['id']
        obj_id = job['data']['object_id']
        type_tt = job['data']['type']
        cl_tt = cl.profile(obj_id)
        print(cl_tt)
        if type_tt not in ["like", "follow"]:
            skip += 1
            ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_green]Không làm việc với nhiệm vụ [bold bright_yellow]['{type_tt}'][/bold bright_yellow].[/bold bright_green]")
            gl.skip_jobs(ads_id, obj_id, acc_id, type_tt)
            continue
        if not cl_tt['status']:
            skip += 1
            ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_green]Nhiệm vụ éo đạt tiêu chuẩn.[/bold bright_green]")
            gl.skip_jobs(ads_id, obj_id, acc_id, type_tt)
            continue
        url = cl_tt['dl_ttt']
        print(cl_tt["web_tt"])
        at.open_url(url)
        ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_green]Đang nhấn nút [bold bright_white][[bold bright_yellow]'{type_tt.upper()}'[/bold bright_yellow]][/bold bright_white].[/bold bright_green]")
        at.wait_for_click(description="Thích") if type_tt == "like" else at.wait_for_click(text="Follow")
        for i in range(10, -1, -1):
            ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_white][[bold bright_yellow]{i}[/bold bright_yellow]][/bold bright_white] [bold bright_green]Đang nhận phần thưởng.[/bold bright_green]")
            time.sleep(1)
        at.back()
        for a in range(1, 4):
            try:
                res = gl.complete_jobs(ads_id, acc_id)
                print(res)
                if res['status'] == 200:
                    fail = 0
                    done += 1
                    earns = res['data']['prices']
                    earn += earns
                    ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_white][[bold bright_yellow]SUCCESS[/bold bright_yellow]][/bold bright_white] [bold bright_green]Nhận thành công [bold bright_white][[bold bright_yellow]+{earns}[/bold bright_yellow]][/bold bright_white].[/bold bright_green]")
                    break
                else:
                    for i in range(5, -1, -1):
                        ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_white][[bold bright_yellow]{i}[/bold bright_yellow]][/bold bright_white] [bold bright_green]Thất bại lần thứ [bold bright_white][[bold bright_yellow]{a}[/bold bright_yellow]][/bold bright_white].[/bold bright_green]")
                        time.sleep(1)
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_white][[bold bright_yellow]FAILURE[/bold bright_yellow]][/bold bright_white] [bold bright_green]Lỗi dell rõ.[/bold bright_green]")
        else:
            skip += 1
            fail += 1
            ui.update_row(row, user, serial, done, skip, earn, f"[bold bright_white][[bold bright_yellow]FAILURE[/bold bright_yellow]][/bold bright_white] [bold bright_green]Nhận thưởng thất bại.[/bold bright_green]")
            gl.skip_jobs(ads_id, obj_id, acc_id, type_tt)

def main():
    try:
        gl = GL()
        adb = adbutils.AdbClient()
        devices = adb.device_list()
        ui = UI(devices)
        for r, s in enumerate(devices, 1):
            thread = threading.Thread(target=run, args=(gl, ui, r, s.serial), daemon=True)
            thread.start()
        with Live(ui.create_table(), refresh_per_second=100) as live:
            ui.update_table(live)
    except ValueError as e:
        print(f"Error: {str(e)}")
    except KeyboardInterrupt:
        print("Stopped by user.")
    except Exception as e:
        print(f"Unexpected error: {str(e)}.")

if __name__ == "__main__":
    main()