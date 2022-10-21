import base64
import json
import re
import urllib.parse


class sub_convert():

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


url_list = []
lines = ['ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTowYTAwZmU1MjZlMzU5MjUyMTU1OTQyNzgzOTAyMDY1Mg@183.232.158.66:8003/?plugin=obfs-local%3Bobfs-local#%5Bss%5D%F0%9F%87%A8%F0%9F%87%B3%5BCN%5D183.232.158.66%3A8003%280a00fe526e3592521559427839020652%29']
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
                # yaml_config_str = ['name', 'server', 'port', 'type', 'uuid', 'alterId', 'cipher', 'tls', 'skip-cert-verify', 'network', 'ws-path', 'ws-headers']
                # vmess_config_str = ['ps', 'add', 'port', 'id', 'aid', 'scy', 'tls', 'net', 'host', 'path']
                # 生成 yaml 节点字典
                if vmess_config['id'] == '':
                    print('节点格式错误')
                else:
                    yaml_url.setdefault(
                        'name', '"' + urllib.parse.unquote(vmess_config['ps']) + '"')
                    yaml_url.setdefault('server', vmess_config['add'])
                    yaml_url.setdefault('port', int(vmess_config['port']))
                    yaml_url.setdefault('type', 'vmess')
                    if vmess_config['id'] != '0':
                        yaml_url.setdefault('uuid', vmess_config['id'])
                    else:
                        continue
                    yaml_url.setdefault(
                        'alterId', int(vmess_config['aid']))
                    vmess_cipher = ["auto", "aes-128-gcm",
                                    "chacha20-poly1305", "none"]
                    if vmess_config['scy'] in vmess_cipher:
                        yaml_url.setdefault('cipher', vmess_config['scy'])
                    else:
                        continue
                    if vmess_config['net'] != '':
                        yaml_url.setdefault('network', vmess_config['net'])
                    vmess_config['path'] = urllib.parse.unquote(
                        vmess_config['path']).split('?')[0]
                    if vmess_config['net'] == 'ws':
                        if vmess_config['tls'] == 'tls':
                            yaml_url.setdefault('tls', 'true')
                        else:
                            yaml_url.setdefault('tls', 'false')
                        # yaml_url.setdefault('skip-cert-verify', 'true')
                        if vmess_config['path'] == '':
                            yaml_url.setdefault('ws-opts', {'path': '/'})
                        else:
                            yaml_url.setdefault(
                                'ws-opts', {}).setdefault('path', vmess_config['path'])
                        if vmess_config['host'] != '':
                            if '%22' in vmess_config['host']:
                                yaml_url.setdefault(
                                    'ws-opts', {}).setdefault('headers', {'host': vmess_config['host'].split('%22')[-2]})
                            else:
                                yaml_url.setdefault(
                                    'ws-opts', {}).setdefault('headers', {'host': vmess_config['host']})
                    elif vmess_config['net'] == 'h2':
                        yaml_url.setdefault('tls', 'true')
                        yaml_url.setdefault(
                            'h2-opts', {}).setdefault('host', '[' + vmess_config['host'] + ']')
                        if vmess_config['path'] == '':
                            yaml_url.setdefault(
                                'h2-opts', {}).setdefault('path', '/')
                        else:
                            yaml_url.setdefault(
                                'h2-opts', {}).setdefault('path', vmess_config['path'])
                    elif vmess_config['net'] == 'grpc':
                        yaml_url.setdefault('tls', 'true')
                        # yaml_url.setdefault('skip-cert-verify', 'true')
                        if vmess_config['host'] == '':
                            yaml_url.setdefault('servername', '""')
                        else:
                            yaml_url.setdefault(
                                'servername', vmess_config['host'])
                        if vmess_config['path'] == '':
                            yaml_url.setdefault(
                                'grpc-opts', {'grpc-service-name': '/'})
                        else:
                            yaml_url.setdefault(
                                'grpc-opts', {'grpc-service-name': vmess_config['path']})
                    elif vmess_config['net'] == 'http':
                        yaml_url.setdefault(
                            'http-opts', {}).setdefault('method', "GET")
                        if vmess_config['path'] == '':
                            yaml_url.setdefault(
                                'http-opts', {}).setdefault('path', '[/]')
                        else:
                            yaml_url.setdefault(
                                'http-opts', {}).setdefault('path', '[' + vmess_config['path'] + ']')
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
                config_first_decode_list = sub_convert.base64_decode(
                    ss_content_array[0]).split(':')
                # include server port
                config_second_list = ss_content_array[1].split(':')
                yaml_url.setdefault('server', config_second_list[0])
                yaml_url.setdefault('port', config_second_list[1])
                yaml_url.setdefault('type', 'ss')
                ss_cipher = ["aes-128-gcm", "aes-192-gcm", "aes-256-gcm", "aes-128-cfb", "aes-192-cfb", "aes-256-cfb", "aes-128-ctr",
                             "aes-192-ctr", "aes-256-ctr", "rc4-md5", "chacha20-ietf", "xchacha20", "chacha20-ietf-poly1305", "xchacha20-ietf-poly1305"]
                if config_first_decode_list[0] in ss_cipher:
                    yaml_url.setdefault(
                        'cipher', config_first_decode_list[0])
                else:
                    continue
                server_password = config_first_decode_list[1]
                if server_password.isdigit() or server_password.replace('.', '').isdigit():
                    yaml_url.setdefault(
                        'password', '!<str> ' + config_first_decode_list[1])
                else:
                    yaml_url.setdefault(
                        'password', config_first_decode_list[1])
                if len(ss_content_array) >= 4:
                    # include more server config
                    parameters_raw = urllib.parse.unquote(
                        ss_content_array[2])
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
                                    yaml_url.setdefault(
                                        'plugin-opts', {}).setdefault('mode', parameter.split('=')[-1])
                                elif 'obfs-host=' in parameter:
                                    yaml_url.setdefault(
                                        'plugin-opts', {}).setdefault('host', '"' + parameter.split('=')[-1] + '"')
                            elif 'v2ray-plugin' in yaml_url['plugin']:
                                if 'mode=' in parameter:
                                    yaml_url.setdefault(
                                        'plugin-opts', {}).setdefault('mode', parameter.split('=')[-1])
                                elif 'tls' in parameter:
                                    yaml_url.setdefault(
                                        'plugin-opts', {}).setdefault('tls', 'true')
                                elif 'mux' in parameter:
                                    yaml_url.setdefault(
                                        'plugin-opts', {}).setdefault('mux', 'true')
                                elif 'host=' in parameter:
                                    yaml_url.setdefault(
                                        'plugin-opts', {}).setdefault('host', parameter.split('=')[-1])
                                elif 'path=' in parameter:
                                    if parameter.split('=')[-1] == '':
                                        yaml_url.setdefault(
                                            'plugin-opts', {}).setdefault('path', '""')
                                    else:
                                        yaml_url.setdefault(
                                            'plugin-opts', {}).setdefault('path', parameter.split('=')[-1])
                    if 'plugin' in yaml_url.keys():
                        if 'plugin-opts' not in yaml_url.keys():
                            yaml_url.setdefault('plugin-opts', {})
                        if 'obfs' in yaml_url['plugin']:
                            if 'mode' not in yaml_url['plugin-opts'].keys():
                                yaml_url.setdefault(
                                    'plugin-opts', {}).setdefault('mode', 'tls')
                            if 'host' not in yaml_url['plugin-opts'].keys():
                                yaml_url.setdefault(
                                    'plugin-opts', {}).setdefault('host', '""')
                        if 'v2ray-plugin' in yaml_url['plugin']:
                            if 'mode' not in yaml_url['plugin-opts'].keys():
                                yaml_url.setdefault(
                                    'plugin-opts', {}).setdefault('mode', 'websocket')
                            if 'tls' not in yaml_url['plugin-opts'].keys():
                                yaml_url.setdefault(
                                    'plugin-opts', {}).setdefault('tls', 'false')
                            if 'host' not in yaml_url['plugin-opts'].keys():
                                yaml_url.setdefault(
                                    'plugin-opts', {}).setdefault('host', '""')
                            if 'path' not in yaml_url['plugin-opts'].keys():
                                yaml_url.setdefault(
                                    'plugin-opts', {}).setdefault('path', '"/"')
                            if 'mux' not in yaml_url['plugin-opts'].keys():
                                yaml_url.setdefault(
                                    'plugin-opts', {}).setdefault('mux', "false")
            except Exception as err:
                print(f'yaml_encode 解析 ss 节点发生错误: {err}')
                pass

        if 'ssr://' in line:
            try:
                ssr_content = sub_convert.base64_decode(
                    line.replace('ssr://', ''))

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
                yaml_url.setdefault(
                    'name', '"' + urllib.parse.unquote(remarks) + '"')
                server_part_list = re.split(':', part_list[0])
                yaml_url.setdefault('server', server_part_list[0])
                yaml_url.setdefault('port', server_part_list[1])
                yaml_url.setdefault('type', 'ssr')
                ssr_cipher = ["aes-128-gcm", "aes-192-gcm", "aes-256-gcm", "aes-128-cfb", "aes-192-cfb", "aes-256-cfb", "aes-128-ctr",
                              "aes-192-ctr", "aes-256-ctr", "rc4-md5", "chacha20-ietf", "xchacha20", "chacha20-ietf-poly1305", "xchacha20-ietf-poly1305"]
                if server_part_list[3] in ssr_cipher:
                    yaml_url.setdefault('cipher', server_part_list[3])
                else:
                    continue
                server_password = sub_convert.base64_decode(
                    server_part_list[5])
                for split_point in password_split_points:
                    if split_point in server_password:
                        server_password = server_password.split(split_point)[
                            0]
                        break
                    else:
                        continue
                if server_password.isdigit() or server_password.replace('.', '').isdigit():
                    yaml_url.setdefault(
                        'password', '!<str> ' + sub_convert.base64_decode(server_part_list[5]))
                else:
                    yaml_url.setdefault(
                        'password', sub_convert.base64_decode(server_part_list[5]))
                ssr_protocol = ["origin", "auth_sha1_v4", "auth_aes128_md5",
                                "auth_aes128_sha1", "auth_chain_a", "auth_chain_b"]
                if server_part_list[2] in ssr_protocol:
                    yaml_url.setdefault('protocol', server_part_list[2])
                else:
                    continue
                ssr_obfs = ["plain", "http_simple", "http_post", "random_head",
                            "tls1.2_ticket_auth", "tls1.2_ticket_fastauth"]
                if server_part_list[4] in ssr_obfs:
                    yaml_url.setdefault('obfs', server_part_list[4])
                else:
                    continue
                for item in ssr_part:
                    if 'obfsparam=' in item:
                        obfs_param = sub_convert.base64_decode(
                            item.replace('obfsparam=', ''))
                        if obfs_param != '':
                            yaml_url.setdefault(
                                'obfs-param', obfs_param.replace('[', '').replace(']', ''))
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
                yaml_url.setdefault(
                    'name', '"' + urllib.parse.unquote(part_list[-1]) + '"')
                yaml_url.setdefault('server', part_list[1].split(':')[0])
                yaml_url.setdefault('port', part_list[1].split(':')[1])
                yaml_url.setdefault('type', 'trojan')
                server_password = part_list[0].replace('trojan://', '')
                if server_password.isdigit() or server_password.replace('.', '').isdigit():
                    yaml_url.setdefault(
                        'password', '!<str> ' + server_password)
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
                                    yaml_url.setdefault(
                                        'ws-opts', {}).setdefault('path', config[5:].split('?')[0])
                                elif 'host=' in config:
                                    yaml_url.setdefault(
                                        'ws-opts', {}).setdefault('headers', {}).setdefault('host', config[5:])
                            elif yaml_url['network'] == 'grpc':
                                if 'servicename=' in config:
                                    yaml_url.setdefault(
                                        'grpc-opts', {}).setdefault('grpc-service-name', config[12:])
                        else:
                            if 'alpn=' in config:
                                yaml_url.setdefault(
                                    'alpn', '[' + config[5:] + ']')
                    if 'network' in yaml_url.keys():
                        if yaml_url['network'] == 'ws':
                            if yaml_url['ws-opts']['path'] == '':
                                yaml_url.setdefault(
                                    'ws-opts', {}).setdefault('path', '/')
            except Exception as err:
                print(f'yaml_encode 解析 trojan 节点发生错误: {err}')
                pass
