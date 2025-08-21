/*
 *
 *yanchao727@gmail.com
 *
 *2012/6/23
*/
var intemass = intemass || {};

intemass.util = {

	getUrl : function (id){
		var $_GET = new Array();
		var u=window.location.toString();
		u=u.split('?');
		if(typeof(u[1]) == 'string'){
			u=u[1].split('&');
			for(i=0;i<u.length;i++){
					s=u[i].split("=");
					eval('$_GET["' + s[0] + '"]' + '="' + s[1]+'"');
					}
		}    
		return $_GET[id];
			 },
	
	isEmail: function(str) {
				return /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+((\.[a-zA-Z0-9_-]{2,3}){1,2})$/.test(str);
			},

	isPhone: function(str) {
		return /^1(3|4|8|5)\d{9}$/.test(str);
	},
	
	escapeHtml: function(s) {
				if(!s) {
					return "";
				}
				return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
			},

	/* *
	 * get navigator's flashversion
	 *
	 */
	getFlashVersion: function() {
		var f = "-", n = navigator; 
		if (n.plugins && n.plugins.length) {
			for (var ii = 0; ii < n.plugins.length; ii++) {
				  if (n.plugins[ii].name.indexOf('Shockwave Flash') != -1) { 
					  f = n.plugins[ii].description.split('Shockwave Flash ')[1]; 
					  break; 
				 } 
			} 
		} else if (window.ActiveXObject) { 
			 for (var ii = 10; ii >= 2; ii--) { 
				try { 
				   var fl = eval("new ActiveXObject('ShockwaveFlash.ShockwaveFlash." + ii + "');"); 
				   if (fl) { 
					   f = ii + '.0'; 
					  break; 
				   }
				} catch (e) { 
			   } 
		   } 
		}
		return f;
	}
}
    
