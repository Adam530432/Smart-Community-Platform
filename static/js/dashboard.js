// 在static/js/dashboard.js中添加
document.addEventListener('DOMContentLoaded', function() {
    // 初始化水电费用趋势图
    const billingsChart = echarts.init(document.getElementById('billingsChart'));
    
    const option = {
        title: {
            text: '近6个月水电费用趋势',
            textStyle: {
                fontSize: 16,
                fontWeight: 'normal'
            }
        },
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow'
            }
        },
        legend: {
            data: ['水费', '电费']
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: ['1月', '2月', '3月', '4月', '5月', '6月']
        },
        yAxis: {
            type: 'value',
            name: '金额 (元)'
        },
        series: [
            {
                name: '水费',
                type: 'line',
                data: [120, 132, 101, 134, 90, 230],
                smooth: true,
                lineStyle: {
                    width: 3
                }
            },
            {
                name: '电费',
                type: 'line',
                data: [220, 182, 191, 234, 290, 330],
                smooth: true,
                lineStyle: {
                    width: 3
                }
            }
        ]
    };
    
    billingsChart.setOption(option);

// 初始化年龄分布饼图
const ageChart = echarts.init(document.getElementById('ageDistributionChart'));
const ageOption = {
    title: {
        text: '社区人口年龄分布',
        left: 'center'
    },
    tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
        orient: 'vertical',
        left: 'left'
    },
    series: [
        {
            name: '年龄分布',
            type: 'pie',
            radius: ['40%', '70%'],  // 环形图
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 10,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {
                show: true,
                formatter: '{b}: {c}人'
            },
            emphasis: {
                label: {
                    show: true,
                    fontSize: '18',
                    fontWeight: 'bold'
                }
            },
            data: [
                { value: 120, name: '0-18岁' },
                { value: 250, name: '19-35岁' },
                { value: 180, name: '36-50岁' },
                { value: 150, name: '51-65岁' },
                { value: 100, name: '65岁以上' }
            ]
        }
    ]
};
ageChart.setOption(ageOption);

// 初始化报修类型统计图
const maintenanceChart = echarts.init(document.getElementById('maintenanceChart'));
const maintenanceOption = {
    title: {
        text: '本月报修类型统计',
        left: 'center'
    },
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'shadow'
        }
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        data: ['水电维修', '门窗维修', '电梯故障', '公共设施', '其他'],
        axisLabel: {
            interval: 0,
            rotate: 30
        }
    },
    yAxis: {
        type: 'value',
        name: '报修次数'
    },
    series: [
        {
            name: '报修次数',
            type: 'bar',
            data: [30, 25, 15, 20, 10],
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: '#83bff6' },
                    { offset: 0.5, color: '#188df0' },
                    { offset: 1, color: '#188df0' }
                ])
            },
            emphasis: {
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#2378f7' },
                        { offset: 0.7, color: '#2378f7' },
                        { offset: 1, color: '#83bff6' }
                    ])
                }
            }
        }
    ]
};
maintenanceChart.setOption(maintenanceOption);

// 在文档加载完成后初始化所有图表
document.addEventListener('DOMContentLoaded', function() {
    // 原有的图表初始化代码...
    
    // 初始化新添加的模块
    initNoticeBoard();
    initActivityCalendar();
    
    // 更新窗口resize事件处理
    window.addEventListener('resize', function() {
        // 原有的resize处理...
        activityChart.resize();
    });
});

// 初始化社区热力图
const mapChart = echarts.init(document.getElementById('communityMapChart'));

// 生成更真实的热力数据
const xSize = 50;
const ySize = 30;
const mapData = [];

// 定义热点区域
const hotspots = [
    { x: 10, y: 5, intensity: 90, radius: 5, name: '小区大门' },
    { x: 25, y: 15, intensity: 85, radius: 4, name: '中心广场' },
    { x: 40, y: 8, intensity: 75, radius: 3, name: '商业街' },
    { x: 15, y: 20, intensity: 70, radius: 3, name: '幼儿园' },
    { x: 35, y: 25, intensity: 80, radius: 4, name: '停车场' },
    { x: 8, y: 15, intensity: 65, radius: 3, name: '健身区' },
    { x: 45, y: 15, intensity: 60, radius: 3, name: '篮球场' },
    { x: 20, y: 8, intensity: 55, radius: 2, name: '垃圾投放点' }
];

