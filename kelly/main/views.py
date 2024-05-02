from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
import pandas as pd

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ast import literal_eval
from selenium.common.exceptions import NoSuchElementException

import time
import random

from datetime import datetime
from tqdm import tqdm
from .models import MatchDB, MatchDB_one, Match_RESULT_DB

def click_xpath(position:str):
    """
    main_login -- 메인화면 로그인 버튼 \n
    id  -- ID 입력 칸 \n
    pw -- PW 입력칸 \n
    login_button -- login 버튼 \n
    buylist_1 -- 게임구매 버튼 \n
    buylist_2 -- 구매가능게임 버튼 \n
    buy_match -- 승부식 게임구매 버튼 \n
    search -- 검색 버튼 \n
    """
    if position=="id":
        position = '//*[@id="loginPopId"]'
    if position =="main_login":
        position = '//*[@id="divTopMbrArea"]/div/div/ul/li[1]/a'
    if position == 'pw':
        position = '//*[@id="loginPopPwd"]'
    if position == 'login_button':
        position = '//*[@id="doLogin"]'
    if position =='buylist_1':
        position = '//*[@id="navListArea"]/li[1]/a'
    if position =='buylist_2':
        position = '//*[@id="navListArea"]/li[1]/ul/li[1]'
    if position =='search':
        position = '//*[@id="btn_gmBuySlipSrchDtl"]'
    if position =='buy_match':
        position = '//*[@id="tbl_protoBuyAbleGameList"]/tbody/tr[1]/td[5]/div'
    if position =='search_finish':
        position = '//*[@id="SlipSrchDtlSrch"]'


    element = driver.find_element(By.XPATH,position)
    actions = ActionChains(driver)
    actions.click(element).perform()

def call_name(x,ground):
    """
    x 번째의 이름 \n
    ground keword -----\n
    home = 홈 경기의 경우 \n
    away = 어웨이 경기의 경우
    """
    if ground == "home":
        position ='#tbd_gmBuySlipList > tr:nth-child('+ str(x) +') > td:nth-child(5) > div > div.cell.tar > span'
    elif ground == "away":
        position ='#tbd_gmBuySlipList > tr:nth-child('+ str(x) +') > td:nth-child(5) > div > div.cell.tal > span'
   
    return  driver.find_element(By.CSS_SELECTOR,position).text


def cal_prob_from_odd(ls):
    # 배당이 2개라면
    if len(ls)==2:
        x = ls[0]
        y = ls[1]
        x_prob = round(y/(x+y),4)
        y_prob = round(x/(x+y),4)
        return [x_prob, y_prob]
    # 배당이 3개라면
    else:
        x = ls[0]
        y = ls[1]
        z = ls[2]
        x_prob = (y+z)/(x+y+z)
        y_prob = (x+z)/(x+y+z)
        z_prob = (x+y)/(x+y+z)

        prob_sum = x_prob+ y_prob+z_prob
        x_prob = round(x_prob/prob_sum,4)
        y_prob = round(y_prob/prob_sum,4)
        z_prob = round(z_prob/prob_sum,4)
        return [x_prob, y_prob, z_prob]
    
def random_select_to_idx(ls):
    # 배당이 2개라면
    seed = random.randint(1,1000)/1000
    if len(ls)==2:
        x = ls[0]
        y = ls[1]
        # 확률을 계산
        prob_list = cal_prob_from_odd(ls)
        if seed <= prob_list[0]:
            return 1
        else:
            return 3
    else:
        x = ls[0]
        y = ls[1]
        z = ls[2]
        prob_list = cal_prob_from_odd(ls)
        if seed <= prob_list[0]:
            return 1
        elif seed <= (prob_list[0]+prob_list[1]):
            return 2
        else:
            return 3


        return [x_prob, y_prob]

        

def odd(x,y,action):
    """
    x = X 번째 경기 \n
    y = y 번째 배당 \n
    action -- keyword\n
     -- 'odd' 배당율 숫자 가져오기 \n
     -- 'click' 배당 버튼 클릭  \n
    """
    
    if action == 'odd':
        odd_value = float(driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(x) +') >  td:nth-child(6) > div > div > button:nth-child('+ str(y) +') > span.db').text[:4])
        return odd_value
    
    if action == "click":
        element = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(x) +') > td:nth-child(6) > div > div > button:nth-child('+ str(y) +')')
        actions = ActionChains(driver)
        actions.click(element).perform()


