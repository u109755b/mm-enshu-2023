// タブを選択する
function _selectParentTabs(tab) {
    tab.addClass('active-tab');
    var parent = tab.parent();
    if (parent.hasClass('group')) {
        parent.show();
        parent.addClass('expanded');
        _selectParentTabs(parent.prev('.tab'));
    }
}
function selectTab(tab) {
    $('.tab').css('font-weight', 'initial');
    $('.tab').removeClass('active-tab');
    tab.css('font-weight', 'bold');
    _selectParentTabs(tab);
}

// サブタブを展開する
function expand(tab) {
    if (tab.next().hasClass('group')) {
        if (!tab.next().hasClass('expanded')) {
            tab.next().show();
            tab.next().addClass('expanded');
        } else {
            tab.next().hide();
            tab.next().removeClass('expanded');
        }
    }
}

// 取得したパラメータをページに反映させる
function apply_params(params) {
    if (Object.keys(params) == 0) return;
    $("#summary").html(params.summary);
    data = {nodes: params.nodes, edges: params.edges};
    network = new vis.Network(container, data, options);
    if (params.chapter_id != null) {
        selectTab($('#' + params.chapter_id));
    }
}


$(function() {
    // ページが更新されたとき、前の章番号を取得し選択する
    fetch(`${gutenbergID}/init/`)
        .then(response => response.json())
        .then(params => {
            if (params.chapter_id != null) {
                selectTab($('#' + params.chapter_id));
            }
        });

    // 章タブを押したとき
    $('.tab').click(function() {
        expand($(this));
        fetch(`${gutenbergID}/section/?chapter_id=${this.id}`)
            .then(response => response.json())
            .then(apply_params);
    });

    // 「前へ」or「次へ」ボタンが押されたとき
    $("#prev, #next").click(function() {
        fetch(`${gutenbergID}/${this.id}/`)     // ${this.id} = prev or next
            .then(response => response.json())
            .then(apply_params);
    });

    // ネットワーク図の再生成（「再生成」ボタンが押されたとき）
    $("#regen").click(function() {
        network = new vis.Network(container, data, options);
    });
});
