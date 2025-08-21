;(function($, undef) {
    $(function() {

        oTable0 = $('#assignments').dataTable({
                    "bJQueryUI": true,
                    "bProcessing": false,
                    "sAjaxSource": "/cpm/student/getassignedassignments/"
                    });

         

        if ($("#dialog-warning p").length > 0){
            var dialogue = $("#dialog-warning").dialog({
                resizable: false,
                width:300,
                modal: true,
                buttons: {
                    OK: function() {
                        $(this).dialog("close");
                    }
                }});
        }
    });
})(jQuery);
