from django.urls import path
from .views import SyncUploadView, SyncPullView, SyncConflictListView

urlpatterns = [
    path("upload/", SyncUploadView.as_view(), name="sync-upload"),
    path("pull/", SyncPullView.as_view(), name="sync-pull"),
    path("conflicts/", SyncConflictListView.as_view(), name="sync-conflicts"),
]