def making_betting_list(df,n):
    
    m = str(datetime.today().month)
    d = str(datetime.today().day)
    h = str(datetime.today().hour)
    min = str(datetime.today().minute)

    if len(m)==1:
        m = "0"+str(m)
    else:
        m = str(m)

    if len(d)==1:
        d = "0"+str(d)
    else:
        d = str(d)

    if len(h)==1:
        h = "0"+str(h)
    else:
        h = str(h)

    if len(min)==1:
        min = "0"+str(min)
    else:
        min = str(min)

    df.columns = ['id','num','date','endtime','gametype','home','away','oddlist','oddproblist']
    df['endtime'] = df['endtime'].apply(lambda x : int(x.replace(":","")))
    df['oddlist'] = df['oddlist'].apply(lambda x :literal_eval(x))
    df['oddproblist'] = df['oddproblist'].apply(lambda x :literal_eval(x))
    
    # 오늘날짜로만 불러오기
    df = df[df['date'].str.startswith(m)]
    df = df[df['date'].str.endswith(d)]
    time_str = int(h+min)
    df = df[df['endtime']>time_str]
    for j, row in df.iterrows():
        # 배당이 2개라면?
        if len(df.loc[j,'oddlist'])==2:
            df.loc[j,'odd1'] = df.loc[j,'oddlist'][0]
            df.loc[j,'odd2'] = 0
            df.loc[j,'odd3'] = df.loc[j,'oddlist'][1]
            df.loc[j,'odd1_prob'] = df.loc[j,'oddproblist'][0]
            df.loc[j,'odd2_prob'] = 0
            df.loc[j,'odd3_prob'] = df.loc[j,'oddproblist'][1]
        else:
            df.loc[j,'odd1'] = df.loc[j,'oddlist'][0]
            df.loc[j,'odd2'] = df.loc[j,'oddlist'][1]
            df.loc[j,'odd3'] = df.loc[j,'oddlist'][2]
            df.loc[j,'odd1_prob'] = round(df.loc[j,'oddproblist'][0],3)
            df.loc[j,'odd2_prob'] = round(df.loc[j,'oddproblist'][1],3)
            df.loc[j,'odd3_prob'] = round(df.loc[j,'oddproblist'][2],3)
        # df.loc[idx,'endtime']

    df['odd1_prob'] = df['odd1_prob'].apply(lambda x: round(x,3))
    df['odd2_prob'] = df['odd2_prob'].apply(lambda x: round(x,3))
    df['odd3_prob'] = df['odd3_prob'].apply(lambda x: round(x,3))

    df['odd1_prob_str'] = df['odd1_prob'].apply(lambda x: str(round(x*100,2))+"%")
    df['odd2_prob_str'] = df['odd2_prob'].apply(lambda x: str(round(x*100,2))+"%")
    df['odd3_prob_str'] = df['odd3_prob'].apply(lambda x: str(round(x*100,2))+"%")
    df['final_pick'] = df['oddlist'].apply(lambda x: random_select_to_idx(x))

    df['idx']=df.index
    df = df.reset_index(drop=True)
    df = df.reset_index()
    df['pick_idx'] = df['idx'].apply(lambda x : x+1)

    # 셔플
    df = df.sample(frac=1)

    # 한개의 홈에 2개이상 조합이 안됨 중복제거
    df_normal = df.drop_duplicates(subset='home')
    df_normal = df_normal.iloc[:n]

    df_normal = df_normal.sort_values(by='idx')

    return df_normal

def making_final_pick_idx(df):
    for i, pick in enumerate(df['final_pick']):
    
        pick_idx = df['pick_idx'].iloc[i]

        odd(pick_idx, pick,'click')


