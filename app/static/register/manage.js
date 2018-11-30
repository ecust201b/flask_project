$(document).ready(function(){
	$('tr').on('click', function(){
		var username = $($(this).children()[0]).text();
		if (username != "用户名") {
			window.location = "./editUser/" + username;
		}
	});
})