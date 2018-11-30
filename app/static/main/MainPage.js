
function setWidth(){
	var xScroll = $(window).height();
	var mHeight = $('.navbar').height();
	var yScroll = $(window).width();
	// $('#carousel-example-generic').css('height', xScroll);
	$('#PPT').css('height', xScroll - 70);
	$('#PPT').css('width', yScroll);
}

$(document).ready(function(){
	setWidth();
	window.onresize = function(){
		setWidth();
	};
	$('.navbar.navbar-inverse').css('margin-bottom', 0)
	if ($('.alert.alert-warning')) {
		$('.alert.alert-warning').css('margin-bottom', 0)
	}
	
	// $('tr').on('click', function(){
	// 	var EqpName = $($(this).children()[0]).text();
	// 	window.location = "./Running/" + EqpName;
	// });

	$("tr").each(function() {
        var $this = $(this);
        var EqpName = $($(this).children()[0]).text();
            //Add new entry
        $this.find("#view").click(function() {
            window.location = "./Running/" + EqpName;
		}); //End add new entry
		
		$this.find("#edit").click(function() {
            window.location = "./engineer/edit_eqp/" + EqpName;
		}); //End add new entry


                //Remove row
        $this.find("#delete").click(function() {
            if($this.find("td").length > 1) {
                var thisRow = $(this).closest("tr");
                thisRow.remove();
			}
			$.ajax({
				type:"GET",
				url: "./engineer/delete_eqp",
				DataType:"json",
				data: {'eqp_name': EqpName},
				success:function(data){
					if (data) {
						console.log(data);
					}
				}
			});
        }); //End remove row
    });

})