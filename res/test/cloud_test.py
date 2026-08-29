from ...res.cloud_task.CloudAutoWeaponBreakTask import CloudAutoWeaponBreakTask

import time

def cloud_test(uiconfig):
    time.sleep(2)
    # 武器突破
    task = CloudAutoWeaponBreakTask(uiconfig)
    # task.test()
    task.run()