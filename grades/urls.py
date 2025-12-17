from django.urls import path
from .views import GradeListView,GradeCreateView,GradeUpdateView,GradeDeleteView

urlpatterns=[
    path("",GradeListView.as_view(),name="grade_list"),
    path("create/",GradeCreateView.as_view(),name="grade_create"),
    #UpdateView的路由，必须要设置一个pk的参数
    path("update/<int:pk>/",GradeUpdateView.as_view(),name="grade_update"),
    path("delete/<int:pk>/",GradeDeleteView.as_view(),name="grade_delete"),
]