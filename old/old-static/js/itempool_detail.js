/*
 * yanchao727@gmail.com
 * 15/06/2012
 *
 */
var oTable=null;
var questionid=null;
var itempoolid = null;

;(function($, undef) {

    $(function(){
        itempoolid = $('#id_itempoolid').val();
        var view = intemass.util.getUrl('view');
        if (!itempoolid){
            itempoolid=-1;
        }

        $("#id_itempoolname").hide();
        setEditableText();
        if(view){
            oTable = $('#questions').dataTable({
                "bJQueryUI": true,
                "bProcessing": false,
                "sAjaxSource": "/itempool/getquestions/?view=1&itempoolid="+itempoolid,
            });
            $("#add_question_a").hide();
            $(".editable").unbind('click.blur');
            $(".editable").unbind('click.editable');
            $(".editable").attr('disabled', true);
            $("#id_description").attr('disabled', true);

        }else{
            oTable = $('#questions').dataTable({
                "bJQueryUI": true,
                "bProcessing": false,
                "sAjaxSource": "/itempool/getquestions/?itempoolid="+itempoolid,
            });

            $("#add_question_a").click(function(){
                var selitempoolid=$("#id_itempoolid").val();
                if (selitempoolid == "-1"){
                    alert("please give a better name of itempool"); 
                }else{
                    location.href= add_question_url +'?itempoolid='+selitempoolid;
                }
            });

            $("#id_description").blur(function(){
                var selitempoolid=$("#id_itempoolid").val();
                var description = $(this).val();
                if (selitempoolid !== '-1'){
                $.post("/itempool/updatedesc/",
                    {'itempoolid':selitempoolid,
                    'description':description,
                    'csrfmiddlewaretoken':csrfvalue},
                    function(payload){
                        if(payload['state'] == 'success'){
                            $("#id_description").val(payload['description']);
                        }
                    },'json');
                }

            });


        }

        $(".editable").editable(function(value,settings){
            $("#id_itempoolname").val(value);
            var curItempoolid=$("#id_itempoolid").val();
            $.ajax({
                type: "GET",
                url: "/itempool/updatename/",
                dataType: "json",
                data: {"itempoolid":curItempoolid,
                    "itempoolname":value},
                success: function(data) {
                    if (data['itempoolname'] && data['itempoolid']){
                        $("#id_itempoolid").children('option:selected').text(data['itempoolname'])
                        $("#id_itempoolid").children('option:selected').val(data['itempoolid'])
                        itempoolid = $("#id_itempoolid").val();
                        pullTableData(view);
                    }
                    return data;
                },
                error:function(XMLHttpRequest, textStatus, errorThrown) {
                          return this;
                }
            });
            return $('#id_itempoolname').val();
        },{
            type:"text",
            onblur:"submit",
            tooltip:"Click to Edit...",
            style: 'display:inline'
        });

        $("#id_itempoolid").change(function(){
            itempoolid = $("#id_itempoolid").val();
            pullTableData(view);
            setEditableText();
        });

    });

    function pullTableData(view){
        setEditableText();
        if (view){
            oTable = $('#questions').dataTable({
                "bJQueryUI": true,
                "bProcessing": false,
                "bDestroy": true,
                "sAjaxSource": "/itempool/getquestions/?view=1&itempoolid="+itempoolid
            });
        }else{
            oTable = $('#questions').dataTable({
                "bJQueryUI": true,
                "bProcessing": false,
                "bDestroy": true,
                "sAjaxSource": "/itempool/getquestions/?itempoolid="+itempoolid
            });
        }
    }

    function setEditableText(){
        var selitempoolname=$('#id_itempoolid').children('option:selected').text();
        var curItempoolid=$("#id_itempoolid").val();
        $('#id_itempoolname').val(selitempoolname);
        $(".editable").text($('#id_itempoolname').val());
        $.get('/itempool/updatedesc/',
                {'itempoolid':curItempoolid},
                function(payload){
                    if(payload['state'] == 'success'){
                        $("#id_description").val(payload['description']);
                    }
                },'json');
    }

})(jQuery);


function deletequestion(questionid){
    var dialogue = $( "#dialog-confirm" ).dialog({
        resizable: false,
        height:150,
        modal: true,
        buttons: {
            "Delete": function() {
                $.post("/question/delete/",
                    {questionid:questionid},
                    function(){},
                    'json');
                oTable.fnDestroy();
                oTable = $('#questions').dataTable({
                    "bProcessing": false,
                       "sAjaxSource": "/itempool/getquestions/?itempoolid="+itempoolid
                });
                $( this ).dialog( "close" );

            },
        Cancel: function() {
                    $( this ).dialog( "close" );
                }
        }
    });
}

