import requests
import json
import base64
import time
import user
import re
from random import randint
from PIL import Image
from io import BytesIO
from datetime import datetime
from urllib.parse import unquote


class GetTicket:
    def __init__(self):
        self.user = user  #用户信息
        self.tickets = {}    #当天车票信息
        self._REPEAT_SUBMIT_TOKEN = ""    #全局重复提交令牌
        self._key_check_isChange = ""    #是否修改密钥
        self._allEncStr = ""    #加密串
        self.session = requests.Session()
    '''
    获取cookie
    '''
    def get_cookies(self):
        # 获取cookie
        url = "https://kyfw.12306.cn/otn/login/conf"
        self.session.get(url)
        url = "https://kyfw.12306.cn/otn/index12306/getLoginBanner"
        self.session.get(url)
        url = "https://kyfw.12306.cn/passport/web/auth/uamtk-static"
        self.session.get(url)

    '''
    获取登入二维码
    '''
    def get_qr_code(self):
        # 获取登入二维码
        url = "https://kyfw.12306.cn/passport/web/create-qr64"
        headers = {
            "Host": "kyfw.12306.cn",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Windows\"",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "Accept": "*/*",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?0",
            "Origin": "https://kyfw.12306.cn",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://kyfw.12306.cn/otn/leftTicket/init",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",

        }
        # 请求体数据
        data = {
            "appid": "otn",
            "_json_att": ""
        }
        response = self.session.post(url, data=data, headers=headers)
        # 检查响应
        if response.status_code == 200:
            try:
                # 解析 JSON 响应
                response_data = json.loads(response.text)
                # 提取二维码图片的 Base64 编码数据
                base64_image = response_data.get("image")
                if base64_image:
                    # 解码 Base64 字符串并生成图像
                    image_data = base64.b64decode(base64_image)
                    image = Image.open(BytesIO(image_data))
                    image.show()  # 显示图片
                    # 保存图片到本地
                    image.save("qr_code.png")
                    print("二维码已成功保存为 qr_code.png")
                    print("请使用手机扫描二维码登录 12306 网站")
                    return response_data.get("uuid")
            except Exception as e:
                print("获取二维码失败", e)

    '''
    检查二维码状态
    '''
    def check_qr_code(self, uuid):
        # 检查二维码状态
        url = "https://kyfw.12306.cn/passport/web/checkqr"
        headers = {'Host': 'kyfw.12306.cn',
                   'Connection': 'keep-alive',
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
                   'Accept': '*/*',
                   'Referer': 'https://kyfw.12306.cn/otn/resources/login.html',
                   }
        data = {
            "uuid": uuid,
            'appid': 'otn'
        }
        try_time = 0
        while True:
            # 发起 POST 请求，传递 cookies
            response = self.session.post(url, data=data, headers=headers)

            if response.status_code == 200:
                # 解析 JSON 数据
                response_data = response.json()
                print(response_data.get("result_message", "No result_message found"))

                # 检查扫码登录是否成功
                if response_data.get("result_message") == "扫码登录成功":
                    print("扫码登录成功")
                    break
                else:
                    print("扫码登录未成功，等待中...")
                    try_time += 1
                    if try_time > 10:
                        print("扫码登录失败，请重试")
                        break

                    time.sleep(1)  # 每秒重试一次
            else:
                print(f"请求失败，状态码: {response.status_code}")
                break  # 如果请求失败，退出循环

    '''
    获取登录令牌
    '''
    def get_login_token(self):
        # 获取登录令牌

        # 模拟登录
        url = "https://kyfw.12306.cn/login/userLogin"
        headers = {
            "Host": "kyfw.12306.cn",
            "Connection": "keep-alive",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
        }
        self.session.get(url, headers=headers)
        time.sleep(0.1)
        url = "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin"
        self.session.get(url, headers=headers)
        time.sleep(0.1)
        # 获取登录令牌
        url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
        data = {'appid': 'otn'}
        time.sleep(0.1)
        headers = {
            "Host": "kyfw.12306.cn",
            "Connection": "keep-alive",
            "Content-Length": "9",
            "sec-ch-ua-platform": '"Windows"',
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?0",
            "Origin": "https://kyfw.12306.cn",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
        }
        response = self.session.post(url, data=data, headers=headers)
        if response.status_code == 200:
            # 解析 JSON 数据
            response_data = response.json()
            if response_data.get("result_message") == "验证通过":
                print("第一步验证通过")
                newapptk = response_data.get("newapptk")
                url = "https://kyfw.12306.cn/otn/uamauthclient"
                headers = {
                    "Host": "kyfw.12306.cn",
                    "Connection": "keep-alive",
                    "Content-Length": "52",
                    "sec-ch-ua-platform": '"Windows"',
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
                    "Accept": "*/*",
                    "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "sec-ch-ua-mobile": "?0",
                    "Origin": "https://kyfw.12306.cn",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Dest": "empty",
                    "Accept-Encoding": "gzip, deflate, br, zstd",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
                }
                data = {
                    'tk': newapptk
                }
                time.sleep(0.1)
                response = self.session.post(url, data=data, headers=headers)
                if response.status_code == 200:
                    # 解析 JSON 数据
                    response_data = response.json()
                    if response_data.get("result_message") == "验证通过":
                        print("第二步验证通过，获取登录令牌成功")
                    else:
                        print("第二步验证失败，请重试")
                else:
                    print(f"第二步验证请求失败，状态码: {response.status_code}")
            else:
                print("第一步验证失败，请重试")
        else:
            print(f"第一步验证请求失败，状态码: {response.status_code}")
    '''
    登入请求
    '''
    def login(self):
        # 二维码登录
        uuid = self.get_qr_code()
        self.check_qr_code(uuid)
        time.sleep(0.05)  # 等待一秒，确保二维码图片已经保存到本地
        # 获取登录令牌
        self.get_login_token()


    '''
    检查登录状态
    '''
    def check_login_status(self):
        # 检查登录状态
        url = "https://kyfw.12306.cn/otn/login/checkUser"
        headers = {
            "Host": "kyfw.12306.cn",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Windows\"",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "Accept": "*/*",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?0",
            "Origin": "https://kyfw.12306.cn",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        }
        data = {
            "appid": "otn",
            "_json_att": ""
        }
        response = self.session.post(url, data=data, headers=headers)
        if response.status_code == 200:
            try:
                # 解析 JSON 响应
                response_data = json.loads(response.text)
                # print(response_data)
                if response_data['data']['flag']:
                    print("用户已登录")
                    return 1
                else:
                    print("用户未登录")
                    # 检查登入状态
                    return 0
                    # self.login()
                    # self.check_login_status()
            except ValueError:
                print("响应不是合法的 JSON 格式：", response.text)

        else:
            print(f"请求失败，状态码：{response.status_code}，响应内容：{response.text}")

    '''
    获取车票信息
    '''
    def get_ticket_info(self):
        # 获取车票信息
        url = f'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={self.user.train_date}&leftTicketDTO.from_station={self.user.from_station}&leftTicketDTO.to_station={self.user.to_station}&purpose_codes=ADULT'
        headers = {
            "Host": "kyfw.12306.cn",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        }
        response = self.session.get(url,headers=headers)
        # 检查响应状态码
        if response.status_code == 200:
            try:
                # 解析 JSON 数据
                data = response.json()

                # 检查返回数据是否有效
                if data.get("data") is None:
                    print("未获取到车票信息")
                    return None

                # 提取车票信息
                train_info_list = data["data"]["result"]
                # 遍历车票信息，提取必要数据
                for train_info in train_info_list:
                    info = train_info.split("|")
                    self.tickets[info[3]] = {
                        'all_trainname': info[2],
                        'from_station_name': info[6],  # 出发站
                        'to_station_name': info[7],  # 到达站
                        'start_time': info[8],  # 出发时间
                        'arrive_time': info[9],  # 到达时间
                        'seat_types': info[11],  # 座位类型
                        'left_ticket': info[12],  # 剩余票数
                        'train_location': info[15],  # 车次位置
                        'seat_discount_info': info[-3],  # 座位优惠信息
                        'secret_str': info[0]  # 加密的字符串
                    }
            except requests.exceptions.JSONDecodeError:
                print("解析返回内容失败，返回内容可能不是 JSON 格式")
                print("返回内容：", response.text)
                return None
        else:
            print(f"请求失败，状态码: {response.status_code}")

    '''
    生成 _uab_collina Cookie 值。
    '''
    @staticmethod   # 静态方法
    def generate_uab_collina():
        """
        生成 _uab_collina Cookie 值。
        结构：
        - 13位当前毫秒时间戳
        - 11位随机数字串
        """
        # 获取当前时间的毫秒时间戳
        timestamp_ms = int(time.time() * 1000)
        timestamp_str = str(timestamp_ms)
        # 生成11位随机数字串
        random_digits = ''.join([str(randint(0, 9)) for _ in range(11)])
        # 拼接成最终的 Cookie 值
        uab_collina = timestamp_str + random_digits
        return uab_collina

    '''
    创建订单
    '''
    def create_order(self, train):
        # 创建订单
        url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
        self.session.headers = {
            "Host": "kyfw.12306.cn",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "Windows",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?0",
            "Origin": "https://kyfw.12306.cn",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        }
        data = {
            'secretStr': unquote(self.tickets[train]['secret_str']),
            'train_date': user.train_date,
            'back_train_date': str(datetime.today().date()),
            'tour_flag': 'dc',  # dc 单程 wf 往返
            'purpose_codes': 'ADULT',  # 成人
            'query_from_station_name': user.start_city,  # 车站/城市信息字典[from_station]
            'query_to_station_name': user.end_city,  # 车站/城市信息字典[to_station]
            'bed_level_info': '',
            'seat_discount_info': self.tickets[train]['seat_discount_info'],
            'undefined': ''
        }
        # 更新cookies
        self.session.cookies.set('_jc_save_fromStation',
                            ''.join([f"%u{ord(c):04X}" for c in self.user.start_city + ","]) + self.user.from_station,
                                 domain='kyfw.12306.cn')
        self.session.cookies.set('_jc_save_toStation',
                            ''.join([f"%u{ord(c):04X}" for c in self.user.end_city + ","]) + self.user.from_station,
                                 domain='kyfw.12306.cn')
        self.session.cookies.set('_jc_save_fromDate', self.user.train_date, domain='kyfw.12306.cn')
        self.session.cookies.set('_jc_save_toDate', str(datetime.today().date()), domain='kyfw.12306.cn')
        self.session.cookies.set('jc_save_wfdc_flag', 'dc', domain='kyfw.12306.cn')
        self.session.cookies.set('guidesStatus', 'off', domain='kyfw.12306.cn')
        self.session.cookies.set('highContrastMode', 'defaltMode', domain='kyfw.12306.cn')
        self.session.cookies.set('ursorStatus', 'off', domain='kyfw.12306.cn')
        del self.session.cookies['_passport_session']
        del self.session.cookies['uamtk']
        del self.session.cookies['BIGipServerportal']
        uab_collina_value = self.generate_uab_collina()
        self.session.cookies.set('_uab_collina', uab_collina_value, domain='kyfw.12306.cn')
        response = self.session.post(url, data=data)
        if response.status_code == 200:
            if response.json().get("status"):
                print("创建订单成功！")
            else:
                print("创建订单失败！")
        else:
            print(f"请求失败，状态码: {response.status_code}")

    '''
    订单初始化
    跳转界面提取界面token和key_check_isChange
    '''
    def init_order(self):
        # 订单初始化
        url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        self.session.headers.update({
        "Host": "kyfw.12306.cn",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "Windows",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "sec-ch-ua-mobile": "?0",
        "Origin": "https://kyfw.12306.cn",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://kyfw.12306.cn/otn/confirmPassenger/initDc",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        })
        data = {
            '_json_att': ''
        }
        # 更新cookies
        uab_collina_value = self.generate_uab_collina()
        self.session.cookies.update({'_uab_collina': uab_collina_value})
        response = self.session.post(url, data=data)
        # print(response.text)
        if response.status_code == 200:
            try:
                self._REPEAT_SUBMIT_TOKEN = re.findall("var globalRepeatSubmitToken = '(.*?)'", response.text)[0]
                self._key_check_isChange = re.findall("'key_check_isChange':'(.*?)'", response.text)[0]
            except IndexError:
                print("提取数据失败！")
        else:
            print(f"请求失败，状态码: {response.status_code}")

    '''
    查询乘车人信息
    '''
    def check_passengers(self):
        # 查询乘车人信息
        url = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
        self.session.headers.update({
        "Host": "kyfw.12306.cn",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "Windows",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "sec-ch-ua-mobile": "?0",
        "Origin": "https://kyfw.12306.cn",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        })
        data = {
            "_json_att": "",
            'REPEAT_SUBMIT_TOKEN': self._REPEAT_SUBMIT_TOKEN
        }
        response = self.session.post(url, data=data)
        if response.status_code == 200:
            try:
                response = response.json()
                print("乘车人信息查询成功")

                self._allEncStr = response['data']['normal_passengers'][0]['allEncStr']
            except ValueError:
                print("响应不是合法的 JSON 格式：", response.text)
        else:
            print("乘车人信息查询失败！")
            print(f"请求失败，状态码：{response.status_code}，响应内容：{response.text}")
    '''
    检查订单信息
    '''
    def check_order_info(self):
        # 检查订单信息
        url = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
        data = {
            "cancel_flag": "2",  # 订单状态，0为取消，2为未取消
            "bed_level_order_num": "000000000000000000000000000000",  # 床位级别订单号
            "passengerTicketStr": f"{self.user.TICKET_CLASS},{self.user.GENDER},1,{self.user.NAME},1,{self.user.ID},{self.user.PHONE_NUMBER},N,{self._allEncStr}",
            # 乘客的票据信息，包含乘客的座位、身份证、票价等信息。
            "oldPassengerStr": f"{self.user.NAME},1,{self.user.ID},1_",  # 需要与 passengerTicketStr 保持一致
            "tour_flag": "dc",  # 票类型dc为单程票
            "whatsSelect": "1",
            "sessionId": "",
            "sig": "",
            "scene": "nc_login",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self._REPEAT_SUBMIT_TOKEN,
        }
        uab_collina_value = self.generate_uab_collina()
        self.session.cookies.update({'_uab_collina': uab_collina_value})
        response = self.session.post(url, data=data)
        if response.status_code == 200:
            if response.json().get("status"):
                print("查询乘车人信息成功")
            else:
                print(response.json().get("data"))
        else:
            print("查询乘车人信息失败！")
            print(f"请求失败，状态码：{response.status_code}，响应内容：{response.text}")

    '''
    提交订单
    '''
    def submit_order(self,train):
        # 提交订单
        url = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"
        self.session.headers.update({
            "Host": "kyfw.12306.cn",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Windows\"",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "sec-ch-ua": "\"Microsoft Edge\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-ch-ua-mobile": "?0",
            "Origin": "https://kyfw.12306.cn",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        })
        data = {
            "train_date": f"{datetime.strptime(user.train_date, "%Y-%m-%d").strftime("%a")} {self.user.month_dict[int(self.user.train_date[5:7])]} {self.user.train_date[-2:]} {self.user.train_date[:4]} 00:00:00 GMT+0800 (中国标准时间)",
            "train_no": self.tickets[train]["all_trainname"],
            "stationTrainCode": train,
            "seatType": self.user.TICKET_CLASS,
            "fromStationTelecode": self.user.from_station,
            "toStationTelecode": self.user.to_station,
            "leftTicket": self.tickets[train]["left_ticket"],
            "purpose_codes": "00",  # 购买车票的用途，00表示普通购票
            "train_location": self.tickets[train]['train_location'],
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self._REPEAT_SUBMIT_TOKEN
        }
        uab_collina_value = self.generate_uab_collina()
        self.session.cookies.update({'_uab_collina': uab_collina_value})
        response = self.session.post(url, data=data)
        if response.status_code == 200:
            print("提交订单成功！")
        else:
            print("提交订单失败！")
            print(f"请求失败，状态码：{response.status_code}，响应内容：{response.text}")

    '''
    确认订单
    '''
    def confirm_order(self, train):
        # 确认订单
        url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
        self.session.headers.update({
        "Host": "kyfw.12306.cn",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "Windows",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "sec-ch-ua-mobile": "?0",
        "Origin": "https://kyfw.12306.cn",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        })
        data = {
            'passengerTicketStr': f"{self.user.TICKET_CLASS},{self.user.GENDER},1,{self.user.NAME},1,{self.user.ID},{self.user.PHONE_NUMBER},N,{self._allEncStr}",
            'oldPassengerStr': f"{self.user.NAME},1,{self.user.ID},1_",
            'randCode': '',
            'purpose_codes': '00',
            'key_check_isChange': self._key_check_isChange,
            'leftTicketStr': self.tickets[train]["left_ticket"],
            'train_location': self.tickets[train]['train_location'],  # one_train[15]
            'choose_seats': '1'+self.user.choose_seats,  # # 选择坐席 ABCDEF 上中下铺 默认为空不选
            'seatDetailType': '000',  #
            'is_jy': 'N',  # 是否为境内预订 默认N
            'is_cj': 'Y',  # 是否为成人票 默认N
            'encryptedData': '',
            'whatsSelect': '1',
            'roomType': '00',
            'dwAll': 'N',  #
            '_json_att': '',
            'REPEAT_SUBMIT_TOKEN': self._REPEAT_SUBMIT_TOKEN  # 1.1.19获取
        }
        # print(data)
        uab_collina_value = self.generate_uab_collina()
        self.session.cookies.update({'_uab_collina': uab_collina_value})
        response = self.session.post(url, data=data)
        if response.status_code == 200:
            response = response.json()
            if response['data']["submitStatus"]:
                print("确认订单成功！")
            else:
                print("确认订单失败！")
        else:
            print(f"请求失败，状态码：{response.status_code}，响应内容：{response.text}")
    '''
    记录日志
    '''
    def base_log(self):
        # 记录日志
        url = "https://kyfw.12306.cn/otn/basedata/log"
        data = {'type': 'dc',
                '_json_att': "",
                'REPEAT_SUBMIT_TOKEN': self._REPEAT_SUBMIT_TOKEN
                }
        del self.session.cookies['_uab_collina']
        response = self.session.post(url, data=data)
        if response.status_code == 200:
            print("记录日志成功！")
        else:
            print("记录日志失败！")
            print(f"请求失败，状态码：{response.status_code}，响应内容：{response.text}")
    '''
    排队出票
    '''
    def queue_order(self):
        # 排队等待 返回waittime(下次发送重复请求所需要的等待时间) 重复发送请求直到获取 requestID 和 orderID
        # 当前时间戳（毫秒）
        random = str(int(time.time() * 1000))

        # 请求的 URL
        url = f"https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random={random}&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN={self._REPEAT_SUBMIT_TOKEN}"
        # print(url)
        self.session.headers.update({
            'Host': 'kyfw.12306.cn',
            'Connection': 'keep-alive',
            'sec-ch-ua-platform': '"Windows"',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
            })
        while True:
            response = self.session.get(url)
            # print(response.text)
            if response.status_code == 200:
                data = response.json()
                # 获取排队等待时间
                wait_time = data['data'].get('waitTime')
                # 获取订单ID
                order_id = data['data'].get('orderId')
                # 如果订单ID已生成，退出循环
                if order_id:
                    print("出票成功！请在10分钟内去12306客户端支付！")
                    return response.cookies, order_id
                # 如果订单ID为null，继续发送请求并等待相应的时间
                print("当前没有订单ID，继续排队...")
                if wait_time == 4:
                    time.sleep(2.95)  # 等待3秒后再次请求
                elif wait_time == -100:
                    time.sleep(1)  #等待1秒后再次请求
                elif wait_time == -2:
                    print("出票失败！")
                    return None
                order_id = self.queue_order()
                return order_id

            else:
                print(f"请求失败，状态码: {response.status_code}")
                break
    '''
    订票完整流程
    '''
    def run(self):
        # 获取车票信息
        self.get_ticket_info()
        try_time = 0
        max_try_time = 5
        while try_time < max_try_time:
            # 遍历车次
            for train in self.user.TRAIN_ID_LIST:
                # 创建订单
                self.create_order(train)
                # 订单初始化
                self.init_order()
                # 获取乘车人信息
                self.check_passengers()
                # 检查订单信息
                self.check_order_info()
                # 提交订单
                self.submit_order(train)
                # 确认订单
                self.confirm_order(train)
                # 记录日志
                self.base_log()
                # 排队出票
                order_id = self.queue_order()
                if order_id:
                    return 1
                else:
                    try_time += 1
        return 0





