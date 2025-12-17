from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView,CreateView,UpdateView,DeleteView

from untils.permissions import RoleRequiredMixin
from .models import Grades
from django.db.models import Q
from .forms import GradesForm

# Create your views here.
class BaseGradeView(RoleRequiredMixin):
    allowed_roles=["admin"]

class GradeListView(BaseGradeView,ListView):
    #指定操作的模型，数据查询自动的，自动生成该模型下的所有数据object_list=Grades.objects.all()
    #注：只有列表类（ListView）且模型名称本身是复数的情况（如Grades）才是object_list默认变量名，如果是单数（Grade），那么默认变量名是grades
    #除了上面的视图类，其他视图类，如CreateView\DeleteView\UpdateView的变量名默认都是模型的名称小写，比如模型名（Grades）变量名是grades;比如模型名（Grade）变量名是grade
    model=Grades
    #请求响应的模板
    template_name="grades/grade_list.html"
    #给model自动获取的变量，设置模板变量名,如果不设置，django会默认变量名模型名_list（小写）
    context_object_name="grades"
    #paginate_by设置每页显示的对象数量，会自动传变量到模板，变量名page_obj
    #当使用ListView并设置paginate_by属性，Django会自动给当前视图添加"?page="查询参数的处理能力
    #分页不依赖路由，也就是给当前路由加了参数"?page="
    paginate_by=10

    #重写父类方法，返回的值会覆盖变量名下的变量，比如变量名grades，如果没有自定义变量名，会覆盖object_list
    def get_queryset(self):
        queryset=super().get_queryset()
        #request 是类的实例属性，不是全局变量或局部变量。所以必须self.request
        search=self.request.GET.get("search")
        if search:
            queryset=queryset.filter(Q(grade_name__contains=search)|Q(grade_code__contains=search))
        return queryset

#这些类如果没有重写form_valid方法，会自动执行form.save()，所以不用写
#如果重写了form_valid方法，就需要在方法里面执行form.save()
class GradeCreateView(BaseGradeView,CreateView):
    model=Grades
    template_name="grades/grade_form.html"
    #继承CreateView，并设置该属性，django会自动生成form变量
    form_class=GradesForm
    #重定向，如果form表单设置了action属性，那么会跳转action，而不会执行success_url
    #但是如果button的type是button,而且a标签嵌套，那么就不会受action影响，会跳转a标签的href
    success_url=reverse_lazy("grade_list")

    def form_valid(self,form):
        #先保存数据
        self.object=form.save()
        #获取页面name="save_next"的value
        save_next=self.request.POST.get("save_next")
        if save_next=="保存并新增下一个":
            #重定向到解析的url
            return redirect(reverse_lazy("grade_create"))
        else:
            #重定向到success_url
            return redirect(self.get_success_url())

class GradeUpdateView(BaseGradeView,UpdateView):
    model = Grades
    template_name = "grades/grade_form.html"
    form_class = GradesForm
    success_url = reverse_lazy("grade_list")

class GradeDeleteView(BaseGradeView,DeleteView):
    model=Grades
    template_name="grades/grade_delete.html"
    success_url=reverse_lazy("grade_list")