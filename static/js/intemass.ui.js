/*
 *
 *yanchao727@gmail.com
 *
 *2012/6/23
*/
var intemass = intemass || {};

intemass.ui = {

	showclientmsg : function (msg){
	        $.blockUI({ 
				message: msg,
				css: { 
					top: 200,
				border: 'none', 
				padding: '15px', 
				backgroundColor: '#000', 
				'-webkit-border-radius': '10px', 
				'-moz-border-radius': '10px', 
				opacity: .5, 
				color: '#fff'
				}});
            setTimeout($.unblockUI, 2000);
		
			 }

}

$(document).ready(function() {
    if ($("#messages_div span").length > 0 ){
        $.blockUI({ 
            message: $('#messages_div'),
            css: { 
                top: 200,
                border: 'none', 
                padding: '15px', 
                backgroundColor: '#000', 
                '-webkit-border-radius': '10px', 
                '-moz-border-radius': '10px', 
                opacity: .5, 
                color: '#fff' 
        }});
        setTimeout($.unblockUI, 3000);
    }

});
