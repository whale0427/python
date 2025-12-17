from io import BytesIO
from pathlib import Path

from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView,CreateView,UpdateView,DeleteView
import json,openpyxl

from untils.permissions import RoleRequiredMixin, role_required
from .models import Teachers
from .forms import TeachersForm
import datetime
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from grades.models import Grades
from untils.handle_excel import ReadExcel

# Create your views here.
class BaseTeacherView(RoleRequiredMixin):
    allowed_roles=["admin"]

class TeacherListView(BaseTeacherView,ListView):
    model=Teachers
    template_name="teachers/teacher_list.html"
    context_object_name="teachers"
    paginate_by=10

    def get_context_data(self,*args,**kwargs):
        context_data=super().get_context_data()
        context_data["grades"]=Grades.objects.all().order_by("grade_code")
        current=self.request.GET.get("grade")
        context_data["current"]=int(current) if current else ""
        return context_data

    def get_queryset(self,*args,**kwargs):
        queryset=super().get_queryset()
        search=self.request.GET.get("search")
        grade=self.request.GET.get("grade")
        if grade:
            queryset=queryset.filter(Q(grade=grade))
        if search:
            queryset=queryset.filter(Q(teacher_name__contains=search)|
                                     Q(phone__contains=search))
        return queryset

class TeacherCreateView(BaseTeacherView,CreateView):
    model=Teachers
    template_name="teachers/teacher_form.html"
    form_class=TeachersForm

    def form_valid(self,form):
        phone=form.cleaned_data["phone"]
        username="teacher"+phone
        password=phone[-6:]
        users=User.objects.filter(username=username)
        if users.exists():
            user=users.first()
        else:
            user=User.objects.create_user(username=username,password=password)
        form.instance.user=user
        form.save()

        return JsonResponse({
            "status":"success",
            "message":"保存成功"
        },status=200)

    def form_invalid(self,form):
        errors=form.errors.as_json()
        return JsonResponse({
            "status":"error",
            "message":errors,
        },status=400)

class TeacherUpdateView(BaseTeacherView,UpdateView):
    model=Teachers
    template_name="teachers/teacher_form.html"
    form_class=TeachersForm

    def form_valid(self,form):
        students=form.save(commit=False)
        phone=form.cleaned_data["phone"]
        username="teacher"+phone
        password=make_password(phone[-6:])
        if "phone" in form.changed_data:
            students.user.username=username
            students.user.password=password
            students.user.save()
        students.save()

        return JsonResponse({
            "status":"success",
            "message":"修改成功",
        },status=200)

    def form_invalid(self,form):
        errors=form.errors.as_json()
        return JsonResponse({
            "status":"error",
            "message":errors,
        },status=400)

class TeacherDeleteView(BaseTeacherView,DeleteView):
    model=Teachers
    success_url=reverse_lazy("teacher_list")
    def delete(self, request, *args, **kwargs):
        self.object=self.get_object()
        try:
            # 先记录当前页码（从请求参数中获取，默认是1）
            current_page = int(request.GET.get('page', 1))
            # 每页显示的条数（根据你的实际分页配置修改，比如这里假设是10条）
            per_page = 10

            self.object.user.delete()
            self.object.delete()

            # 重新查询所有教师数据，计算新的分页信息
            all_teachers = Teachers.objects.all()
            paginator = Paginator(all_teachers, per_page)
            total_pages = paginator.num_pages
            # 计算目标页码：如果当前页大于总页数（说明当前页是最后一页且删除后无数据），则跳转到上一页
            target_page = current_page if current_page <= total_pages else (current_page - 1) if (current_page - 1) >= 1 else 1

            return JsonResponse({
                "status":"success",
                "message":"删除成功",
                "target_page": target_page,  # 返回目标页码
            },status=200)
        except Exception as e:
            return JsonResponse({
                "status":"error",
                "message":"删除错误，"+str(e),
            },status=400)

class TeacherBulkDeleteView(BaseTeacherView,DeleteView):
    model=Teachers
    success_url=reverse_lazy("teacher_list")

    def post(self,request,*args,**kwargs):
        checks=request.POST.getlist("teacher_ids")
        if not checks:
            return JsonResponse({
                "status":"error",
                "message":"请选择要删除的数据",
            },status=400)
        current_page = int(request.GET.get("page", 1))
        page_by=10
        teachers=Teachers.objects.all()
        paginator=Paginator(teachers,page_by)
        page_tag=current_page if current_page<=paginator.num_pages else (current_page-1) if (current_page-1)>=1 else 1
        teachers = self.get_queryset().filter(pk__in=checks)
        try:
            for teacher in teachers:
                teacher.user.delete()
                teacher.delete()
        except Exception as e:
            return JsonResponse({
                "status":"error",
                "message":"删除失败，"+str(e),
            })
        return JsonResponse({
            "status":"success",
            "message":"删除成功",
            "page_tag":page_tag,
        },status=200)

