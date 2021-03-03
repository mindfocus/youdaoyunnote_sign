import requests
import json
import time
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 配置各种key
# Server酱申请的skey
SCKEY = os.environ['SCKEY']
# 钉钉机器人的 webhook
webhook = os.environ['webhook']

# 配置通知方式 0=dingding 1=weixin 2=全都要 其他为不推送
notice = os.environ['notice']

global contents
contents = ''


def output(content):
    global contents
    content += '  '
    contents += content + '\n'
    content += '  '
    print(content)


# server酱推送
def server():
    global contents
    message = {"text": "新知小站签到通知！", "desp": contents}
    r = requests.post("https://sc.ftqq.com/" + SCKEY + ".send", data=message)
    if r.status_code == 200:
        print('[+]server酱已推送，请查收')


# 钉钉消息推送
def dingtalk():
    webhook_url = webhook
    dd_header = {"Content-Type": "application/json", "Charset": "UTF-8"}
    global contents
    dd_message = {
        "msgtype": "text",
        "text": {
            "content": f'新知小站签到通知！\n{contents}'
        }
    }
    r = requests.post(url=webhook_url,
                      headers=dd_header,
                      data=json.dumps(dd_message))
    if r.status_code == 200:
        print('[+]钉钉消息已推送，请查收  ')


def checkin(username, password):
    login_url = 'http://www.xinzhixiaozhan.com/wp-content/themes/modown/action/login.php'
    login_param = {
        'log': username,
        'pwd': password,
        'action': "mobantu_login"
    }
    session = requests.session()
    # 登录
    a = session.post(url=login_url, data=login_param, verify=False)
    # 签到
    checkin_url = 'http://www.xinzhixiaozhan.com/wp-content/themes/modown/action/user.php'
    check_param = {
        'action': "user.checkin"
    }
    r = session.post(url=checkin_url, data=check_param)
    # 当前时间
    times = time.strftime('%Y-%m-%d %H:%M:%S',
                          time.localtime())
    output('[+]当前签到时间：' + times)
    if r.status_code == 200:
        # 格式话
        info = json.loads(r.text)
        # 一共签到获得
        if info['error'] == 0:
            output('[+]用户： 签到成功!')
        else:
            output('[+]用户： 签到失败!')
            output('[+]原因： ' + info['msg'])
    else:
        output('[+]用户： 签到失败!')
        output('[+]原因： status code:' + r.status_code)

def main():
    output('---开始【新知每日签到】---')
    count = os.environ.get('xz_count')
    if count != None :
        for index in range(0, int(count)):
            # 账号
            username = os.environ['xz_username_' + str(index)]
            # 密码
            password = os.environ['xz_password_' + str(index)]
            checkin(username, password)

    output('---结束【新知每日签到】---')
    if notice == '0':
        try:
            dingtalk()
        except Exception:
            print('[+]请检查钉钉配置是否正确')
    elif notice == '1':
        try:
            server()
        except Exception:
            print('[+]请检查server酱配置是否正确')
    elif notice == '2':
        try:
            dingtalk()
        except Exception:
            print('[+]请检查钉钉配置是否正确')
        try:
            server()
        except Exception:
            print('[+]请检查server酱配置是否正确')
    else:
        print('[+]选择不推送信息')


def main_handler(event, context):
    return main()


if __name__ == '__main__':
    main()
