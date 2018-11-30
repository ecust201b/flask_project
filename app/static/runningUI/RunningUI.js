var data_pie = [];

function picture_pie(data, obj) {
    var option = {
    	title : {
            text: '平台运行状况总览',
        },
        tooltip: {
            trigger: 'item',
            formatter: "{a} <br/>{b}: {c} ({d}%)"
        },
        legend: {
            orient: 'vertical',
            x: 'right',
            data: ['故障占比', '报警占比', '正常运行']
        },
        series: [
            {
                name:'时间占比',
                type:'pie',
                radius: ['40%', '70%'],
                label: {
                    normal: {
                        show: false,
                        formatter: '{a|{a}}{abg|}\n{hr|}\n  {b|{b}：}{c}  {per|{d}%}  ',
                        backgroundColor: '#eee',
                        borderColor: '#aaa',
                        borderWidth: 1,
                        borderRadius: 4,
                        // shadowBlur:3,
                        // shadowOffsetX: 2,
                        // shadowOffsetY: 2,
                        // shadowColor: '#999',
                        // padding: [0, 7],
                        rich: {
                            a: {
                                color: '#999',
                                lineHeight: 22,
                                align: 'center'
                            },
                            abg: {
                               backgroundColor: '#333',
                                width: '100%',
                                align: 'right',
                                height: 22,
                                borderRadius: [4, 4, 0, 0]
                            },
                            hr: {
                                borderColor: '#aaa',
                                width: '100%',
                                borderWidth: 0.5,
                                height: 0
                            },
                            b: {
                                fontSize: 12,
                                lineHeight: 22
                            },
                            per: {
                                color: '#eee',
                                backgroundColor: '#334455',
                                padding: [2, 4],
                                borderRadius: 2
                            }
                        }
                    },
                    emphasis: {
                        show: false
                    }
                },
                data:data
            }
        ]
    };
    obj.setOption(option);
    $(window).resize(function(){
        obj.resize();
    });
}

function setpicCSS(){
	height = $(window).height();
	width = $(window).width();
	$('#picture5').css({
		'height' : height / 2.4,
		'width' : width / 3,
		'margin': '0 auto',
	});
	height2 = $('#picture5').height();
	$('.tablerow').height(height2 / 3);
	height1 = $('.tablerow').height();
	$('img').height(height1 / 2);
	height3 = $('.tablerow').height() - $('img').height();
	$('img:gt(0)').css({
		'margin-top' : height3 / 3
	});
	height4 = 300 - $('div.weight').height();
	$('div.weight').css({
		'margin-top' : height4 / 2
	});
}

function judge(data,tag){
	if (data['state' + tag] == 1) {
		$('td.' + tag).css({
			'background-color': 'yellow',
		});
	}
	else {
		$('td.' + tag).css({});
	}

	if (data['state' + tag] == 2) {
		$('td.' + tag).css({
			'background-color': 'red',
		});
	}
	else {
		$('td.' + tag).css({});
	}

	if (data['partial' + tag == 1]) {
		$('img.img' + tag).css({
			'visibility': "visible",
		})
	}
	else {
		$('img.img' + tag).css({
			'visibility': "hidden",
		})
	}

}

// function getNowFormatDate() {
//     var date = new Date();
//     var seperator1 = "-";
//     var seperator2 = ":";
//     var month = date.getMonth() + 1;
//     var strDate = date.getDate();
//     if (month >= 1 && month <= 9) {
//         month = "0" + month;
//     }
//     if (strDate >= 0 && strDate <= 9) {
//         strDate = "0" + strDate;
//     }
//     var currentdate = date.getYear() + seperator1 + month + seperator1 + strDate
//             + " " + date.getHours() + seperator2 + date.getMinutes()
//             + seperator2 + date.getSeconds();
//     return currentdate;
// }


