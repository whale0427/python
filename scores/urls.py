from django.urls import path
from .views import (ScoreListView,ScoreCreateView,ScoreUpdateView,ScoreDeleteView,
                    ScoreBulkDeleteView,score_import,score_export,ScoreLookListView,
                    MyScoreListView)

urlpatterns=[
    path("",ScoreListView.as_view(),name="score_list"),
    path("create/",ScoreCreateView.as_view(),name="score_create"),
    path("update/<int:pk>/",ScoreUpdateView.as_view(),name="score_update"),
    path("delete/<int:pk>/",ScoreDeleteView.as_view(),name="score_delete"),
    path("bulk_delete/",ScoreBulkDeleteView.as_view(),name="score_bulk_delete"),
    path("import/",score_import,name="score_import"),
    path("export/",score_export,name="score_export"),
    path("look/<int:pk>/",ScoreLookListView.as_view(),name="score_look"),
    path("my_score/",MyScoreListView.as_view(),name="my_score"),
]