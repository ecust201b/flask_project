function picture(title, obj, real, pred, time) {
    var option = {
        title : {
            text: title
        },
        tooltip : {
            trigger: 'axis'
        },
        legend: {
            data:['实际值', '估计值'],
            orient: 'vertical',
            x: 'right'
        },
        toolbox: {
            show : false,
            feature : {
                mark : {show: true},
                dataView : {show: true, readOnly: false},
                magicType : {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        dataZoom : {
            show : false,
            start : 0,
            end : 100
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : true,
                data : time
            },
        ],
        yAxis : [
            {
                type : 'value',
                scale: true,
                name : '传感器电压值读数',
                boundaryGap: [0.2, 0.2]
            },
        ],
        series : [
            {
                name:'实际值',
                type:'line',
                data: real
            },
            {
                name:'估计值',
                type:'line',
                data: pred
            }
        ]
    };
    obj.setOption(option);
    $(window).resize(function(){
        obj.resize();
    });
};

function updata(obj, realValue, predValue, axisData) {
    var option = obj.getOption();
    var data0 = option.series[0].data;
    var data1 = option.series[1].data;
    data0.shift();
    data0.push(realValue);
    data1.shift();
    data1.push(predValue);
    option.xAxis[0].data.shift();
    option.xAxis[0].data.push(axisData);
    obj.setOption(option);
};

function update_date(id){
    $.ajax({
		type:"POST",
        url: "/newscale/QueryPredInt",
        data: {'id': id},
		success:function(data){
            updata(myChart1, data.real, data.pred, data.time);
		}
	});
}


var pic_timer;

$(document).ready(function(){
    myChart1 = echarts.init(picture1);
    picture('传感器详情', myChart1, 0, 0, 0);

    $('td.val').on('click', function(){
        $('#myModal').modal('show');
        $(window).resize();
        var id = $(this).attr("class").split(" ")[0];
        var data = {'id': id};
        $.ajax({
            type:"POST",
            url: "/newscale/QueryPred",
            DataType:"json",
            data:data,
            success:function(data){
                picture('故障详情', myChart1, data.real, data.pred, data.time);
                pic_timer = window.setInterval(function(){
                    update_date(id);
                },2000);
            }
        });

    })

    $(window).resize(function(){
        myChart1.resize();
    });

    $('#myModal').on('hidden.bs.modal', function (e) {
        clearInterval(pic_timer);
    })

})