# Create your views here.
class AutoBet(APIView):
    def get(self, request):
        # 쿼리를 받음
        id = request.GET.get('username')
        pw = request.GET.get('password')
        sports = request.GET.get('sports')
        betstyle = request.GET.get('betstyle')
        cashlimit = request.GET.get('cashlimit')
        max_kelly = request.GET.get('max_kelly')
        


        # 크롬 드라이버 실행
        chrome_options = webdriver.ChromeOptions()
        global driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.implicitly_wait(1)

        # 
        if cashlimit == "":
            # 현재 보유금액을 가져옴
            current_cash = int(driver.find_element(By.CSS_SELECTOR,'#dsmnAmt > a > strong').text.replace(",",""))
        else:
            current_cash = int(cashlimit)


        m = datetime.today().month
        d = datetime.today().day


        url = 'https://www.betman.co.kr/'
        # 드라이버 url 연결 
        driver.get(url)
        driver.implicitly_wait(1)

        # 메인화면 로그인 버튼 클릭
        click_xpath('main_login')
        
        # id 입력버튼 클릭
        click_xpath("id")
        # id 입력
        driver.find_element(By.XPATH,'//*[@id="loginPopId"]').send_keys(id)

        # pw 입력버튼 클릭
        click_xpath('pw')
        # pw 입력
        driver.find_element(By.XPATH,'//*[@id="loginPopPwd"]').send_keys(pw)

        # 로그인 버튼 클릭
        click_xpath('login_button')
        time.sleep(0.5)

        # 게임구매 버튼 지정
        click_xpath('buylist_1')


        # 구매 가능게임 버튼 클릭
        click_xpath('buylist_2')


        # # 팝업 종료 버튼 클릭
        # element = driver.find_element(By.XPATH,'/html/body/div[2]/div[1]/button/span[1]')
        # if element:
        #     actions = ActionChains(driver)
        #     actions.click(element).perform()

        # click_xpath('/html/body/div[2]/div[1]/button/span[1]')
        # 승부식 게임구매 버튼 클릭
        click_xpath('buy_match')

        
                
        # //*[@id="tbl_protoBuyAbleGameList"]/tbody/tr[1]/td[5]/div/a

        betting_sports_dict ={
            '전체' : '//*[@id="chkSportsAll"]',
            '축구' : '//*[@id="chkSportsSC"]',
            '농구' : '//*[@id="chkSportsBK"]',
            '야구' : '//*[@id="chkSportsBS"]',
        }

            
        # 배팅할 종목만 확인
        current_betting_sports = betting_sports_dict[sports]

        
        # 0. 검색창을 클릭 --> 일반 
        click_xpath('search')

        # 경기유형 딕셔너리 초기화
        betstyle_dict ={
        '전체' : '//*[@id="chkGmTypAll"]',
        '일반' : '//*[@id="chkGmTyp0"]',
        '핸디캡' : '//*[@id="chkGmTyp2"]',
        '언더오버' : '//*[@id="chkGmTyp9"]',
        '승1패' : '//*[@id="chkGmTyp13"]',
        '승5패' : '//*[@id="chkGmTyp14"]',
        }

        click_xpath(betstyle_dict[betstyle])


        # 날짜 결정 
        # 전체 //*[@id="chkWeekDayAll"] 월 //*[@id="chkWeekDay1"] 금 //*[@id="chkWeekDay5"] 토 //*[@id="chkWeekDay6"]  일 //*[@id="chkWeekDay0"] 
        element = driver.find_element(By.XPATH, '//*[@id="chkWeekDayAll"]')
        actions = ActionChains(driver)
        actions.click(element).perform()

        # 종목 결정 
        click_xpath(current_betting_sports)

        #  검색완료
        click_xpath('search_finish')




     # 배트맨 경기 종목 조회 완료 ===============
        # 경기 개수 확인
        # 경기 개수 초기화
        sports_cnt = 0
        
        ccs_list = []
        for i in range(100):
            ccs = str('#tbd_gmBuySlipList > tr:nth-child(') + str(i+1) + ')'
            ccs_list.append(ccs)
        for idx ,ccs in enumerate(ccs_list):
            try :
                check = driver.find_element(By.CSS_SELECTOR, ccs)
                if check:
                    sports_cnt += 1
                else:
                    break
            except:

                break
        print(f"{sports_cnt}개의 경기가 있습니다")
        
        if sports_cnt <2 :
            warning = "베팅하기에 경기가 너무 적습니다."
            return render(request,"main/home.html", context = dict(
                warning = warning,
            ),status=200)

        
        # 데이터를 저장할 기초 dataframe 생성
        betting_df = pd.DataFrame(columns=['no','teams','kelly_rate','odd','amt','cash'])
        # 현재까지 배팅한 종목리스트를 초기화 함
        betting_list = []
        # 현재까지 클릭 기록리스트를 초기화 함
        click_record = []
        # 현재까지 예상 승률리스트를 초기화 함
        win_rate_list =[]
        # 현재까지 배팅한 종목의 수를 초기화 함
        betting_cnt = 0
        # 배당비율을 초기화 함
        final_betting_odd = 1 


        # 정배당인 경우 그 종목에 ADVANTAGE_POINT_PLUS 만큼 승률을 (+) 함 
        ADVANTAGE_POINT_PLUS = 0.08
        # 정배당인 경우 그 종목에 (고배당/저배당-1)/ADVANTAGE_POINT_RATE 만큼 더함
        ADVANTAGE_POINT_RATE = 2

        # RANDOM_RATE = 0.35


        # sports_cnt 종목 수만큼 반복시작
        for i in range(1,sports_cnt+1):
            # 캘리비율을 초기화 함
            Kelly_rate = 0
            # 1. 경기의 번호와 홈팀/어웨이팀의 이름을 가져온다.
            betting_name = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(i) +') > td:nth-child(1) > span').text
            home_team = call_name(i,'home')
            away_team = call_name(i,'away')

            date = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(i) +') > td:nth-child(2)').text[:5]
            match_month =  int(date.split('.')[0])
            match_day =  int(date.split('.')[1])
            if m != match_month or d != match_day:
                print("오늘 날짜의 경기가 아닙니다")
                continue


            # 언오버 기준값
            under_over_point = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(i) +') > td:nth-child(5) > div > div.cell.tar > div > span').text[:4]
            
            # 언더 베팅의 배당율을 가져온다.
            under_betting_Odds = odd(i,1,'odd')
            # 오버 베팅의 배당율을 가져온다.
            over_betting_Odds = odd(i,3,'odd')

            # 
            if under_betting_Odds > over_betting_Odds:
                # 오버배당 클릭
                odd(i,3,'click')
                # 현재 배팅한 리스트에 포함
                betting_list.append([betting_name,home_team,away_team,under_over_point,over_betting_Odds])
                # 배당율 업데이트
                final_betting_odd *= over_betting_Odds
                # 현재 배당 개수를 업데이트
                betting_cnt += 1
                # 클릭 기록을 업데이트
                click_record.append(str(i)+"-3")

                # 배당률 역산 승률
                win_rate = under_betting_Odds/(under_betting_Odds+over_betting_Odds)
                # 배당률 어드밴티지 가산
                advantage = (under_betting_Odds/over_betting_Odds-1)/ADVANTAGE_POINT_RATE + ADVANTAGE_POINT_PLUS
                win_rate = win_rate * (1+advantage)
                win_rate_list.append(win_rate)
                print(f"오버 승리확률: {win_rate*100:.2f}%")

            elif over_betting_Odds > under_betting_Odds:
                # 언더배당 클릭
                odd(i,1,'click')
                # 현재 배팅한 리스트에 포함
                betting_list.append([betting_name,home_team,away_team,under_over_point,under_betting_Odds])
                # 배당율 업데이트
                final_betting_odd *= under_betting_Odds
                # 현재 배당 개수를 업데이트
                betting_cnt += 1
                # 클릭 기록을 업데이트
                click_record.append(str(i)+"-1")


                # 배당률 역산 승률
                win_rate = over_betting_Odds/(under_betting_Odds+over_betting_Odds)
                # 배당률 어드밴티지 가산
                advantage = (over_betting_Odds/under_betting_Odds-1)/ADVANTAGE_POINT_RATE + ADVANTAGE_POINT_PLUS
                win_rate = win_rate * (1+advantage)
                win_rate_list.append(win_rate)
                print("배팅개시 언더에 베팅")
                print(f"언더 승리확률: {win_rate*100:.2f}%")
            else:
                pass

            if betting_cnt==2:               
                final_betting_odd -= 1
                # 캘리비율 계산
                joint_win_rate = win_rate_list[0] * win_rate_list[1]
                print(f'승리확률 : {joint_win_rate*100:.2f}%')
                win_rate_list = []
                # 캘리비율 계산
                Kelly_rate = ((final_betting_odd + 1)*joint_win_rate -1)/final_betting_odd

                if max_kelly == "":
                    MAX_KELLY_RATE = 0.05
                else:
                    MAX_KELLY_RATE = int(max_kelly)/100
                
                
                # 캘리비율 최대값 제한
                
                if Kelly_rate >= MAX_KELLY_RATE:
                    Kelly_rate = 0.1
                    print(f"캘리비율 {Kelly_rate*100:.2f}%===제한 적용")
                elif Kelly_rate > 0:
                    print(f"캘리비율 {Kelly_rate*100:.2f}%")
                # 캘리비율이 0인경우
                else:
                    print(f"캘리비율{Kelly_rate*100:.2f}% \n 캘리비율이 음수입니다 배팅 부적합")
                    # 배당율 초기화 
                    final_betting_odd = 1
                    betting_cnt = 0

                    # 버튼 클릭 취소 
                    for record in click_record:
                        record = record.split("-")
                        position = record[0]
                        betting_direction = record[1]
                        element = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(position) +') > td:nth-child(6) > div > div > button:nth-child('+str(betting_direction)+')')
                        actions = ActionChains(driver)
                        actions.click(element).perform()
                    # 클릭 리스트 초기화
                    click_record = []
                    betting_list = []
                    win_rate_list = []
                    continue

                # 현재금액과 캘리비율을 연산
                betting_amt = round(Kelly_rate * current_cash,-2)
                # 100원 미만인 경우 100원으로 설정
                if betting_amt <= 100:
                    betting_amt = 100
                current_cash -= betting_amt

                betting_name = betting_list[0][0] +"-"+ betting_list[1][0]
                betting_teams = betting_list[0][1] +"vs"+ betting_list[0][2]  +"-"+betting_list[1][1] +"vs"+ betting_list[1][2] 

                # 데이터 표시용으로 변경
                Kelly_rate = str(round(Kelly_rate*100,1)) + "%"
                final_betting_odd = str(round(final_betting_odd+1,2))

                temp_df = pd.DataFrame([[betting_name,betting_teams,Kelly_rate,final_betting_odd,betting_amt,current_cash]])
                temp_df.columns =['no','teams','kelly_rate','odd','amt','cash']

                betting_df = pd.concat( [betting_df,temp_df],axis=0)

                # 금액 입력버튼 클릭
                click_xpath('//*[@id="buyAmt"]')

                temp_betting_amt = betting_amt/10
                # 금액 입력
                driver.find_element(By.XPATH,'//*[@id="buyAmt"]').clear()
                driver.find_element(By.XPATH,'//*[@id="buyAmt"]').send_keys(str(temp_betting_amt))

        
                # 카트 담기 클릭
                click_xpath('//*[@id="asideGameTabBtn0"]/button[1]')
                time.sleep(1)
                
                # 초기화 
                final_betting_odd = 1
                betting_cnt = 0
                betting_list = []
                click_record = []
                win_rate_list = []
                print("DB에 저장합니다.")

        print(betting_df)
            










        return render(request,"main/main.html", context = dict(
            
            betting_df =betting_df
            # odd1 = kelly_odd_list[0],
            # odd2 = kelly_odd_list[1],
            # odd3 = kelly_odd_list[2],
            # final_betting_direction1 = final_betting_direction_list[0],
            # final_betting_direction2 = final_betting_direction_list[1],
            # final_betting_direction3 = final_betting_direction_list[2],
            # Kelly_rate_amt = Kelly_rate_amt,
            # Kelly_rate = Kelly_rate

        ),status=200) #context html로 넘길것.
    
    # TODO 배팅 버튼 후 처리
    # 아직까지 맨위의 3개만 배팅하도록 설정되어있음
    
    # DB를 활용하여 일자와 경기번호를 조합하여 중복투자 방지 기능 추가하고
    # 중복되는경우 다른 경기 3개로 조합하여 투자하도록 할것
    
    # 현재 메인페이지에서 바로 투자되는데 이를 보완할 것

    # Kelly 값이 마이너스인 경우 투자하지 않도록 하거나 다른 대안투자방법으로 변경할것
    

