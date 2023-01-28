#!/usr/bin/env python3

import json
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter

# 文件路径定义
sub_list_json = './subscription/others/sub_list.json'


with open(sub_list_json, 'r', encoding='utf-8') as f:  # 载入订阅链接
    raw_list = json.load(f)
    f.close()


def check_url(url):  # 判断远程远程链接是否已经更新
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))
    try:
        resp = s.get(url, timeout=2)
        status = resp.status_code
    except Exception:
        status = 404
    if status == 200:
        isAccessable = True
    else:
        isAccessable = False
    return isAccessable


class update_url():

    def update_main(update_enable_list=[0, 11, 25, 35, 43, 54, 57, 67, 75]):
        if len(update_enable_list) > 0:
            for id in update_enable_list:
                status = update_url.update(id)
                update_url.update_write(id, status[1], status[1])
            updated_list = json.dumps(
                raw_list, sort_keys=False, indent=2, ensure_ascii=False)
            file = open(sub_list_json, 'w', encoding='utf-8')
            file.write(updated_list)
            file.close()
        else:
            print('Don\'t need to be updated.')

    def update_write(id, status, updated_url):
        if status == 404:
            print(f'Id {id} URL 无可用更新\n')
        else:
            if updated_url != raw_list[id]['url']:
                raw_list[id]['url'] = updated_url
                print(f'Id {id} URL 更新至 : {updated_url}\n')
            else:
                print(f'Id {id} URL 无可用更新\n')

    def update(id):
        if id == 0:
            # remarks: pojiezhiyuanjun/freev2, 将原链接更新至 https://raw.fastgit.org/pojiezhiyuanjun/freev2/master/%MM%(DD - 1).txt
            # today = datetime.today().strftime('%m%d')
            # 得到当前日期前一天 https://blog.csdn.net/wanghuafengc/article/details/42458721
            yesterday = (datetime.today() + timedelta(-1)).strftime('%m%d')
            front_url = 'https://raw.githubusercontent.com/pojiezhiyuanjun/freev2/master/'
            end_url = 'clash.yml'
            # 修改字符串中的某一位字符 https://www.zhihu.com/question/31800070/answer/53345749
            url_update = front_url + yesterday + end_url
            return [0, url_update]

        elif id == 11:
            today = datetime.today()
            front_url = 'https://raw.githubusercontent.com/halfaaa/Free/main/'
            end_url = '.txt'
            url_update = front_url + \
                str(today.month) + "." + str(today.day) + \
                "." + str(today.year) + end_url
            if check_url(url_update):
                return [21, url_update]
            else:
                return [21, 404]

        elif id == 43:
            # remarks: v2raydy/v2ray, 将原链接更新至 https://https://raw.githubusercontent.com/v2raydy/v2ray/main/%MM-%(DD - 1)%str%1.txt
            # 得到当前日期前一天 https://blog.csdn.net/wanghuafengc/article/details/42458721
            today = datetime.today().strftime('%Y%m%d')
            month = datetime.today().strftime('%Y%m') + '/'
            front_url = 'https://nodefree.org/dy/'
            end_url = '.txt'
            url_update = front_url + month + today + end_url
            if check_url(url_update):
                return [43, url_update]
            else:
                return [43, 404]

        elif id == 25:
            today = datetime.today().strftime('%Y%m%d')
            month = datetime.today().strftime('%m') + '/'
            year = datetime.today().strftime('%Y') + '/'
            front_url = 'https://v2rayshare.com/wp-content/uploads/'
            end_url = '.txt'
            url_update = front_url + year + month + today + end_url
            if check_url(url_update):
                return [25, url_update]
            else:
                return [25, 404]

        elif id == 35:
            url_raw = 'https://raw.githubusercontent.com/arielherself/autosub/main/subs.txt'
            url_update_array = []

            try:
                resp = requests.get(url_raw, timeout=2)
                resp_content = resp.content.decode('utf-8')
                resp_content = resp_content.split('\n')
                for line in resp_content:
                    if 'http' in line:
                        url_update_array.append(line)
                    else:
                        continue
                url_update = '|'.join(url_update_array)
                return [35, url_update]
            except Exception as err:
                print(err)
                return [37, 404]

        elif id == 54:
            url_raw = [
                "https://raw.githubusercontent.com/RenaLio/Mux2sub/main/urllist",
                "https://raw.githubusercontent.com/RenaLio/Mux2sub/main/sub_list"
            ]
            url_update_array = []
            try:
                for url in url_raw:
                    resp = requests.get(url, timeout=3)
                    resp_content = resp.content.decode('utf-8')
                    resp_content = resp_content.split('\n')
                    for line in resp_content:
                        if 'http' in line:
                            url_update_array.append(line)
                        else:
                            continue
                url_update = '|'.join(url_update_array)
                return [54, url_update]
            except Exception as err:
                print(err)
                return [54, 404]

        elif id == 57:
            today = datetime.today().strftime('%Y%m%d')
            month = datetime.today().strftime('%m') + '/'
            year = datetime.today().strftime('%Y') + '/'
            front_url = 'https://clashnode.com/wp-content/uploads/'
            end_url = '.txt'
            url_update = front_url + year + month + today + end_url
            if check_url(url_update):
                return [57, url_update]
            else:
                return [57, 404]

        elif id == 67:
            today = datetime.today().strftime('%m%d')
            front_url = 'https://raw.githubusercontent.com/Strongmiao168/v2ray/main/'
            url_update = front_url + today
            if check_url(url_update):
                return [57, url_update]
            else:
                return [57, 404]

        elif id == 75:
            url_raw = 'https://raw.githubusercontent.com/RiverFlowsInUUU/collectSub/main/sub/' + \
                str(datetime.today().year) + '/' + str(datetime.today().month) + '/' + \
                str(datetime.today().month)+'-' + \
                str(datetime.today().day)+'.yaml'
            if check_url(url_raw):
                try:
                    resp = requests.get(url_raw, timeout=2)
                    resp_content = resp.content.decode('utf-8')
                    resp_content = resp_content.split('\n')
                    url_update_array = []
                    for line in resp_content:
                        if '- ' in line:
                            line = line.replace("- ", "")
                            url_update_array.append(line)
                    url_update = '|'.join(url_update_array)
                    return [75, url_update]
                except Exception as err:
                    print(err)
                    return [75, 404]
            else:
                return [75, 404]


if __name__ == '__main__':
    update_url.update_main()
