/*
 * 表单缓存与提交模块。
 *
 * 负责：
 * - 从 airscript.get("asdata") 读取上次保存的配置
 * - 合并默认值 DEFAULT_FORM_DATA
 * - 修正 checkbox 的回填状态
 * - 提交时保存 asdata 并通知 Python 端启动脚本
 *
 * 依赖：
 * - form-options.js 中的 DEFAULT_FORM_DATA、CHECKBOX_FIELDS
 * - jQuery
 * - airscript
 */

// 读取缓存配置，并合并默认值。缓存 JSON 解析失败时保留默认值，避免 UI 空白。
function loadFormData() {
    var data = $.extend({}, DEFAULT_FORM_DATA);
    var cache_data = airscript.get("asdata");
    if (cache_data && cache_data !== "undefined") {
        try {
            var cached_json = JSON.parse(cache_data);
            $.extend(data, cached_json);
        } catch (e) {
            console.error("数据解析失败", e);
        }
    }
    return data;
}

// 把缓存里的 checkbox 字符串 "off" 转成 false，供 layui form.val 正确回填。
function normalizeCheckboxFields(data) {
    $.each(CHECKBOX_FIELDS, function(index, key) {
        if (data[key] === "off") {
            data[key] = false;
        }
    });
}

// 绑定“运行”按钮提交逻辑。提交前会把未勾选 checkbox 补成 "off"。
function bindFormSubmit(form) {
    form.on('submit(demo2)', function(data) {
        var field = data.field;

        $('input[type="checkbox"]').each(function() {
            var name = $(this).attr('name');
            if (name && !field.hasOwnProperty(name)) {
                field[name] = "off";
            }
        });

        var dataStr = JSON.stringify(field);

        airscript.save("asdata", dataStr);
        airscript.call("submit", dataStr);

        airscript.close();
        return false;
    });
}
