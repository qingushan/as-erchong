from ascript.android.screen import FindColors
from ascript.android.screen import Colors
from ascript.android.screen import Ocr
from ascript.android.system import R
from ascript.android.screen import OcrX


from ...res.task.BaseGame import BaseGame
from ...res.assets.color import mijin_color, common_color

import time
import re


class BaseFind(BaseGame):
    def __init__(self):
        super().__init__()

    def find_color(self, colors, rect=None, space=5, ori=2, diff=0.9):
        return FindColors.find(colors=colors, rect=rect, space=space, ori=ori, diff=diff)

    def findall_color(self, colors, rect=None, space=5, ori=2, diff=0.9):
        return FindColors.find_all(colors=colors, rect=rect, space=space, ori=ori, diff=diff)

    def ocr(self, rect=None, pattern=None, bitmap=None, confidence=0.1):
        res = Ocr.mlkitocr_v2(rect=rect, pattern=pattern, bitmap=bitmap)
        return res

    def ocrx(self,rect=None,region=0.9):
        # 点阵识别
        res = OcrX.find_all(R.res("font.t"),rect=rect,region=region)
        return res

    def ocrx_in_text(self,pattern,rect=None,region=0.9):
        # 点阵识别是否匹配某个字符串(正则)
        res = self.ocrx(rect=rect,region=region)
        if res:
            if re.findall(pattern,res):
                return True
        
        return False

    def is_text_re_in_ocr(self,rect=None, pattern=None, bitmap=None, confidence=0.1):
        # ocr结果是否满足正则表达式
        result = []
        res = Ocr.mlkitocr_v2(rect=rect, bitmap=bitmap)
        if res:
            for r in res:
                if (re.findall(re.compile(pattern), r.text)):
                    result.append(r)
                    # result = True
                    break

        return result
                
    def await_until_color(self, color_dict, color_name, time_out=10):
        # 等待某个颜色出现
        start_time = time.time()

        while 1:
            if time.time() - start_time > time_out:
                return False

            res = self.find_my_color(color_dict=color_dict,color_name=color_name)
            if res:
                return res

            time.sleep(0.1)
        
    def await_until_ocr(self, rect=None, pattern=None, bitmap=None, confidence=0.1, time_out=10):
        # ocr等待某个文字出现
        start_time = time.time()

        while 1:
            if time.time() - start_time > time_out:
                return False

            res = self.is_text_re_in_ocr(rect=rect, pattern=pattern, bitmap=bitmap, confidence=confidence)
            # res = self.ocr(rect=rect, pattern=pattern, bitmap=bitmap, confidence=confidence)
            if res:
                return res

            time.sleep(0.1)

    def huagong_find_enemy(self):
        # 花弓范围内是否有敌人
        res = Colors.count("#F0252A-#0c0508|#FF1C1F|#FF1C20",rect=[420,138,859,583])
        if res >= 100:
            return True

        return False

    def skill_e_consume_0(self):
        # 小技能消耗是否为0(夫人)
        res = self.find_color(common_color["小技能消耗为0"]["colors"],rect=common_color["小技能消耗为0"]["rect"])
        if res:
            return True
        else:
            return False

    def find_my_color(self,color_dict,color_name):
        # 根据传入的字典查找对应的颜色
        colors = color_dict[color_name]['colors']
        rect = color_dict[color_name]['rect']
        diff = color_dict[color_name]['diff']
        res = self.find_color(colors=colors,rect=rect,diff=diff)
        return res

    def find_my_colors(self,color_dict,color_name):
        # 根据传入的字典查找所有对应的颜色
        colors = color_dict[color_name]['colors']
        rect = color_dict[color_name]['rect']
        diff = color_dict[color_name]['diff']
        res = self.findall_color(colors=colors,rect=rect,diff=diff)
        return res

    def findall_my_color(self,color_dict,color_name):
        # 根据传入的字典查找对应的颜色
        colors = color_dict[color_name]['colors']
        rect = color_dict[color_name]['rect']
        diff = color_dict[color_name]['diff']
        res = self.findall_color(colors=colors,rect=rect,diff=diff)
        return res

    def skill_q_mp_is_ok(self):
        # 蓝量是否可以释放大招
        n = Colors.count("#D41C42-#410216",rect=[924,642,962,662],sim=0.9)
        if n >= 10:
            return False
        else:
            return True

    def skill_e_mp_is_ok(self):
        # 蓝量是否可以释放小技能
        n = Colors.count("#D41C42-#410216",rect=[894,645,914,661],sim=0.9)
        if n >= 10:
            return False
        else:
            return True


