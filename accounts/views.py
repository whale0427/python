from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import LoginForm
from teachers.models import Teachers
from students.models import Students

# Create your views here.
def user_login(request):
    if request.method=="POST":
        form_class=LoginForm(request.POST)
        #处理验证失败
        if not form_class.is_valid():
            errors=form_class.errors.as_json()
            return JsonResponse({"status": "error", "message": errors}, status=400)
        #处理验证成功
        username=form_class.cleaned_data["username"]
        password=form_class.cleaned_data["password"]
        role=form_class.cleaned_data["role"]
        request.session["user_name"] = username

        # # 新增：获取是否记住密码的参数（前端传的是字符串，需要转布尔）
        # remember_me = request.POST.get("remember_password", "false") == "true"

        if role=="teacher":
            try:
                teacher=Teachers.objects.get(phone=username)
                username = "teacher" + username
                user=authenticate(username=username,password=password)
            except Teachers.DoesNotExist:
                return JsonResponse({"status":"error","message":"老师信息不存在"},status=404)
        elif role=="student":
            try:
                student=Students.objects.get(student_number=username)
                username = "student" + username
                user=authenticate(username=username,password=password)
            except Students.DoesNotExist:
                return JsonResponse({"status": "error", "message": "学生信息不存在"}, status=404)
        else:
            try:
                user=authenticate(username=username,password=password)
            except User.DoesNotExist:
                return JsonResponse({"status": "error", "message": "管理员信息不存在"}, status=404)
        if user:
            if user.is_active==1:
                #将已验证(authenticate)的用户与当前(session)会话绑定，建立用户的登录状态
                #作用：将user与当前session绑定，设置登录cookie/session
                login(request,user)
                # # 新增：处理记住密码的逻辑
                # if remember_me:
                #     # 设置session过期时间为7天（60*60*24*7秒）
                #     request.session.set_expiry(60 * 60 * 24 * 7)
                # else:
                #     # 不记住：浏览器关闭后失效（默认行为）
                #     request.session.set_expiry(0)
                request.session["user_role"]=role
                return JsonResponse({"status":"success","message":"登录成功","role":role},status=200)
            else:
                return JsonResponse({"status": "error", "message": "当前用户已被禁用"}, status=403)
        else:
            return JsonResponse({"status": "error", "message": "用户名或密码错误"}, status=404)
    return render(request,"accounts/login.html")

def user_logout(request):
    # if 'user_role' in request.session:
    #     del request.session["user_role"]
    request.session.flush()
    logout(request)
    return redirect("user_login")

def change_password(request):
    if request.method=="POST":
        #PasswordChangeForm是Django内置的密码修改表单类（来自django.contrib.auth.forms）
        # 专门用于处理用户修改密码的逻辑，包含了密码验证的规则（比如旧密码是否正确、新密码是否符合复杂度要求等）
        #request对象的user属性，代表当前登录的用户对象（Django 的认证系统会自动将登录用户绑定到request.user）
        # PasswordChangeForm的第一个参数必须是用户对象，因为需要验证该用户的旧密码。
        #request对象的POST属性，是一个类似字典的对象，包含了用户通过表单提交的所有 POST 数据（比如旧密码、新密码、确认新密码）
        form_class=PasswordChangeForm(request.user,request.POST)
        if not form_class.is_valid():
            errors=form_class.errors.as_json()
            return JsonResponse({"status": "error", "message": errors}, status=400)
        #调用表单实例的save()方法，该方法会执行密码修改的逻辑（将用户的密码更新为新密码，并保存到数据库），返回修改后的用户对象。
        user=form_class.save()
        #用于更新用户的会话认证哈希。update_session_auth_hash(当前的请求对象, 修改后的用户对象)
        update_session_auth_hash(request, user)
        return JsonResponse({"status": "success", "message": "密码修改成功"}, status=200)
    return render(request,"accounts/change_password.html")