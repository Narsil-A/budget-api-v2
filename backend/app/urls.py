from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'budgetapp'

# DRF Router
router = DefaultRouter()
router.register(r'budget', views.BudgetViewSet)
router.register(r'budgetcategories', views.BudgetCategoryViewSet)
router.register(r'budgetcategorygroups', views.BudgetCategoryGroupViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'Payee', views.PayeeViewSet, basename='Payee')

urlpatterns = [
    path('logout/', views.logout, name='logout'),
    path('login/', views.login_view, name='login'),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/register/',
         views.UserCreateView.as_view(),
         name='user-create'),
     path('users/register/login',
         views.UserCreateView.as_view(),
         name='login'),
    path('users/obtain-auth-token/',
         views.ObtainAuthTokenCookieView.as_view(),
         name='obtain-auth-token'),
    path('users/<int:pk>/',
         views.UserRetrieveUpdateDestroyView.as_view(),
         name='user-detail'),
    path('user-info/', views.UserDetailView.as_view(), name='user-info'),
    path('copy-budget/', views.BudgetViewSet.as_view({'get': 'list'}), name='copy-budget'),
    path('', include(router.urls)),
]
