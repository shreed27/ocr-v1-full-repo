;
(function($, undef) {
    $(function() {
        var oTable = $('#data_list').dataTable({
            "bJQueryUI": true,
            "bProcessing": true,
            "sAjaxSource": "/paper/getall/?forwhat=teacher_report",
            "width": "80px",
        });

        $("#data_list_filter").css({
            "display": "none"
        });

        $('#id_level').attr({
            'onBlur': 'submitform'
        });
    });

    $(function() {
        var ooTable = $('#asgn_data_list').dataTable({
            "bJQueryUI": true,
            "bProcessing": true,
            "sAjaxSource": "/paper/getall/?forwhat=teacher_report&report_type=closeness_report",
            "width": "80px",
        });

        $("#data_list_filter").css({
            "display": "none"
        });

        $('#id_asgn_level').attr({
            'onBlur': 'submitform'
        });
    });
})(jQuery);

function submitform() {
    var oTable = $('#data_list').dataTable();
    var year = $('#id_year').val();
    var subject = $('#id_subject').val();
    var level = $('#id_level').val();
    oTable.fnFilter(year, 0);
    oTable.fnFilter(subject, 1);
    oTable.fnFilter(level, 2);
}

var checkdetailmark = function() {
    var paperids = [];
    var oTable = $('#data_list').dataTable();

    $('input', oTable.fnGetNodes()).each(function() {
        if ($(this).attr('checked') === 'checked') {
            paperids.push($(this).attr('name'));
        }
    });

    $('#paperids').val(paperids);
    document.formx1.submit();
};

var selectall = function() {
    var oTable = $('#data_list').dataTable();
    $('input', oTable.fnGetNodes()).each(function() {
        $(this).attr('checked', !$(this).attr('checked'));
    });
};


//new closenes report starts here.
function asgnFilterform() {
    var oTable = $('#asgn_data_list').dataTable();
    var year = $('#id_asgn_year').val();
    var subject = $('#id_asgn_subject').val();
    var level = $('#id_asgn_level').val();
    oTable.fnFilter(year, 0);
    oTable.fnFilter(subject, 1);
    oTable.fnFilter(level, 2);
};

var getClosnessReport = function() {
    var assignment_id = parseInt($("input[name$='closeness_report']:checked").val());

    if (!assignment_id) {
        intemass.ui.showclientmsg("Assignment not found !");
    } else {
        $.ajax({
                url: '/report/get_closeness_report/',
                type: 'POST',
                dataType: 'json',
                data: {
                    'assignment_id': assignment_id
                },
            })
            .done(function(data) {
                if (data.success) {
                    var questions = data.response.questions;

                    var table_data = [];

                    for (var i in questions) {
                        var q_name = questions[i]['question_name'];
                        var points = questions[i]['points'];
                        var point_list = questions[i]['point_list'];

                        var point_list_html = "<ol>";
                        for (var l in point_list) {
                            point_list_html += '<li>' + point_list[l] + '</li>';
                        }
                        point_list_html += "</ol>";

                        var c_ol_html = "<ol>";
                        var w_ol_html = "<ol>";

                        for (var pt in points) {
                            var correct = points[pt]['correct'];
                            var wrong = points[pt]['wrong'];

                            var c_html = "<li><ul>";
                            var w_html = "<li><ul>";

                            for (item in correct) {
                                if (correct[item]) {
                                    c_html += "<li>" + correct[item] + "</li>";
                                }
                            }

                            for (item in wrong) {
                                if (wrong[item]) {
                                    w_html += "<li>" + wrong[item] + "</li>";
                                }
                            }

                            if (c_html != "<li><ul>") {
                                c_ol_html += c_html + "</ul></li>";
                            } else {
                                c_ol_html += "<li>No students found</li>"
                            }

                            if (w_html != "<li><ul>") {
                                w_ol_html += w_html + "</ul></li>";
                            } else {
                                w_ol_html += "<li>No students found</li>"
                            }
                        }

                        if (c_ol_html != "<ol>") {
                            c_ol_html += "</ol>";
                        }

                        if (w_ol_html != "<ol>") {
                            w_ol_html += "</ol>";
                        }

                        table_data.push([q_name, point_list_html, c_ol_html, w_ol_html]);
                    }

                    if (table_data) {
                        $('#asgn_closeness_report').dataTable({
                            "aaData": table_data,
                            "bJQueryUI": true,
                            "ordering": false,
                            "bDestroy": true,
                        });
                    }
                    $('.asgn_closeness_report').css('display', 'block');
                } else {
                    intemass.ui.showclientmsg("Sorry, Data retrival failed !");
                }
            })
            .fail(function(data) {
                intemass.ui.showclientmsg("Sorry, Data retrival failed !");
            })
            .always(function(data) {
                console.log(data, "data");
            });
    }
};

function noAssignment(){
    intemass.ui.showclientmsg("Assignment not found !");
};