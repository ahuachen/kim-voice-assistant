# -*- coding: utf-8-*-
import logging
import requests
import json

WORDS = ["天气", "天气预报"]
PRIORITY = 0
logger = logging.getLogger()
from src.components.aliyun_fc.fc_client import FcClient
import xml.etree.ElementTree as ET
from src.config.profile import city, myname, ali_appcode
from src.config.path import APP_PATH
from src.plugins import is_all_word_segment_in_text,plugin_output


def handle(text, mic, profile, iot_client=None,chatbot=None):
    mic.say('正在查询天气...')

    fc_client = FcClient.get_instance()

    tree = ET.parse(APP_PATH + '/src/plugins/resources/weather-moji-citys.xml')  # 载入数据
    xml_root = tree.getroot()    #获取根节点
    elements = xml_root.findall('./city[@name="' + city + '"]')
    try:
        city_id = elements[0].get('id')
    except:
        mic.say('没有找到你设定的城市，请修改profile配置文件')
    finally:
        if city_id is None:
            mic.say('没有找到你设定的城市，请修改profile配置文件')

    data = {
        'host': 'http://freecityid.market.alicloudapi.com',
        'path': '/whapi/json/alicityweather/briefforecast3days',
        'method': 'POST',
        'appcode': ali_appcode,
        'payload': {
            'cityId': city_id
        },
        'bodys': {},
        'querys': ''
    }
    return_text = ''
    result_raw = json.loads(fc_client.call_function('aliyun_apimarket', payload=data).data.decode('utf8'))
    if result_raw['msg'] == 'success':
        return_text += myname+'为您播报，'+result_raw['data']['city']['name']+'天气预报，'
        if is_all_word_segment_in_text(['明天', '明日'], text):
            forecast = result_raw['data']['forecast'][1]
            day = '明天'
        elif is_all_word_segment_in_text(['后天', '明日'], text):
            forecast = result_raw['data']['forecast'][2]
            day = '后天'
        else:
            forecast = result_raw['data']['forecast'][0]
            day = '今天'
        forecast_output = return_text + day + forecast['conditionDay']+'，白天气温，'+forecast['tempDay'].replace('-', '零下')+\
                       '摄氏度，夜间气温，'+forecast['tempNight'].replace('-', '零下')+\
                       '摄氏度，'+forecast['windDirNight']+forecast['windLevelDay'].replace('-', '到')+'级'
        plugin_output(text, mic, forecast_output)
    else:
        mic.say('天气获取失败')


def is_valid(text):
    """
        Returns True if input is related to the time.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return is_all_word_segment_in_text(WORDS, text)

