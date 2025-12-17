import json
from io import BytesIO
from pathlib import Path
import re
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView,UpdateView,DeleteView
from openpyxl import Workbook

from untils.permissions import RoleRequiredMixin
from .forms import ScoresForm
from .models import Scores
from students.models import Students
from grades.models import Grades
from untils.handle_excel import ReadExcel

# Create your views here.
class BaseScoreView(RoleRequiredMixin):
    allowed_roles=["admin","teacher"]

class ScoreListView(BaseScoreView,ListView):
    model=Scores
    template_name="scores/score_list.html"
    context_object_name="scores"
    paginate_by=10

    def get_queryset(self):
        queryset=super().get_queryset()
        queryset=Scores.objects.all().order_by("pk")
        search=self.request.GET.get("search")
        grade_id=self.request.GET.get("grade")
        if search:
            queryset=Scores.objects.filter(Q(student_name__contains=search)|
                                           Q(student_number__contains=search)).order_by("pk")
        if grade_id:
            queryset=Scores.objects.filter(grade=grade_id).order_by("pk")
        return queryset

    def get_context_data(self):
        context_data=super().get_context_data()
        context_data["grades"]=Grades.objects.all().order_by("pk")
        current=self.request.GET.get("grade")
        context_data["current"]=int(current) if current else None
        return context_data

class ScoreCreateView(BaseScoreView,CreateView):
    model=Scores
    template_name="scores/score_form.html"
    form_class=ScoresForm
    success_url=reverse_lazy("score_list")

    def form_valid(self,form):
        student_number=form.cleaned_data["student_number"]
        student=Students.objects.get(student_number=student_number)
        form.instance.student=student
        form.instance.grade=student.grade
        form.save()
        return JsonResponse({"status":"success","message":"保存成功"},status=200)

    def form_invalid(self,form):
        errors=form.errors.as_json()
        return JsonResponse({"status":"error","message":errors},status=400)

class ScoreUpdateView(BaseScoreView,UpdateView):
    model=Scores
    template_name="scores/score_form.html"
    form_class=ScoresForm
    success_url=reverse_lazy("score_list")

    def form_valid(self,form):
        form.save()
        return JsonResponse({"status":"success","message":"保存成功"},status=200)

    def form_invalid(self,form):
        errors=form.errors.as_json()
        return JsonResponse({"status":"error","message":errors},status=400)

class ScoreDeleteView(BaseScoreView,DeleteView):
    model=Scores
    success_url=reverse_lazy("score_list")

    def delete(self,request,*args,**kwargs):
        self.object=self.get_object()
        current=int(request.GET.get("page",1))
        if self.object:
            try:
                self.object.delete()
                page_by=10
                scores=Scores.objects.all()
                paginator=Paginator(scores,page_by)
                page_tag=current if current<=paginator.num_pages else (current-1) if (current-1)>0 else 1
                return JsonResponse({
                    "status":"success",
                    "message":"删除成功",
                    "page_tag":page_tag,
                },status=200)
            except Exception as e:
                return JsonResponse({"status":"error","message":str(e)},status=400)
        else:
            return JsonResponse({"status":"error","message":"删除的数据本身就不存在，请刷新页面"},status=404)

class ScoreBulkDeleteView(BaseScoreView,DeleteView):
    model=Scores
    success_url=reverse_lazy("score_list")

    def post(self,request,*args,**kwargs):
        score_ids=request.POST.getlist("score_ids",None)
        if not score_ids:
            return JsonResponse({"status":"error","message":"数据不存在，请重新选择要删除的数据"},status=404)
        scores=self.get_queryset().filter(pk__in=score_ids)
        try:
            for score in scores:
                score.delete()
            current = request.GET.get("page", 1)
            scores=Scores.objects.all()
            page_by=10
            paginator = Paginator(scores,page_by)
            page_tag=current if current<=paginator.num_pages else (current-1) if (current-1)>0 else 1
            return JsonResponse({
                "status":"success",
                "message":"删除成功",
                "page_tag":page_tag,
            },status=200)
        except Exception as e:
            return JsonResponse({"status":"error","message":str(e)},status=400)

