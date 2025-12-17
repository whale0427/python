document.addEventListener("DOMContentLoaded",function(){
    //侧边栏选中
    const sidebarLinks = document.querySelectorAll('.menu a');
    // 1. 读取data-key的存储值
    const activeKey = localStorage.getItem('activeSidebarKey');
    if (activeKey) {
        sidebarLinks.forEach(link => {
            link.classList.remove('active');
            // 匹配data-key属性
            if (link.getAttribute('data-key') === activeKey) {
                link.classList.add('active');
            }
        });
    }
    // 2. 点击事件存储data-key
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            //再次遍历的目的是为了全局清零
            sidebarLinks.forEach(item => item.classList.remove('active'));
            //重新给当前的链接加上属性
            this.classList.add('active');
            // 存储当前的data-key
            localStorage.setItem('activeSidebarKey', this.getAttribute('data-key'));
        });
    });
    //取消全部
    const title_list=document.getElementById("title_list");
    title_list.addEventListener("click",function(){
        // 核心逻辑：1. 移除所有侧边栏链接的active类
        sidebarLinks.forEach(link => {
            link.classList.remove('active');
        });
        // 2. 清空本地存储的activeSidebarKey，避免刷新后又显示active样式
        localStorage.removeItem('activeSidebarKey');
    });
})