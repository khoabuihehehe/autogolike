#!/usr/bin/env python
# -*- coding: utf-8 -*-

from curl_cffi.requests import Session
from pathlib import Path

class GL:
    def __init__(self):
        self.s = Session()
        self.s.verify = True
        self.s.impersonate = "chrome124"
        self.s.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'content-type': 'application/json;charset=utf-8',
            'origin': 'https://app.golike.net',
            't': 'VFZSak1FOVVZM2RPYWxWNlRsRTlQUT09',
            'user-agent': 'Mozilla/5.0 (Linux; Android 9; SM-N976N Build/PQ3B.190801.10101846; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.82 Mobile Safari/537.36'
        }
        self.b = "https://gateway.golike.net/api"
        self.af = self.load_auth()

    def load_auth(self):
        af = Path("data/authors.txt")
        af.parent.mkdir(parents=True, exist_ok=True)
        if not af.exists() or not af.read_text():
            auth = input("Nhập AUTH: ")
            af.write_text(auth)
        else:
            auth = af.read_text()
        self.s.headers.update({'authorization': auth})
        return af

    def get_user(self):
        res = self.s.get(f"{self.b}/users/me").json()
        if res.get("status") == 401:
            self.af.unlink()
            raise ValueError("Authorization không chính xác!")
        return res.get("data")

    def get_accounts(self):
        res = self.s.get(f"{self.b}/tiktok-account").json()
        if res.get("status") != 200:
            error = res.get("error")
            raise ValueError(error)
        return res.get("data")

    def get_jobs(self, acc_id):
        return self.s.get(
            f"{self.b}/advertising/publishers/tiktok/jobs",
            params={'account_id': acc_id, 'data': 'null'}
        ).json()

    def skip_jobs(self, ads_id, obj_id, acc_id, job_type):
        self.s.post(f"{self.b}/report/send", json={'description': 'Tôi không muốn làm Job này', 'users_advertising_id': ads_id, 'type': 'ads', 'provider': 'tiktok', 'fb_id': acc_id, 'error_type': 0})
        self.s.post(f"{self.b}/advertising/publishers/tiktok/skip-jobs", json={'ads_id': ads_id, 'object_id': obj_id, 'account_id': acc_id, 'type': job_type})

    def complete_jobs(self, ads_id, acc_id):
        return self.s.post(
            f"{self.b}/advertising/publishers/tiktok/complete-jobs",
            json={'ads_id': ads_id, 'account_id': acc_id, 'async': True, 'data': None}
        ).json()