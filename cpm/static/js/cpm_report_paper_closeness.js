// Support for Summarization Closeness Report (see report_paper.html)
//
// This only shows for teacher reports, for which the paper ID's have been 
// defined (i.e., pids).
//

$(document).ready(function(){
    // Hide if no paper ID's defined
    if (pids != "") {
        $("#closeness_band_info").show();
    }

    // Create the DataTables control
    // See http://datatables.net/usage/features for description of options.
    var oTable = $('#closeness_data_list').dataTable(
        {
	    // Standard Intemass datatable properties
            "bJQueryUI": true,
            "bProcessing": true,
            "bSeverside": true,
	    // Non-Standard Intemass datatable properties:
	    // shows mimimal info in table header and footer
            "bPaginate": false,
            "bFilter": false,
	    "bInfo": false,
	    // "bAutoWidth": false,
	    "bAutoWidth": true,
	    // Datasource information
            "sAjaxSource": "/cpm/paper/getall_closeness/",

            "fnServerData": function( sSource, aoData, fnCallback ) {
                var oData={"pids": pids};
                $.post(sSource,oData,function(json) { 
                    fnCallback(json);
                },"json");
            }
        });
    // DEBUG (under Chrome): console.log("[closeness] oTable: "); console.dir(oTable);
});
