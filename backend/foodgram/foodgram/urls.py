from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('recipes.urls')),
    path('static/', include('about.urls', namespace='static')),
]
