from pathlib import Path
import json
import openpyxl
from io import BytesIO

from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView,CreateView,UpdateView,DeleteView

from untils.permissions import RoleRequiredMixin
from .models import Students
from grades.models import Grades
from .forms import StudentsForm
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import datetime
from untils.handle_excel import WriteExcel,ReadExcel
from scores.models import Scores
from scores.forms import ScoresForm


# Create your views here.
class BaseStudentView(RoleRequiredMixin):
    allowed_roles=["admin","teacher","student"]

class StudentListView(BaseStudentView,ListView):
    model=Students
    template_name="students/student_list.html"
    context_object_name="students"
    paginate_by=10

    def get_queryset(self):
        queryset = super().get_queryset()
        grade_id = self.request.GET.get("grade")
        search = self.request.GET.get("search")
        if grade_id:
            #可以用grade，也可以用grade_pk，只是如果方便查看外键或者主键关系就用id或者pk
            queryset = queryset.filter(Q(grade=grade_id))
        if search:
            queryset = queryset.filter(Q(student_name__contains=search) | Q(student_number__contains=search))
        return queryset

    def get_context_data(self,*args,**kwargs):
        context=super().get_context_data()
        context["grades"]=Grades.objects.all().order_by("grade_code")
        # 避免没有传grade参数导致出现int(None)，所以单独领出来赋值，然后来判断是否为空，如果空就传None，不空就转换int类型
        #转换int是为了前端判断用
        grade=self.request.GET.get("grade")
        context["current"]=int(grade) if grade else None
        return context

class StudentCreateView(BaseStudentView,CreateView):
    model=Students
    template_name="students/student_form.html"
    form_class=StudentsForm

    #forms.py没有抛出异常错误，就会调用form_valid
    #post请求会进入这里
    def form_valid(self,form):
        # 表单字段处理
        student_name = form.cleaned_data["student_name"]
        student_number = form.cleaned_data["student_number"]
        username="student"+student_number
        password = student_number[-6:]
        # 判断auth_user是否有对应的数据
        users = User.objects.filter(username=username)
        if users.exists():
            #如果有，获取第一条数据；这样写的目的是因为users是集合，就算只有一条记录也是集合
            user = users.first()
        else:
            #如果没有，就用django给auth_user自带的create_user查询方法
            user = User.objects.create_user(username=username, password=password)
        # 同步到students表的user字段
        #form.instance就是Students()空的实例模型
        form.instance.user = user
        # 只有form_class存在的时候，才需要form.save()保存更新到数据库
        # 保存到数据库
        form.save()

        #返回JSON响应
        return JsonResponse({
            "status":"success",
            "message":"操作成功"
        },status=200)

    #处理错误信息,forms.py抛出异常错误，就会调用form_invalid
    def form_invalid(self,form):
        errors=form.errors.as_json()
        return JsonResponse({
            "status":"error",
            "message":errors,
        },status=400)

class StudentScoreCreateView(BaseStudentView,CreateView):
    model=Students
    template_name = "scores/score_form.html"
    form_class=ScoresForm

    def get_initial(self):
        initial = super().get_initial()
        student_pk = self.kwargs.get('pk')
        if student_pk:
            try:
                student = Students.objects.get(pk=student_pk)
                initial['student_name'] = student.student_name
                initial['student_number'] = student.student_number
            except Students.DoesNotExist:
                pass
        return initial

    def get_context_data(self,*args,**kwargs):
        context=super().get_context_data()
        context["ceshi"]=1
        return context

    def form_valid(self,form,*args,**kwargs):
        self.object=self.get_object()
        form.instance.student = self.object
        form.save()
        return JsonResponse({"status":"success","message":"操作成功"},status=200)

    def form_invalid(self,form):
        errors=form.errors.as_json()
        return JsonResponse({"status":"error","message":errors,},status=400)

