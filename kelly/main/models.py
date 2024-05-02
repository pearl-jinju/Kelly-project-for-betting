from django.db import models


# 경기번호 날짜 ID
# Create your models here.
class Check(models.Model):
    user             = models.TextField(default="-")   # 유저 아이디
    match_number     = models.TextField(default="-") 
    date             = models.TextField(default="-") 
    teams            = models.TextField(default="-") 
    kelly_rate       = models.FloatField(default=0) 
    odd              = models.FloatField(default=0)    
    amt              = models.IntegerField(default=0)    
    cash              = models.IntegerField(default=0)   

class MatchDB(models.Model):
    num               = models.TextField(default="-")   # 유저 아이디
    date              = models.TextField(default="-") 
    end_time          = models.TextField(default="-") 
    betting_type      = models.TextField(default="-") 
    home_team         = models.TextField(default="-") 
    away_team         = models.TextField(default="-")
    odd_list          = models.TextField(default="-")  
    prob_from_odd_list= models.TextField(default="-") 
    betting_sports    = models.TextField(default="-") 
    league_name       = models.TextField(default="-") 
    handicap_value    = models.TextField(default=0) 
    under_over_value  = models.TextField(default=0) 

class Match_RESULT_DB(models.Model):
    num               = models.TextField(default="-")   # 유저 아이디
    date              = models.TextField(default="-") 
    betting_type      = models.TextField(default="-") 
    home_team         = models.TextField(default="-") 
    away_team         = models.TextField(default="-")
    odd_list          = models.TextField(default="-")  
    prob_from_odd_list= models.TextField(default="-") 
    betting_sports    = models.TextField(default="-") 
    league_name       = models.TextField(default="-") 
    handicap_value    = models.TextField(default=0) 
    under_over_value  = models.TextField(default=0) 
    match_result_value= models.TextField(default=0) # 경기결과 점수
    match_winner      =  models.TextField(default=0) # 경기결과 0 없음 1홈 2무 3어웨이
    match_date         =  models.TextField(default=0)
class MatchDB_one(models.Model):
    num               = models.TextField(default="-")   # 유저 아이디
    date              = models.TextField(default="-") 
    end_time          = models.TextField(default="-") 
    betting_type      = models.TextField(default="-") 
    home_team         = models.TextField(default="-") 
    away_team         = models.TextField(default="-")
    odd_list          = models.TextField(default="-")  
    prob_from_odd_list= models.TextField(default="-") 
    betting_sports    = models.TextField(default="-") 
    league_name       = models.TextField(default="-") 
    handicap_value    = models.TextField(default=0) 
    under_over_value  = models.TextField(default=0)     
