/*
 * yanchao727@gmail.com
 * 15/06/2012
 *
 */

;(function($, undef) {

    $(function(){
        pullZtreeData();
        var view = intemass.util.getUrl('view');
        var dragId;
        $('#id_papername').hide();

        if (view){
            $(".editable").unbind('click.editable');
            $("#button").hide();
            $("#id_ptype").attr("disabled","disabled");
            $("#id_duration").attr("disabled","disabled");
            $("#id_passpoint").attr("disabled","disabled");
            $("#id_year").attr("disabled","disabled");
            $("#id_subject").attr("disabled","disabled");
            $("#id_level").attr("disabled","disabled");
        }else{
            $('#id_duration').timepicker({});
            $(".editable").editable(function(value,settings){
                var data = $('#id_papername').val(); 
                $("#id_papername").val(value);
                return $('#id_papername').val();
            },{
                type:"text",
                onblur:"submit",
                tooltip:"Click to Edit...",
                onedit:function(value, settings){
                },
                style: 'margin:0 0;display:inline;'
            });

        }

        setEditableText();
        $("#id_paperid").change(function(){
            pullZtreeData();
            setEditableText();
        });


    });

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
        zTree = $.fn.zTree.getZTreeObj("questions");
        type = {
            "Y": "ps",
            "N": "ps"
        };
        zTree.setting.check.chkboxType = type;
        setSelectedNodes(zTree);
    };

    var pullZtreeData = function(){
        var curpaperid=$("#id_paperid").val();
        var view = intemass.util.getUrl('view'); 
        $.ajax({
            type: "POST",
            url: "/paper/getquestions/",
            dataType: "json",
            data: {"paperid":curpaperid,"view":view},
            success: function(data) {
                qnum=data[0]['qnum'];
                if (qnum && qnum!=''){
                    $("#qnum").text(qnum);
                }else{
                    $("#qnum").text("0");
                }
                data.shift();
                $.fn.zTree.init($("#questions"), setting, data);
                return setCheck();
            },
            error:function(XMLHttpRequest, textStatus, errorThrown) {
                      $("#snum").text("0");
                      $("#qnum").text("0");
                      return this;
                  }
        });
    };

    var setEditableText = function(){
        var selpapername = $('#id_paperid').children('option:selected').text();
        var curpaperid = $("#id_paperid").val();
        $('#id_papername').val(selpapername);
        $(".editable").text($('#id_papername').val());
        if (curpaperid != -1) {
            $.ajax({
                type: "GET",
                url: "/paper/updatename/",
                dataType: "json",
                data: {"paperid":curpaperid,
                       "papername":selpapername},
                success: function(data) {
                    if (data['papername'] && data['paperid']){
                        $("#id_paperid").children('option:selected').text(data['papername']);
                        $("#id_paperid").children('option:selected').val(data['paperid']);
                        pullZtreeData();
                    }
                    if(data['duration']){
                        $("#id_ptype").children('option:selected').text(data['ptype']);
                        $('#id_ptype').val(data['ptype']);
                        $('#id_duration').val(data['duration']);
                        $("#id_year").children('option:selected').text(data['year'][1]);
                        $('#id_year').val(data['year'][0]);
                        $("#id_level").children('option:selected').text(data['level'][1]);
                        $('#id_level').val(data['level'][0]);
                        $("#id_subject").children('option:selected').text(data['subject'][1]);
                        $('#id_subject').val(data['subject'][0]);
                    }
                    return data;
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                           return this;
                }
            });
        }else{
            $('#id_duration').val('');
        }
    };

})(jQuery);

var setSelectedNodes = function(zTree){
    var sNodes = zTree.getCheckedNodes();
    var qids = [];
    if (sNodes.length > 0) {
        for (node in sNodes){
            if (sNodes[node].getParentNode() != null)
                qids.push(sNodes[node].qid);
        }
        $("#snum").text(qids.length);
    }else{
        $("#snum").text("0");
    }
    return qids;
};


function submitform(){
    var treeObj = $.fn.zTree.getZTreeObj("questions");
    var qids = setSelectedNodes(treeObj);
    if (!qids){
        intemass.ui.showclientmsg("You have to choose one student at least!");
    }else{
        $("#id_questionlist").val(qids);
        var selpapername = $("#id_papername").val();
        if(!selpapername || selpapername === ""){
            intemass.ui.showclientmsg("Paper name cannot be empty");
        }else if (selpapername && selpapername === "New Paper"){
            intemass.ui.showclientmsg("Please choose a better paper name instead of \"New Paper\"");
        }else{
            document.forms[0].submit();
        }
    }
} 
