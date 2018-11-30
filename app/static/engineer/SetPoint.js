$(document).ready(function(){
	$('div.form-group.required').each(function(){
		$(this).addClass('col-md-6 col-sm-6');
		$(this).css({
			'margin-bottom': 10,
		});
	})
	$('#submit').addClass('col-md-offset-3 col-sm-offset-3 col-md-4 col-sm-4');
	$('table input').width('100%');

	var sencer_num = 1;

	$('#num').on('change',function(){
		sencer_num = parseInt($('#num').val())
	})

	$("div[data-toggle=fieldset]").each(function() {
        var $this = $(this);
            
            //Add new entry
        $this.find("button[data-toggle=fieldset-add-row]").click(function() {
            var target = $($(this).data("target"))
            var oldrow = target.find("tr[data-toggle=fieldset-entry]:last");
            var row = oldrow.clone(true, true);
			var elem_id = row.find(":input")[0].id;
			var elem_num = parseInt(elem_id.replace(/.*-(\d{1,4})-.*/m, '$1')) + 1;
			if ($('tr').length - 1 >= sencer_num) {
				alert("传感器数量已到设定值！");
			} else {
				row.attr('data-id', elem_num);
				row.find(":input").each(function() {
					var id = $(this).attr('id').replace('-' + (elem_num - 1) + '-', '-' + (elem_num) + '-');
					$(this).attr('name', id).attr('id', id).val('').removeAttr("checked");
				});
				oldrow.after(row);
			}
        }); //End add new entry

                //Remove row
        $this.find("button[data-toggle=fieldset-remove-row]").click(function() {
            if($this.find("tr[data-toggle=fieldset-entry]").length > 1) {
                var thisRow = $(this).closest("tr[data-toggle=fieldset-entry]");
                thisRow.remove();
            }
        }); //End remove row
    });

})