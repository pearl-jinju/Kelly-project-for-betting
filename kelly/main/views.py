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

import time
import random

from datetime import datetime


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


def odd(x:int,y:int,action):
    """
    x = X 번째 경기 \n
    y = y 번째 배당 \n
    action -- keyword\n
     -- 'odd' 배당율 숫자 가져오기 \n
     -- 'click' 배당 버튼 클릭  \n
    """

    if action == 'odd':
        return float(driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(x) +') >  td:nth-child(6) > div > div > button:nth-child('+ str(y) +') > span.db').text[:4])
    if action == "click":
        element = driver.find_element(By.CSS_SELECTOR,'#tbd_gmBuySlipList > tr:nth-child('+ str(x) +') > td:nth-child(6) > div > div > button:nth-child('+ str(y) +')')
        actions = ActionChains(driver)
        actions.click(element).perform()

# Create your views here.
# Create your views here.
class AutoBet(APIView):
    def get(self, request):
        # 쿼리를 받음
        id = request.GET.get('username')
        pw = request.GET.get('password')
        sports = request.GET.get('sports')
        betstyle = request.GET.get('betstyle')
        cashlimit = request.GET.get('cashlimit')


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
        ADVANTAGE_POINT_PLUS = 0.1
        # 정배당인 경우 그 종목에 (고배당/저배당-1)/ADVANTAGE_POINT_RATE 만큼 더함
        ADVANTAGE_POINT_RATE = 2


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

                
                # 캘리비율 최대값 제한
                MAX_KELLY_RATE = 0.1
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
    

class MainPage(APIView):
    def get(self, request):
                 
    
        return render(request,"main/home.html", context = dict(

        ),status=200) #context html로 넘길것
    