class Save_Recent_Data(APIView):
    def get(self, request):

        MatchDB.objects.all().delete()
        MatchDB_one.objects.all().delete()

        id = request.GET.get('username')
        pw = request.GET.get('password')

        request.session['id']=id
        request.session['pw']=pw

        # request.data.get('id',None)  

                # 크롬 드라이버 실행
        chrome_options = webdriver.ChromeOptions()
        global driver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.implicitly_wait(1)


        m = datetime.today().month
        d = datetime.today().day


        url = 'https://www.betman.co.kr/main/mainPage/gamebuy/buyableGameList.do'
        # 드라이버 url 연결 
        driver.get(url)
        driver.implicitly_wait(1)

        # 메인화면 로그인 버튼 클릭
        click_xpath('main_login')
        
        # id 입력버튼 클릭
        click_xpath("id")
        # id 입력
        driver.find_element(By.XPATH,'//*[@id="loginPopId"]').send_keys(id)

        # pw 입력버튼 클릭
        click_xpath('pw')
        # pw 입력
        driver.find_element(By.XPATH,'//*[@id="loginPopPwd"]').send_keys(pw)

        # 로그인 버튼 클릭
        click_xpath('login_button')
        time.sleep(0.5)
        # 승부식 게임구매 버튼 클릭
        click_xpath('buy_match')

        driver.implicitly_wait(1)

        sports_cnt = 0
        
        ccs_list = []
        for i in tqdm(range(500)):
            ccs = str('#tbd_gmBuySlipList > tr:nth-child(') + str(i+1) + ')'
            ccs_list.append(ccs)
        for idx ,ccs in enumerate(ccs_list):
            try :
                check = driver.find_element(By.CSS_SELECTOR, ccs)
                if check:
                    sports_cnt += 1
                else:
                    break
            except:

                break
        print(f"{sports_cnt}개의 경기가 있습니다")

        # 결과 df 생성
        result_df =pd.DataFrame()
        for idx in tqdm(range(1,sports_cnt+1)):
        # for idx in tqdm(range(1,10)):
            date = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(2)').text[:5]
            end_time = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(2)').text[-8:-2]
            match_month =  int(date.split('.')[0])
            match_day =  int(date.split('.')[1])

            # if m != match_month or d != match_day:
            #     print("오늘 날짜의 경기가 아닙니다")
            #     break

            # 1. 경기의 번호와 홈팀/어웨이팀의 이름을 가져온다.
            betting_name = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(1) > span').text
            betting_type = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(4) > span').text
            betting_sports = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(3) > span.icoGame.small').text
            league_name = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(3) > span.db.fs11').text

            handicap_value = '0'
            under_over_value = '0'

            try:
                value_text = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(5) > div > div.cell.tar > div > span').text
                value_type = value_text.split(' ')[0]
                value = value_text.split(' ')[1]
                if value_type == "H":
                    handicap_value = value
                elif value_type =="U/O":
                    under_over_value = value
            except:
                pass

            home_team = call_name(idx,'home')
            away_team = call_name(idx,'away')

            odd_list = []
            odd_position_list  = []
            global odd

            for position in [1,3,2]:
                try:
                    odd_value = odd(idx,position,'odd')
                    odd_list.append(odd_value)
                    odd_position_list.append([idx,position])
                except:
                    break
            prob_from_odd_list = cal_prob_from_odd(odd_list)
            # selected_idx = random_select_to_idx(odd_list)

            
            # '번호','경기일자','마감일시,'게임유형','홈팀','원정팀','배당률리스트','배당별확률','최종선택위치'
            temp_df = pd.DataFrame([[betting_name,date,end_time,betting_type,home_team,away_team,odd_list,prob_from_odd_list,betting_sports,league_name,handicap_value,under_over_value]])
            temp_df.columns = ['번호','경기일자','마감일시','게임유형','홈팀','원정팀','배당률리스트','배당별확률','스포츠명','리그명','핸디','언오버']
            result_df =  pd.concat([result_df,temp_df.copy()], axis=0)

        # DB에 저장하는데 우선 중복검사를 한후에 할것


        new_data_cnt = 0

        for index, row in result_df.iterrows():
            num = row['번호']
            date = row['경기일자']
            end_time = row['마감일시']
            betting_type = row['게임유형']
            home_team = row['홈팀']
            away_team = row['원정팀']


            db_check =  MatchDB.objects.filter(
                num = num,
                date = date,
                end_time = end_time,
                betting_type = betting_type,
                home_team = home_team,
                away_team = away_team,

            ).count()

            # db에 없다면???
            if db_check==0:
                new_data_cnt += 1
                odd_list = row['배당률리스트']
                prob_from_odd_list = row['배당별확률']
                betting_sports = row['스포츠명']
                league_name = row['리그명']
                handicap_value = row['핸디']
                under_over_value = row['언오버']

                MatchDB.objects.create(
                num = num,
                date = date,
                end_time = end_time,
                betting_type = betting_type,
                home_team = home_team,
                away_team = away_team,
                betting_sports = betting_sports,
                league_name = league_name,
                handicap_value = handicap_value,
                under_over_value = under_over_value
                )
            # DB에 있다면??
            else:
                pass

        # # 한경기 배팅 ===========================
        # click_xpath('//*[@id="content"]/div/div[1]/div[2]/div/ul/li[2]/button')

        # driver.implicitly_wait(1)

        # sports_cnt = 0
        
        # ccs_list = []
        # for i in tqdm(range(500)):
        #     ccs = str('#tbd_gmBuySlipList > tr:nth-child(') + str(i+1) + ')'
        #     ccs_list.append(ccs)
        # for idx ,ccs in enumerate(ccs_list):
        #     try :
        #         check = driver.find_element(By.CSS_SELECTOR, ccs)
        #         if check:
        #             sports_cnt += 1
        #         else:
        #             break
        #     except:

        #         break
        # print(f"{sports_cnt}개의 경기가 있습니다")

        # # 결과 df 생성
        # result_df_one =pd.DataFrame()
        # for idx in tqdm(range(1,sports_cnt+1)):
        # # for idx in tqdm(range(1,10)):
        #     date = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(2)').text[:5]
        #     end_time = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(2)').text[-8:-2]
        #     match_month =  int(date.split('.')[0])
        #     match_day =  int(date.split('.')[1])

        #     # if m != match_month or d != match_day:
        #     #     print("오늘 날짜의 경기가 아닙니다")
        #     #     break

        #     # 1. 경기의 번호와 홈팀/어웨이팀의 이름을 가져온다.
        #     betting_name = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(1) > span').text
        #     betting_type = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(4) > span').text
        #     betting_sports = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(3) > span.icoGame.small').text
        #     league_name = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(3) > span.db.fs11').text

        #     # handicap_value = 0
        #     # under_over_value = 0

        #     # try:
        #     #     value_text = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(5) > div > div.cell.tar > div > span').text
        #     #     value_type = value_text.split(' ')[0]
        #     #     value = value_text.split(' ')[1]
        #     #     if value_type == "H":
        #     #         handicap_value = value
        #     #     elif value_type =="U/O":
        #     #         under_over_value = value
        #     # except:
        #     #     pass
        #     home_team = call_name(idx,'home')
        #     away_team = call_name(idx,'away')

        #     odd_list = []
        #     odd_position_list  = []

        #     for position in [1,3,2]:
        #         try:
        #             odd_value = odd(idx,position,'odd')
        #             odd_list.append(odd_value)
        #             odd_position_list.append([idx,position])
        #         except:
        #             break
        #     prob_from_odd_list = cal_prob_from_odd(odd_list)
        #     # selected_idx = random_select_to_idx(odd_list)
            
        #     # '번호','경기일자','마감일시,'게임유형','홈팀','원정팀','배당률리스트','배당별확률','최종선택위치'
        #     # temp_df = temp_df = pd.DataFrame([[betting_name,date,end_time,betting_type,home_team,away_team,odd_list,prob_from_odd_list,betting_sports,league_name,handicap_value,under_over_value]])
        #     temp_df = temp_df = pd.DataFrame([[betting_name,date,end_time,betting_type,home_team,away_team,odd_list,prob_from_odd_list,betting_sports,league_name]])
        #     temp_df.columns =  ['번호','경기일자','마감일시','게임유형','홈팀','원정팀','배당률리스트','배당별확률','스포츠명','리그명','핸디','언오버']
        #     result_df_one =  pd.concat([result_df_one,temp_df.copy()], axis=0)

        # # DB에 저장하는데 우선 중복검사를 한후에 할것


        # new_data_cnt_one = 0

        # for index, row in result_df_one.iterrows():
        #     num = row['번호']
        #     date = row['경기일자']
        #     end_time = row['마감일시']
        #     betting_type = row['게임유형']
        #     home_team = row['홈팀']
        #     away_team = row['원정팀']

        #     db_check =  MatchDB_one.objects.filter(
        #         num = num,
        #         date = date,
        #         end_time = end_time,
        #         betting_type = betting_type,
        #         home_team = home_team,
        #         away_team = away_team,
        #     ).count()

        #     # db에 없다면???
        #     if db_check==0:
        #         new_data_cnt_one += 1
        #         odd_list = row['배당률리스트']
        #         prob_from_odd_list = row['배당별확률']
        #         betting_sports = row['스포츠명']
        #         league_name = row['리그명']
        #         # handicap_value = row['핸디']
        #         # under_over_value = row['언오버']

        #         MatchDB_one.objects.create(
        #         num = num,
        #         date = date,
        #         end_time = end_time,
        #         betting_type = betting_type,
        #         home_team = home_team,
        #         away_team = away_team,
        #         betting_sports = betting_sports,
        #         league_name = league_name,
        #         # handicap_value = handicap_value,
        #         # under_over_value = under_over_value
        #         )
        #     # DB에 있다면??
        #     else:
        #         pass


        return render(request,"main/save_result.html", context = dict(
            new_data_cnt = new_data_cnt,
            # new_data_cnt_one = new_data_cnt_one,
            result_df = result_df,
            # result_df_one = result_df_one

        ),status=200) #context html로 넘길것
    
