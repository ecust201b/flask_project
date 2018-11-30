function picture(title, obj, axisData, P940_1, P940_2, P940_3, P940_4) {
    var option = {
        title : {
            text: title
        },
        tooltip : {
            trigger: 'axis'
        },
        legend: {
            data:['WeightTag1', 'WeightTag2', 'WeightTag3', 'WeightTag4'],
            orient: 'vertical',
            x: 'right',
            top: 'middle'
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true, yAxisIndex: false},
                dataView : {show: true, readOnly: false},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        dataZoom : {
            show : true,
            start : 0,
            end : 100
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : true,
                data : axisData
            },
            
        ],
        yAxis : [
            {
                type : 'value',
                scale: true,
                name : '传感器重量读数(kg)',
                boundaryGap: [0.2, 0.2]
            },
        ],
        series : [
            {
                name:'WeightTag1',
                type:'line',
                data:P940_1
            },
            {
                name:'WeightTag2',
                type:'line',
                data:P940_2
            },
            {
                name:'WeightTag3',
                type:'line',
                data:P940_3
            },
            {
                name:'WeightTag4',
                type:'line',
                data:P940_4
            }
        ]
    };
    obj.setOption(option);
    $(window).resize(function(){
        obj.resize();
    });
};

$(document).ready(function(){
    myChart1 = echarts.init(picture1);
    picture('历史趋势查询', myChart1, 0, 0, 0, 0, 0);
    $('form').on('submit', function(e){
        e.preventDefault();
        picture('历史趋势查询', myChart1, 0, 0, 0, 0, 0);
        $("table tbody").html("");
        var startdate = $('#startdate').val();
        var enddate = $('#enddate').val();
        var eqp = $('#eqp').val();
        if (!enddate) {
            var enddate = 'noEnd';
        }
        var data = {"startTime": startdate, "endTime": enddate, "eqp": eqp};
        $.ajax({
            type:"POST",
            url: "/newscale/engineer/operationQuery",
            DataType:"json",
            data:data,
            success:function(data){
                if (data) {
                    for (var i = 0; i < data.Timestamp.length; i++) {
                        $('tbody').append('<tr><td>'+(i+1)+'</td><td>'+data.Timestamp[i]+'</td><td>'+data.standard[i]+'</td><td>'+data.zeropoint[i]+'</td></tr>');
                    }
                }
            }
        });

        $.ajax({
            type:"POST",
            url: "/newscale/engineer/historyQuery",
            DataType:"json",
            data:data,
            success:function(data){
                picture('历史趋势查询', myChart1, data.axisData, data.Tag1, data.Tag2, data.Tag3, data.Tag4);
            }
        });
    })
})