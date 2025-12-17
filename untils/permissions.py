from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy

def role_required(*allowed_roles):
    def decorator(func):
        def _authenticate_user(request,*args,**kwargs):
            user_role=request.session.get("user_role")
            if request.user.is_authenticated and user_role in allowed_roles:
                return func(request, *args,**kwargs)
            else:
                #两种方式都可以返回登录页面，但是第二种最好
                # 直接返回一个 HTTP 200 响应，原本地址栏的URL不会发生变化；属于同一次 HTTP 请求的响应，没有新的请求产生。
                # return render(request,"accounts/login.html")
                #返回一个 HTTP 302 重定向响应，原本地址栏的URL会变成目标URL；会产生两次 HTTP 请求（第一次是当前请求，返回 302；第二次是浏览器请求目标 URL）。
                return HttpResponseRedirect(reverse_lazy("user_login"))
        return _authenticate_user
    return decorator

class RoleRequiredMixin(AccessMixin):
    allowed_roles=[]

    def dispatch(self,request,*args,**kwargs):
        disp=super().dispatch(request,*args,**kwargs)
        if not request.user.is_authenticated:
            # 调用AccessMixin提供的handle_no_permission方法（默认会返回 403 禁止访问，或跳转到登录页）。
            # 如果settings里面配置了LOGIN_URL，那么用户未登录，Django 会自动重定向到LOGIN_URL对应的页面。
            #Django的LOGIN_URL是'/accounts/login/'（这是 Django 内置的默认登录页路径），所以要看情况去该这个配置
            return self.handle_no_permission()

        user_role=request.session.get("user_role")

        if not (request.user.is_superuser == 1 or user_role in self.allowed_roles):
            #如果角色不允许，重定向到登录页（reverse_lazy是 Django 中反向解析 URL 的方法）
            return HttpResponseRedirect(reverse_lazy("user_login"))
        return disp