// 原有的轮播图和天气图标代码保持不变
document.addEventListener('DOMContentLoaded', function() {
    const slider = document.querySelector('.slider');
    let slideIndex = 0;

    function showNextSlide() {
        slideIndex++;
        if (slideIndex > 2) {
            slideIndex = 0;
            slider.style.transition = 'none';
            slider.style.transform = `translateX(0)`;
            setTimeout(() => {
                slider.style.transition = 'transform 0.5s ease';
            }, 50);
        } else {
            slider.style.transform = `translateX(-${slideIndex * 33.33}%)`;
        }
    }

    setInterval(showNextSlide, 5000);
});

function getWeatherIcon(iconCode) {
    const iconMap = {
        '01d': 'sun',
        '01n': 'moon',
        '02d': 'cloud-sun',
        '02n': 'cloud-moon',
        '03d': 'cloud',
        '03n': 'cloud',
        '04d': 'cloud',
        '04n': 'cloud',
        '09d': 'cloud-showers-heavy',
        '09n': 'cloud-showers-heavy',
        '10d': 'cloud-sun-rain',
        '10n': 'cloud-moon-rain',
        '11d': 'bolt',
        '11n': 'bolt',
        '13d': 'snowflake',
        '13n': 'snowflake',
        '50d': 'smog',
        '50n': 'smog'
    };
    return iconMap[iconCode] || 'question';
}

// 访客管理系统相关代码
document.addEventListener('DOMContentLoaded', function() {
    // 访客目的选择逻辑
    const purposeSelect = document.getElementById('purpose');
    const otherPurposeGroup = document.getElementById('otherPurposeGroup');
    
    if (purposeSelect) {
        purposeSelect.addEventListener('change', function() {
            if (this.value === '其他') {
                otherPurposeGroup.style.display = 'block';
            } else {
                otherPurposeGroup.style.display = 'none';
                document.getElementById('other_purpose').value = '';
            }
        });
    }

    // 访客搜索功能
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            const searchText = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('.records-table tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchText) ? '' : 'none';
            });
        });
    }

    // 日期筛选功能
    const dateFilter = document.getElementById('dateFilter');
    if (dateFilter) {
        dateFilter.addEventListener('change', function(e) {
            const selectedDate = e.target.value;
            const rows = document.querySelectorAll('.records-table tbody tr');
            
            rows.forEach(row => {
                const visitDate = row.querySelector('td:nth-child(4)').textContent.split(' ')[0];
                row.style.display = visitDate === selectedDate ? '' : 'none';
            });
        });
    }

    // 模态框关闭功能
    const closeButtons = document.querySelectorAll('.close');
    closeButtons.forEach(button => {
        button.onclick = function() {
            this.closest('.modal').style.display = 'none';
        }
    });

    // 点击模态框外部关闭
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    }
});

// 生成访客通行码
function generateQRCode(recordId) {
    const modal = document.getElementById('qrModal');
    const qrcodeDiv = document.getElementById('qrcode');
    
    if (qrcodeDiv) {
        qrcodeDiv.innerHTML = ''; // 清除旧的二维码
        
        // 生成新的二维码
        new QRCode(qrcodeDiv, {
            text: `visitor_${recordId}`,
            width: 200,
            height: 200,
            colorDark: "#1a4f8e",
            colorLight: "#ffffff",
            correctLevel: QRCode.CorrectLevel.H
        });
        
        modal.style.display = 'block';
    }
}

// 查看访客详情
function viewDetails(recordId) {
    const modal = document.getElementById('visitorModal');
    const detailsDiv = document.getElementById('visitorDetails');
    
    // 这里可以添加从后端获取详细信息的 fetch 请求
    fetch(`/visitor/details/${recordId}`)
        .then(response => response.json())
        .then(data => {
            detailsDiv.innerHTML = `
                <div class="details-content">
                    <p><strong>访客姓名：</strong>${data.visitor_name}</p>
                    <p><strong>身份证号：</strong>${data.id_number}</p>
                    <p><strong>联系电话：</strong>${data.phone}</p>
                    <p><strong>访问住户：</strong>${data.visit_apartment}</p>
                    <p><strong>来访目的：</strong>${data.purpose}</p>
                    <p><strong>到访时间：</strong>${data.visit_time}</p>
                    <p><strong>状态：</strong>${data.status}</p>
                </div>
            `;
            modal.style.display = 'block';
        });
}

// 标记访客离开
function markAsLeft(recordId) {
    if (confirm('确认该访客已离开？')) {
        fetch(`/visitor/mark_left/${recordId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('操作失败：' + data.message);
            }
        })
        .catch(error => {
            alert('操作失败，请稍后重试');
        });
    }
}