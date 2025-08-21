;(function($, undef) {
    $(function(){
        var oTable = $('#data_list').dataTable(
            {
                "bJQueryUI": true,
                "bProcessing": true,
                "sAjaxSource": "/mcq/paper/getall/?forwhat=teacher_report",
                "width":"80px",
            });

        $("#data_list_filter").css({"display": "none"});

        $('#id_level').attr({'onBlur':'submitform'});
    });

})(jQuery);

function submitform(){
    var oTable = $('#data_list').dataTable();
    var year = $('#id_year').val();
    var subject = $('#id_subject').val();
    var level = $('#id_level').val();
    oTable.fnFilter(year, 0);
    oTable.fnFilter(subject, 1);
    oTable.fnFilter(level, 2);
}

var checkdetailmark = function(){
    var paperids = [];
    var oTable = $('#data_list').dataTable();

    $('input', oTable.fnGetNodes()).each(function(){
        if($(this).attr('checked') === 'checked'){
            paperids.push($(this).attr('name'));
        }
    });

    $('#paperids').val(paperids);
    document.formx1.submit();
};

var selectall = function(){
    var oTable = $('#data_list').dataTable();
    $('input', oTable.fnGetNodes()).each(function(){
        $(this).attr('checked',!$(this).attr('checked'));
    });
};
