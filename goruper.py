"""grouper.py

EXIF 기반 파일 분류(동영상 파일도 가능한지 확인요망)

필수 설정 변수
    _path_dir       # 작업 경로
    _is_year_path_dir       # _path_dir가 연도폴더인지 아닌지
    _fr_year        # 생성할 폴더 시작년도
    _to_year        # 생성할 폴더 종료년도

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


#!/usr/bin/python
# -*- coding: utf-8 -*-

"""



import shutil
import os
import re

from PIL import Image, ExifTags



# 기초 데이터 설정
_months = ['01', '02', '03', '04',
           '05', '06', '07', '08',
           '09', '10', '11', '12']  # 월폴더

_ext_filter_img = ['.jpg', '.jpeg', '.png', '.gif']     # 사진 확장자 Filter
_ext_filter_video = ['.mp4', '.mov', '.mkv', '.avi']    # 동영상 확장자 Filter
_ext_filter_all = _ext_filter_img + _ext_filter_video          # 모든 확장자 Filter

_exif_filter = ['DateTimeOriginal', 'DateTimeDigitized', 'DateTime']    # EXIF 날짜 Tag Filter

_path_dir = ''  # 디렉토리 설정(연도폴더)
#''C:\Users\user\Desktop\PythonTestData'  # 디렉토리 설정(연도폴더)

_is_year_path_dir = None        # _path_dir가 연도폴더인지 아닌지

_fr_year = ''       # 생성할 폴더 시작년도
_to_year = ''       # 생성할 폴더 종료년도



def get_year_list(year_fr, year_to):
    """기간에 해당하는 연도를 리스트로 생성하여 리턴한다.
    시작년도가 종료년도보다 크면 None 리턴

    :param
        year_fr: 시작년도
        year_to: 종료년도

    :return:
        연도 리스트
    """
    years = []

    if year_fr > year_to:
        years = None

    try:
        y_fr = int(year_fr)
        y_to = int(year_to)

        for i in range(y_fr, y_to+1):
            years.append(i)

    except Exception as e:
        print(e)

    return years


def set_path_dir(path_dir):
    _path_dir = path_dir


def set_ext_filter_all():
    _ext_filter_all = _ext_filter_img + _ext_filter_video


def set_ext_filter_img(ext):
    _ext_filter_img = ext
    set_ext_filter_all()


def set_ext_filter_video(ext):
    _ext_filter_video = ext
    set_ext_filter_all()


def make_year_dirs(path_dir, years, crt_ym):
    """해당 경로 하위에 연도 폴더를 생성한다.
    디렉토리 정보를 매개변수로 받아 해당 경로 내부에 연도폴더가 존재하지 않으면 생성한다.
    연도폴더가 과도하게 생성되는걸 방지하기 위해 10개만 생성한다.

    :param
        path_dir: 경로
        std_year: 연도폴더 시작년도

    :return:
        연도 리스트
    """

    print('기준 path_dir : ' + path_dir)

    f_ls = os.listdir(path_dir)
    f_ls.sort()

    # print(f_ls)

    len_years = len(years)

    if len_years > 10:  # 10개 초과하여 생성되지 않도록 years 재설정 한다.
        year_fr = min(years)
        years = get_year_list(year_fr, year_fr+9)

    for year in years:
        path_year = os.path.join(path_dir, str(year))
        if not (os.path.isdir(path_year)):
            print(str(year), '연폴더 생성')
            os.makedirs(path_year)
            if crt_ym:
                print('월폴더 생성 시작')
                make_ym_dirs(path_year)



def make_ym_dirs(path_dir):
    """해당 경로 하위에 연도_월 폴더를 생성한다.
    특정 연도폴더의 디렉토리 정보를 매개변수로 받아 해당 연도폴더 내부에 연도_월 폴더가 존재하지 않으면 생성한다.

    :param
        path_dir: 특정 연도폴더의 경로

    :return:
        리턴 없음
    """

    year = os.path.basename(path_dir)  # 경로의 마지막 폴더 이름 가져온다(연도)
    try:
        year = int(year)
    except Exception as e:
        print(e)

    if isinstance(year, int) \
            and len(str(year)) == 4:     # 숫자이고, 네글자인 경우
        for i in range(12):  # YYYY_MM 형태로 폴더를 만든다
            ym = str(year) + '_' + _months[i]  # 월폴더 명
            if not (os.path.isdir(os.path.join(path_dir, ym))):  # 월폴더가 없는 경우
                os.makedirs(os.path.join(path_dir, ym))  # 월폴더 생성
                print(os.path.join(path_dir, ym), '디렉토리 생성 완료')



def del_dir_do_not_contain_anything(path_dir, upper_path_dir=None):
    """빈폴더인 경우 삭제한다.
    폴더 내부 파일리스트를 확인해서 데이터가 없는 경우 해당 폴더를 삭제한다.

    :param
        path_dir: 경로

    :return:
        리턴 없음
    """
    f_ls = os.listdir(path_dir)  # 폴더 내부 파일 리스트를 가져온다
    f_ls.sort()

    if not f_ls:
        try:
            os.rmdir(path_dir)
            print(path_dir + ' 폴더 삭제 : 내부파일 없음')
        except Exception as e:
            print(path_dir, e)
    else:
        for i in f_ls:
            full_path = os.path.join(path_dir, i)
            if os.path.isdir(full_path):
                del_dir_do_not_contain_anything(full_path, path_dir)

    if not upper_path_dir:
        del_dir_do_not_contain_anything(path_dir, 'None')



