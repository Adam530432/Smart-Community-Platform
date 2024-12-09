document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.slider img');
    let currentIndex = 0;

    function showNextImage() {
        images[currentIndex].style.opacity = 0;
        currentIndex = (currentIndex + 1) % images.length;
        images[currentIndex].style.opacity = 1;
    }

    setInterval(showNextImage, 5000); // 每5秒切换一次图片
});