from ...res.task.BaseTask import BaseTask
from ...res.assets.color import *

from ascript.android import system

import re


class AutoLMYYTask(BaseTask):
    # 联袂演绎
    def __init__(self, uiconfig=None):
        super().__init__()

        self.uiconfig = uiconfig

        self.task_name = '联袂演绎'

        self.my_level_count = 0  # 当前已参加关卡数量

        self.box_count = 0      # 获取奖励箱子数量

        self.now_boss = ""      # 当前boss

        # 筛选打什么
        self.select_config = {
            "奖励":[],
            "等级":[],
            "倍率":[]
        }

        self.level_max_count = 0  # 副本执行次数

        self.level_finish_count = 0  # 探索完成次数，不论成功失败
        self.level_ok_count = 0  # 探索成功次数
        self.level_faile_count = 0  # 探索失败次数

        self.set_skill_config()

        # 关卡点击位置
        self.level_click_pos = {
            "第一关": (1188, 170),
            "第二关": (1189, 285),
            "第三关": (1187, 398),
            "第四关": (1190, 512),
            "第五关": (1187, 608)
        }

    def set_skill_config(self):
        # 初始化技能配置
        print(f"追踪boss方式：{self.uiconfig['lmyy_trace_boss']}")
        self.role_skill_util.init_config(
            self.uiconfig.get('lmyy_role', '0'),
            {
                "lmyy_trace_boss": self.uiconfig.get('lmyy_trace_boss', '0')
            }
        )

    def init_task(self):
        # 初始化
        self.level_max_count = 99999

        # 筛选条件设置
        if self.uiconfig['lmyy_select_mod_f'] == 'on':
            self.select_config["奖励"].append("风箱子")

        if self.uiconfig['lmyy_select_mod_h'] == 'on':
            self.select_config["奖励"].append("火箱子")

        if self.uiconfig['lmyy_select_mod_l'] == 'on':
            self.select_config["奖励"].append("雷箱子")

        if self.uiconfig['lmyy_select_mod_s'] == 'on':
            self.select_config["奖励"].append("水箱子")

        if self.uiconfig['lmyy_select_mod_g'] == 'on':
            self.select_config["奖励"].append("光箱子")

        if self.uiconfig['lmyy_select_mod_a'] == 'on':
            self.select_config["奖励"].append("暗箱子")

        if self.uiconfig['lmyy_select_grade_50'] == 'on':
            self.select_config["等级"].append("50")

        if self.uiconfig['lmyy_select_grade_70'] == 'on':
            self.select_config["等级"].append("70")

        if self.uiconfig['lmyy_select_grade_90'] == 'on':
            self.select_config["等级"].append("90")

        if self.uiconfig['lmyy_select_grade_110'] == 'on':
            self.select_config["等级"].append("110")

        if self.uiconfig['lmyy_select_scale_100'] == 'on':
            self.select_config["倍率"].append("100%")

        if self.uiconfig['lmyy_select_scale_200'] == 'on':
            self.select_config["倍率"].append("200%")

        if self.uiconfig['lmyy_select_scale_800'] == 'on':
            self.select_config["倍率"].append("800%")

        if self.uiconfig['lmyy_select_scale_2000'] == 'on':
            self.select_config["倍率"].append("2000%")

        print(f"筛选配置：\n{self.select_config}")

    def go_to_level(self):
        # 前往副本
        print(f"开始前往---{self.task_name}")
        self.click_color_to_color(common_color, "角色血条-绿色", common_color, "主界面菜单展示", x=38, y=30)
        self.sleep(1)
        self.click_color_to_color(common_color, "主界面菜单展示", common_color, "左上角红色退出", x=339, y=239)
        self.sleep(2)
        res = None
        for i in range(3):
            for i in range(5):
                res = self.is_text_re_in_ocr(rect=[5,77,267,638], pattern="(演|联|绎)")
                if res:
                    break
                self.sleep(0.5)
            if res:
                break
            else:
                self.slide(98, 533, 106, 113, dur=500)
                self.sleep(4)
        if not res:
            print(f"没有找到--{self.task_name}，退出")
            self.click_color_to_color(common_color, "左上角红色退出", common_color, "主界面菜单展示", x=40, y=32)
            self.sleep(1)
            for i in range(3):
                self.click(634, 666)

            res = self.find_my_color(common_color, "角色血条-绿色")
            if res:
                print("成功返回主界面")
            else:
                print("返回主界面失败")

            return False

        x = res[0].x
        y = res[0].y

        # self.click_color_to_color(common_color, "左上角红色退出", lmyy_color, "联袂演绎-前往", x=x, y=y)
        self.click_until_ocr(x=x, y=y, rect=[1052,148,1254,198], pattern="演")
        self.sleep(1)
        

        self.click_color_to_color(lmyy_color, "联袂演绎-前往", lmyy_color, "联袂演绎-主页面", x=1073, y=680)
        self.sleep(2)
        print(f"成功进入---{self.task_name}")
        return True

    def get_box_count(self):
        # 获取当前箱子数量
        res = self.ocr(rect=[405,391,941,438])
        if res:
            for r in res:
                text = r.text
                print(text)
                result = re.findall(r"\d+", text)
                print(result)
                if len(result) > 0:
                    self.box_count += int(result[0])
                    print(f"获得箱子数量：{int(result[0])}，当前总箱子数量：{self.box_count}")
                    self.refresh_log()

    def check_my_level_count(self):
        # 检查当前已参加关卡数量
        self.click(48, 188)
        self.sleep(3)

        # 判断是否可以领取奖励
        res = self.is_text_re_in_ocr(rect=[1025,628,1275,694],pattern="[全部领取]+")
        if res:
            print("有奖励可以领取")
            self.click(1155,654)
            self.sleep(3)
            self.get_box_count()
            self.click_until_ocr(490,675,rect=[84,632,237,696], pattern="筛选")
            self.sleep(1)
            # 点击大厅再返回，刷新
            self.click(48,117)
            self.sleep(3)
            self.click(48, 188)
            self.sleep(3)

        res = self.ocr(rect=[292, 12, 498, 54])
        if res:
            for r in res:
                text = r.text
                print(text)
                result = re.findall(r"\d", text)
                print(result)
                if len(result) > 0:
                    self.my_level_count = int(result[0])
                    break

        print(f"当前已参加关卡数量：{self.my_level_count}")

    def open_available_joined_level(self):
        # 检查自己已参加关卡中是否有可打副本，成功时停留在关卡详情页
        status = False

        if self.my_level_count == 0:
            print("当前关卡数量0")
            return status

        index_ = 1
        for key, xy in self.level_click_pos.items():
            print(key)
            if index_ > self.my_level_count:
                print("所有关卡已确认完毕")
                break
            self.click_until_ocr(x=xy[0], y=xy[1], rect=[44, 418, 429, 548], pattern="献度")
            self.sleep(1)
            print("成功进入关卡")

            # 判断关卡是否可打
            res = self.await_until_ocr(rect=[407, 540, 867, 680], pattern="演绎", time_out=3)
            if res:
                print("当前关卡可战斗！")
                status = True
                break
            else:
                print("当前关卡冷却中，继续寻找")
                self.click_until_ocr(x=48, y=32, rect=[84,632,237,696], pattern="筛选")
                self.sleep(1)

            index_ += 1

        return status

    def apply_hall_filter(self):
        # 应用大厅筛选条件
        print("开始筛选")
        res = self.click_until_ocr(x=113, y=663, rect=[701,544,876,590], pattern="确认")
        self.sleep(1)

        # 向上滑动
        self.slide(958,324,949,486,dur=500)
        self.sleep(2)

        # 清除
        self.click(497,564,after_sleep=1)

        # 筛选箱子
        self.slide(1014,237, 778,233, dur=500)
        self.sleep(1)

        if "风箱子" in self.select_config["奖励"]:
            self.click(624,291,after_sleep=0.5)
        
        if "火箱子" in self.select_config["奖励"]:
            self.click(704,291,after_sleep=0.5)

        if "雷箱子" in self.select_config["奖励"]:
            self.click(786,291,after_sleep=0.5)

        if "水箱子" in self.select_config["奖励"]:
            self.click(865,291,after_sleep=0.5)

        if "光箱子" in self.select_config["奖励"]:
            self.click(946,292,after_sleep=0.5)

        if "暗箱子" in self.select_config["奖励"]:
            self.click(1026,291,after_sleep=0.5)

        # 筛选等级
        if "50" in self.select_config["等级"]:
            self.click(242,388,after_sleep=0.5)

        if "70" in self.select_config["等级"]:
            self.click(526,388,after_sleep=0.5)

        if "90" in self.select_config["等级"]:
            self.click(809,388,after_sleep=0.5)

        if "110" in self.select_config["等级"]:
            self.click(242,449,after_sleep=0.5)

        # 筛选倍率
        self.slide(634,477, 654,186, dur=500)
        self.sleep(1)

        if "100%" in self.select_config["倍率"]:
            self.click(240,424,after_sleep=0.5)

        if "200%" in self.select_config["倍率"]:
            self.click(526,424,after_sleep=0.5)

        if "800%" in self.select_config["倍率"]:
            self.click(810,424,after_sleep=0.5)

        if "2000%" in self.select_config["倍率"]:
            self.click(240,483,after_sleep=0.5)

        self.sleep(1)

        # 确认
        self.click(781,564)
        self.sleep(1)

    def fast_enter_opened_level(self):
        # 快速进入当前打开的关卡详情页
        res = self.await_until_click_ocr(rect=[407, 540, 867, 680], pattern="(参与|演绎)", time_out=5)
        if res:
            print("当前关卡可战斗！")
        else:
            print("关卡异常，大厅进入副本不可打")
            return False

        res = self.await_color(common_color, "角色血条-绿色", out_time=10)
        if not res:
            print("检查是否还在关卡页面，可能满人了")
            res = self.is_text_re_in_ocr(rect=[407, 540, 867, 680], pattern="(前往|参与)")
            if res:
                print("房间满人，退出")
                self.click_until_ocr(x=48, y=32, rect=[84,632,237,696], pattern="[筛选舞台]+")
                self.sleep(1)
                return False

        res = self.await_color(common_color, "角色血条-绿色", out_time=50)
        if not res:
            print("进入副本异常")
            self.click_until_ocr(x=48, y=32, rect=[84,632,237,696], pattern="[筛选舞台]+")
            self.sleep(1)
            return False

        # 重置技能时间
        self.role_skill_util.set_role_skill_config()

        print("成功进入副本")
        return True

    def find_and_enter_hall_level_fast(self):
        # 大厅快速找房，找到房间后立即尝试进入副本
        self.apply_hall_filter()

        while 1:
            self.click(976,655,after_sleep=0.5)

            res = None
            for i in range(3):
                res = self.is_text_re_in_ocr(rect=[532,315,847,445], pattern="无符合条件")
                if res:
                    break
                self.sleep(0.1)

            if res:
                # 刷新
                # print("无房间，刷新")
                # self.click(976,655,after_sleep=1)
                pass
            else:
                # 有房间
                # 点击第一个
                res = self.click_until_ocr(x=self.level_click_pos["第一关"][0], y=self.level_click_pos["第一关"][1], rect=[44, 418, 429, 548], pattern="献度")
                if not res:
                    print("大厅进入副本失败")
                    continue

                print("成功进入关卡")

                if self.fast_enter_opened_level():
                    return True
                else:
                    # 检查是否成功返回主界面
                    if self.is_text_re_in_ocr(rect=[44, 418, 429, 548], pattern="献度"):
                        self.click_until_ocr(x=48, y=32, rect=[84, 632, 237, 696], pattern="筛选")
                        self.sleep(1)

    def from_dt_select_level(self):
        # 切到大厅并快速找房进本
        self.click(48,117)
        self.sleep(3)

        # 点击协会
        # self.click(604,82)
        # self.sleep(3)

        return self.find_and_enter_hall_level_fast()

        # 点击第一个
        # res = self.click_until_ocr(x=self.level_click_pos["第一关"][0], y=self.level_click_pos["第一关"][1], rect=[44, 418, 429, 548], pattern="献度")
        # if not res:
        #     print("大厅进入副本失败")
        #     return False

        # self.sleep(1)
        # print("成功进入关卡")

        # 判断关卡是否可打
        # res = self.await_until_ocr(rect=[407, 540, 867, 680], pattern="演绎", time_out=5)
        # if res:
        #     print("当前关卡可战斗！")
        #     return True
        # else:
        #     print("关卡异常，大厅进入副本不可打")
        #     return False

    def go_in_level(self):
        # 进入副本
        res = self.await_until_click_ocr(rect=[407, 540, 867, 680], pattern="(前往|参与)", time_out=30)
        if not res:
            print("进入副本失败")
            return False

        res = self.await_color(common_color, "角色血条-绿色", out_time=10)
        if not res:
            print("检查是否还在关卡页面，可能满人了")
            res = self.is_text_re_in_ocr(rect=[407, 540, 867, 680], pattern="(前往|参与)")
            if res:
                print("房间满人，退出")
                self.click_until_ocr(x=48, y=32, rect=[84,632,237,696], pattern="筛选")
                self.sleep(1)
                return False

        res = self.await_color(common_color, "角色血条-绿色", out_time=50)
        if not res:
            print("进入副本异常")
            self.click_until_ocr(x=48, y=32, rect=[84,632,237,696], pattern="筛选")
            self.sleep(1)
            return False

        # 重置技能时间
        self.role_skill_util.set_role_skill_config()

        self.now_boss = ""  # 重置boss

        print("成功进入副本")
        return True

    def quit_level(self):
        # 退出当前副本
        print("退出当前副本")
        res = self.find_my_color(ze_weapon_color, "队友-副本结束")
        if res:
            print("结束界面")
            self.click_color_to_color(ze_weapon_color, "队友-副本结束", common_color, "副本退出-再次进行", x=392, y=526,
                                      out_time=60), 675
            self.sleep(3)
            return True
        self.click_color_to_color(common_color, "角色血条-绿色", common_color, "地图esc界面", x=40, y=29)
        self.sleep(1)
        self.click_color_to_color(common_color, "地图esc界面", common_color, "退出委托-确定", x=1189, y=639)
        self.sleep(1)
        self.click_color_to_color(common_color, "退出委托-确定", common_color, "副本退出-再次进行", x=777, y=412,
                                  out_time=60)
        self.sleep(1)
        print("退出成功")

    def level_exit(self):
        # 副本结束，返回主界面
        res = self.find_my_color(ze_weapon_color, "队友-副本结束")
        if res:
            self.click_color_to_color(ze_weapon_color, "队友-副本结束", common_color, "角色血条-绿色", x=1141, y=672,
                                      out_time=60)
            self.sleep(1)

        for i in range(3):
            self.click(634, 666)

        res = self.find_my_color(common_color, "角色血条-绿色")
        if res:
            print("成功返回主界面")
        else:
            print("返回主界面失败")

    def get_boss(self):
        """
        识别当前BOSS
        """
        res = self.ocr(rect=[545,10,749,49])
        if res:
            for r in res:
                text = r.text
                result = re.findall("雪国", text)
                if len(result) > 0:
                    if self.now_boss != "雪国的野兽":
                        self.now_boss = "雪国的野兽"
                        print(f"BOSS切换，当前BOSS：{self.now_boss}")
                    return True

                result = re.findall("炼火", text)
                if len(result) > 0:
                    if self.now_boss != "炼火的典狱长":
                        self.now_boss = "炼火的典狱长"
                        print(f"BOSS切换，当前BOSS：{self.now_boss}")
                    return True

                result = re.findall("历战者", text)
                if len(result) > 0:
                    if self.now_boss != "历战者":
                        self.now_boss = "历战者"
                        print(f"BOSS切换，当前BOSS：{self.now_boss}")
                    return True

                result = re.findall("审判官", text)
                if len(result) > 0:
                    if self.now_boss != "蒙恩的审判官":
                        self.now_boss = "蒙恩的审判官"
                        print(f"BOSS切换，当前BOSS：{self.now_boss}")
                    return True

                result = re.findall("哈洛吉", text)
                if len(result) > 0:
                    if self.now_boss != "欺惑者哈洛吉":
                        self.now_boss = "欺惑者哈洛吉"
                        print(f"BOSS切换，当前BOSS：{self.now_boss}")
                    return True

                result = re.findall("西比尔", text)
                if len(result) > 0:
                    if self.now_boss != "西比尔":
                        self.now_boss = "西比尔"
                        print(f"BOSS切换，当前BOSS：{self.now_boss}")
                    return True

                result = re.findall("巨噬者", text)
                if len(result) > 0:
                    if self.now_boss != "巨噬者":
                        self.now_boss = "巨噬者"
                        print(f"BOSS切换，当前BOSS：{self.now_boss}")
                    return True

                result = re.findall("苦修士", text)
                if len(result) > 0:
                    if self.now_boss != "蒙恩的苦修士":
                        self.now_boss = "蒙恩的苦修士"
                        print(f"BOSS切换，当前BOSS：{self.now_boss}")
                    return True

                result = re.findall("生者", text)
                if len(result) > 0:
                    if self.now_boss != "蜕生者":
                        self.now_boss = "蜕生者"
                        print(f"BOSS切换，当前BOSS：{self.now_boss}")
                    return True

    def combat(self):
        # 战斗
        print("开始战斗")

        start_time = self.time()

        max_time = 60 * 9999

        while 1:
            res = self.is_text_re_in_ocr(rect=[531,614,754,658],pattern="离开")
            if res:
                print("战斗完成")
                self.click_until_ocr(x=637, y=635, rect=[84, 632, 237, 696], pattern="筛选",time_out=60)
                self.sleep(1)
                return True

            if self.time() - start_time > max_time:
                return False

            # 识别BOSS
            self.get_boss()

            # 释放技能
            self.role_skill_util.combat()

            self.sleep(0.1)

    def refresh_log(self):
        # 刷新日志
        text = f"当前任务：{self.task_name}  次数：{self.level_finish_count}/{self.level_max_count}  获取箱子数量：{self.box_count}"
        self.logui.change_log_text(text)

    def run(self):
        self.init_task()
        self.refresh_log()

        if self.uiconfig["lmyy_semi_automatic"] == "on":
            # 半自动
            self.go_in_level()
            self.combat()
            return True

        self.go_to_level()

        while 1:
            
            already_entered_level = False

            self.refresh_log()

            print(f"计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")

            if self.level_finish_count >= self.level_max_count:
                print(f"任务完成,计划执行 {self.level_max_count} 次,当前已完成 {self.level_finish_count} 次")
                self.level_exit()
                return True

            # 检查当前参加的关卡
            self.check_my_level_count()
            if self.my_level_count > 0:
                res = self.open_available_joined_level()
                if not res:
                    # 在已参加的战斗中没有找到可以战斗的
                    if self.my_level_count < 5:
                        # 前往大厅筛选
                        res = self.from_dt_select_level()
                        if res:
                            already_entered_level = True
                    else:
                        # 满了，等待
                        self.sleep(10)
                        continue
            else:
                # 前往大厅筛选
                res = self.from_dt_select_level()
                if not res:
                    continue

                already_entered_level = True

            # 大厅抢房成功时已经进入副本；已参加关卡只打开详情页，需要在这里统一入本
            if not already_entered_level:
                res = self.go_in_level()
                if not res:
                    continue

            res = self.combat()
            if res:
                self.level_finish_count += 1
                self.level_ok_count += 1
            else:
                self.level_finish_count += 1
                self.level_faile_count += 1
