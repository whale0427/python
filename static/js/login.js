document.addEventListener("DOMContentLoaded",function(){
    //登录页面账号密码切换文本功能
    select_role();
    // 页面加载时，从localStorage读取并填充用户信息
    loadSavedUserInfo();
});
// 从localStorage加载用户信息并填充表单
//function loadSavedUserInfo() {
//    const savedInfo = localStorage.getItem("loginUserInfo");
//    if (savedInfo) {
//        const { role, username, password } = JSON.parse(savedInfo);
//        // 选中身份
//        const roleRadio = document.querySelector(`input[name='role'][value='${role}']`);
//        if (roleRadio) {
//            roleRadio.checked = true;
//            updateLabels(); // 触发标签文本更新
//        }
//        // 填充账号密码
//        document.getElementById("username").value = username;
//        document.getElementById("password").value = password;
//        // 勾选记住密码
//        document.getElementById("remember_password").checked = true;
//    }
//}
//登录页面账号密码切换文本功能
function select_role(){
    const radio_roles=document.querySelectorAll("input[name='role']");
    radio_roles.forEach(result=>{
        result.addEventListener("change",updateLabels);
    });
    updateLabels();
}
function updateLabels(){
    const selected_radio=document.querySelector("input[name='role']:checked");
    const your_username=document.querySelector(".your_username");
    const your_password=document.querySelector(".your_password");
    if(selected_radio){
        const selected_radio_value=selected_radio.value;
        switch(selected_radio_value){
            case "admin":
                your_username.textContent="用户名";
                your_password.textContent="密码";
                break;
            case "teacher":
                your_username.textContent="电话";
                your_password.textContent="密码";
                break;
            case "student":
                your_username.textContent="学号";
                your_password.textContent="密码";
                break;
        };
    }else{
        your_username.textContent="你的账号：";
        your_password.textContent="你的密码：";
    }
};
//登录
function submitLogin(){
    if(!validate_form()) return;
    const url=document.querySelector("button[class='login']").dataset.url;
    const csrf_token=document.querySelector("input[name='csrfmiddlewaretoken']")?.value;
     if (!csrf_token) {
        Swal.fire("错误", "CSRF Token不存在", "error");
        return;
    };
    const loginForm=document.getElementById("loginForm");
    const formData=new FormData(loginForm);
    fetch(url,{
        method:"POST",
        headers:{
            "X-Requested-With":"XMLHttpRequest",
            "X-CSRFToken":csrf_token,
        },
        body:formData,
    }).then(response=>response.json())
    .then(data=>{
        if(data.status==="success"){
//            // 登录成功：根据是否勾选记住密码，保存/清空用户信息
//            const rememberMe = document.getElementById("remember_password").checked;
//            const selectedRole = document.querySelector("input[name='role']:checked").value;
//            const username = document.getElementById("username").value;
//            const password = document.getElementById("password").value;
//            if (rememberMe) {
//                // 保存到localStorage（注意：生产环境不建议存密码）
//                localStorage.setItem("loginUserInfo", JSON.stringify({
//                    role: selectedRole,
//                    username: username,
//                    password: password
//                }));
//            } else {
//                // 清空localStorage
//                localStorage.removeItem("loginUserInfo");
//            }
            Swal.fire({
                icon:"success",
                text:data.message,
                showConfirmButton:false,
                timer:1500,
                didClose:()=>{
                    if(data.role=="student"){
                        const my_score=document.querySelector("input[name='my_score']")?.value;
                        localStorage.setItem('activeSidebarKey', "my_score");
                        window.location.href=my_score;
                    }else{
                        localStorage.setItem('activeSidebarKey', "student_list");
                        window.location.href="/";
                    };
                },
            });
        }else{
            throw new Error(data.message);
        }
    })
    .catch(error=>{
        Swal.fire("error",error.message,"error");
    })
};
function validate_form(){
    const selected_radio=document.querySelector("input[name='role']:checked");
    const username=document.getElementById("username")?.value;
    const password=document.getElementById("password")?.value;
    if(!selected_radio){
        Swal.fire("error","请先选择身份","error");
        return false;
    };
    if(!username){
        const username_content=document.querySelector(".your_username").textContent;
        Swal.fire("error","请输入"+username_content,"error");
        return false;
    };
    if(!password){
        const password_content=document.querySelector(".your_password").textContent;
        Swal.fire("error","请输入"+password_content,"error");
        return false;
    };
    return true;
}