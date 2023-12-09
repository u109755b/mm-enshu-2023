// タブを選択する
function _selectParentTabs(tab) {
    tab.addClass('active-tab');
    var parent = tab.parent();
    if (parent.hasClass('group')) {
        parent_tab = parent.prev('.tab');
        expand(parent_tab);
        _selectParentTabs(parent_tab);
    }
}
function selectTab(tab) {
    $('.tab').css('font-weight', 'initial');
    $('.tab').removeClass('active-tab');
    fold($('.group').prev('.tab'));
    tab.css('font-weight', 'bold');
    _selectParentTabs(tab);
}

// サブタブを展開する
function expand(tab) {
    tab.next().show();
    tab.next().addClass('expanded');
    tab.removeClass('expand-icon');
    tab.addClass('fold-icon');
}
// サブタブを折り畳む
function fold(tab) {
    tab.next().hide();
    tab.next().removeClass('expanded');
    tab.removeClass('fold-icon');
    tab.addClass('expand-icon');
}
// サブタブが展開されていれば折りたたむ、折り畳まれていれば展開する
function toggle_expanding_folding(tab) {
    if (tab.next().hasClass('group')) {
        if (!tab.next().hasClass('expanded')) expand(tab);
        else fold(tab);
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
        toggle_expanding_folding($(this));
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
