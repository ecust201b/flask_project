var data_pie = [];
var myChart2;
var myChart3;
var myChart4;

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


function picture_trend(title, obj, axisData, P940_1, P940_2) {
    var option = {
        title : {
            text: title
        },
        tooltip : {
            trigger: 'axis'
        },
        legend: {
            data:['零点变化', '标定误差'],
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
                name : '传感器重量读数(kg)',
                boundaryGap: [0.2, 0.2]
            },
        ],
        series : [
            {
                name:'零点变化',
                type:'line',
                data:P940_1
            },
            {
                name:'标定误差',
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

function picture_pie(data, obj) {
    var option = {
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

function clear(){
    $('form:eq(1) input').each(function(){
        $(this).val();
    })
    $("#fault tbody").html("");
    $("#operate tbody").html("");
    picture_trend('运行趋势', myChart4, 0, 0, 0);
    picture('传感器读数历史趋势', myChart2, 0, 0, 0, 0, 0);
    data_pie = [];
    picture_pie(data_pie, myChart3);
}


$(document).ready(function(){
    $('form:eq(1) div.form-group.required').each(function(){
        $(this).addClass('col-md-6 col-sm-6');
        $(this).css({
            'margin-bottom': 10,
        });
    })
    $('form:eq(1) input').each(function(){
        $(this).attr('disabled', 'disabled');
        $(this).css({
            'border': 'none',
            'background-color':'transparent',
            '-webkit-box-shadow': 'none',
            'box-shadow': 'none'
        });
    })
    myChart4 = echarts.init(picture4);
    picture_trend('运行趋势', myChart4, 0, 0, 0);
    data_pie.push({value:1, name:'故障占比'});
    data_pie.push({value:1, name:'报警占比'});
    data_pie.push({value:1, name:'正常运行'});
    myChart3 = echarts.init(picture3);
    picture_pie(data_pie, myChart3);
	myChart2 = echarts.init(picture2);
	picture('传感器读数历史趋势', myChart2, 0, 0, 0, 0, 0);

    $('form').on('submit', function(e){
        e.preventDefault();
        clear();
        var startdate = $('#startdate').val() + ':00';
        var enddate = $('#enddate').val();
        if (!enddate) {
            var enddate = 'noEnd';
        }
        else{
            enddate += ':00';
        }
        var eqpName = $('#eqp').val();
        var dataEqp = {'eqp': eqpName};
        var dataDate = {'startTime': startdate, 'endTime': enddate};
        // title query
        $.ajax({
            type:"POST",
            url: "/scale/report/infoQuery",
            DataType:"json",
            data:dataEqp,
            success:function(data){
                if (data.fail) {alert('查询失败无此设备！');}
                else {
                    for (var key in data) {
                        $('#' + key).val(data[key]);
                    }
                }
            }
        })
        //pie_data query
        $.ajax({
            type:"POST",
            url: "/scale/report/pieDataQuery",
            DataType:"json",
            data:dataDate,
            success:function(data){
                data_pie = [];
                data_pie.push({value:data.fault, name:'故障占比'});
                data_pie.push({value:data.alarm, name:'报警占比'});
                data_pie.push({value:data.normal, name:'正常运行'});
                picture_pie(data_pie, myChart3);
            }
        })
        // data history query
        $.ajax({
            type:"POST",
            url: "/scale/engineer/faultQuery",
            DataType:"json",
            data:dataDate,
            success:function(data){
                picture('传感器读数历史趋势', myChart2, data.axisData, data.Tag1, data.Tag2, data.Tag3, data.Tag4);
            }
        });
        // operation query
         $.ajax({
            type:"POST",
            url: "/scale/engineer/operationQuery",
            DataType:"json",
            data:dataDate,
            success:function(data){
                if (data) {
                    for (var i = 0; i < data.Timestamp.length; i++) {
                        $('#operate tbody').append('<tr><td>'+(i+1)+'</td><td>'+data.Timestamp[i]+'</td><td>'+data.record[i]+'</td><td>'+data.standard[i]+'</td><td>'+data.zeropoint[i]+'</td></tr>');
                    }
                }
            }
        });
        //trend query
        $.ajax({
            type:"POST",
            url: "/scale/report/trendQuery",
            DataType:"json",
            data:dataDate,
            success:function(data){
                picture_trend('运行趋势', myChart4, data.axisData, data.zero, data.standard);
            }
        });
        // fault table
        $.ajax({
            type:"POST",
            url: "/scale/report/faultTable",
            DataType:"json",
            data:dataDate,
            success:function(data){
                if (data) {
                    for (var i = 0; i < data.fault_time.length; i++) {
                        if (data.fault_level[i] == 2) {
                            var str = '<tr class="danger"><td>'+(i+1)+'</td><td>'+data.fault_time[i]+'</td><td>'+data.recover_time[i]+'</td><td>'+data.period_second[i]+'</td><td style="color:red;">'+data.fault_reason[i]+'</td>';
                            if (data.fault_state[i] == '未修复') {
                                str += '<td style="color:red;"><strong>'+data.fault_state[i]+'</strong></td></tr>';
                            }
                            else{
                                str += '<td style="color:green;"><strong>'+data.fault_state[i]+'</strong></td></tr>';
                            }
                            $('#fault tbody').append(str);
                        }
                        else{
                            var str = '<tr class="warning"><td>'+(i+1)+'</td><td>'+data.fault_time[i]+'</td><td>'+data.recover_time[i]+'</td><td>'+data.period_second[i]+'</td><td style="color:orange;">'+data.fault_reason[i]+'</td>';
                            if (data.fault_state[i] == '未修复') {
                                str += '<td style="color:red;"><strong>'+data.fault_state[i]+'</strong></td></tr>';
                            }
                            else{
                                str += '<td style="color:green;"><strong>'+data.fault_state[i]+'</strong></td></tr>';
                            }
                            $('#fault tbody').append(str);
                        }
                    }
                }
            }
        });


    })
    
    
})