class StudentUpdateView(BaseStudentView,UpdateView):
    model=Students
    template_name="students/student_form.html"
    form_class=StudentsForm

    def form_valid(self, form):
        # 获取student实例对象，但是不保存到数据库
        student = form.save(commit=False)
        student_number = form.cleaned_data["student_number"]
        #判断student_name是否在更改的数据集里
        if 'student_number' in form.changed_data:
            student.user.username = datetime.date.today().strftime("%Y%m%d") + student_number
            #用django自带的方法进行加密
            student.user.password = make_password(student_number[-6:])
            # 将更改的数据保存到user模型（这是自带的模型）
            student.user.save()
        # 将数据保存到students模型
        student.save()

        return JsonResponse({
            "status": "success",
            "message": "操作成功",
        }, status=200)

    def form_invalid(self, form):
        errors=form.errors.as_json()
        return JsonResponse({
            "status": "error",
            "message": errors,
        }, status=400)

class StudentDeleteView(BaseStudentView,DeleteView):
    model=Students
    success_url=reverse_lazy("student_list")
    #delete请求会进入这里
    def delete(self,request,*args,**kwargs):
        #获取具体传的是什么数据库实例的单个对象
        #self.get_object()相当于是Students.objects.get(pk=1)
        #self.object就是自定义的属性名称，可以随便改名
        self.object=self.get_object()
        #异常处理，如果删除的单个对象不存在，异常处理
        try:
            self.object.user.delete()
            self.object.delete()
            return JsonResponse({
                "status":"success",
                "message":"删除成功",
            },status=200)
        except Exception as e:
            return JsonResponse({
                "status":"error",
                "message":"删除失败，"+str(e),
            },status=500)

class StudentBulkDeleteView(BaseStudentView,DeleteView):
    model=Students
    success_url=reverse_lazy("student_list")
    #批量删除用post
    def post(self,request,*args,**kwargs):
        selectids=request.POST.getlist("student_ids")
        if not selectids:
            return JsonResponse({
                "status":"error",
                "message":"请选择要删除的数据",
            })
        self.objectlist=self.get_queryset().filter(pk__in=selectids)

        try:
            for self.object in self.objectlist:
                self.object.user.delete()
                self.object.delete()
            return JsonResponse({
                "status":"success",
                "message":"批量删除成功",
            },status=200)
        except Exception as e:
            return JsonResponse({
                "status":"error",
                "message":"批量删除失败，"+str(e),
            },status=500)