class MainPage(APIView):
    def get(self, request):
                 
    
        return render(request,"main/home.html", context = dict(
            

        ),status=200) #context html로 넘길것
    

class DBsearch(APIView):
    def get(self, request):
        id = request.GET.get('username')
        pw = request.GET.get('password')

        request.session['id']= id
        request.session['pw']= pw

        m = str(datetime.today().month)
        d = str(datetime.today().day)
        h = str(datetime.today().hour)
        min = str(datetime.today().minute)

        if len(m)==1:
            m = "0"+str(m)
        else:
            m = str(m)

        if len(d)==1:
            d = "0"+str(d)
        else:
            d = str(d)

        if len(h)==1:
            h = "0"+str(h)
        else:
            h = str(h)

        if len(min)==1:
            min = "0"+str(min)
        else:
            min = str(min)
        

        df = pd.DataFrame(MatchDB.objects.all().values_list())
        df.columns = ['id','num','date','endtime','gametype','home','away','oddlist','oddproblist']
        df['endtime'] = df['endtime'].apply(lambda x : int(x.replace(":","")))
        df['oddlist'] = df['oddlist'].apply(lambda x :literal_eval(x))
        df['oddproblist'] = df['oddproblist'].apply(lambda x :literal_eval(x))
        
        # 오늘날짜로만 불러오기
        df = df[df['date'].str.startswith(m)]
        df = df[df['date'].str.endswith(d)]
        time_str = int(h+min)
        df = df[df['endtime']>time_str]
        for idx, row in df.iterrows():
            # 배당이 2개라면?
            if len(df.loc[idx,'oddlist'])==2:
                df.loc[idx,'odd1'] = df.loc[idx,'oddlist'][0]
                df.loc[idx,'odd2'] = 0
                df.loc[idx,'odd3'] = df.loc[idx,'oddlist'][1]
                df.loc[idx,'odd1_prob'] = df.loc[idx,'oddproblist'][0]
                df.loc[idx,'odd2_prob'] = 0
                df.loc[idx,'odd3_prob'] = df.loc[idx,'oddproblist'][1]
            else:
                df.loc[idx,'odd1'] = df.loc[idx,'oddlist'][0]
                df.loc[idx,'odd2'] = df.loc[idx,'oddlist'][1]
                df.loc[idx,'odd3'] = df.loc[idx,'oddlist'][2]
                df.loc[idx,'odd1_prob'] = round(df.loc[idx,'oddproblist'][0],3)
                df.loc[idx,'odd2_prob'] = round(df.loc[idx,'oddproblist'][1],3)
                df.loc[idx,'odd3_prob'] = round(df.loc[idx,'oddproblist'][2],3)
            # df.loc[idx,'endtime']

        df['odd1_prob'] = df['odd1_prob'].apply(lambda x: round(x,3))
        df['odd2_prob'] = df['odd2_prob'].apply(lambda x: round(x,3))
        df['odd3_prob'] = df['odd3_prob'].apply(lambda x: round(x,3))

        df['odd1_prob_str'] = df['odd1_prob'].apply(lambda x: str(round(x*100,2))+"%")
        df['odd2_prob_str'] = df['odd2_prob'].apply(lambda x: str(round(x*100,2))+"%")
        df['odd3_prob_str'] = df['odd3_prob'].apply(lambda x: str(round(x*100,2))+"%")
        # df['final_pick'] = df['oddlist'].apply(lambda x: random_select_to_idx(x))
        df = df.reset_index(drop=True)
        df = df.reset_index()
        df['pick_idx'] = df['index'].apply(lambda x : x+1)

        return render(request,"main/main.html", context = dict(
            df = df
            
        ),status=200) #context html로 넘길것
    
