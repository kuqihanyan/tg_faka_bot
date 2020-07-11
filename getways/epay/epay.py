import requests
import hashlib
import json
import re

# 易支付API地址
API = 'https://home.bakbak.cn/'
# 商户ID
ID = 1041
# 商户密钥
KEY = 'm6KM7yP6L213125XmZ7QwwFKwYkm1BK'
# 支付成功跳转链接
JUMP_URL = "https://kangle.bakbak.cn/paysuccess.html"


def submit(money, name, trade_id):
    data = {'notify_url': JUMP_URL, 'pid': ID, 'return_url': JUMP_URL, 'sitename': 'Faka_Bot'}
    data.update(money=money, name=name, out_trade_no=trade_id)
    items = data.items()
    items = sorted(items)
    wait_sign_str = ''
    for i in items:
        wait_sign_str += str(i[0]) + '=' + str(i[1]) + '&'
    wait_for_sign_str = wait_sign_str[:-1] + KEY
    # print("输出待加密字符串" + '\n' + wait_sign_str)
    sign = hashlib.md5(wait_for_sign_str.encode('utf-8')).hexdigest()
    # print("输出订单签名：" + sign)
    data.update(sign=sign, sign_type='MD5')
    print(data)
    try:
        req = requests.post(API + 'submit.php', data=data)
        print(req.text)
        content = re.search(r"<script>(.*)</script>", req.text).group(1)
        print(content)
        if 'http' in content:
            pay_url = re.search(r"href=\'(.*)\'", content).group(1)
            return_data = {
                'status': 'Success',
                'type': 'url',
                'data': pay_url
            }
            return return_data
        else:
            pay_url = API + re.search(r"\.\/(.*)\'", content).group(1)
            print(pay_url)
            return_data = {
                'status': 'Success',
                'type': 'url',  # qrcode
                'data': pay_url
            }
            return return_data
    except Exception as e:
        print('submit | API请求失败')
        print(e)
        return_data = {
            'status': 'Failed',
            'data': 'API请求失败'
        }
        return return_data


def query(out_trade_no):
    try:
        req = requests.get(API + 'api.php?act=order&pid={}&key={}&out_trade_no={}'.format(ID, KEY, out_trade_no),
                           timeout=5)
        print(req.text)
        rst = re.search(r"(\{.*?\})", req.text).group(1)
        print(rst)
        rst_dict = json.loads(rst)
        print(rst_dict)
        code = str(rst_dict['code'])
        if int(code) == 1:
            pay_status = str(rst_dict['status'])
            if pay_status == '1':
                print('支付成功')
                return '支付成功'
            else:
                print('支付失败')
                return '支付失败'
        else:
            print('查询失败，订单号不存在')
            return '查询失败，订单号不存在'
    except Exception as e:
        print(e)
        print('epay | 查询请求失败')
        return 'API请求失败'


def cancel(out_trade_no):
    print('订单已经取消')
