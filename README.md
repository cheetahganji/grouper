# grouper

EXIF 기반 파일 분류(동영상 파일도 가능한지 확인요망)

하기 EXIF 기준으로 파일을 분류하며 순서는 다음과 같다.
    BASE EXIF
    1. DateTimeOriginal
    2. DateTimeDigitized
    3. DateTime

확장자 필터
    - jpg/jpeg/png/gif 등
    - mp4/mov/mkv/avi 등

작업흐름
    # 연도폴더와 하위 월폴더 생성
    # 작업 경로 내부 파일별로 EXIF 정보 가져오기
    # 파일별로 가장 이전 EXIF 날짜 가져오기
    # 파일별 EXIF 날짜 태그를 기준으로 최종 경로를 구하고(없는 경우 파일명으로 최종 경로 구함), 현재경로와 최종경로를 딕셔너리로 가져오기
    # 현재경로와 최종경로 정보를 기준으로 파일 이동
    # 폴더가 빈폴더인 경우 삭제