def student_excel_import(request):
    if request.method=="POST":
        files=request.FILES.get("excel_file")
        #判断文件是否上传
        if not files:
            return JsonResponse({
                "status":"error",
                "message":"请上传学生信息excel文件"
            },status=400)
        ext=Path(files.name).suffix
        suffixs=[".xlsx",".xls"]
        #判断是否excel文件
        if ext.lower() not in suffixs:
            return JsonResponse({
                "status":"error",
                "message":"文件类型错误，请上传格式为.xlsx或者.xls文件"
            },status=400)

        read_excel=ReadExcel(files)
        datas=read_excel.get_data()
        genders=["男","女"]
        if datas[0] != ["班级","学号","姓名","性别","生日","电话","地址"]:
            return JsonResponse({"status":"error","message":"文件内格式不正确，请调整格式之后重新上传"},status=400)
        for row in datas[1:]:
            grade_name,student_number,student_name,gender,birthday,phone,address=row
            student_number=str(student_number)
            phone = str(phone)
            if not Grades.objects.filter(grade_name=grade_name).exists():
                return JsonResponse({"status":"error","message":f"{student_number}的{grade_name}班级不存在，请修改之后重新上传"},status=400)
            if Students.objects.filter(student_number=student_number).exists():
                return JsonResponse({"status":"error","message":f"{student_number}的学号已存在，请修改之后重新上传"},status=400)
            if len(student_number) !=10:
                return JsonResponse({"status": "error", "message": f"学号为{student_number}的学号长度必须为10位"}, status=400)
            if len(student_name) <2 or len(student_name) >50:
                return JsonResponse({"status": "error", "message": f"学号为{student_number}的姓名长度不符合规范（2-50）"}, status=400)
            if len(gender) !=1 and gender not in genders:
                return JsonResponse({"status": "error", "message": f"学号为{student_number}的性别不允许为空或者内容有误"}, status=400)
            if not isinstance(birthday,datetime.date):
                return JsonResponse({"status": "error", "message": f"学号为{student_number}的生日格式不对，应为YYYY-MM-DD"}, status=400)
            if birthday.date() > datetime.date.today():
                return JsonResponse({"status": "error", "message": f"学号为{student_number}的生日要在今天之前"}, status=400)
            if len(phone)!=11:
                return JsonResponse({"status": "error", "message": f"学号为{student_number}的电话长度必须为11位"}, status=400)
            if not ("省" in address and "市" in address):
                return JsonResponse({"status": "error", "message": f"学号为{student_number}的地址必须包含省、市"}, status=400)
            print("-" * 10)
            print(row)
            print("-" * 10)
            try:
                username=datetime.date.today().strftime("%Y%m%d")+student_number
                password=student_number[-6:]
                user=User.objects.filter(username=username).first()
                grade=Grades.objects.get(grade_name=grade_name)
                if not user:
                    user=User.objects.create_user(username=username,password=password)
                Students.objects.create(
                    student_number=student_number,
                    student_name=student_name,
                    gender="M" if gender=="男" else "F",
                    birthday=birthday.date(),
                    phone=phone,
                    address=address,
                    user=user,
                    grade=grade,
                )
            except Exception as e:
                return JsonResponse({
                    "status":"error",
                    "message":"上传失败，"+str(e),
                },status=500)
        return JsonResponse({"status":"success","message":"上传成功"},status=200)

def student_excel_export(request):
    if request.method=="POST":
        #不能用get获取属性，因为前端传的是json数据不是表单数据，得用json.loads()
        data=json.loads(request.body)
        grade_id=data.get("grade")
        if not grade_id:
            return JsonResponse({
                "status":"error",
                "message":"班级参数缺失"
            },status=400)
        try:
            grade=Grades.objects.get(pk=grade_id)
        except Grades.DoesNoExist:
            return JsonResponse({
                "status":"error",
                "message":"班级不存在",
            },status=404)
        students=Students.objects.filter(grade=grade_id)
        if not students.exists():
            return JsonResponse({"status":"error","message":"该班级目前没有学生"},status=404)

        workbook=openpyxl.Workbook()
        worksheet=workbook.active

        row_title=["班级","学号","姓名","性别","生日","电话","地址"]
        worksheet.append(row_title)

        for student in students:
            if student.gender=="M":
                student.gender="男"
            else:
                student.gender="女"

            worksheet.append([student.grade.grade_name,student.student_number,student.student_name,
                              student.gender,student.birthday,student.phone,student.address])

        # 创建一个内存中的二进制文件对象
        excel_file = BytesIO()
        # 将Excel工作簿保存到内存文件对象
        workbook.save(excel_file)
        # 关闭工作簿，释放资源
        workbook.close()
        # 将文件指针移动到开头位置
        excel_file.seek(0)
        # excel_file.read()：从当前位置（开头）读取整个缓冲区内容
        # content_type设置响应的MIME类型，告诉浏览器这是Excel文件；
        # "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"是.xlsx文件的MIME类型
        response = HttpResponse(excel_file.read(),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        # 设置HTTP响应头，控制文件下载行为。如果没有这个头部，某些浏览器可能尝试在页面内打开Excel
        # Content-Disposition 是HTTP头部字段
        # attachment;告诉浏览器以附件形式处理，即下载文件而不是在页面打开
        # filename='students.xlsx'：指定下载时的默认文件名
        response["Content-Disposition"] = "attachment;filename='students.xlsx'"
        return response
