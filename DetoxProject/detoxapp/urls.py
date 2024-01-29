from django.urls import path
from .appviews import tongue_views, question_views, prescription_views, question_views_new, tongue_detail_views
from .appviews import login_views, user_views
from django.contrib.auth import views as auth_views

app_name = "detox"

urlpatterns = [
    #main
    path('',tongue_views.main),
    path('survey_project/',question_views.survey_project),

    #login URL
    path('signup/',login_views.signup, name='signup'),
    path('mypage/',login_views.mypage, name='mypage'),
    path('login/', auth_views.LoginView.as_view(template_name='detoxapp/login.html'), name='login'),
    path('logout/',auth_views.LogoutView.as_view(), name='logout'),
    path('delete_user/<int:id>/',login_views.delete_user, name='delete_user'),
    path('user/',user_views.user, name='user'),
    path('changeAuthActiveAjax/', user_views.changeAuthActiveAjax),
    path('changeAuthGroupAjax/', user_views.changeAuthGroupAjax),
    path('changeGroupPermissionAjax/', user_views.changeGroupPermissionAjax),
    path('addDeleteGroup/', user_views.addDeleteGroup),
    path('actAuthPasswordChangeAjax/', user_views.actAuthPasswordChangeAjax),
    path('actAuthPasswordCheckAjax/', user_views.actAuthPasswordCheckAjax),
    path('alert/', user_views.alert),

    #tongue URL
    path('tongue_list/<str:page>',tongue_views.tongue_list),

    #tongue_detail URL
    path('tongue_detail/',tongue_detail_views.tongue_detail),
    path('upload_tongue/',tongue_detail_views.upload_tongue),
    path('segment_tongue/',tongue_detail_views.segment_tongue),
    path('predict_tongue/',tongue_detail_views.predict_tongue),
    path('label_tongue/',tongue_detail_views.label_tongue),

    
    #question_new URL
    path('question_info/<str:page>',question_views_new.question_info, name="survey"),
    path('question_submit/<int:pagenum>',question_views_new.question_submit),
    path('question_result/<str:type>',question_views_new.question_result),

    #prescription URL
    path('prescription/',prescription_views.prescription),
    path('prescription_result/',prescription_views.prescription_result),
    path('prescription_save/',prescription_views.prescription_save),
]

