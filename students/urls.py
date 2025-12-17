from django.urls import path
from .views import (StudentListView,StudentCreateView,StudentUpdateView,StudentDeleteView,
                    StudentBulkDeleteView,student_excel_import,student_excel_export,
                    StudentScoreCreateView)

urlpatterns=[
    path("",StudentListView.as_view(),name="student_list"),
    path("create/",StudentCreateView.as_view(),name="student_create"),
    path("student_score_create/<int:pk>",StudentScoreCreateView.as_view(),name="student_score_create"),
    path("update/<int:pk>/",StudentUpdateView.as_view(),name="student_update"),
    path("delete/<int:pk>/",StudentDeleteView.as_view(),name="student_delete"),
    path("bulk_delete/",StudentBulkDeleteView.as_view(),name="student_bulk_delete"),
    path("import/",student_excel_import,name="student_import"),
    path("export/",student_excel_export,name="student_export"),
]