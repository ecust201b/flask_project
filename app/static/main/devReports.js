var myChart2;
var myChart4;

function picture_trend(obj, axisData, P940_1, P940_2) {
    var option = {
        tooltip : {
            trigger: 'axis'
        },
        legend: {
            data:['事件1', '事件2', '事件3', '事件4', '事件5', '事件6', '事件7', '事件8'],
            orient: 'vertical',
            x: 'right',
            top: 'middle'
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true, yAxisIndex: false},
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
                name : '发生次数',
                boundaryGap: [0.2, 0.2]
            },
        ],
        series : [
            {
                name:'事件1',
                type:'line',
                data:P940_1
            },
            {
                name:'事件2',
                type:'line',
                data:P940_2
            },
            {
                name:'事件3',
                type:'line',
                data:P940_2
            },
            {
                name:'事件4',
                type:'line',
                data:P940_2
            },
            {
                name:'事件5',
                type:'line',
                data:P940_2
            },
            {
                name:'事件6',
                type:'line',
                data:P940_2
            },
            {
                name:'事件7',
                type:'line',
                data:P940_2
            },
            {
                name:'事件8',
                type:'line',
                data:P940_2
            }
        ]
    };
    obj.setOption(option);
    $(window).resize(function(){
        obj.resize();
    });
};
function picture(obj, axisData, P940_1, P940_2, P940_3, P940_4) {
    var option = {
        tooltip : {
            trigger: 'axis'
        },
        legend: {
            data:['报警1', '报警2', '报警3', '报警4'],
            orient: 'vertical',
            x: 'right',
            top: 'middle'
        },
        toolbox: {
            show : true,
            feature : {
                mark : {show: true},
                dataZoom : {show: true, yAxisIndex: false},
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
                name : '发生次数',
                boundaryGap: [0.2, 0.2]
            },
        ],
        series : [
            {
                name:'报警1',
                type:'line',
                data:P940_1
            },
            {
                name:'报警2',
                type:'line',
                data:P940_2
            },
            {
                name:'报警3',
                type:'line',
                data:P940_3
            },
            {
                name:'报警4',
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
function clear(){
    $('form:eq(1) input').each(function(){
        $(this).val();
    })
    picture_trend('运行趋势', myChart4, 0, 0, 0);
    picture('传感器读数历史趋势', myChart2, 0, 0, 0, 0, 0);
}

$(document).ready(function(){
    $('form input').each(function(){
        $(this).attr('disabled', 'disabled');
        $(this).css({
            'border': 'none',
            'background-color':'transparent',
            '-webkit-box-shadow': 'none',
            'box-shadow': 'none'
        });
    })
    myChart4 = echarts.init(picture2);
    myChart2 = echarts.init(picture1);
    picture_trend(myChart4, 0, 0, 0);
    picture(myChart2, 0, 0, 0, 0, 0);
});