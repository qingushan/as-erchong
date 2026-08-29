/*
 * 表单静态配置集中放在这里。
 *
 * 这个文件只放“常量/映射”，不绑定事件，也不直接操作 DOM。
 * 新增任务类型、checkbox 回填字段、默认表单值时，优先改这里。
 *
 * 加载顺序要求：
 * - 必须在 form-cache.js、task-list.js、form-main.js 之前加载。
 */

// 表单默认值。首次启动或者缓存里缺少字段时，会用这里的值兜底。
var DEFAULT_FORM_DATA = {
    mijin_max_num: "10",
    mijin_grade: "40",
    mijin_role: "1",
    global_check_month_card: "on"
};

/*
 * checkbox 回填字段清单。
 *
 * Layui 的 form.val 回填 checkbox 时，如果缓存中某个字段是字符串 "off"，
 * 需要先转换为 false，否则可能出现未勾选状态无法正确恢复的问题。
 *
 * 注意：提交时不需要依赖这个列表。提交逻辑会扫描页面上所有 checkbox，
 * 自动把未勾选项补成 "off"。这里主要服务于“从缓存恢复 UI 状态”。
 */
var CHECKBOX_FIELDS = [
    'fish_map_bhc', 'fish_map_jjd', 'fish_map_xsd', 'fish_map_fxb', 'fish_map_bnc', 'fish_map_csy', 'fish_map_krg', 'fish_map_wms',
    'global_check_month_card', 'task_loop', 'global_timed_offline', 'global_check_game_is_offline',
    'mihan_level_type_quli', 'mihan_level_type_tanxian', 'mihan_level_type_esho', 'mijin_run_old', 'global_do_mosaic',
    'mihan_task_level_role', 'mihan_task_level_weapon',
    'mihan_task_level_mod', 'game_activity_name', 'game_activity_action_crouch', 'game_activity_e_saiqi', 'refresh_time_is_execute_mihan',
    'mod_activity_shr', 'daily_task_mod', 'daily_task_take_a_picture', 'daily_task_get_fishing_lure', 'daily_task_get_wjqc', 'daily_task_get_daily_award',
    'global_time_5_offline', 'role_tupo_capture_moling', 'game_activity_get_score', 'fish_map_djyw', 'fish_map_cxq', 'fish_map_ylx', 'wuqi_tupo_moling_run',
    'fish_insane', 'fish_map_bhcz', 'ze_weapon_semi_automatic', 'lmyy_select_money', 'lmyy_select_hd', 'lmyy_select_jjb', 'lmyy_select_role_exp',
    'lmyy_select_weapon_exp', 'lmyy_select_wtmhxs', 'lmyy_select_grade_50', 'lmyy_select_grade_70', 'lmyy_select_grade_90', 'lmyy_select_grade_110', 'lmyy_select_scale_100',
    'lmyy_select_scale_200', 'lmyy_select_scale_800', 'lmyy_select_scale_2000', 'lmyy_semi_automatic'
];

// 任务类型 -> 页面展示名称。任务列表渲染时使用，避免在 task-list.js 中写长 if/else。
var TASK_TYPE_NAME_MAP = {
    mijin: "迷津",
    daily_task: "日常任务",
    mod: "夜航手册",
    jiaojiaobi: "皎皎币",
    role_tupo: "角色突破",
    role_exp: "角色经验",
    mozhixie: "魔之楔",
    wuqi_tupo: "武器突破",
    wuqi_exp: "武器经验",
    husong: "护送",
    mihan: "委托密函",
    fish: "钓鱼",
    cjsxj: "沉浸式戏剧",
    game_activity: "活动",
    ze_weapon: "灾厄武器",
    lmyy: "联袂演绎",
    cloud_wuqi_tupo: "云-武器突破",
    cloud_role_tupo: "云-角色突破",
    cloud_wuqi_exp: "云-武器经验",
    cloud_game_activity: "云-活动"
};
