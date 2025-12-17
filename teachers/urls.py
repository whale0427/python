from django.urls import path
from .views import (TeacherListView,TeacherCreateView,TeacherUpdateView,TeacherDeleteView,
                    TeacherBulkDeleteView,teacher_import,teacher_export)

urlpatterns=[
    path("",TeacherListView.as_view(),name="teacher_list"),
    path("create/",TeacherCreateView.as_view(),name="teacher_create"),
    path("update/<int:pk>/",TeacherUpdateView.as_view(),name="teacher_update"),
    path("delete/<int:pk>/",TeacherDeleteView.as_view(),name="teacher_delete"),
    path("bulk_delete/",TeacherBulkDeleteView.as_view(),name="teacher_bulk_delete"),
    path("import/",teacher_import,name="teacher_import"),
    path("export/",teacher_export,name="teacher_export"),
]