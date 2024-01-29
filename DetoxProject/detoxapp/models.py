from django.db import models
from django.contrib.auth.models import AbstractBaseUser  # 기본 유저모델 임포트
from django.contrib.auth.models import BaseUserManager, PermissionsMixin  # 임포트
from django.utils import timezone
import datetime

class UserManager(BaseUserManager):
	# 필수로 필요한 데이터를 선언
    def create_user(self, name, email, username, password=None):
        if not username:
            raise ValueError('Users must have an username')
        user = self.model(
            name=name,
            email=email,
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    # python manage.py createsuperuser 사용 시 해당 함수가 사용됨
    def create_superuser(self, email, username, password=None):
        user = self.create_user(
            email=email,
            username=username,
            password=password
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


#"name", "username", "password", "email", "phone", "join_date"
class User(AbstractBaseUser, PermissionsMixin):
    # DB에 저장할 데이터를 선언
    name = models.CharField("사용자 이름", max_length=10, null=False)
    username = models.CharField("사용자 계정", max_length=20, unique=True)
    password1 = models.CharField("비밀번호", max_length=128)  # 해시되기 때문에 max_length가 길어야함
    password2 = models.CharField("비밀번호", max_length=128)  # 해시되기 때문에 max_length가 길어야함
    email = models.EmailField("이메일 주소", max_length=50)
    phone = models.CharField("전화번호", max_length=100, default='01000000000')
    join_date = models.CharField("가입일", max_length=100, default=datetime.datetime.now(), blank=True)
    # 활성화 여부 (기본값은 True)
    is_active = models.BooleanField(default=True)

    # 관리자 권한 여부 (기본값은 False)
    is_admin = models.BooleanField(default=False)

    # 실제 로그인에 사용되는 아이디
    USERNAME_FIELD = 'username'

    # 어드민 계정을 만들 때 입력받을 정보 ex) email
    # 사용하지 않더라도 선언이 되어야함
    # USERNAME_FIELD와 비밀번호는 기본적으로 포함되어있음
    REQUIRED_FIELDS = ['name']

    # custom user 생성 시 필요
    objects = UserManager()
	
    # 어드민 페이지에서 데이터를 제목을 어떻게 붙여줄 것인지 지정
    def __Str__(self):
        return f"{self.username} / {self.name} 님의 계정입니다"
    
    # admin 권한 설정
    @property
    def is_staff(self):
        return self.is_admin


class Meta(models.Model):
    class Meta:
        permissions = (
       ('view_question_manage', '고객 문진결과 접근 권한'),
       ('view_user_manage', '계정 설정화면 접근 권한'),)