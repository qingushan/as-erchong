from ascript.android.system import R
from ascript.android.ui import WebWindow
import json

def tunnel(k,v):
    print(k,v)
    if k =="close":
        print(v) # 用户点X关闭了窗口
    elif k =="submit":
        print(v) # 用户点击确定并回传了数据
        # resobj = json.loads(v)
        # print(resobj)

formw =  WebWindow(R.ui("form.html"),tunnel)
formw.height("70vh")
formw.show()