class Save_All_Data(APIView):
    def get(self, request):

        # Match_RESULT_DB.objects.all().delete()
        global driver
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('headless') # headless 모드 설정
        chrome_options.add_argument("window-size=1920x1080") # 화면크기(전체화면)
        chrome_options.add_argument("disable-gpu") 
        chrome_options.add_argument("disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')

        # 속도 향상을 위한 옵션 해제
        prefs = {'profile.default_content_setting_values':
                  {
                    'cookies' : 2,
                    'images': 2,
                    'plugins' : 2, 
                    'popups': 2,
                    'geolocation': 2,
                    'notifications' : 2,
                    'auto_select_certificate':  2,
                    'fullscreen' : 2,
                    'mouselock' : 2, 
                    'mixed_script': 2,
                    'media_stream' : 2, 
                    'media_stream_mic' : 2, 
                    'media_stream_camera': 2,
                    'protocol_handlers' : 2, 
                    'ppapi_broker' : 2, 
                    'automatic_downloads': 2, 
                    'midi_sysex' : 2, 
                    'push_messaging' : 2, 
                    'ssl_cert_decisions': 2,
                    'metro_switch_to_desktop' : 2, 
                    'protected_media_identifier': 2, 
                    'app_banner': 2, 'site_engagement' : 2,
                    'durable_storage' : 2
                                      }
                                      }   
        

        chrome_options.add_experimental_option('prefs', prefs)

        
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.implicitly_wait(1)

        #
        '''
        24년도 : 1- 54
        23년도 : 1- 153
        22년도 : 1- 108
        '''

        y_2022 = range(108,0,-1)
        y_2023 = range(153,0,-1)
        y_2024 = range(53,0,-1)

        date_list = []
        # 230001

        def zeros(n):
            zero = ""
            for i in range(n):
                zero += "0"
            return zero



        for year in ['24','23','23']:
            if year == '22':
                for i in y_2022:
                    zero_cnt = 4-len(str(i))
                    year_text = year + zeros(zero_cnt) + str(i)
                    date_list.append(year_text)
            if year == '23':
                for i in y_2023:
                    zero_cnt = 4-len(str(i))
                    year_text = year + zeros(zero_cnt) + str(i)
                    date_list.append(year_text)
            if year == '24':
                for i in y_2024:
                    zero_cnt = 4-len(str(i))
                    year_text = year + zeros(zero_cnt) + str(i)
                    date_list.append(year_text)

 


        # # https://www.betman.co.kr/main/mainPage/gamebuy/closedGameSlip.do?gmId=G101&gmTs=240047&gameDivCd=C

        for match_date in date_list:

            if Match_RESULT_DB.objects.filter(match_date=match_date).count() != 0:
                print("DB 중복")
                continue
            url = 'https://www.betman.co.kr/main/mainPage/gamebuy/closedGameSlip.do?gmId=G101&gmTs='+str(match_date)+'&gameDivCd=C'
            # 드라이버 url 연결 
            
            driver.get(url)
            driver.implicitly_wait(10)
            # 경기 수 초기화
            sports_cnt = 0

            ccs_list = []
            for i in tqdm(range(5000)):
                ccs = str('#tbd_gmBuySlipList > tr:nth-child(') + str(i+1) + ')'
                ccs_list.append(ccs)
            for idx ,ccs in enumerate(ccs_list):
                try :
                    check = driver.find_element(By.CSS_SELECTOR, ccs)
                    if check:
                        sports_cnt += 1
                    else:
                        break
                except:

                    break
            
            # 결과 df 생성
            result_df =pd.DataFrame()
            result_ls = []
            # for idx in tqdm(range(1,3)):
            for idx in tqdm(range(1,sports_cnt+1)):
                
                # 경기일자
                date = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(7)').text[:5]
                # 1. 경기의 번호와 홈팀/어웨이팀의 이름을 가져온다.
                betting_name = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(1) > span').text
                betting_type = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(4) > span').text
                betting_sports = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(3) > span.icoGame.small').text
                league_name = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(3) > span.db.fs11').text
                print(betting_name,betting_type,betting_sports,league_name)
                handicap_value = 0
                under_over_value = 0
                try:
                    value_text = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(5) > div > div.cell.tar > div > span').text
                    value_type = value_text.split(' ')[0]
                    value = value_text.split(' ')[1].replace("사전조건","")
                    if value_type == "H":
                        handicap_value = value
                    elif value_type =="U/O":
                        under_over_value = value

                except NoSuchElementException:
                    pass

                print(handicap_value,under_over_value)

                match_result =[]
                match_winner = 0

                
                try:
                    # 홈 점수 가져오기                   
                    value_home = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(5) > div > div.cell.tar > strong').text.replace('점수\n',"")
                    match_result.append(value_home) 
                    # 어웨이 점수 가져오기
                    value_away = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(5) > div > div.cell.tal > strong').text.replace('점수\n',"")
                    match_result.append(value_away)
                except NoSuchElementException:
                    pass

                try:
                    # 언오버 점수 가져오기
                    value_under_over = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(idx) +') > td:nth-child(5) > div > strong').text.replace('점수\n',"").replace('총 ',"")
                    match_result.append(value_under_over)

                except NoSuchElementException:
                    pass

                print(match_result)

                home_team = call_name(idx,'home')
                away_team = call_name(idx,'away')

                print(home_team,away_team)
                # 승자분석
                try:

                    # 승무패 분석
                    if len(match_result)==2:
                        # 승1패 경기
                        if betting_type =="승1패":
                            point = float(match_result[0]) -  float(match_result[1]) 
                            if point > 1:
                                match_winner = 1
                            elif 1>= point >= -1:
                                match_winner = 2                            
                            else:
                                match_winner = 3    
                        # 승5패 경기
                        elif betting_type =="승5패":

                            point = float(match_result[0]) -  float(match_result[1]) 
                            
                            if point > 5:
                                match_winner = 1
                            elif 5>= point >= -5:
                                match_winner = 2                            
                            else:
                                match_winner = 3   

                        # 승무패 경기
                        else:
                            if float(match_result[0]) > float(match_result[1]):
                                match_winner = 1
                            elif float(match_result[0]) == float(match_result[1]):
                                match_winner = 2
                            else:
                                match_winner = 3
                    # 언더오버 경기
                    else:
                        if float(match_result[0]) > float(under_over_value):
                            match_winner = 3                         
                        else:
                            match_winner = 1

                except NoSuchElementException:
                    match_result = []
                    match_winner = 0

                print(match_winner)

                    
                try:
                    odd_list = []
                    for position in [1,3,2]:
                        try:
                            odd_value = odd(idx,position,'odd')
                            odd_list.append(odd_value)
                        except:
                            break
                    prob_from_odd_list = cal_prob_from_odd(odd_list)
                except NoSuchElementException:
                    odd_list=[]
                    prob_from_odd_list = []
                    # selected_idx = random_select_to_idx(odd_list)

                print(odd_list)
                print(prob_from_odd_list)
                
                # '번호','경기일자','마감일시,'게임유형','홈팀','원정팀','배당률리스트','배당별확률','최종선택위치'

                result_ls.append([betting_name,date,betting_type,home_team,away_team,odd_list,prob_from_odd_list,betting_sports,league_name,handicap_value,under_over_value,match_result,match_winner,match_date])
                # # temp_df = pd.DataFrame([[betting_name,date,betting_type,home_team,away_team,odd_list,prob_from_odd_list,betting_sports,league_name,handicap_value,under_over_value,match_result,match_winner,match_date]])
                # temp_df.columns = ['번호','경기일자','게임유형','홈팀','원정팀','배당률리스트','배당별확률','스포츠명','리그명','핸디','언오버','경기결과','승자','회차']
                # result_df = pd.concat([result_df,temp_df],axis=0)
            # DB에 저장하는데 우선 중복검사를 한후에 할것

            result_df = pd.DataFrame(result_ls)
            result_df.columns = ['번호','경기일자','게임유형','홈팀','원정팀','배당률리스트','배당별확률','스포츠명','리그명','핸디','언오버','경기결과','승자','회차']
            print(result_df)
            new_data_cnt = 0

            for index, row in result_df.iterrows():
                num = row['번호']
                date = row['경기일자']
                betting_type = row['게임유형']
                home_team = row['홈팀']
                away_team = row['원정팀']


                db_check =  Match_RESULT_DB.objects.filter(
                    num = num,
                    date = date,
                    betting_type = betting_type,
                    home_team = home_team,
                    away_team = away_team,

                ).count()

                # db에 없다면???
                if db_check==0:
                    new_data_cnt += 1
                    odd_list = row['배당률리스트']
                    prob_from_odd_list = row['배당별확률']
                    betting_sports = row['스포츠명']
                    league_name = row['리그명']
                    handicap_value = row['핸디']
                    under_over_value = row['언오버']
                    match_result_value = row['경기결과']
                    match_winner = row['승자']
                    match_date = row['회차']
        

                    Match_RESULT_DB.objects.create(
                    num = num,
                    date = date,
                    betting_type = betting_type,
                    home_team  =home_team,
                    away_team = away_team,
                    odd_list = odd_list,
                    prob_from_odd_list  =  prob_from_odd_list,
                    betting_sports = betting_sports,
                    league_name = league_name,
                    handicap_value = handicap_value,
                    under_over_value = under_over_value,
                    match_result_value = match_result_value,
                    match_winner = match_winner,
                    match_date = match_date
                    )
                # DB에 있다면??
                else:
                    pass
                
                match_result = []
                match_winner = 0


        return render(request,"main/save_match_result.html", context = dict(

  
            
        ),status=200) #context html로 넘길것