def get_file_list(path_dir):
    f_ls = os.listdir(path_dir)  # 폴더 내부 파일 리스트를 가져온다
    f_ls.sort()

    return f_ls



def get_exif_file(path_item):
    """해당 이미지의 EXIF 정보를 가져온다
    파일의 EXIF를 얻고, 각 EXIF TAG와 TAG값을 딕셔너리에 담는다.

    :param
        path_item: 파일 경로(파일명 포함)

    :return:
        exif_raw_data: EXIF RAW 정보
        exif_data: EXIF TAG별 값을 갖는 딕셔너리
    """

    ext = os.path.splitext(path_item)[1].lower()


    if os.path.isfile(path_item) and ext in ext_filter:
        exif_data = {}
        img = Image.open(path_item)

        try:
            exif_raw_data = img._getexif()

            if exif_raw_data is not None:
                for tag, value in exif_raw_data.items():
                    decodedTag = ExifTags.TAGS.get(tag, tag)
                    exif_data[decodedTag] = value

        except Exception as ex:
            print('get_exif() Exception : ', ex)
            return None, None

        else:
            return exif_raw_data, exif_data
    else:
        return None, None


def get_exif_multi_file(path_dir):
    """해당 경로에 있는 모든 파일의 EXIF 정보를 가져온다
    파일의 EXIF를 얻고, 각 EXIF TAG와 TAG값을 딕셔너리에 담는다.

    :param
        path_item: 파일 경로

    :return:
        파일별 exif_data를 갖는 딕셔너리
    """

    exif_raw_data = {}
    exif_data = {}

    exif_data_files = {}

    if os.path.isdir(path_dir):

        path_item = os.listdir(path_dir)  # 폴더 내부 파일 리스트를 가져온다
        f_full_path_ls = []

        for item_name in path_item:
            f_full_path_ls.append(os.path.join(path_dir, item_name))

        for item_name in f_full_path_ls:
            exif_raw_data, exif_data = get_exif_file(item_name)
            exif_data_files[item_name] = exif_data

        return exif_data_files
    else:
        return None


def get_oldest_date(exif_data_files):
    min_date_files = {}

    for key in exif_data_files:
        inner_dict = exif_data_files[key]
        # print(str(key), inner_dict)
        if inner_dict:
            date_time = []
            # print(str(key) + ' -> inner_dict :', inner_dict)
            for inner_key in inner_dict:
                if str(inner_key).find('Date') > -1:
                    inner_value = inner_dict[inner_key]
                    # print(str(key) + ' -> ' + str(inner_key) + ' : ' + str(inner_value))
                    date_time.append(inner_value)
            # print(str(key))
            # print(str(key) + ' -> min_date : ' + min(date_time))

            if len(date_time):
                min_date_files[str(key)] = min(date_time)

    return min_date_files




def get_path_src_dst(min_date_files):

    path_src_dst = {}

    p = re.compile(r'(\d{4}).*?(\d{2}).*?(\d{2})')

    for file in min_date_files:
        file_name = os.path.basename(file)
        std_date = min_date_files[file]

        if os.path.isfile(file):
            m = p.match(std_date)

            # EXIF 정보로 일자를 가져오지 못하면 파일명에서 일자를 찾는다.
            if m is None:
                m = p.search(file_name)

            if m:
                year = m.group(1)
                year_month = m.group(1) + '_' + m.group(2)
                if _is_year_path_dir:
                    dst_path_item = os.path.join(_path_dir, year_month, file_name)
                else:
                    dst_path_item = os.path.join(_path_dir, year, year_month, file_name)

                path_src_dst[file] = dst_path_item

    return path_src_dst




if __name__ == "__main__":

    # 기초 데이터 설정
    ext_filter = ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.mkv', '.avi']      # 확장자 필터

    _path_dir = 'C:/Users/user/Desktop/ddd'    # 작업 경로  ex) 'C:/Users/user/Desktop/ccc'
    _is_year_path_dir = False        # _path_dir가 연도폴더인지 아닌지

    _fr_year = '2010'       # 생성할 폴더 시작년도
    _to_year = '2019'       # 생성할 폴더 종료년도

    if os.path.isdir(_path_dir):
        # 연도폴더와 하위 월폴더 생성
        if not _is_year_path_dir:
            years = get_year_list(_fr_year, _to_year)
            make_year_dirs(_path_dir, years, crt_ym=True)
        else:
            print(_path_dir)
            # year = os.path.basename(_path_dir)
            # years = get_year_list(year, year)
            make_ym_dirs(_path_dir)

        


        # 작업 경로 내부 파일별로 EXIF 정보 가져오기
        exif_data_files = get_exif_multi_file(_path_dir)

        # 파일별로 가장 이전 EXIF 날짜 가져오기
        min_date_files = get_oldest_date(exif_data_files)

        # 파일별 EXIF 날짜 태그를 기준으로 최종 경로를 구하고(없는 경우 파일명으로 최종 경로 구함), 현재경로와 최종경로를 딕셔너리로 가져오기
        path_src_dst = get_path_src_dst(min_date_files)
        
        # 현재경로와 최종경로 정보를 기준으로 파일 이동
        for key in path_src_dst:
            try:
                shutil.move(key, path_src_dst[key])  # 파일 이동
                print('COMPLETION >>>  [' + key + ']  ->  [' + path_src_dst[key] + ']')
            except Exception as e:
                print('ERROR >>>  [' + key + ']', e)

        # 폴더가 빈폴더인 경우 삭제
        del_dir_do_not_contain_anything(_path_dir)


