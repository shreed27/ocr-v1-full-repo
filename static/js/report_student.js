;(function($, undef) {

	$(function(){
     oTable = $('#papers').dataTable({
                    "bJQueryUI": true,
                    "bProcessing": true,
                    "sAjaxSource": "/student/gethistoryanswers/",
                    "width":"100px"
            });
        });
})(jQuery);
