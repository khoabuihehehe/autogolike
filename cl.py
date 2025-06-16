#!/usr/bin/env python
# -*- coding: utf-8 -*-

from curl_cffi.requests import Session
import re, json

class CL:
    def __init__(self):
        self.s = Session()
        self.s.verify = True
        self.s.impersonate = "chrome124"
        self.s.headers = {
            'accept-language': 'en-US;q=0.6,en;q=0.5',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Safari/537.36'
        }
        self.b = "https://www.tiktok.com/"

    def profile(self, user_id):
        try:
            res = self.s.get(f"{self.b}@{user_id}")
            res.raise_for_status()
            match = re.search(r'"user":\s*({(?:[^{}]|{[^{}]*})*})', res.text)
            if not match:
                return {'status': False, 'error': 'Dell tìm thấy tài khoản'}
            data = json.loads(match.group(1))
            if data.get("privateAccount"):
                return {'status': False, 'error': 'Dính riêng tư'}
            useruid = data["id"]
            uniqueid = data["uniqueId"]
            return {'status': True, 'web_tt': f'{self.b}@{uniqueid}', 'dl_ttt': f'tiktok://user/profile/{useruid}?refer=web&gd_label=click_wap_download_follow&type=need_follow&needlaunchlog=1'}
        except Exception as e:
            return {'status': False, 'error': str(e)}