(function ($) {
    $.fn.t2hTablesorter = function(options) {
        var settings = $.extend(true, {
            widthFixed : true,
            widgets : ['zebra', 'stickyHeaders', 'filter'],
            headers: {
                0: { sorter: 'checkbox' },
            },
            widgetOptions: {
                filter_reset : "#clear-filters",
                filter_functions: {
                    0: { 
                        "Checked" : function(e, n, f, i) { return n === 'checked'; },
                        "Unchecked" : function(e, n, f, i) { return n === 'unchecked'; }
                    },
                },
            },
        }, options);

        var $table = $(this);
        $table.tablesorter(settings);
            
        $('#check-visible').click(function() {
            $table.find('tbody :checkbox').prop('checked', false);
            $table.find('tbody tr:not(".filtered") :checkbox').prop('checked', true);
            $table.trigger('update');
        });

        $('#check-none').click(function() {
            $table.find('tbody :checkbox').prop('checked', false);
            $table.trigger('update');
        });
    };
}(jQuery));
