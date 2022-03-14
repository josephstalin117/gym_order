#coding=utf-8
import requests
import datetime
import time
import config
import json
from requests.adapters import HTTPAdapter

class GymTime:
    def __init__(self, gym_dict):
        for key in gym_dict:
            setattr(self, key, gym_dict[key])


def is_gym_order(date, startTime, endTime):
    url = "http://wechartdemo.zckx.net/API/TicketHandler.ashx?dataType=json&date=" + date + "&projectNo=1000000637&method=GetStrategyList";
    s.mount('http://', HTTPAdapter(max_retries=3))
    s.mount('https://', HTTPAdapter(max_retries=3))
    print(time.strftime('%Y-%m-%d %H:%M:%S'))
    try:
        data = s.get(url, timeout=10).json().get("list")
    except s.exceptions.RequestException as e:
        print(e)

    for item in data:
        gym_item = GymTime(item)
        if startTime == gym_item.sTime and endTime == gym_item.eTime:
            if gym_item.isCanReserve == 1 and gym_item.restCount > 0:
                return True
            else:
                return False

    return False


def gym_order(date, time_detail, user_info, open_id, request_session):
    url = "http://wechartdemo.zckx.net/Ticket/SaveOrder?"

    other_info = {
        'styleNo': "1000001069",
        'styleGroupNo': "1000000379",
        'styleName': "体育馆健身房",
        'price': "0.00",
        'discountPrice': "0.00",
        'ticketNum': 1,
        'solutionNo': "1000000632",
        'projectNo': "1000000637"
    }

    data = {
        'userInfoList': [user_info],
        'timeList': [time_detail],
        'styleInfoList': [other_info],
        'userDate': date,
        'totalprice': 0,
        'openId': open_id,
        'sellerNo': 'weixin'
    }
    url = url + 'dataType=json&orderJson=' + str(data)
    request_session.mount('http://', HTTPAdapter(max_retries=3))
    request_session.mount('https://', HTTPAdapter(max_retries=3))
    
    try:
        r = request_session.post(url, timeout=10)
    except request_session.RequestException as e:
        print(e)

    try:
        return r.json()
    except:
        return None


def is_success_order(date, open_id):
    url = "https://wechartdemo.zckx.net/Ticket/MyOrder?openId=" + open_id
    gym_html = s.get(url).text
    new_date = date.split("-")[0] + '年' + date.split("-")[1] + '月' + date.split("-")[2] + '日'
    if new_date in gym_html:
        return True
    return False


# wechat
def send_message(key, title, body):
    msg_url = "https://sc.ftqq.com/{}.send?text={}&desp={}".format(key, title, body)
    requests.get(msg_url)


if __name__ == "__main__":
    #server_key = ""

    user_info = config.user_info
    open_id = config.openId

    server_key = config.server_key

    #user_info = {
    #    'userName': '',
    #    'userPhone': '',
    #    'userIdentityNo': '',
    #}
    #openId = ''

    gym_time = 17

    s = requests.Session()
    header = {"User-Agent": "Mozilla/5.0 (Linux; Android 10;  AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/66.0.3359.126 MQQBrowser/6.2 TBS/045136 Mobile Safari/537.36 wxwork/3.0.16 MicroMessenger/7.0.1 NetType/WIFI Language/zh",}
    s.headers.update(header)

    order_time = {
        "12": {"minDate": "12:00", "maxDate": "14:00", "strategy": "1000000175"},
        "14": {"minDate": "14:30", "maxDate": "16:30", "strategy": "1000000176"},
        "17": {"minDate": "17:00", "maxDate": "19:00", "strategy": "1000000174"}
    }
    date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    time_detail = order_time.get(str(gym_time))

    #flag = is_gym_order(date, time_detail.get("minDate"), time_detail.get("maxDate"))
    flag = True

    if flag:
        n = 0
        while n < 10:
            r = gym_order(date, time_detail, user_info, open_id, s)
            n += 1
            print("times", n)
            if r == None:
                time.sleep(2)
                pass
            elif r['Code'] == '100000':
                send_message(server_key, str(gym_time) + "预约成功" + r['Code'], r)
                print("预约成功")   
                print("code:", r['Code'])
                break
            elif r['Code'] == '100099': 
                send_message(server_key, str(gym_time) + "预约失败" + r['Code'], r)
                print("预约失败")
                print("code:", r['Code'])
                break
            elif r['Code'] == '110000': 
                print("预约失败, 预约时间错误")
                print("code:", r['Code'])
                break
            else:
                print("预约失败")
                print(r)
    else:
        send_message(server_key, str(gym_time) + "不可预约", flag)
        print("不可预约")
