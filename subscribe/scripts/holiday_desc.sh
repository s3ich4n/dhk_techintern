#!/bin/bash

echo "[o] 이메일 전송 배치파일 실행."

weekday="weekday"

values=$(python parse_holiday_data.py 2>&1)

if [[ ${values} == ${weekday} ]]; then
    echo "[o] 오늘은 주중인 것으로 감지되었습니다. sendmail을 실행합니다."
    tmp=$(cd ../.. && python manage.py sendmail)
else
    echo "[!] 주말 혹은 공휴일입니다. 실행을 중지합니다."
fi