def score_import(request):
    if request.method == "POST":
        excel_file=request.FILES.get("excel_file")
        if not excel_file:
            return JsonResponse({"status":"error","message":"请选择文件上传"},status=404)
        ext=Path(excel_file.name).suffix
        suffixs=[".xlsx","xls"]
        if ext.lower() not in suffixs:
            return JsonResponse({"status":"error","message":"请上传excel文件"},status=400)
        read_excel=ReadExcel(excel_file)
        datas=read_excel.get_data()
        if not datas:
            return JsonResponse({"status":"error","message":"文件内容为空，请填写内容重新上传"},status=400)
        if datas[0] != ["考试名称","学生姓名","学号","语文","数学","英语","班级"]:
            return JsonResponse({"status":"error","message":"内容格式不对，应为（考试名称,学生姓名,学号,语文,数学,英语,班级）"},status=400)

        for row in datas[1:]:
            title,student_name,student_number,chinese_score,math_score,english_score,grade=row
            chinese_score=str(chinese_score)
            math_score=str(math_score)
            english_score=str(english_score)
            student=Students.objects.get(student_number=student_number)
            if not student:
                return JsonResponse({"status":"error","message":f"学号{student_name}不存在"},status=400)
            if student_name!=student.student_name:
                return JsonResponse({"status": "error", "message": f"学号{student_number}的姓名有误"}, status=400)
            pattern = r"^(\d{1,3})$|^(\d{1,3}\.\d{1})$"
            if not re.match(pattern,chinese_score):
                return JsonResponse({"status": "error", "message": f"姓名{student_name}的语文成绩格式有误，应为000.0或者1-3位数"}, status=400)
            if not re.match(pattern,math_score):
                return JsonResponse({"status": "error", "message": f"姓名{student_name}的数学成绩格式有误，应为000.0或者1-3位数"}, status=400)
            if not re.match(pattern,english_score):
                return JsonResponse({"status": "error", "message": f"姓名{student_name}的英语成绩格式有误，应为000.0或者1-3位数"}, status=400)
            grade=Grades.objects.get(grade_name=grade)
            if not grade:
                return JsonResponse({"status": "error", "message": f"姓名{student_name}的班级不存在"}, status=400)
            print(title,student_name,student_number,chinese_score,math_score,english_score,grade)
            try:
                Scores.objects.create(
                    title=title,
                    student_name=student_name,
                    student_number=student_number,
                    chinese_score=chinese_score,
                    math_score=math_score,
                    english_score=english_score,
                    student=student,
                    grade=grade
                )
            except Exception as e:
                return JsonResponse({"status":"error","message":"导入失败"+str(e)},status=400)
        return JsonResponse({"status":"success","message":"导入成功"},status=200)

def score_export(request):
    if request.method == "POST":
        grade_id=json.loads(request.body)["grade_id"]
        checked =json.loads(request.body)["checked"]
        if grade_id:
            grade = Grades.objects.get(pk=grade_id)
            if not grade:
                return JsonResponse({"status":"error","message":"班级参数缺失"},status=404)
            scores=Scores.objects.filter(grade=grade_id).order_by("pk")
            if not scores:
                return JsonResponse({"status":"error","message":"当前班级没有学生成绩数据"},status=404)
            workbook=Workbook()
            worksheet=workbook.active
            worksheet.append(["考试名称","学生姓名","学号","语文","数学","英语","班级"])
            for score in scores:
                worksheet.append([score.title,score.student_name,score.student_number,score.chinese_score,
                                  score.math_score,score.english_score,score.grade.grade_name])
            excel_file=BytesIO()
            workbook.save(excel_file)
            workbook.close()
            excel_file.seek(0)
            response=HttpResponse(excel_file.read(),content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"]="attachment;filename='score.xlsx'"
            return response
        elif checked:
            scores=Scores.objects.filter(pk__in=checked).order_by("pk")
            if not scores:
                return JsonResponse({"status": "error", "message": "当前成绩数据缺失"}, status=404)
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.append(["考试名称", "学生姓名", "学号", "语文", "数学", "英语", "班级"])
            for score in scores:
                worksheet.append([score.title, score.student_name, score.student_number, score.chinese_score,
                                  score.math_score, score.english_score, score.grade.grade_name])
            excel_file = BytesIO()
            workbook.save(excel_file)
            workbook.close()
            excel_file.seek(0)
            response = HttpResponse(excel_file.read(),
                                    content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response["Content-Disposition"] = "attachment;filename='score.xlsx'"
            return response

class ScoreLookListView(ListView):
    model= Scores
    template_name = "scores/score_look.html"
    context_object_name="scores"

    def get_context_data(self, **kwargs):
        context_data=super().get_context_data()
        score_id=self.kwargs.get("pk")
        score=Scores.objects.get(pk=score_id)
        context_data["scores"]=score
        context_data["score_sum"]=score.chinese_score+score.math_score+score.english_score
        return context_data

class MyScoreListView(ListView):
    model=Scores
    template_name="students/my_score.html"
    context_object_name="scores"
    paginate_by=10

    def get_queryset(self):
        queryset=super().get_queryset()
        student_number=self.request.user.username.replace("student","")
        queryset=Scores.objects.filter(student_number=student_number).order_by("pk")
        search = self.request.GET.get("search")
        if search:
            queryset=Scores.objects.filter(Q(title__icontains=search)).order_by("pk")
        return queryset