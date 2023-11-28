$(document).ready(function() {
    function addActiveClassToParentTabs(tab) {
        var parentDiv = tab.parent();
        if (parentDiv.hasClass('group')) {
            parentDiv.prev('.tab').addClass('active-tab');
            addActiveClassToParentTabs(parentDiv);
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

    $('.tab').click(function() {
        $('.tab').removeClass('active-tab');
        $(this).addClass('active-tab');
        addActiveClassToParentTabs($(this));
        expand($(this))
    });
});
