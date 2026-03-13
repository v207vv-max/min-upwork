from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("projects/", include("projects.urls")),
    path("bids/", include("bids.urls")),
    path("contracts/", include("contracts.urls")),
    path("reviews/", include("reviews.urls")),
    path("chat/", include("chat.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