class Pick(APIView):
    def get(self, request):
        
        # print(games)
        id = request.session.get('id',None)
        pw = request.session.get('pw',None)
        
        df = pd.DataFrame(MatchDB.objects.all().values_list())
        df_normal = making_betting_list(df,10)


        # 한폴
        # df_one = pd.DataFrame(MatchDB_one.objects.all().values_list())
        # df_normal_one = making_betting_list(df_one,1)


        global driver
        chrome_options = webdriver.ChromeOptions()

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.implicitly_wait(1)

        url = 'https://www.betman.co.kr/main/mainPage/gamebuy/buyableGameList.do'
        # 드라이버 url 연결 
        driver.get(url)
        driver.implicitly_wait(1)

        # 메인화면 로그인 버튼 클릭
        click_xpath('main_login')
        # id 입력버튼 클릭
        click_xpath("id")
        # id 입력
        driver.find_element(By.XPATH,'//*[@id="loginPopId"]').send_keys(id)
        # pw 입력버튼 클릭
        click_xpath('pw')
        # pw 입력
        driver.find_element(By.XPATH,'//*[@id="loginPopPwd"]').send_keys(pw)
        # 로그인 버튼 클릭
        click_xpath('login_button')
        # 승부식 게임구매 버튼 클릭
        click_xpath('buy_match')
    
        # 최종 pick 생성
        making_final_pick_idx(df_normal)

        # 금액 입력
        temp_betting_amt = 100
        driver.find_element(By.XPATH,'//*[@id="buyAmt"]').clear()
        driver.find_element(By.XPATH,'//*[@id="buyAmt"]').send_keys(str(temp_betting_amt))

        
        # 카트 담기 클릭
        click_xpath('//*[@id="asideGameTabBtn0"]/button[1]')
        driver.implicitly_wait(3)

        final_odd = driver.find_element(By.XPATH,'//*[@id="allotTxt"]').text
        final_amt = driver.find_element(By.XPATH,'//*[@id="allotAmtTxt"]').text

        # 구매 절차
        click_xpath('//*[@id="divTopMbrArea"]/div/div/ul[1]/li[5]/a')
        driver.implicitly_wait(10)
        click_xpath('//*[@id="totalChe03"]')
        driver.implicitly_wait(3)
        click_xpath('//*[@id="purchaseBtn"]')
        driver.implicitly_wait(3)
        click_xpath('//*[@id="countBtn"]')
        driver.implicitly_wait(3)
        click_xpath('//*[@id="mypgPassword"]')
        driver.implicitly_wait(3)
        driver.find_element(By.XPATH,'//*[@id="mypgPassword"]').send_keys(pw)
        time.sleep(3)
        click_xpath('//*[@id="countBtn"]')
        driver.implicitly_wait(3)

        return render(request,"main/betting_result.html", context = dict(
            df_normal = df_normal,
            # df_one_normal = df_one_normal,
            final_odd = final_odd,
            final_amt = final_amt,
  
            
        ),status=200) #context html로 넘길것


    
