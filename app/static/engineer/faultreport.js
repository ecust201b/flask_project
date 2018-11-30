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
};


$(document).ready(function(){
    myChart1 = echarts.init(picture1);
    picture('故障详情', myChart1, 0, 0, 0, 0, 0);

    $('tr').on('click', function(){
        $('#myModal').modal('show');
        $(window).resize();
        var startTime = $($(this).children()[1]).text();
        if ($($(this).children()[2]).text() == '——') {
            var endTime = "noEnd"
        }
        else {
            var endTime = $($(this).children()[2]).text();
        }
        var data = {'startTime': startTime, 'endTime': endTime};
        $.ajax({
            type:"POST",
            url: "/new/engineer/faultQuery",
            DataType:"json",
            data:data,
            success:function(data){
                picture('故障详情', myChart1, data.axisData, data.Tag1, data.Tag2, data.Tag3, data.Tag4);
            }
        });

    })

    $(window).resize(function(){
        myChart1.resize();
    });

})