# AlertYo

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
  * dev_{개발자 이름 이니셜}
    * dev_kde.py
    * dev_ksr.py
    * dev_nic.py
    * dev_yse.py
 ### 1-3. 데이터베이스 설정
  * 데이터베이스 설정 시 자신의 로컬 데이터베이스 설정에 맞게 정보 변경!!
       * 'NAME': 'alertyo_db',
       * 'USER': 'local_dev_ksr',
       * 'PASSWORD': '1234',
       * 'HOST': '127.0.0.1',
       * 'PORT': '5432',

    
 ### 1-4. 모델 마이그레이션
 ~~~
 python manage.py migrate --settings=configuration.settings.dev_{name}
 ~~~  
 
 ### 1-5. 더미데이터 추가 
 ~~~
 python manage.py loaddata demo.json --settings=configuration.settings.dev_{name}
 ~~~
 
 ### 1-6. 서버 실행
 ~~~
 python manage.py runserver --settings=configuration.settings.dev_{name}
 ~~~

 ---   

## 2. Specification
* Python 3.6.6
* Django 2.1.2
* django-debug-toolbar 1.10.1
* postgresql 9.6
* [fullcalendar 3.9.0](https://github.com/fullcalendar)
    * bootstrap 4 support
    * jquery 3.3.1
     
     
 
## 3. 프로젝트 구조 


### configuration
  * settings
      * base.py : 장고 설정의 공통된 내용
      * dev_{name}.py : 개인 개발환경 세팅 
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