@role_required("admin")
def teacher_import(request):
    if request.method=="POST":
        excel_file=request.FILES.get("excel_file")
        if not excel_file:
            return JsonResponse({
                "status": "error",
                "message": "请上传老师信息excel文件"
            }, status=400)
        ext=Path(excel_file.name).suffix
        excel_suffix=[".xlsx",".xls"]
        if ext.lower() not in excel_suffix:
            return JsonResponse({
                "status": "error",
                "message": "上传的文件必须是excel类型"
            }, status=400)
        datas=ReadExcel(excel_file).get_data()
        if datas[0]!=["姓名","班级","电话","性别","生日"]:
            return JsonResponse({
                "status":"error",
                "message":"上传的excel文件内容的表头格式不正确"
            },status=400)
        for row in datas[1:]:
            teacher_name,grade,phone,gender,birthday=row
            phone=str(phone)

            if len(teacher_name) <2 or len(teacher_name)>50:
                return JsonResponse({"status":"error","message":f"{teacher_name}的姓名长度不符合规范（2-50）"},
                                    status=400)
            if len(phone)!=11:
                return JsonResponse({"status": "error", "message": f"{teacher_name}的电话长度不为11位"},
                                    status=400)
            if not Grades.objects.get(grade_name=grade):
                return JsonResponse({"status": "error", "message": f"{teacher_name}的班级不存在"},
                                    status=400)
            if len(gender)!=1:
                return JsonResponse({"status": "error", "message": f"{teacher_name}的性别不允许为空"},
                                    status=400)
            if not isinstance(birthday,datetime.date):
                return JsonResponse({"status": "error", "message": f"{teacher_name}的生日格式不对，应为：YYYY-MM-DD"},
                                    status=400)
            try:
                username = "teacher" + phone[-6:]
                password = phone[-6:]
                user = User.objects.filter(username=username).first()
                grade=Grades.objects.get(grade_name=grade)
                if not user:
                    user=User.objects.create_user(username=username,password=password)
                Teachers.objects.create(
                    teacher_name=teacher_name,
                    phone=phone,
                    gender="M" if gender=="男" else "F",
                    birthday=birthday,
                    user=user,
                    grade=grade,
                )
            except Exception as e:
                return JsonResponse({
                    "status": "error",
                    "message": "上传失败，" + str(e),
                }, status=500)
        return JsonResponse({"status": "success", "message": "上传成功"}, status=200)

@role_required("admin")
def teacher_export(request):
    if request.method=="POST":
        data=json.loads(request.body)
        grade_id=data.get("grade")
        checked=data.get("checked")
        print(checked)
        if grade_id:
            grade=Grades.objects.get(pk=grade_id)
            if not grade:
                return JsonResponse({"status":"error","message":"班级参数不存在"},status=404)
            teachers = Teachers.objects.filter(grade=grade_id)
            if not teachers.exists():
                return JsonResponse({"status": "error", "message": "该班级目前没有老师"}, status=404)
            workbook=openpyxl.Workbook()
            worksheet=workbook.active
            worksheet.append(["姓名","班级","电话","性别","生日"])
            for teacher in teachers:
                if teacher.gender == "M":
                    teacher.gender = "男"
                else:
                    teacher.gender = "女"
                worksheet.append([teacher.teacher_name,teacher.grade.grade_name,teacher.phone,teacher.gender,teacher.birthday])
            excel_file=BytesIO()
            workbook.save(excel_file)
            workbook.close()
            excel_file.seek(0)
            response=HttpResponse(excel_file.read(),content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"]="attachment;filename='teacher.xlsx'"
            return response
        elif checked:
            teachers=Teachers.objects.filter(pk__in=checked)
            if not teachers.exists():
                return JsonResponse({"status": "error", "message": "老师姓名参数不存在"}, status=404)
            workbook = openpyxl.Workbook()
            worksheet = workbook.active
            worksheet.append(["姓名", "班级", "电话", "性别", "生日"])
            for teacher in teachers:
                if teacher.gender == "M":
                    teacher.gender = "男"
                else:
                    teacher.gender = "女"
                worksheet.append(
                    [teacher.teacher_name, teacher.grade.grade_name, teacher.phone, teacher.gender, teacher.birthday])
            excel_file = BytesIO()
            workbook.save(excel_file)
            workbook.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = "attachment;filename='teacher.xlsx'"
            return response
    return JsonResponse({"status": "error", "message": "请求资源错误"}, status=500)
