#!/usr/bin/env python3

import base64
import json
import re
import socket
import urllib.parse

import geoip2.database
import requests
# from ping3 import ping
from requests.adapters import HTTPAdapter


class sub_convert():
    def get_node_from_sub(url_raw='', server_host='http://127.0.0.1:25500'):
        # 使用远程订阅转换服务
        # server_host = 'https://sub.xeton.dev'
        # 使用本地订阅转换服务
        # 分割订阅链接
        urls = url_raw.split('|')
        sub_content = []
        for url in urls:
            # 对url进行ASCII编码
            url_quote = urllib.parse.quote(url, safe='')
            # 转换并获取订阅链接数据
            converted_url = server_host+'/sub?target=mixed&url='+url_quote+'&list=true'
            try:
                s = requests.Session()
                s.mount('http://', HTTPAdapter(max_retries=5))
                s.mount('https://', HTTPAdapter(max_retries=5))
                resp = s.get(converted_url, timeout=30)
                # 如果解析出错，将原始链接内容拷贝下来
                if 'No nodes were found!' in resp.text:
                    print(resp.text + '\n下载订阅文件……')
                    resp = s.get(url, timeout=30)
                node_list = resp.text
            except Exception as err:
                # 链接有问题，直接返回原始错误
                print('网络错误，检查订阅转换服务器是否失效:' + '\n' +
                      converted_url + '\n' + err + '\n')
            # 改名
            node_list_formated = sub_convert.format(node_list)
            sub_content.append(node_list_formated)
        sub_content_all = ''.join(sub_content)
        return sub_content_all

    def format(node_list):
        # 重命名
        password_split_points = ["("]
        node_list_formated_array = []
        # 替换://://字符串，以修复后期toclash转换错误
        node_list = node_list.replace('://://', '://')
        node_list_array = node_list.split('\n')
        for node in node_list_array:
            # ss有多种格式，需要分别处理
            if 'ss://' in node and 'vless://' not in node and 'vmess://' not in node:
                try:
                    node_del_head = node.replace('ss://', '')
                    if '@' in node_del_head:
                        node_part = re.split('@|#', node_del_head, maxsplit=2)
                        server_head = sub_convert.find_country(
                            node_part[1].split(':')[0])
                        server_body = node_part[1].split('/?')[0]
                        password = sub_convert.base64_decode(
                            node_part[0]).split(':')[-1]
                        name_renamed = server_head + server_body + '(' + password + ')'
                        node_part[2] = urllib.parse.quote(
                            name_renamed, safe='')
                        node_raw = node_part[0] + '@' + \
                            node_part[1] + '#' + node_part[2]
                        node = 'ss://' + node_raw
                    else:
                        node_part = node_del_head.split('#')
                        node_part_head_decoded = sub_convert.base64_decode(
                            node_part[0])
                        node_part_head = re.split(
                            '@|:', node_part_head_decoded, maxsplit=0)
                        server_port = node_part_head[-1].split('/?')[0]
                        server = node_part_head[-2]
                        server_head = sub_convert.find_country(
                            server)
                        password = node_part_head[-3]
                        name_renamed = server_head + server +  ':' + server_port + '(' + password + ')'
                        node_part[1] = urllib.parse.quote(
                            name_renamed, safe='')
                        node_raw = node_part[0] + '#' + node_part[1]
                        node = 'ss://' + node_raw
                    node_list_formated_array.append(node)
                except Exception as err:
                    print(f'改名 ss 节点发生错误: {err}')
            elif 'ssr://' in node:
                try:
                    node_del_head = node.replace('ssr://', '')
                    node_part = sub_convert.base64_decode(
                        node_del_head).split('/?')
                    # example : 194.50.171.214:9566:origin:rc4:plain:bG5jbi5vcmcgOGw/?obfsparam=&remarks=5L-E572X5pavTQ&group=TG5jbi5vcmc
                    node_part_head = node_part[0].split(':')
                    server_head = sub_convert.find_country(
                        node_part_head[0])
                    password = sub_convert.base64_decode(node_part_head[5])
                    for split_point in password_split_points:
                        if split_point in password:
                            password = password.split(split_point)[0]
                            break
                        else:
                            continue
                    name_renamed = server_head + node_part_head[0] + ':' + node_part_head[1] + '(' + password + ')'
                    node_part_foot = node_part[-1].split('&')
                    for i in range(len(node_part_foot)):
                        if 'remarks' in node_part_foot[i]:
                            node_part_foot[i] = 'remarks=' + \
                                sub_convert.base64_encode(name_renamed)
                            break
                    node_part_foot_str = '&'.join(node_part_foot)
                    node_raw = sub_convert.base64_encode(
                        node_part[0] + '/?' + node_part_foot_str)
                    node = 'ssr://' + node_raw
                    node_list_formated_array.append(node)
                except Exception as err:
                    print(f'改名 ssr 节点发生错误: {err}')
            elif 'vmess://' in node:
                try:
                    node_del_head = node.replace('vmess://', '')
                    node_json_raw = sub_convert.base64_decode(node_del_head)
                    if '"' in node_json_raw:
                        node_json = json.loads(node_json_raw)
                    else:
                        node_json = eval(node_json_raw)
                    name_renamed = sub_convert.find_country(node_json['add']) + node_json['add'] + ':' + str(node_json['port']) + '(' + node_json['id'] + ')'
                    node_json['ps'] = name_renamed
                    node_json_dumps = json.dumps(node_json)
                    node_raw = sub_convert.base64_encode(node_json_dumps)
                    node = 'vmess://' + node_raw
                    node_list_formated_array.append(node)
                except Exception as err:
                    print(f'改名 vmess 节点发生错误: {err}')
            elif 'trojan://' in node:
                try:
                    node_del_head = node.replace('trojan://', '')
                    node_part = re.split('@|#', node_del_head, maxsplit=2)
                    server_head = sub_convert.find_country(
                        node_part[1].split(':')[0])
                    password = node_part[0]
                    name_renamed = server_head + node_part[1].split('?')[0] + '(' + password + ')'
                    node_raw = node_part[0] + '@' + \
                        node_part[1] + '#' + urllib.parse.quote(name_renamed)
                    node = 'trojan://' + node_raw
                    node_list_formated_array.append(node)
                except Exception as err:
                    print(f'改名 trojan 节点发生错误: {err}')
        node_list_formated = '\n'.join(node_list_formated_array)
        if node_list_formated == '':
            return node_list_formated
        else:
            return node_list_formated + '\n'

    def duplicate_removal(node_list):
        node_list_dr_array = []
        node_name_dr_array = []
        for node in node_list:
            if ("ss://" in node or "ssr://" in node or "trojan://" in node and "vless://" not in node):
                node_name = sub_convert.get_node_name(node)
                if '127.' not in node_name or 'localhost' in node_name:
                    if node_name not in node_name_dr_array:
                        node_name_dr_array.append(node_name)
                        node_list_dr_array.append(node)
                else:
                    continue
        return node_list_dr_array

    def get_node_name(node):
        name = ""
        if 'ss://' in node and 'vless://' not in node and 'vmess://' not in node:
            try:
                node_del_head = node.replace('ss://', '')
                node_part = node_del_head.split('#')
                name = urllib.parse.unquote(node_part[1])
            except Exception as err:
                print(f'获取节点名错误: {err}')
        elif 'ssr://' in node:
            try:
                node_del_head = node.replace('ssr://', '')
                node_part = sub_convert.base64_decode(
                    node_del_head).split('/?')
                node_part_foot = node_part[-1].split('&')
                for i in range(len(node_part_foot)):
                    if 'remarks' in node_part_foot[i]:
                        name = sub_convert.base64_decode(
                            node_part_foot[i].replace('remarks=', ''))
                        break
            except Exception as err:
                print(f'获取节点名错误: {err}')
        elif 'vmess://' in node:
            try:
                node_del_head = node.replace('vmess://', '')
                node_json = json.loads(
                    sub_convert.base64_decode(node_del_head))
                name = node_json['ps']
            except Exception as err:
                print(f'获取节点名错误: {err}')
        elif 'trojan://' in node:
            try:
                node_del_head = node.replace('trojan://', '')
                node_part = re.split('@|#', node_del_head, maxsplit=2)
                name = urllib.parse.unquote(node_part[-1])
            except Exception as err:
                print(f'获取节点名错误: {err}')
        return name

    def find_country(server):
        emoji = {
            'AD': '🇦🇩', 'AE': '🇦🇪', 'AF': '🇦🇫', 'AG': '🇦🇬',
            'AI': '🇦🇮', 'AL': '🇦🇱', 'AM': '🇦🇲', 'AO': '🇦🇴',
            'AQ': '🇦🇶', 'AR': '🇦🇷', 'AS': '🇦🇸', 'AT': '🇦🇹',
            'AU': '🇦🇺', 'AW': '🇦🇼', 'AX': '🇦🇽', 'AZ': '🇦🇿',
            'BA': '🇧🇦', 'BB': '🇧🇧', 'BD': '🇧🇩', 'BE': '🇧🇪',
            'BF': '🇧🇫', 'BG': '🇧🇬', 'BH': '🇧🇭', 'BI': '🇧🇮',
            'BJ': '🇧🇯', 'BL': '🇧🇱', 'BM': '🇧🇲', 'BN': '🇧🇳',
            'BO': '🇧🇴', 'BQ': '🇧🇶', 'BR': '🇧🇷', 'BS': '🇧🇸',
            'BT': '🇧🇹', 'BV': '🇧🇻', 'BW': '🇧🇼', 'BY': '🇧🇾',
            'BZ': '🇧🇿', 'CA': '🇨🇦', 'CC': '🇨🇨', 'CD': '🇨🇩',
            'CF': '🇨🇫', 'CG': '🇨🇬', 'CH': '🇨🇭', 'CI': '🇨🇮',
            'CK': '🇨🇰', 'CL': '🇨🇱', 'CM': '🇨🇲', 'CN': '🇨🇳',
            'CO': '🇨🇴', 'CR': '🇨🇷', 'CU': '🇨🇺', 'CV': '🇨🇻',
            'CW': '🇨🇼', 'CX': '🇨🇽', 'CY': '🇨🇾', 'CZ': '🇨🇿',
            'DE': '🇩🇪', 'DJ': '🇩🇯', 'DK': '🇩🇰', 'DM': '🇩🇲',
            'DO': '🇩🇴', 'DZ': '🇩🇿', 'EC': '🇪🇨', 'EE': '🇪🇪',
            'EG': '🇪🇬', 'EH': '🇪🇭', 'ER': '🇪🇷', 'ES': '🇪🇸',
            'ET': '🇪🇹', 'EU': '🇪🇺', 'FI': '🇫🇮', 'FJ': '🇫🇯',
            'FK': '🇫🇰', 'FM': '🇫🇲', 'FO': '🇫🇴', 'FR': '🇫🇷',
            'GA': '🇬🇦', 'GB': '🇬🇧', 'GD': '🇬🇩', 'GE': '🇬🇪',
            'GF': '🇬🇫', 'GG': '🇬🇬', 'GH': '🇬🇭', 'GI': '🇬🇮',
            'GL': '🇬🇱', 'GM': '🇬🇲', 'GN': '🇬🇳', 'GP': '🇬🇵',
            'GQ': '🇬🇶', 'GR': '🇬🇷', 'GS': '🇬🇸', 'GT': '🇬🇹',
            'GU': '🇬🇺', 'GW': '🇬🇼', 'GY': '🇬🇾', 'HK': '🇭🇰',
            'HM': '🇭🇲', 'HN': '🇭🇳', 'HR': '🇭🇷', 'HT': '🇭🇹',
            'HU': '🇭🇺', 'ID': '🇮🇩', 'IE': '🇮🇪', 'IL': '🇮🇱',
            'IM': '🇮🇲', 'IN': '🇮🇳', 'IO': '🇮🇴', 'IQ': '🇮🇶',
            'IR': '🇮🇷', 'IS': '🇮🇸', 'IT': '🇮🇹', 'JE': '🇯🇪',
            'JM': '🇯🇲', 'JO': '🇯🇴', 'JP': '🇯🇵', 'KE': '🇰🇪',
            'KG': '🇰🇬', 'KH': '🇰🇭', 'KI': '🇰🇮', 'KM': '🇰🇲',
            'KN': '🇰🇳', 'KP': '🇰🇵', 'KR': '🇰🇷', 'KW': '🇰🇼',
            'KY': '🇰🇾', 'KZ': '🇰🇿', 'LA': '🇱🇦', 'LB': '🇱🇧',
            'LC': '🇱🇨', 'LI': '🇱🇮', 'LK': '🇱🇰', 'LR': '🇱🇷',
            'LS': '🇱🇸', 'LT': '🇱🇹', 'LU': '🇱🇺', 'LV': '🇱🇻',
            'LY': '🇱🇾', 'MA': '🇲🇦', 'MC': '🇲🇨', 'MD': '🇲🇩',
            'ME': '🇲🇪', 'MF': '🇲🇫', 'MG': '🇲🇬', 'MH': '🇲🇭',
            'MK': '🇲🇰', 'ML': '🇲🇱', 'MM': '🇲🇲', 'MN': '🇲🇳',
            'MO': '🇲🇴', 'MP': '🇲🇵', 'MQ': '🇲🇶', 'MR': '🇲🇷',
            'MS': '🇲🇸', 'MT': '🇲🇹', 'MU': '🇲🇺', 'MV': '🇲🇻',
            'MW': '🇲🇼', 'MX': '🇲🇽', 'MY': '🇲🇾', 'MZ': '🇲🇿',
            'NA': '🇳🇦', 'NC': '🇳🇨', 'NE': '🇳🇪', 'NF': '🇳🇫',
            'NG': '🇳🇬', 'NI': '🇳🇮', 'NL': '🇳🇱', 'NO': '🇳🇴',
            'NP': '🇳🇵', 'NR': '🇳🇷', 'NU': '🇳🇺', 'NZ': '🇳🇿',
            'OM': '🇴🇲', 'PA': '🇵🇦', 'PE': '🇵🇪', 'PF': '🇵🇫',
            'PG': '🇵🇬', 'PH': '🇵🇭', 'PK': '🇵🇰', 'PL': '🇵🇱',
            'PM': '🇵🇲', 'PN': '🇵🇳', 'PR': '🇵🇷', 'PS': '🇵🇸',
            'PT': '🇵🇹', 'PW': '🇵🇼', 'PY': '🇵🇾', 'QA': '🇶🇦',
            'RE': '🇷🇪', 'RO': '🇷🇴', 'RS': '🇷🇸', 'RU': '🇷🇺',
            'RW': '🇷🇼', 'SA': '🇸🇦', 'SB': '🇸🇧', 'SC': '🇸🇨',
            'SD': '🇸🇩', 'SE': '🇸🇪', 'SG': '🇸🇬', 'SH': '🇸🇭',
            'SI': '🇸🇮', 'SJ': '🇸🇯', 'SK': '🇸🇰', 'SL': '🇸🇱',
            'SM': '🇸🇲', 'SN': '🇸🇳', 'SO': '🇸🇴', 'SR': '🇸🇷',
            'SS': '🇸🇸', 'ST': '🇸🇹', 'SV': '🇸🇻', 'SX': '🇸🇽',
            'SY': '🇸🇾', 'SZ': '🇸🇿', 'TC': '🇹🇨', 'TD': '🇹🇩',
            'TF': '🇹🇫', 'TG': '🇹🇬', 'TH': '🇹🇭', 'TJ': '🇹🇯',
            'TK': '🇹🇰', 'TL': '🇹🇱', 'TM': '🇹🇲', 'TN': '🇹🇳',
            'TO': '🇹🇴', 'TR': '🇹🇷', 'TT': '🇹🇹', 'TV': '🇹🇻',
            'TW': '🇹🇼', 'TZ': '🇹🇿', 'UA': '🇺🇦', 'UG': '🇺🇬',
            'UM': '🇺🇲', 'US': '🇺🇸', 'UY': '🇺🇾', 'UZ': '🇺🇿',
            'VA': '🇻🇦', 'VC': '🇻🇨', 'VE': '🇻🇪', 'VG': '🇻🇬',
            'VI': '🇻🇮', 'VN': '🇻🇳', 'VU': '🇻🇺', 'WF': '🇼🇫',
            'WS': '🇼🇸', 'XK': '🇽🇰', 'YE': '🇾🇪', 'YT': '🇾🇹',
            'ZA': '🇿🇦', 'ZM': '🇿🇲', 'ZW': '🇿🇼',
            'RELAY': '🏁',
            'NOWHERE': '🇦🇶',
        }
        if server.replace('.', '').isdigit():
            ip = server
        else:
            try:
                # https://cloud.tencent.com/developer/article/1569841
                ip = socket.gethostbyname(server)
            except Exception:
                ip = server
        with geoip2.database.Reader('./utils/Country.mmdb') as ip_reader:
            try:
                response = ip_reader.country(ip)
                country_code = response.country.iso_code
            except Exception:
                ip = '0.0.0.0'
                country_code = 'NOWHERE'

        if country_code == 'CLOUDFLARE':
            country_code = 'RELAY'
        elif country_code == 'PRIVATE':
            country_code = 'RELAY'
        if country_code in emoji:
            name_emoji = emoji[country_code]
        else:
            name_emoji = emoji['NOWHERE']
        return '[' + name_emoji + ']'

    def write_to_node(node_list_array, path):
        node_list = '\n'.join(node_list_array)
        node_list_file = open(path, 'w', encoding='utf-8')
        node_list_file.write(node_list)
        node_list_file.close()

    def write_to_base64(node_list_array, path):
        node_list = '\n'.join(node_list_array)
        node_list_base64 = sub_convert.base64_encode(node_list)
        node_list_base64_file = open(path, 'w', encoding='utf-8')
        node_list_base64_file.write(node_list_base64)
        node_list_base64_file.close()

    def write_to_clash(node_list_array, path):
        # 使用远程订阅转换服务
        # server_host = 'https://api.v1.mk'
        for i in range(0, len(node_list_array), 2000):
            node_list_array_part = node_list_array[i:i + 2000]
            node_list_part = sub_convert.yaml_encode(node_list_array_part)
            node_list_part_file = open(
                f'{path}{(i+1)//2000}.yaml', 'w', encoding='utf-8')
            node_list_part_file.write(node_list_part)
            node_list_part_file.close()

    def base64_encode(url_content):  # 将 URL 内容转换为 Base64
        base64_content = base64.b64encode(
            url_content.encode('utf-8')).decode('ascii')
        return base64_content

    def base64_decode(url_content):  # Base64 转换为 URL 链接内容
        if '-' in url_content:
            url_content = url_content.replace('-', '+')
        elif '_' in url_content:
            url_content = url_content.replace('_', '/')
        # print(len(url_content))
        missing_padding = len(url_content) % 4
        if missing_padding != 0:
            # 不是4的倍数后加= https://www.cnblogs.com/wswang/p/7717997.html
            url_content += '='*(4 - missing_padding)
        try:
            base64_content = base64.b64decode(url_content.encode(
                'utf-8')).decode('utf-8', 'ignore')  # https://www.codenong.com/42339876/
            base64_content_format = base64_content
            return base64_content_format
        except UnicodeDecodeError:
            base64_content = base64.b64decode(url_content)
            base64_content_format = base64_content
            return base64_content

    def yaml_encode(lines):  # 将 URL 内容转换为 YAML (输出默认 YAML 格式)
        url_list = []
        password_split_points = ["("]
        for line in lines:
            yaml_url = {}
            if 'vmess://' in line:
                try:
                    vmess_json_config = json.loads(
                        sub_convert.base64_decode(line.replace('vmess://', '')))
                    vmess_default_config = {
                        'v': 'Vmess Node', 'ps': 'Vmess Node', 'add': '0.0.0.0', 'port': 0, 'id': '',
                        'aid': 0, 'scy': 'auto', 'net': '', 'type': '', 'host': vmess_json_config['add'], 'path': '/', 'tls': ''
                    }
                    vmess_default_config.update(vmess_json_config)
                    vmess_config = vmess_default_config
                    #yaml_config_str = ['name', 'server', 'port', 'type', 'uuid', 'alterId', 'cipher', 'tls', 'skip-cert-verify', 'network', 'ws-path', 'ws-headers']
                    #vmess_config_str = ['ps', 'add', 'port', 'id', 'aid', 'scy', 'tls', 'net', 'host', 'path']
                    # 生成 yaml 节点字典
                    if vmess_config['id'] == '':
                        print('节点格式错误')
                    else:
                        yaml_url.setdefault('name', '"' + urllib.parse.unquote(vmess_config['ps']) + '"')
                        if '[' in vmess_config['add'] or ']' in vmess_config['add']:
                            yaml_url.setdefault('server', vmess_config['add'].replace('[', '').replace(']', ''))
                        else:
                            yaml_url.setdefault('server', vmess_config['add'])
                        yaml_url.setdefault('port', int(vmess_config['port']))
                        yaml_url.setdefault('type', 'vmess')
                        if vmess_config['id'] == '0' or re.findall("[f-z]", vmess_config['id']):
                            continue
                        else:
                            yaml_url.setdefault('uuid', vmess_config['id'])
                        yaml_url.setdefault('alterId', int(vmess_config['aid']))
                        vmess_cipher = ["auto", "aes-128-gcm", "chacha20-poly1305", "none"]
                        if vmess_config['scy'] in vmess_cipher:
                            yaml_url.setdefault('cipher', vmess_config['scy'])
                        else:
                            continue                            
                        if vmess_config['net'] != '':
                            yaml_url.setdefault('network', vmess_config['net'])
                        vmess_config['path'] = urllib.parse.unquote(vmess_config['path']).split('?')[0]
                        if vmess_config['net'] == 'ws':
                            if vmess_config['tls'] == 'tls':
                                yaml_url.setdefault('tls', 'true')
                            else:
                                yaml_url.setdefault('tls', 'false')
                            # yaml_url.setdefault('skip-cert-verify', 'true')
                            if vmess_config['path'] == '':
                                yaml_url.setdefault('ws-opts', {'path': '/'})
                            else:
                                yaml_url.setdefault('ws-opts', {}).setdefault('path', vmess_config['path'])
                            if vmess_config['host'] != '':
                                if '%' in vmess_config['host']:
                                    yaml_url.setdefault('ws-opts', {}).setdefault('headers', {'host': '"' + vmess_config['host'] + '"'})
                                else:
                                    yaml_url.setdefault('ws-opts', {}).setdefault('headers', {'host': vmess_config['host']})
                        elif vmess_config['net'] == 'h2':
                            yaml_url.setdefault('tls', 'true')
                            yaml_url.setdefault('h2-opts', {}).setdefault('host', '[' + vmess_config['host'] + ']')
                            if vmess_config['path'] == '':
                                yaml_url.setdefault('h2-opts', {}).setdefault('path', '/')
                            else:
                                yaml_url.setdefault('h2-opts', {}).setdefault('path', vmess_config['path'])
                        elif vmess_config['net'] == 'grpc':
                            yaml_url.setdefault('tls', 'true')
                            # yaml_url.setdefault('skip-cert-verify', 'true')
                            if vmess_config['host'] == '':
                                yaml_url.setdefault('servername', '""')
                            else:
                                yaml_url.setdefault('servername', vmess_config['host'])
                            if vmess_config['path'] == '':
                                yaml_url.setdefault('grpc-opts', {'grpc-service-name': '/'})
                            else:
                                yaml_url.setdefault('grpc-opts', {'grpc-service-name': vmess_config['path']})
                        elif vmess_config['net'] == 'http':
                            yaml_url.setdefault('http-opts', {}).setdefault('method', "GET")
                            if vmess_config['path'] == '':
                                yaml_url.setdefault('http-opts', {}).setdefault('path', '[/]')
                            else:
                                yaml_url.setdefault('http-opts', {}).setdefault('path', '[' + vmess_config['path'] + ']')
                except Exception as err:
                    print(f'yaml_encode 解析 vmess 节点发生错误: {err}')
                    pass

            if 'ss://' in line and 'vless://' not in line and 'vmess://' not in line:
                try:
                    ss_content = line.replace('ss://', '')
                    ss_content_array = re.split('@|\/\?|#', ss_content)
                    yaml_url.setdefault(
                        'name', '"' + urllib.parse.unquote(ss_content_array[-1]) + '"')
                    # include cipher password
                    config_first_decode_list = sub_convert.base64_decode(ss_content_array[0]).split(':')
                    # include server port
                    config_second_list = ss_content_array[1].split(':')
                    if "::" in config_second_list[:-1]:
                        continue
                    else:
                        yaml_url.setdefault('server', (':'.join(config_second_list[:-1])).replace("]","").replace("[",""))
                    yaml_url.setdefault('port', config_second_list[-1])
                    yaml_url.setdefault('type', 'ss')
                    ss_cipher = ["aes-128-gcm", "aes-192-gcm", "aes-256-gcm", "aes-128-cfb", "aes-192-cfb", "aes-256-cfb", "aes-128-ctr", "aes-192-ctr", "aes-256-ctr", "rc4-md5", "chacha20-ietf", "xchacha20", "chacha20-ietf-poly1305", "xchacha20-ietf-poly1305"]
                    if config_first_decode_list[0] in ss_cipher:
                        yaml_url.setdefault('cipher', config_first_decode_list[0])
                    else:
                        continue
                    server_password = config_first_decode_list[1].replace('!str', '').replace('!<str>', '').replace('!<str', '').replace(' ', '')
                    if server_password.isdigit() or server_password.replace('.', '').isdigit():
                        yaml_url.setdefault('password', '!<str> ' + server_password)
                    elif (server_password == ''):
                        continue
                    else:
                        yaml_url.setdefault('password', server_password)
                    if len(ss_content_array) >= 4:
                        # include more server config
                        parameters_raw = urllib.parse.unquote(ss_content_array[2])
                        parameters = parameters_raw.split(';')
                        # or 'plugin=' in parameter for parameter in parameters:
                        if 'plugin=' in str(parameters):
                            if 'obfs' in str(parameters):
                                yaml_url.setdefault('plugin', 'obfs')
                            elif 'v2ray-plugin' in str(parameters):
                                yaml_url.setdefault('plugin', 'v2ray-plugin')
                        for parameter in parameters:
                            if 'plugin' in yaml_url.keys():
                                if 'obfs' in yaml_url['plugin']:
                                    if 'obfs=' in parameter:
                                        yaml_url.setdefault('plugin-opts', {}).setdefault('mode', parameter.split('=')[-1])
                                    elif 'obfs-host=' in parameter:
                                        yaml_url.setdefault('plugin-opts', {}).setdefault('host', '"' + parameter.split('=')[-1] + '"')
                                elif 'v2ray-plugin' in yaml_url['plugin']:
                                    if 'mode=' in parameter:
                                        yaml_url.setdefault('plugin-opts', {}).setdefault('mode', parameter.split('=')[-1])
                                    elif 'tls' in parameter:
                                        yaml_url.setdefault('plugin-opts', {}).setdefault('tls', 'true')
                                    elif 'mux' in parameter:
                                        yaml_url.setdefault('plugin-opts', {}).setdefault('mux', 'true')
                                    elif 'host=' in parameter:
                                        yaml_url.setdefault('plugin-opts', {}).setdefault('host', parameter.split('=')[-1])
                                    elif 'path=' in parameter:
                                        if parameter.split('=')[-1] == '':
                                            yaml_url.setdefault('plugin-opts', {}).setdefault('path', '"/"')
                                        else:
                                            yaml_url.setdefault('plugin-opts', {}).setdefault('path', parameter.split('=')[-1])
                        if 'plugin' in yaml_url.keys():
                            if 'plugin-opts' not in yaml_url.keys():
                                yaml_url.setdefault('plugin-opts', {})
                            if 'obfs' in yaml_url['plugin']:
                                if 'mode' not in yaml_url['plugin-opts'].keys():
                                    yaml_url.setdefault('plugin-opts', {}).setdefault('mode', 'tls')
                            if 'v2ray-plugin' in yaml_url['plugin']:
                                if 'mode' not in yaml_url['plugin-opts'].keys():
                                    yaml_url.setdefault('plugin-opts', {}).setdefault('mode', 'websocket')
                except Exception as err:
                    print(f'yaml_encode 解析 ss 节点发生错误: {err}')
                    pass

            if 'ssr://' in line:
                try:
                    ssr_content = sub_convert.base64_decode(line.replace('ssr://', ''))

                    part_list = ssr_content.split('/?')
                    if '&' in part_list[1]:
                        # 将 SSR content /？后部分参数分割
                        ssr_part = part_list[1].split('&')
                        for item in ssr_part:
                            if 'remarks=' in item:
                                remarks_part = item.replace('remarks=', '')
                        try:
                            remarks = sub_convert.base64_decode(remarks_part)
                        except Exception:
                            remarks = 'ssr'
                    else:
                        remarks_part = part_list[1].replace('remarks=', '')
                        try:
                            remarks = sub_convert.base64_decode(remarks_part)
                        except Exception:
                            remarks = 'ssr'
                            print(f'SSR format error, content:{remarks_part}')
                    yaml_url.setdefault('name', '"' + urllib.parse.unquote(remarks) + '"')
                    server_part_list = re.split(':', part_list[0])
                    if "NULL" in server_part_list[0]:
                        continue
                    else:
                        yaml_url.setdefault('server', server_part_list[0])
                    yaml_url.setdefault('port', server_part_list[1])
                    yaml_url.setdefault('type', 'ssr')
                    ssr_cipher = ["aes-128-gcm", "aes-192-gcm", "aes-256-gcm", "aes-128-cfb", "aes-192-cfb", "aes-256-cfb", "aes-128-ctr", "aes-192-ctr", "aes-256-ctr", "rc4-md5", "chacha20-ietf", "xchacha20", "chacha20-ietf-poly1305", "xchacha20-ietf-poly1305"]
                    if server_part_list[3] in ssr_cipher:
                        yaml_url.setdefault('cipher', server_part_list[3])
                    else:
                        continue
                    server_password = sub_convert.base64_decode(server_part_list[5])
                    for split_point in password_split_points:
                        if split_point in server_password:
                            server_password = server_password.split(split_point)[0]
                            break
                        else:
                            continue
                    if server_password.isdigit() or server_password.replace('.', '').isdigit():
                        yaml_url.setdefault('password', '!<str> ' + sub_convert.base64_decode(server_part_list[5]))
                    else:
                        yaml_url.setdefault('password', sub_convert.base64_decode(server_part_list[5]))
                    ssr_protocol = ["origin", "auth_sha1_v4", "auth_aes128_md5", "auth_aes128_sha1", "auth_chain_a", "auth_chain_b"]
                    if server_part_list[2] in ssr_protocol:
                        yaml_url.setdefault('protocol', server_part_list[2])
                    else:
                        continue
                    ssr_obfs = ["plain", "http_simple", "http_post", "random_head", "tls1.2_ticket_auth", "tls1.2_ticket_fastauth"]
                    if server_part_list[4] in ssr_obfs:
                        yaml_url.setdefault('obfs', server_part_list[4])
                    else:
                        continue
                    for item in ssr_part:
                        if 'obfsparam=' in item:
                            obfs_param = sub_convert.base64_decode(
                                item.replace('obfsparam=', ''))
                            if obfs_param != '':
                                yaml_url.setdefault('obfs-param', '"' + obfs_param + '"')
                            else:
                                yaml_url.setdefault('obfs-param', '""')
                        elif 'protoparam=' in item:
                            protocol_param = sub_convert.base64_decode(
                                item.replace('protoparam=', ''))
                            if protocol_param != '':
                                yaml_url.setdefault(
                                    'protocol-param', protocol_param.replace('[', '').replace(']', ''))
                            else:
                                yaml_url.setdefault('protocol-param', '""')
                    if 'obfs-param' not in yaml_url.keys():
                        yaml_url.setdefault('obfs-param', '""')
                    if 'protocol-param' not in yaml_url.keys():
                        yaml_url.setdefault('protocol-param', '""')
                except Exception as err:
                    print(f'yaml_encode 解析 ssr 节点发生错误: {err}')
                    pass

            if 'trojan://' in line:
                try:
                    url_content = line.replace('trojan://', '')
                    part_list = re.split('@|\?|#', url_content)
                    yaml_url.setdefault('name', '"' + urllib.parse.unquote(part_list[-1]) + '"')
                    yaml_url.setdefault('server', part_list[1].split(':')[0])
                    yaml_url.setdefault('port', part_list[1].split(':')[1])
                    yaml_url.setdefault('type', 'trojan')
                    server_password = urllib.parse.unquote(part_list[0].replace('trojan://', '')).replace('!str', '').replace('!<str>', '').replace(' ', '')
                    if server_password.isdigit() or server_password.replace('.', '').isdigit():
                        yaml_url.setdefault('password', '!<str> ' + server_password)
                    elif not server_password:
                        yaml_url.setdefault('password', '""')
                    elif server_password == 'null':
                        yaml_url.setdefault('password', '"' + server_password + '"')
                    else:
                        yaml_url.setdefault('password', server_password)
                    if len(part_list) == 4:
                        for config in part_list[2].split('&'):
                            if 'sni=' in config:
                                yaml_url.setdefault('sni', config[4:])
                            elif 'type=' in config:
                                yaml_url.setdefault('network', config[5:])
                            if 'network' in yaml_url.keys():
                                yaml_url.setdefault('udp', 'true')
                                if yaml_url['network'] == 'ws':
                                    if 'path=' in config:
                                        yaml_url.setdefault('ws-opts', {}).setdefault('path', config[5:].split('?')[0])
                                    elif 'host=' in config:
                                        yaml_url.setdefault('ws-opts', {}).setdefault('headers', {}).setdefault('host', config[5:])
                                elif yaml_url['network'] == 'grpc':
                                    if 'servicename=' in config:
                                        yaml_url.setdefault('grpc-opts', {}).setdefault('grpc-service-name', config[12:])
                            else:
                                if 'alpn=' in config:
                                    yaml_url.setdefault('alpn', '[' + config[5:] + ']')
                        if 'network' in yaml_url.keys():
                            if yaml_url['network'] == 'ws':
                                if 'ws_opts' not in yaml_url.keys():
                                    yaml_url.setdefault('ws-opts', {})
                                if yaml_url['ws-opts']['path'] == '':
                                    yaml_url.setdefault('ws-opts', {}).setdefault('path', '/')
                            if yaml_url['network'] == 'grpc':
                                if 'grpc-opts' not in yaml_url.keys():
                                    yaml_url.setdefault('grpc-opts', {})
                                if 'grpc-service-name' not in yaml_url['grpc-opts'].keys():
                                    yaml_url.setdefault('grpc-opts', {}).setdefault('grpc-service-name', '""')
                except Exception as err:
                    print(f'yaml_encode 解析 trojan 节点发生错误: {err}')
                    pass
            if yaml_url['server'] == '' or yaml_url['port'] == 0:
                continue
            # if not ping(yaml_url['server'],1):
            #     continue
            yaml_node_raw = str(yaml_url)
            yaml_node_body = yaml_node_raw.replace('\'', '')
            yaml_node_head = '  - '
            yaml_node = yaml_node_head + yaml_node_body
            url_list.append(yaml_node)
        yaml_head = 'proxies:\n'
        yaml_content = yaml_head + '\n'.join(url_list)

        return yaml_content
