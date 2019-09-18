import re
import json
import os
import requests


class Spider(object):
    def __init__(self):
        self.url_base = 'https://www.instagram.com/{user_name}/'  # 用户主页
        self.uri = 'https://www.instagram.com/graphql/query/?query_hash=a5164aed103f24b03e7b7747a2d94e3c&variables' \
                   '=%7B%22id%22%3A%22{user_id}%22%2C%22first%22%3A12%2C%22after%22%3A%22{cursor}%22%7D'
        self.headers = {
            'Connection': 'keep-alive',
            'Host': 'www.instagram.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/68.0.3440.106 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.proxies = {
            'https': 'https://127.0.0.1:1087'
        }
        self.count = 0
        self.dir = '/Users/oldzhg/Downloads/'

    def run(self):
        user_name = input("请输入您想下载的用户名：（网址如https://www.instagram.com/instagram/，instagram即用户名）\n")
        url_base = self.url_base.format(user_name=user_name)
        res = requests.get(url_base, headers=self.headers, proxies=self.proxies)
        self.dir = self.dir + user_name + '/'
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        if res.status_code == 200:
            html = (res.content.decode())
            pattern = re.compile('edge_owner_to_timeline_media":(.*?),"edge_saved_media"')
            text_json = json.loads(pattern.search(html).group(1))
            user_id = re.findall('"profilePage_([0-9]+)"', html)[0]
            print("开始下载，请耐心等待-------------------------------------")
            self.json_dispose(text_json, user_id)
        if res.status_code == 404:
            print("输入的用户名有错，请核对后重新输入\n")

    def json_dispose(self, text_json, user_id):
        data = text_json.get('data')
        if data:
            data = data.get('user').get('edge_owner_to_timeline_media')
            has_next_page = data.get('page_info').get('has_next_page')
            end_cursor = data.get('page_info').get('end_cursor')
            edges = data.get('edges')
        else:
            has_next_page = text_json.get('page_info').get('has_next_page')
            end_cursor = text_json.get('page_info').get('end_cursor')
            edges = text_json.get("edges")
        for edge in edges:
            img_url = edge['node']['display_url']
            # media_caption = edge['node']['edge_media_to_caption']['edges']
            caption = str(self.count)
            self.count = self.count + 1
            with open(self.dir + caption + '.jpg', 'wb') as f:
                f.write(requests.get(img_url, proxies=self.proxies).content)
                f.flush()
            print("已下载 %d 张图片" % self.count)
        if has_next_page:
            url = self.uri.format(user_id=user_id, cursor=end_cursor)
            # print(url)
            self.request_url(url, user_id)
        else:
            print('OK--------------------------------------------')

    def request_url(self, url, user_id):
        self.headers.update({
            "x-requested-with": "XMLHttpRequest",
            "accept": "*/*",
        })
        text_json = requests.get(url, headers=self.headers, proxies=self.proxies).json()
        self.json_dispose(text_json, user_id)


if __name__ == '__main__':
    spider = Spider()
    spider.run()
