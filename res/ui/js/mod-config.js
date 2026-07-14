/*
 * 夜航手册多配置模块。
 *
 * 负责“夜航手册”页里的多组执行计划：
 * - 添加一组等级/次数/关卡配置
 * - 删除某一组配置
 * - 渲染配置表格
 *
 * 真正提交给 Python 的数据放在隐藏域 #input_mod_config_list 中，格式是 JSON 字符串。
 */

// 夜航手册配置队列。每一项结构：{ grade, num, level }。
var modConfigList = [];

// 从缓存数据中恢复夜航手册配置队列。缓存异常时回退为空数组。
function initModConfigList(data) {
    try {
        if (data.mod_config_list) {
            modConfigList = JSON.parse(data.mod_config_list);
        }
    } catch(e) {
        modConfigList = [];
    }
}

// 渲染夜航手册配置表格，并同步隐藏域，保证提交时能带上最新配置。
function renderModList() {
    var html = '';
    if (modConfigList.length === 0) {
        html = '<tr><td colspan="4" style="text-align:center; color:#999; font-size:12px;">暂无计划，请上方添加</td></tr>';
    } else {
        $.each(modConfigList, function(index, item) {
            html += '<tr>';
            html += '  <td>' + item.grade + '级</td>';
            html += '  <td>' + item.num + '次</td>';
            html += '  <td>' + item.level + '</td>';
            html += '  <td style="text-align: center;">';
            html += '    <button type="button" class="layui-btn layui-btn-danger layui-btn-xs btn-del-mod" data-index="' + index + '">';
            html += '      <i class="layui-icon layui-icon-delete"></i>';
            html += '    </button>';
            html += '  </td>';
            html += '</tr>';
        });
    }
    $("#mod_config_body").html(html);
    $("#input_mod_config_list").val(JSON.stringify(modConfigList));
}

// 绑定添加/删除夜航手册配置事件。
function bindModConfigEvents(layer) {
    $("#btn_add_mod_config").click(function() {
        var gradeVal = $("#add_mod_grade").val();
        var numVal = $("#add_mod_num").val();
        var levelVal = $("#add_mod_level").val();

        if (!numVal || numVal <= 0) {
            layer.msg("次数必须大于0", {icon: 5, anim: 6});
            return;
        }

        modConfigList.push({
            grade: gradeVal,
            num: numVal,
            level: levelVal
        });

        renderModList();
        layer.msg('已加入计划', {icon: 1, time: 800});
    });

    $(document).on("click", ".btn-del-mod", function() {
        var index = $(this).data("index");

        layer.confirm('确定删除这组配置吗？', {title:'提示', btn: ['确定','取消']}, function(confirmIndex) {
            modConfigList.splice(index, 1);
            renderModList();
            layer.close(confirmIndex);
        });
    });
}
