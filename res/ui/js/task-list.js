/*
 * 任务列表模块。
 *
 * 负责“任务”页中任务队列的内存数据、表格渲染、添加/删除/上下移动。
 * 真正提交给 Python 的数据放在隐藏域 #input_task_list 中，格式是 JSON 字符串。
 *
 * 依赖：
 * - form-options.js 中的 TASK_TYPE_NAME_MAP
 * - jQuery
 * - layui layer，由 form-main.js 调用 bindTaskListEvents(layer) 传入
 */

// 当前任务队列。页面运行期间所有增删移动都先改这个数组，再同步到隐藏域。
var currentTaskList = [];

// 从缓存数据中恢复任务队列。缓存异常时回退为空数组，避免整个 UI 初始化失败。
function initTaskList(data) {
    try {
        if (data.task_list) {
            currentTaskList = JSON.parse(data.task_list);
        }
    } catch(e) {
        currentTaskList = [];
    }
}

// 将任务 type 转成用户可读名称。未配置的 type 直接显示原始值，方便排查新任务遗漏映射。
function getTaskTypeName(type) {
    return TASK_TYPE_NAME_MAP[type] || type;
}

// 渲染任务表格，并把 currentTaskList 同步写入隐藏域，保证提交时能带上最新队列。
function renderTaskList() {
    var html = '';
    if (currentTaskList.length === 0) {
        $("#task_empty_tip").show();
    } else {
        $("#task_empty_tip").hide();
        $.each(currentTaskList, function(index, item) {
            html += '<tr>';
            html += '<td>' + (index + 1) + '</td>';
            html += '<td>' + getTaskTypeName(item.type) + '</td>';
            html += '<td>';
            html += '  <div class="task-btns">';
            html += '    <button type="button" class="layui-btn layui-btn-primary layui-btn-xs btn-move-up ' + (index === 0 ? 'layui-btn-disabled' : '') + '" data-index="' + index + '"><i class="layui-icon layui-icon-up"></i></button>';
            html += '    <button type="button" class="layui-btn layui-btn-primary layui-btn-xs btn-move-down ' + (index === currentTaskList.length - 1 ? 'layui-btn-disabled' : '') + '" data-index="' + index + '"><i class="layui-icon layui-icon-down"></i></button>';
            html += '    <button type="button" class="layui-btn layui-btn-danger layui-btn-xs btn-delete-task" data-index="' + index + '"><i class="layui-icon layui-icon-delete"></i></button>';
            html += '  </div>';
            html += '</td>';
            html += '</tr>';
        });
    }
    $("#task_list_body").html(html);
    $("#input_task_list").val(JSON.stringify(currentTaskList));
}

// 绑定任务列表相关按钮事件。动态生成的按钮使用事件委托绑定。
function bindTaskListEvents(layer) {
    $("#btn_add_task").click(function() {
        var typeVal = $("#task_select_type").val();
        currentTaskList.push({
            type: typeVal
        });
        renderTaskList();
        layer.msg('添加成功', {icon: 1, time: 500});
    });

    $(document).on("click", ".btn-delete-task", function() {
        var index = $(this).data("index");
        currentTaskList.splice(index, 1);
        renderTaskList();
    });

    $(document).on("click", ".btn-move-up", function() {
        var index = $(this).data("index");
        if (index > 0) {
            var temp = currentTaskList[index];
            currentTaskList[index] = currentTaskList[index - 1];
            currentTaskList[index - 1] = temp;
            renderTaskList();
        }
    });

    $(document).on("click", ".btn-move-down", function() {
        var index = $(this).data("index");
        if (index < currentTaskList.length - 1) {
            var temp = currentTaskList[index];
            currentTaskList[index] = currentTaskList[index + 1];
            currentTaskList[index + 1] = temp;
            renderTaskList();
        }
    });
}
