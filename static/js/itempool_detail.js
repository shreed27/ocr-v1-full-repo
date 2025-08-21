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
        pullZtreeData();

        itempoolid = $('#id_itempoolid').val();
        var view = intemass.util.getUrl('view');
        if (!itempoolid){
            itempoolid=-1;
        }
        if (view){
         $('.form').removeAttr('style').css('height','600px');
         $('.greenBtn').hide();
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
        //pullZtreeData();
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
        var setting = {
        edit: {
                  enable: true,
                  showRemoveBtn: false,
                  showRenameBtn: false,
                  editNameSelectAll: false,
                  drag: {
                      isCopy: false,
                      isMove: true,
                      prev: true,
                      next: true,
                      inner: false
                  }
              },
        data: {
                  simpleData: {
                                  enable: true
                              }
              },
        check: {
                   enable: true
               },
        callback : {
                       beforeDrag: beforeDrag,
                       beforeDrop: beforeDrop
                   }
    };

    var beforeDrag = function(treeId, treeNodes) {
        for (var i = 0, l = treeNodes.length; i < l; i++) {
            dragId = treeNodes[i].pId;
            if (!treeNodes[i].drag) {
                return false;
            }
        }
        return true;
    };

    var beforeDrop = function(treeId, treeNodes, targetNode, moveType) {
        console.log(targetNode);
        return (targetNode.pId === dragId) ? true : false;
    };

    var setCheck = function() {
        var type, zTree;
        zTree = $.fn.zTree.getZTreeObj("teacher_list");
        type = {
            "Y": "ps",
            "N": "ps"
        };
        zTree.setting.check.chkboxType = type;
        setSelectedNodes(zTree);
    };
    var pullZtreeData = function(){
        var curritem_id=$("#id_itempoolid").val();
        var view = intemass.util.getUrl('view');
        $.ajax({
            type: "GET",
            url: "/itempool/teacherlist/",
            dataType: "json",
            data: {"itempool_id":curritem_id,"view":view},
            success: function(data) {
                qnum=data[0]['qnum'];
                if (qnum && qnum!=''){
                    $("#qnum").text(qnum);
                }else{
                    $("#qnum").text("0");
                }
                data.shift();
                $.fn.zTree.init($("#teacher_list"), setting, data);
                return setCheck();
            },
            error:function(XMLHttpRequest, textStatus, errorThrown) {
                      $("#snum").text("0");
                      $("#qnum").text("0");
                      return this;
                  }
        });
    };

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

var setSelectedNodes = function(zTree){
    var sNodes = zTree.getCheckedNodes();
    var qids = [];
    if (sNodes.length > 0) {
        for (node in sNodes){
            if (sNodes[node].getParentNode() != null)
                console.log(sNodes[node].qid)
                qids.push(sNodes[node].qid);
        }
        $("#snum").text(qids.length);
    }else{
        $("#snum").text("0");
    }

    return qids;
};
function submitform(){
    var treeObj = $.fn.zTree.getZTreeObj("teacher_list");
    var tpids = setSelectedNodes(treeObj);
    if (!tpids){
        intemass.ui.showclientmsg("You have to choose one teacher at least!");
    }else{

        var curritem_id=$("#id_itempoolid").val();
        $.ajax({
            url:'/itempool/addteacher/',
            type:'POST',
            dataType: "json",
            data:{'itempool_id':curritem_id,'teacher_ids':JSON.stringify(tpids)},
            success:function(data){
                if(data['response'] == 'success'){
                    intemass.ui.showclientmsg("Teacher Added successfully");
                }
                console.log('success')
            }
        });


    }
}