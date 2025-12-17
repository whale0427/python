document.addEventListener("DOMContentLoaded",function(){
    //全选
    checked();
    //新增
    iframe_add();
    //保存
    teacher_create();
    //编辑
    teacher_editor();
    //删除
    teacher_delete();
    //批量删除
    teacher_bulk_delete();
    //导入
    teacher_import();
    //导出
    teacher_export();
});
//全选
function checked(){
    const select_all=document.getElementById("select_all");
    if(select_all){
        select_all.addEventListener("click",function(){
            document.querySelectorAll("input[name='teacher_ids']").forEach(result=>{
                result.checked=select_all.checked;
            })
        });
    }
};
//保存并新增下一个
var savenext=null;
function save_next(){
    savenext=1;
};
//新增
function iframe_add(){
    const btn_add=document.getElementById("btn_add")
    if(btn_add){
        const url=btn_add.dataset.url;
        btn_add.addEventListener("click",function(){
            Swal.fire({
                position:"top-right",
                html:`<iframe src=${url} style="width:100%;height:500px;" frameborder="0"></iframe>`,
                showConfirmButton:false,
            })
        })
    }
};
//保存
function teacher_create(){
    const form=document.querySelector("form.saveform");
    if(!form) return;
    form.addEventListener("submit",function(e){
        e.preventDefault();
        const formData=new FormData(form);
        fetch(form.getAttribute("action"),{
            method:"POST",
            headers:{
                "X-Requested-With":"XMLHttpRequest",
                "X-CSRFToken":formData.get("csrfmiddlewaretoken"),
            },
            body:formData,
        })
        .then(response=>response.json())
        .then(data=>{
            if(data.status==="success"){
                Swal.fire({
                    icon:"success",
                    text:data.message,
                    confirmButtonText:"关闭",
                    allowOutsideClick:false,
                    allowEscapeKey:false,
                }).then(result=>{
                    if(result.isConfirmed){
                        if(savenext===1){
                            window.location.reload()
                        }else{
                            window.parent.location.reload()
                        }
                    }
                })
            }else{
                const errors=JSON.parse(data.message);
                let errormessage="";
                for(const field in errors){
                    if(errors.hasOwnProperty(field)){
                        errors[field].forEach(error=>{
                            errormessage+=`<li style="color:red;text-align:left;margin-left:20px;">${error.message}</li>`
                        })
                    }
                };
                Swal.fire({
                    icon:"error",
                    title:"验证失败",
                    html:errormessage,
                    confirmButtonText:"关闭",
                    allowOutsideClick:false,
                    allowEscapeKey:false,
                });
            }
        }).catch(error=>{
            Swal.fire({
                icon:"error",
                title:"网络错误",
                text:"服务器请求失败,请稍后再试。"+error,
                confirmButtonText:"关闭",
                allowOutsideClick:false,
                allowEscapeKey:false,
            })
        })
    })
};
//编辑
function teacher_editor(){
    document.querySelectorAll("#btn_editor").forEach(result=>{
        result.addEventListener("click",function(e){
            e.preventDefault();
            const url=result.getAttribute("href");
            Swal.fire({
                position:"top-right",
                html:`<iframe src=${url} style="width:100%;height:500px;" frameborder="0"></iframe>`,
                showConfirmButton:false,
            })
        })
    })
};
//删除
function teacher_delete(){
    document.querySelectorAll("#btn_delete").forEach(result=>{
        result.addEventListener("click",function(e){
            e.preventDefault();
            const url=result.getAttribute("href");
            const csrf_token=document.getElementById("csrf_token")?.value
            // 获取当前页面的查询参数（用于保留搜索条件等）
            const currentSearchParams = new URLSearchParams(window.location.search);
            Swal.fire({
                icon:"warning",
                title:"确认是否删除",
                showCancelButton:true,
                confirmButtonText:"是",
                cancelButtonText:"否",
            }).then(result=>{
                if(result.isConfirmed){
                    fetch(url,{
                        method:"DELETE",
                        headers:{
                            "X-Requested-With":"XMLHttpRequest",
                            "X-CSRFToken":csrf_token,
                        },
                    })
                    .then(response=>response.json())
                    .then(data=>{
                        if(data.status==="success"){
                            Swal.fire({
                                icon:"success",
                                text:data.message,
                                confirmButtonText:"关闭",
                                allowOutsideClick:false,
                                allowEscapeKey:false,
                            }).then(result=>{
                                // 关键修改：替换page参数为后端返回的target_page，然后跳转
                                currentSearchParams.set('page', data.target_page);
                                // 拼接新的URL并跳转
                                //绝对 URL：包含完整的协议、域名、路径、参数，比如：
                                //http://localhost:8000/teacher/list/?page=3&search=张三
                                //相对 URL：只包含路径和参数（不包含协议、域名）
                                //window.location.href是相对URL
                                window.location.href = `${window.location.pathname}?${currentSearchParams.toString()}`;
                            })
                        }
                    })
                    .catch(error=>{
                        Swal.fire({
                            icon:"error",
                            text:error.message,
                            confirmButtonText:"关闭",
                            allowOutsideClick:false,
                            allowEscapeKey:false,
                        })
                    })
                }
            });
        })
    })
};
//批量删除
function teacher_bulk_delete(){
    const btn_delete_all=document.getElementById("btn_delete_all");
    const window_search_params=new URLSearchParams(window.location.search);
    btn_delete_all.addEventListener("click",function(){
        const checks=document.querySelectorAll("input[name='teacher_ids']:checked");
        if(checks.length===0){
            Swal.fire("提醒","请选择要删除的数据","warning");
            return;
        }
        Swal.fire({
            icon:"warning",
            text:"确认是否删除",
            showCancelButton:true,
            cancelButtonText:"否",
            confirmButtonText:"是",
            allowOutsideClick:false,
            allowEscapeKey:false,
        }).then(result=>{
            if(result.isConfirmed){
                const formData=new FormData();
                const url=btn_delete_all.dataset.url;
                const csrf_token=document.getElementById("csrf_token")?.value;
                checks.forEach(check=>{
                    formData.append(check.name,check.value);
                })
                fetch(url,{
                    method:"POST",
                    headers:{
                        "X-Requested-With":"XMLHttpRequest",
                        "X-CSRFToken":csrf_token,
                    },
                    body:formData,
                })
                .then(response=>response.json())
                .then(data=>{
                    if(data.status==="success"){
                        Swal.fire({
                            icon:"success",
                            text:data.message,
                            confirmButtonText:"关闭",
                            allowOutsideClick:false,
                            allowEscapeKey:false,
                        }).then(result=>{
                            if(result.isConfirmed){
                                window_search_params.set("page",data.page_tag)
                                window.location.href=`${window.location.pathname}?${window_search_params.toString()}`
                            }
                        })
                    }else{
                        throw new Error(data.message);
                    }
                })
                .catch(error=>{
                    Swal.fire("错误",error.message,"error");
                });
            }
        })
    });
};
//导入
function teacher_import(){
    const btn_import=document.getElementById("btn_import")
    btn_import.addEventListener("click",function(){
        Swal.fire({
            title: "选择要导入的文件",
            input: "file",
            inputAttributes: {
                "accept": ".xlsx,.xls",
                "aria-label": "上传老师信息excel文件"
            },
            showCancelButton:true,
            cancelButtonText:"关闭",
            confirmButtonText:"上传",
            showLoaderOnConfirm:true,
            preConfirm:(file)=>{
                if(!file){
                    Swal.fire("warning","请选择要上传的excel文件","warning");
                    return;
                }
                const formData=new FormData();
                const url=btn_import.dataset.url;
                const csrf_token=document.getElementById("csrf_token")?.value;
                formData.append("excel_file",file);
                return fetch(url,{
                    method:"POST",
                    headers:{
                        "X-Requested-With":"XMLHttpRequest",
                        "X-CSRFToken":csrf_token,
                    },
                    body:formData,
                }).then(response=>response.json())
                .then(data=>{
                    if(data.status==="success"){
                        Swal.fire({
                            icon:"success",
                            text:data.message,
                            confirmButtonText:"关闭",
                            allowOutsideClick:false,
                            allowEscapeKey:false,
                        }).then(result=>{
                            if(result.isConfirmed){
                                window.location.reload();
                            }
                        })
                    }else{
                        throw new Error(data.message);
                    }
                })
                .catch(error=>{
                    Swal.showValidationMessage(error.message||error);
                })
            },
            allowOutsideClick:()=> !Swal.isLoading(),
        })
    })
};
//导出
function teacher_export(){
    const btn_export=document.getElementById("btn_export");
    btn_export.addEventListener("click",function(){
        const select=document.querySelector("select[name='grade']");
        let value=""
        if(select.selectedIndex>0){
            value=select.options[select.selectedIndex]?.value;
        }
        const grade_name=select.options[select.selectedIndex]?.textContent;
        const url=btn_export.dataset.url;
        const csrf_token=document.getElementById("csrf_token")?.value;
        let checked=[];
        let teacher_name="";
        document.querySelectorAll("input[name='teacher_ids']:checked").forEach(result=>{
            checked.push(result.value);
            teacher_name+=result.dataset.teacher_name+",";
        })
        if(!value&&(checked.length<1)){
            Swal.fire("提醒","请选择要导出老师信息的对应班级、或选中要导出的数据","warning");
            return;
        }else if(value){
            content=grade_name;
        }else{
            content=teacher_name;
        }
        Swal.fire({
            icon:"warning",
            title:"导出",
            text:"当前选择导出的是"+content,
            showCancelButton:true,
            confirmButtonText:"确定",
            cancelButtonText:"取消",
        }).then(result=>{
            if(result.isConfirmed){
                fetch(url,{
                    method:"POST",
                    headers:{
                        "X-Requested-With":"XMLHttpRequest",
                        "X-CSRFToken":csrf_token,
                        "Content-Type":"application/json",
                    },
    <!--                body:JSON.stringify({value})或者下面这个都行-->
                    body:JSON.stringify({grade:value,checked:checked})
                })
                .then(response=>{
                    console.log(response);
                    if(!response.ok){
                        response.json().then(result=>{
                            Swal.fire({
                                icon:"error",
                                title:"错误",
                                text:"服务器响应错误。"+result.message,
                                confirmButtonText:"好的",
                            });
                        });
                        throw new Error("网络或服务器错误");
                    };
                    return response.blob();
                })
                .then(blob=>{
                    const url=window.URL.createObjectURL(blob);
                    const a=document.createElement("a");
                    document.body.appendChild(a);
                    a.style.display="none";
                    a.href=url;
                    a.download=grade_name+"teacher.xlsx";
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                    Swal.fire("成功","导出成功","success");
                })
                .catch(error=>{
                    Swal.fire("导出失败",error.message,"error");
                })
            }
        })
    })
};