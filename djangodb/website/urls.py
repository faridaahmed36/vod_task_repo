from django.urls import path
from . import views
from .views import subscribe, unsubscribe

urlpatterns = [
    path('', views.home, name="home"),
    path('signup/', views.signup, name="signup"),
    path('signin/', views.signin, name="signin"),
    path('taskpage/', views.taskpage, name="taskpage"),
    path('add-task/', views.add_task, name="add_task"),
    path('edit-task/<int:task_id>/', views.edit_task, name="edit_task"),
    path('delete-task/<int:task_id>/', views.delete_task, name="delete_task"),
    path('batch-delete/', views.batch_delete_tasks, name="batch_delete_tasks"),
    path('restore_task/<int:task_id>/', views.restore_task, name='restore_task'),
    path('logout/', views.logout_user, name='logout'),
    ################
    path('subscribe/', subscribe, name='subscribe'),
    path('unsubscribe/', unsubscribe, name='unsubscribe'),
    path('subscription/', views.subscribe, name='subscription'),
]