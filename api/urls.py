from django.urls import include, path

from api.views import ConversationApiView, MessageApiView, UserApiView

urlpatterns = [
    # User urls
    path('auth/register', UserApiView.register, name='register'),
    path('auth/logout', UserApiView.auth_logout, name='auth_logout'),
    path('auth/validate', UserApiView.auth_validated, name='auth_validate'),
    path('auth/login/username', UserApiView.auth_username, name='auth_username'),
    path('auth/', include('social.apps.django_app.urls', namespace='auth_social')),
    # Conversation urls
    path('conversation', ConversationApiView.get, name='conversation'),
    path('conversation/<str:id>', ConversationApiView.rud, name='conversation'),
    # Message urls
    path('message', MessageApiView.send, name='message'),
    path('message/<str:id>', MessageApiView.delete, name='message'),
]