# 2018 딜리버리히어로코리아 Tech Internship 프로젝트

이 소스코드는 2018 딜리버리히어로코리아 Tech Internship 프로젝트 때 당시 Tech Intern이었던 저와 다른 3분의 동기와 함께 작성한 소스코드 입니다.

## 1. How to start project
### 1-1. 가상환경 설치
  ``
  ~~~
  $ python3 -m venv Alertyo 
  $ pip install -r requirements.txt
  ~~~
  OR
  ~~~
  PyCharm -> preference -> Project AlertYo -> python interpreter -> show all -> (+)click -> ok
  $ pip install -r requirements.txt
  ~~~
<br>

 requirements.txt 에서 install 할때  django-admin 설치 실패 하는 문제가 간혹 발생할 수 있음
 ~~~
 pip install UnicodeDecodeError: 'ascii' codec can't decode byte 0xe6 in position 162
 ~~~
  
 이런경우 해당 프로젝트 경로에서 `$ pip install django-admin`으로 수동 설치해주고 다시 `$ pip install -r requirements.txt` 하면 정상 설치

 ### 1-2. 세팅 환경
  * 개발 참여자별 세팅 환경을 가지고 있음   
  * dev_{number}
    * dev_001.py
    * dev_002.py
    * dev_003.py
    * dev_004.py
 ### 1-3. 데이터베이스 설정
  * 데이터베이스 설정 시 자신의 로컬 데이터베이스 설정에 맞게 정보 변경
       * 'NAME': '',
       * 'USER': '',
       * 'PASSWORD': '',
       * 'HOST': '127.0.0.1',
       * 'PORT': '5432',

    
 ### 1-4. 모델 마이그레이션
 ~~~
 python manage.py migrate --settings=configuration.settings.dev_{number}
 ~~~  
 
 ### 1-5. 더미데이터 추가 
 ~~~
 python manage.py loaddata demo.json --settings=configuration.settings.dev_{number}
 ~~~
 
 ### 1-6. 서버 실행
 ~~~
 python manage.py runserver --settings=configuration.settings.dev_{number}
 ~~~

 ---   

## 2. Specification
* Language and Web Framework: Python 3.6.6, Django 2.1.2
* DB: PostgreSQL 9.6
* FE: jquery 3.3.1, [FullCalendar 3.9.0](https://github.com/fullcalendar)
* 그 외 다른 파이썬 라이브러리는 `requirements.txt`를 참고해 주세요

---
 
## 3. 프로젝트 구조 


### configuration
  * settings
      * base.py : 장고 설정의 공통된 내용
      * dev_{number}.py : 개인 개발환경 세팅 
      * production.py : 배포 세팅 
    
### apps
  * app
    * exception : 공통된 익셉션 처리
    * fixtures : 테스트에 사용되는 json더미데이터 파일
    * forms : 등록/수정에 사용되는 form
    * ...    
### static & template     
   * static
        * common : 여러 앱에서 공통으로 사용하는 정적 파일
        * schedule: schedule 앱에서 사용하는 정적 파일
        * account: account 앱에서 사용하는 정적 파일 
        * ...
   
   * template
        * static 구조와 동일

---

## 4. 참고

* 민감 정보는 export를 위해 FIXME tag를 붙이고 삭제됨.

---

### 5. Special Thanks to

* 4개월간 함께했던 남은 동기 3분들께
* 물심양면으로 도와주셨던 멘토분들과 다른 모든분들께
