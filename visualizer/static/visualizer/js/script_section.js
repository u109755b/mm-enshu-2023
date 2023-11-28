function selectParentTabs(tab) {
    tab.addClass('active-tab');
    var parent = tab.parent();
    if (parent.hasClass('group')) {
        parent.show()
        parent.addClass('expanded')
        selectParentTabs(parent.prev('.tab'));
    }
}

function selectTab(tab) {
    $('.tab').css('font-weight', 'initial')
    $('.tab').removeClass('active-tab');
    tab.css('font-weight', 'bold');
    tab.addClass('active-tab');
    var parent = tab.parent();
    if (parent.hasClass('group')) {
        parent.show()
        parent.addClass('expanded')
        selectParentTabs(parent.prev('.tab'));
    }
}

function expand(tab) {
    if (tab.next().hasClass('group')) {
        if (!tab.next().hasClass('expanded')) {
            tab.next().show();
            tab.next().addClass('expanded');
        } else {
            tab.next().hide()
            tab.next().removeClass('expanded');
        }
    }
}

$(function() {
    $('.tab').click(function() {
        selectTab($(this));
        expand($(this))
    });
});
