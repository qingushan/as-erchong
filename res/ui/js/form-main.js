/*
 * 表单入口文件。
 *
 * 这个文件只做初始化编排：
 * - 绑定关闭按钮
 * - 初始化 layui 组件
 * - 加载缓存数据并回填表单
 * - 初始化任务列表、夜航手册配置列表
 * - 绑定各模块事件
 *
 * 具体业务逻辑分散在其他 js 文件中，尽量不要把大段功能重新塞回这里。
 */

// 顶部关闭按钮。这里不用等 layui 初始化，只依赖 jQuery 和 airscript。
$(function() {
    $("#asui_close").click(function() {
        airscript.call("close", "用户点了关闭");
        airscript.close();
    });
});

// Layui 初始化入口。所有依赖 layui form/layer 的模块都从这里接入。
layui.use(['form', 'layer', 'element'], function() {
    var laydate = layui.laydate;
    laydate.render({
        elem: '#ID-laydate-type-time',
        type: 'time'
    });

    var form = layui.form;
    var layer = layui.layer;
    var element = layui.element;

    // 更新日志按钮。
    bindUpdateLog(layer);

    // 读取缓存并回填所有普通表单项。
    var data = loadFormData();
    normalizeCheckboxFields(data);
    form.val('formFilter', data);

    // 恢复需要手动渲染的复杂字段。
    initTaskList(data);
    initModConfigList(data);

    renderTaskList();
    renderModList();

    form.render();

    // 绑定各功能模块的交互事件。
    bindTaskListEvents(layer);
    bindModConfigEvents(layer);
    bindFormSubmit(form);
});