// 生成更自然的热力分布
for (let i = 0; i < xSize; i++) {
    for (let j = 0; j < ySize; j++) {
        let value = 20; // 基础人流量
        
        // 计算每个点受热点区域的影响
        hotspots.forEach(spot => {
            const distance = Math.sqrt(
                Math.pow(i - spot.x, 2) + Math.pow(j - spot.y, 2)
            );
            // 根据距离计算热点影响
            if (distance < spot.radius * 3) {
                value += (spot.intensity * (1 - distance / (spot.radius * 3)));
            }
        });
        
        // 添加随机波动
        value += Math.random() * 15 - 7.5;
        value = Math.min(100, Math.max(0, value));
        
        mapData.push([i, j, Math.round(value)]);
    }
}

const mapOption = {
    title: {
        text: '社区实时热力分布',
        subtext: '展示区域人流密度',
        left: 'center',
        top: 10
    },
    tooltip: {
        position: 'top',
        formatter: function (params) {
            return `人流密度: ${params.data[2]}%`;
        }
    },
    grid: {
        top: '15%',
        bottom: '20%',
        containLabel: true
    },
    xAxis: {
        type: 'value',
        min: 0,
        max: xSize - 1,
        show: false
    },
    yAxis: {
        type: 'value',
        min: 0,
        max: ySize - 1,
        show: false
    },
    visualMap: {
        min: 0,
        max: 100,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '5%',
        inRange: {
            color: [
                '#d5e8ff',  // 最低密度 - 淡蓝色
                '#95c5ff',
                '#ffeda0',
                '#feb24c',
                '#f03b20'   // 最高密度 - 红色
            ]
        }
    },
    series: [{
        name: '人流密度',
        type: 'heatmap',
        data: mapData,
        emphasis: {
            itemStyle: {
                shadowBlur: 10,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
        },
        pointSize: 8,
        blurSize: 10,
        // 添加地点标注
        markPoint: {
            symbol: 'pin',
            symbolSize: 50,
            itemStyle: {
                color: '#2f4554',
                shadowBlur: 10,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
            },
            data: hotspots.map(spot => ({
                name: spot.name,
                value: spot.name,
                xAxis: spot.x,
                yAxis: spot.y,
                label: {
                    formatter: '{b}',
                    color: '#fff',
                    fontSize: 12,
                    fontWeight: 'bold',
                    backgroundColor: 'rgba(47, 69, 84, 0.8)',
                    padding: [4, 8],
                    borderRadius: 4
                }
            }))
        }
    }]
};

mapChart.setOption(mapOption);

// 时间切换功能的更新逻辑
const updateHeatmap = (time) => {
    const baseData = [...mapData];
    let newData;
    
    switch(time) {
        case '早高峰':
            newData = baseData.map(item => {
                let value = item[2];
                // 入口和停车场区域人流量显著增加
                if ((item[0] < 15 && item[1] < 10) || // 入口区域
                    (item[0] > 30 && item[1] > 20)) { // 停车场区域
                    value = Math.min(100, value * 2);
                }
                return [item[0], item[1], value];
            });
            break;
        case '晚高峰':
            newData = baseData.map(item => {
                let value = item[2];
                // 商业街和休闲区域人流量增加
                if ((item[0] > 35 && item[1] < 15) || // 商业街
                    (item[0] > 20 && item[1] < 20)) { // 休闲区域
                    value = Math.min(100, value * 1.8);
                }
                return [item[0], item[1], value];
            });
            break;
        case '周末':
            newData = baseData.map(item => {
                let value = item[2];
                // 休闲娱乐区域人流量增加
                if ((item[0] > 15 && item[0] < 35) && 
                    (item[1] > 10 && item[1] < 25)) {
                    value = Math.min(100, value * 1.5);
                }
                return [item[0], item[1], value];
            });
            break;
        default:
            newData = baseData;
    }
    
    mapChart.setOption({
        series: [{
            data: newData
        }]
    });
};

// 创建时间切换按钮
const controlsDiv = document.createElement('div');
controlsDiv.className = 'chart-controls';
timeButtons.forEach(time => {
    const button = document.createElement('button');
    button.className = 'chart-control-btn';
    button.textContent = time;
    button.onclick = () => updateHeatmap(time);
    controlsDiv.appendChild(button);
});

// 将按钮添加到图表容器前
document.getElementById('communityMapChart').parentElement.insertBefore(
    controlsDiv, 
    document.getElementById('communityMapChart')
);


// 响应窗口大小变化
window.addEventListener('resize', function() {
    ageChart.resize();
    maintenanceChart.resize();
});
});