function getData(){
	var urlPath = window.location.pathname;
	urlPath = urlPath.split("/");
	dataSend = urlPath[3];
	$.ajax({
    	type:"POST",
		// url: "/newscale/QueryNow",
		url: "/newscale/QueryPredInt2",
		DataType:"json",
		data:{'eqp': dataSend},
		success:function(data){
			if(data){
				$('#Tag1').text(data.Tag1 + '(kg)');
	            $('#Tag2').text(data.Tag2 + '(kg)');
	            $('#Tag3').text(data.Tag3 + '(kg)');
	            $('#Tag4').text(data.Tag4 + '(kg)');
				$('#weight').text(data.weight.toFixed(2));
				var flag = data.flag;
				if (flag == 0) {
					$('img.img1').css({'visibility': "hidden",});
					$('img.img2').css({'visibility': "hidden",});
					$('img.img3').css({'visibility': "hidden",});
					$('img.img4').css({'visibility': "hidden",});
				}
				else if (flag == 1) {
					$('img.img1').css({'visibility': "visible",});
					$('img.img2').css({'visibility': "hidden",});
					$('img.img3').css({'visibility': "hidden",});
					$('img.img4').css({'visibility': "hidden",});
				}
				else if (flag == 2) {
					$('img.img1').css({'visibility': "hidden",});
					$('img.img2').css({'visibility': "visible",});
					$('img.img3').css({'visibility': "hidden",});
					$('img.img4').css({'visibility': "hidden",});
				}
				else if (flag == 3) {
					$('img.img1').css({'visibility': "hidden",});
					$('img.img2').css({'visibility': "hidden",});
					$('img.img3').css({'visibility': "visible",});
					$('img.img4').css({'visibility': "hidden",});
				}
				else {
					$('img.img1').css({'visibility': "hidden",});
					$('img.img2').css({'visibility': "hidden",});
					$('img.img3').css({'visibility': "hidden",});
					$('img.img4').css({'visibility': "visible",});
				}
	            // judge(data,1);
	            // judge(data,2);
	            // judge(data,3);
	            // judge(data,4);
	            
			}
		}
	});

	// $('tbody:eq(1) > *').remove()
	$.ajax({
		type:"POST",
		url: "/newscale/QueryFault",
		DataType:"json",
		data:{'eqp': dataSend},
		success:function(data){
			$('table:eq(1) > tbody').remove();
			$('thead').after("<tbody></tbody>");
			for (var i = data.id.length; i > 0; i--) {
				if (data.fault_level[i - 1] == 2) {
					var addstr = '<tr class="danger" id="'+ (data.id.length - i + 1) +'"><td>'+ (data.id.length - i + 1) +'</td><td>'+ data.fault_time[i - 1] +'</td><td>'+ data.recover_time[i - 1] +'</td><td>'+ data.period_second[i - 1] +'</td><td style="color: red;">'+ data.fault_reason[i - 1] +'</td>'
					if (data.fault_state[i - 1] == '未修复'){
						addstr = addstr + '<td style="color: red;">' + data.fault_state[i - 1] + '<strong></strong></td></tr>'
					}
					else {
						addstr = addstr + '<td style="color: green;">' + data.fault_state[i - 1] + '<strong></strong></td></tr>'
					}
				}
				else if (data.fault_level[i - 1] == 1) {
					var addstr = '<tr class="warning" id="'+ (data.id.length - i + 1) +'"><td>'+ (data.id.length - i + 1) +'</td><td>'+ data.fault_time[i - 1] +'</td><td>'+ data.recover_time[i - 1] +'</td><td>'+ data.period_second[i - 1] +'</td><td style="color: orange;">'+ data.fault_reason[i - 1] +'</td>'
					if (data.fault_state[i - 1] == '未修复'){
						addstr = addstr + '<td style="color: red;">' + data.fault_state[i - 1] + '<strong></strong></td></tr>'
					}
					else {
						addstr = addstr + '<td style="color: green;">' + data.fault_state[i - 1] + '<strong></strong></td></tr>'
					}
				}
				if (!($('#' + i).length)) {
					$('tbody:eq(1)').append(addstr);
				}
			}
		}
	});
}



$(document).ready(function(){
	// $('img.img1').hide();
	// $('img.img2').hide();
	// $('img.img3').hide();
	// $('img.img4').hide();
	setpicCSS();
	window.onresize = function(){
		setpicCSS();
	};
	window.setTimeout("getData()",0);
    window.setInterval("getData()",5000);
    data_pie.push({value:1, name:'故障占比'});
    data_pie.push({value:1, name:'报警占比'});
    data_pie.push({value:1, name:'正常运行'});
    myChart3 = echarts.init(picture2);
    picture_pie(data_pie, myChart3);
})