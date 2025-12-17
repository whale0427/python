document.addEventListener("DOMContentLoaded",function(){
    //全选、取消全选
    checked();
    //新增
    score_add();
    //保存
    score_create();
    //编辑
    score_editor();
    //删除
    score_delete();
    //批量删除
    score_bulk_delete();
    //导入
    score_import();
    //导出
    score_export();
    //查看
    score_look();
})
//全选、取消全选
function checked(){
    const select_all=document.getElementById("select_all")
    if(select_all){
        select_all.addEventListener("click",function(){
            document.querySelectorAll("input[name='score_ids']").forEach(check=>{
                check.checked=select_all.checked;
            })
        })
    }

};
//保存并新增下一个
var savenext=0;
function save_next(){
    savenext=1;
};
//新增
function score_add(){
    const btn_add=document.getElementById("btn_add");
    if(!btn_add) return;
    const url=btn_add.dataset.url;
    btn_add.addEventListener("click",function(){
        Swal.fire({
            position:"top-right",
            html:`<iframe src=${url} style="width:100%;height:500px;" frameborder="0"></iframe>`,
            showConfirmButton:false,
        });
    });
};
//保存
function score_create(){
    const saveform=document.querySelector("form.saveform");
    if(!saveform) return;
    const url=saveform.dataset.url;
    const csrf_token=document.querySelector("input[name='csrfmiddlewaretoken']")?.value;
    saveform.addEventListener("submit",function(e){
        const formData=new FormData(saveform);
        e.preventDefault();
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
                Swal.fire({
                    icon:"success",
                    title:"成功",
                    text:data.message,
                    confirmButtonText:"好的",
                    allowOutsideClick:false,
                    allowEscapeKey:false,
                }).then(result=>{
                    if(result.isConfirmed){
                        if(savenext==0){
                            window.parent.location.reload();
                        }else{
                            window.location.reload();
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
                throw new Error(errormessage);
            }
        }).catch(error=>{
            Swal.fire("error",error.message,"error");
        })
    })
};
//编辑
function score_editor(){
    const btn_editors=document.querySelectorAll("#btn_editor");
    btn_editors.forEach(btn_editor=>{
        const url=btn_editor.dataset.url;
        const csrf_token=document.querySelector("input[name='csrfmiddlewaretoken']");
        btn_editor.addEventListener("click",function(e){
            e.preventDefault();
            Swal.fire({
                position:"top-right",
                html:`<iframe src=${url} style="width:100%;height:500px;" frameborder="0"></iframe>`,
                showConfirmButton:false,
            })
        })
    })
};
//删除
function score_delete(){
    const btn_deletes=document.querySelectorAll("#btn_delete");
    const csrf_token=document.querySelector("input[name='csrfmiddlewaretoken']")?.value;
    btn_deletes.forEach(btn_delete=>{
        const url=btn_delete.dataset.url;
        const urlparams=new URLSearchParams(window.location.search);
        btn_delete.addEventListener("click",function(){
            Swal.fire({
                icon:"warning",
                title:"提醒",
                text:"确定是否删除",
                showCancelButton:true,
                confirmButtonText:"确定",
                cancelButtonText:"取消",
            }).then(result=>{
                if(result.isConfirmed){
                    fetch(url,{
                        method:"DELETE",
                        headers:{
                            "X-Requested-With":"XMLHttpRequest",
                            "X-CSRFToken":csrf_token,
                        },
                    }).then(response=>response.json())
                    .then(data=>{
                        if(data.status==="success"){
                            Swal.fire("success",data.message,"success")
                            .then(result=>{
                                urlparams.set("page",data.page_tag);
                                window.location.href=`${window.location.pathname}?${urlparams.toString()}`;
                            });
                        }else{
                            throw new Error(data.message);
                        }
                    })
                    .catch(error=>{
                        Swal.fire("error",error.message,"error");
                    })
                }else{
                    return;
                }
            })
        })
    })
};
//批量删除
function score_bulk_delete(){
    const btn_delete_all=document.getElementById("btn_delete_all");
    btn_delete_all.addEventListener("click",function(){
        const checkeds=document.querySelectorAll("input[name='score_ids']:checked");
        if(checkeds){
            Swal.fire({
                icon:"warning",
                title:"提醒",
                text:"确认是否删除",
                showCancelButton:true,
                confirmButtonText:"确认",
                cancelButtonText:"关闭",
            }).then(result=>{
                if(result.isConfirmed){
                    const url=btn_delete_all.dataset.url;
                    const csrf_token=document.querySelector("input[name='csrfmiddlewaretoken']")?.value;
                    const formData=new FormData();
                    checkeds.forEach(check=>{
                        formData.append(check.name,check.value);
                    });
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
                            Swal.fire("success",data.message,"success")
                            .then(result=>{
                                if(result.isConfirmed){
                                    const url_params=new URLSearchParams(window.location.search);
                                    url_params.set("page",data.page_tag);
                                    window.location.href=`${window.location.pathname}?${url_params.toString()}`
                                }
                            })
                        }else{
                            throw new Error(data.message);
                        }
                    })
                    .catch(error=>{
                        Swal.fire("error","哈哈"+error.message,"error");
                    })
                }
            })
        }else{
            Swal.fire("error","请选择要删除的数据","error");
        }
    })
};
//导入
function score_import(){
    const btn_import=document.getElementById("btn_import");
    btn_import.addEventListener("click",function(){
        Swal.fire({
            title: "导入文件",
            input: "file",
            inputAttributes: {
                "accept": ".xlsx,.xls",
                "aria-label": "请上传excel文件"
            },
            showCancelButton:true,
            confirmButtonText:"上传",
            cancelButtonText:"关闭",
            allowEscapeKey:false,
            showLoaderOnConfirm:true,
            preConfirm:(file)=>{
                const url=btn_import.dataset.url;
                const csrf_token=document.querySelector("input[name='csrfmiddlewaretoken']")?.value;
                const formData=new FormData();
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
                        Swal.fire("success",data.message,"success")
                        .then(result=>{
                            window.location.reload();
                        })
                    }else{
                        throw new Error(data.message);
                    }
                })
                .catch(error=>{
                    Swal.fire("error",error.message,"error");
                });
            },
            allowOutsideClick:()=> !Swal.isLoading(),
        })
    })
};
//导出
function score_export(){
    const btn_export=document.getElementById("btn_export");
    btn_export.addEventListener("click",function(){
        const select=document.querySelector("select[name='grade']");
        const grade_id=select.options[select.selectedIndex]?.value;
        const grade_name=select.options[select.selectedIndex]?.text;
        let checked=[];
        let score_student_name="";
        document.querySelectorAll("input[name='score_ids']:checked").forEach(result=>{
            checked.push(result.value);
            score_student_name+=result.dataset.score_student_name+",";
        });
        if(!grade_id&&(checked.length<1)){
            Swal.fire("error","请选择要导出的班级成绩、或选中要导出的数据","error");
            return;
        }else if(grade_id){
            content=grade_name;
        }else{
            content=score_student_name;
        }
        Swal.fire({
            icon:"question",
            title:"导出",
            text:"确认是否导出"+content+"的成绩",
            showCancelButton:true,
            confirmButtonText:"确认",
            cancelButtonText:"取消",
        }).then(result=>{
            if(result.isConfirmed){
                const url=btn_export.dataset.url;
                const csrf_token=document.querySelector("input[name='csrfmiddlewaretoken']")?.value;
                fetch(url,{
                    method:"POST",
                    headers:{
                        "X-Requested-With":"XMLHttpRequest",
                        "X-CSRFToken":csrf_token,
                        "Content-Type":"application/json",
                        "Content-Type":"application/json",
                    },
                    body:JSON.stringify({grade_id,checked}),
                }).then(response=>{
                    if(!response.ok){
                        throw new Error("服务器或网络错误，请稍后再试");
                    };
                    return response.blob();
                }).then(blob=>{
                    const blob_url=window.URL.createObjectURL(blob);
                    const a=document.createElement("a");
                    document.body.appendChild(a);
                    a.style.display="none";
                    a.href=blob_url;
                    a.download=content.slice(0,8)+"成绩.xlsx";
                    a.click();
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(blob_url);
                }).catch(error=>{
                    Swal.fire("error",error.message,"error");
                })
            }
        })
    })
};
//查看
function score_look(){
    const btn_look=document.querySelectorAll("#btn_look");
    btn_look.forEach(result=>{
        result.addEventListener("click",function(){
            const url=result.dataset.url;
            Swal.fire({
                html:`<iframe src=${url} style="width:100%;height:300px;" frameborder="0"></iframe>`,
                showConfirmButton:false,
            })
        });
    });
};