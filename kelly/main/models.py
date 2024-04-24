from django.db import models


# 경기번호 날짜 ID
# Create your models here.
class Check(models.Model):
    user             = models.TextField(default='-')   # 유저 아이디
    match_number     = models.TextField(default='-') 
    date             = models.TextField(default='-') 
    teams            = models.TextField(default='-') 
    kelly_rate       = models.FloatField(default=0) 
    odd              = models.FloatField(default=0)    
    amt              = models.IntegerField(default=0)    
    cash              = models.IntegerField(default=0)   