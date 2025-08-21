$(document).ready(function(){
    oTable = $('#data_list').dataTable(
        {
            "bJQueryUI": true,
            "width":"50px",
            "bProcessing": true,
            "bSeverside": true,
            "sAjaxSource": "/paper/getall/",
            "fnServerData": function( sSource, aoData, fnCallback ) {
                oData={"pids": pids};
                $.post(sSource,oData,function(json) { 
                    fnCallback(json);
                },"json");
            }
        });
});


function submitform(){
    var oTable = $('#data_list').dataTable();
    var year = $('#id_year').val();
    var subject = $('#id_subject').val();
    var level = $('#id_level').val();
    oTable.fnFilter(year,0);
    oTable.fnFilter(subject,1);
    oTable.fnFilter(level,2);
}

function checkdetailpaper(){
    var paperids = [];
    
    $('input', oTable.fnGetNodes()).each(function(){
        if($(this).attr('checked') === 'checked'){
            paperids.push($(this).attr('name'));
        }
    });
    $('#paperids').val(paperids);
    document.formx1.submit();
}

function selectall(){
    oTable = $('#data_list').dataTable();
    $('input', oTable.fnGetNodes()).each(function(){
        $(this).attr('checked',!$(this).attr('checked'));
    });
}


