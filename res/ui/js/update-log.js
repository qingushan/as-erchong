/*
 * 更新日志弹窗模块。
 *
 * 日志内容从 res/ui/updateLogs.json 读取，点击“关于脚本”里的“更新日志”按钮时加载。
 * 第一次加载后会缓存在 updateLogsCache 中，后续重复打开弹窗不再重复请求 JSON。
 *
 * 依赖：
 * - jQuery
 * - layui layer，由 form-main.js 调用 bindUpdateLog(layer) 传入
 */

// 更新日志缓存。null 表示还没有加载过 updateLogs.json。
var updateLogsCache = null;

// 简单 HTML 转义，避免日志文本里的特殊字符破坏弹窗结构。
function escapeHtml(text) {
    return String(text || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

/*
 * 渲染日志正文。
 *
 * 推荐格式是 content 数组：
 *   "content": ["1.第一行", "2.第二行"]
 *
 * 为了兼容旧数据，如果 content 还是字符串，也会原样返回。
 */
function renderLogContent(content) {
    if ($.isArray(content)) {
        return $.map(content, function(line) {
            return '<p>' + escapeHtml(line) + '</p>';
        }).join('');
    }
    return String(content || '');
}

// 拼出右侧详情区域 HTML，包括版本标题和正文。
function buildLogDetail(data) {
    return '<h4>' + escapeHtml(data.version) + ' (' + escapeHtml(data.date) + ')</h4>' +
        '<div>' + renderLogContent(data.content) + '</div>';
}

// 打开更新日志弹窗，并绑定左侧版本列表的点击切换。
function openUpdateLogLayer(layer, updateLogs) {
    if (!updateLogs || !updateLogs.length) {
        layer.msg('暂无更新日志');
        return;
    }

    var menuHtml = '';
    $.each(updateLogs, function(index, item) {
        menuHtml += '<div class="log-version-item ' + (index === 0 ? 'active' : '') + '" data-index="' + index + '">' + escapeHtml(item.version) + '</div>';
    });

    layer.open({
        type: 1,
        title: '更新日志',
        area: ['90%', '70%'],
        shadeClose: true,
        content: '<div class="log-container">' +
                '  <div class="log-left-menu">' + menuHtml + '</div>' +
                '  <div class="log-right-content" id="log_detail_view">' +
                buildLogDetail(updateLogs[0]) +
                '  </div>' +
                '</div>',
        success: function(layero, index) {
            layero.find('.log-version-item').click(function() {
                var idx = $(this).data('index');
                var data = updateLogs[idx];

                layero.find('.log-version-item').removeClass('active');
                $(this).addClass('active');
                layero.find('#log_detail_view').html(buildLogDetail(data));
            });
        }
    });
}

// 绑定“更新日志”按钮。这个函数由 form-main.js 在 layui 初始化完成后调用。
function bindUpdateLog(layer) {
    $(document).on('click', '#btn_show_logs', function() {
        if (updateLogsCache) {
            openUpdateLogLayer(layer, updateLogsCache);
            return;
        }

        $.getJSON('updateLogs.json')
            .done(function(updateLogs) {
                updateLogsCache = updateLogs;
                openUpdateLogLayer(layer, updateLogsCache);
            })
            .fail(function() {
                layer.msg('更新日志加载失败');
            });
    });
}
