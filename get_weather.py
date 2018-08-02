#! /bin/env python
# -*- coding: utf-8 -*-
"""
查询实时天气
"""

import re
import os
import sys
import json
import jieba
import datetime
from urllib import request
# sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# import city

os.chdir(os.path.dirname(os.path.realpath(__file__)))

class weather_query():
    url = 'https://tianqi.so.com/weather/'
    # 包含天气日期星期的html代码段
    weather_week = '<ul class="weather-columns"><li>([\s\S]*?)</li'
    # 日期与星期
    week = '<!-- ([\S\s]*?) -->'
    # 日期与星期
    dataaa = '-->([\s\S]*?)</div>'
    # 包含天气的代码段
    weather = r'<div class="weather-icon weather-icon-([\s\S]*?)\n'
    temperature = r'\n  </div><div>([\s\S]*?)</div><div class="aqi-label'

    # 包含指数的html的代码段
    index_data = r'<div class="tab-pane"([\S\s]*?)</div></div></div>'
    # 指数
    index_index = '<div class="tip-title tip-icon-([\S\s]*?)">'
    # 建议
    index_sugge = '<div class="tip-cont" title="([\s\S]*?)"'

    # 城市名称
    city_n = ""

    # 模拟http请求（私有方法）
    def __get_htmls(self, codes):
        urll = str(self.url + codes)
        ht = request.urlopen(urll)
        html = ht.read()
        html = str(html, encoding='utf-8')

        return html

    def __analyze(self, ff, html):
        # 天气
        if ff == 1:
            weather_weeks = re.findall(self.weather_week, html)
        # 指数
        else:
            weather_weeks = re.findall(self.index_data, html)

        return weather_weeks

    # 查询近期十五天之内的天气
    def __analyze_weather(self, weather_weeks):

        star_lists = []

        for we in weather_weeks:
            data_l = re.findall(self.dataaa, we)  # 分割星期，日期
            weather_l = re.findall(self.weather, we)  # 天气
            temp = re.findall(self.temperature, we) # 温度
            wind = we.split("<div>")[-1].strip("</div>")

            data_ll = data_l[0].split()
            week1 = data_ll[0]  # 星期
            data1 = data_ll[1]  # 日期
            weat = weather_l[0].split()
            weather_l = weat[1]  # 天气
            weather_all = weather_l + "," + temp[0] + "," + wind

            star_list = {'week': week1, "data": data1, "weather": weather_all}
            star_lists.append(star_list)

        return star_lists

    def __analyze_indexs(self, index_code):

        star_indexs = []

        for ind in index_code:
            indexs = re.findall(self.index_index, ind)
            sugges = re.findall(self.index_sugge, ind)

            for i in (range(0, len(indexs) - 1)):
                res_index = indexs[i].split('"')
                star_index = {'index': res_index[2], 'sugges': sugges[i]}
                star_indexs.append(star_index)

        return star_indexs

    def __show_weather(self, star_lists):
        ret_str = ""
        ret_str += "***************** %s最近的天气如下：*************\n\n" % self.city_n
        for re in star_lists:
            ret_str += "星期：" + re['week'] + "    日期：" + re['data'] + "   天气：" + re['weather'] + "\n"
            # print(rs)
        return ret_str

    def __show_index(self, star_indexs):
        print("*****************  两天指数及建议： ****************\n")
        print("\n\n*****************  今天建议如下  *****************\n\n")
        l = 0
        for re in star_indexs:
            l = l + 1
            fg = re['index'].split("：")

            if fg[0] == "过敏指数":
                if l > 1:
                    print("\n\n*****************  明天建议如下  *****************\n\n")
            print(re['index'] + "\t         建议：" + re['sugges'])

    def __city_num(self, city_name):
        if "市" in str(city_name):
            city_name = str(city_name).strip("市")
        code = -1
        try:
            with open("./city.json", 'r', encoding="utf-8") as c:
                dic = json.load(c)
                code = dic[str(city_name)]
                # print(dic)
        except:
            print("这个城市没有查不到...")
        self.city_n = city_name
        # print("您查询的是" + city_name + "城市代码为：" + code)
        return code

    def go(self, city_name, date=""):
        """
        :param city_name:
        :param week: 今天，明天，下面是星期
        :param data: 日期，格式07-09
        :return:
        """
        codes = self.__city_num(city_name)
        if codes != -1:
            html = self.__get_htmls(codes)

            # 查询天气
            weather_weeks = self.__analyze(1, html)
            star_lists = self.__analyze_weather(weather_weeks)
            flag = 0
            if date == "999":
                return self.__show_weather(star_lists)
            for ret in star_lists:
                # if date == ret["week"] or date == ret["data"]:
                if date == ret["data"][1:-1]:
                    flag = 1
                    if "雨" in ret["weather"]:
                        # print("天气：" + ret["weather"] + ",请记得带伞哦")
                        return "天气：" + ret["weather"] + ",请记得带伞哦"
                    else:
                        # print("天气：" + ret["weather"] + ",美好的一天从现在开始")
                        return "天气：" + ret["weather"] + ",美好的一天从现在开始"
                    break
            if flag == 0:
                # print("抱歉,您查找的天气信息暂时没有哦~")
                return "抱歉,您查找的天气信息暂时没有哦~"
        else:
            return "这个城市没有查不到..."
            # 查询指数
            # indexs = self.__analyze(2, html)
            # star_indexs = self.__analyze_indexs(indexs)

            # 展示天气
            # self.__show_weather(star_lists)

            # 展示指数
            # self.__show_index(star_indexs)

    def match_rule(self, input_str):
        """
        规则匹配天气请求文本
        :param input_str:
        :return:
        """
        month = ""
        exc_day = ""
        if "月" in input_str and ("日" in input_str or "号" in input_str):
            if "月" in input_str:
                month = input_str[0:input_str.index("月")]
                if len(month) < 2:
                    month = "0" + month
            if "日" in input_str:
                exc_day = input_str[input_str.index("月")+1:input_str.index("日")]
                if len(exc_day) < 2:
                    exc_day = "0" + exc_day
            if "号" in input_str:
                exc_day = input_str[input_str.index("月")+1:input_str.index("号")]
                if len(exc_day) < 2:
                    exc_day = "0" + exc_day
        date = month + "-" + exc_day
        city_name = ""
        today = datetime.date.today()
        weekday_num = today.isoweekday()
        deltaday_1 = datetime.timedelta(days=1)
        deltaday_2 = datetime.timedelta(days=2)
        deltaday_3 = datetime.timedelta(days=3)
        ISOFORMAT = '%m-%d'

        new_input = input_str.replace("星期", "周").replace("礼拜", "周").replace("本周", "周")
        jieba.load_userdict("./hainan_words.txt")
        seg = jieba.cut(new_input)
        seg_list = []
        tmp = "/".join(seg)
        for i in tmp.split('/'):
            seg_list.append(i)
        with open("./city.json", 'r', encoding="utf-8") as c:
            dic = json.load(c)
        with open("./region.json", 'r', encoding="utf-8") as r:
            area_dic = json.load(r)
        tmp_day = -99
        for item in seg_list:
            if "周" in item:
                if "一" in item:
                    tmp_day = 1 - weekday_num
                if "二" in item:
                    tmp_day = 2 - weekday_num
                if "三" in item:
                    tmp_day = 3 - weekday_num
                if "四" in item:
                    tmp_day = 4 - weekday_num
                if "五" in item:
                    tmp_day = 5 - weekday_num
                if "六" in item:
                    tmp_day = 6 - weekday_num
                if "日" in item or "天" in item or "末" in item:
                    tmp_day = 7 - weekday_num
                if "下" in item:
                    tmp_day += 7
                next_day = datetime.timedelta(days=tmp_day)
                to_next = today + next_day
                date = to_next.strftime(ISOFORMAT)
            elif "今天" in item:
                date = today.strftime(ISOFORMAT)
            elif "明天" in item:
                to1 = today + deltaday_1
                date = to1.strftime(ISOFORMAT)
            elif "后天" in item:
                to2 = today + deltaday_2
                date = to2.strftime(ISOFORMAT)
            elif "大后天" in item:
                to3 = today + deltaday_3
                date = to3.strftime(ISOFORMAT)
            elif item in area_dic.keys():
                city_tmp = area_dic[item]
                if city_tmp.strip("市") in dic.keys():
                    city_name = city_tmp
            elif item.strip("市") in dic.keys():
                city_name = item
        if "最近" in input_str or "几天" in input_str or "一周" in input_str:
            date = "999"
        return date, city_name


if __name__ == "__main__":
    wq = weather_query()
    # wq.go("哈密", "明天")
    # wq.go("北京市", "明天")
    # wq.match_rule("明天海口的天气？")
    # wq.match_rule("下周一定安天气如何？") # 歧义句

    # date, city_name = wq.match_rule("下礼拜六海口市的天气？")
    # date, city_name = wq.match_rule("下周一海口市的天气？")
    # date, city_name = wq.match_rule("后天海口的天气？")
    # date, city_name = wq.match_rule("7月15号海口的天气？")
    # 天气，气温，风速，风向，温度
    date, city_name = wq.match_rule("明天三亚的气温？")
    # print(date, city_name)
    info = wq.go(city_name, date)
    print(info)
    # print(str(sys.argv[1]) + ": " + str(sys.argv[2]))
