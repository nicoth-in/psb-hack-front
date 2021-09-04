import base64
import json
import re


import aiohttp
import asyncio


from PIL import Image
from pydantic import BaseModel
from pytesseract import Output
import pytesseract
import numpy as np
import cv2
import time
import os
from pdf2image import convert_from_path
import pandas as pd
import textract
import os
import csv
from fastapi import FastAPI, Header
import requests
import base64
from requests_toolbelt.multipart.encoder import MultipartEncoder
import mimetypes


#auth = 'T2JpZ2FpbDpPYmlnYWlsSDR1'





def detect_russian_word(imagePNG):
    text = pytesseract.image_to_string(Image.open(imagePNG), lang='rus')
    print(text)


file_types = [
    {
        "keys": ['Устав', 'Уставный капитал', 'Органы управления', 'Резервный фонд', 'Бюллетени'],
        "path": ['Юридическое досье', 'Учредительные и иные внутренние документы (положения)'],
        "code": '33a37ce4-c6a9-4dad-8424-707abd47c125',
        "name": "Устав_действующий"
    },
    {
        "keys": ['Положение о совете директоров','Председатель совета директоров', 'Письменное мнение', 'Опросный лист'],
        "path": ['Юридическое досье', 'Учредительные и иные внутренние документы (положения)'],
        "code": '555ced1c-c169-4d61-9a82-348801494581',
        "name": "Положение о СД"
    },
    {
        "keys": ['Бухгалтерский баланс','0710001', 'Актив', 'Пассив'],
        "path": ['Финансовое досье', '$year', '$quart', 'Бухгалтерская отчетность'],
        "code": '4f501f4a-c665-4cc8-9715-6ed26e7819f2',
        "name": "Бухгалтерская отчетность_форма 1"
    },
    {
        "keys": ['Отчет о финансовых результатах','0710002','Чистая прибыль','Налог на прибыль'],
        "path": ['Финансовое досье', '$year', '$quart', 'Бухгалтерская отчетность'],
        "code": 'cabd193c-f9a9-4a9c-a4ae-80f0347adf40',
        "name": "Бухгалтерская отчетность_форма 2"
    },
    {
        "keys": ['Бухгалтерский баланс','0710001', 'Актив', 'Пассив',],
        "path": ['Финансовое досье', '$year', '$quart', 'Бухгалтерская отчетность'],
        "code": '2e321818-4571-43ae-9e08-2ade54b83e14',
        "name": "Бухгалтерская отчетность_форма 1 _промежуточная"
    },
    {
        "keys": ['Отчет о финансовых результатах', '0710002', 'Чистая прибыль', 'Налог на прибыль'],
        "path": ['Финансовое досье', '$year', '$quart', 'Бухгалтерская отчетность'],
        "code": '3b4f4647-f755-4100-bd63-059627107919',
        "name": "Бухгалтерская отчетность_форма 2 _промежуточная"
    },
    {
        "keys": ['Аудиторское заключение', 'Сведения об аудируемом лице', 'Сведения об аудиторе', 'Основание для выражения мнения', 'Ответственность аудитора'],
        "path": ['Финансовое досье', '$year', '$quart', 'Бухгалтерская отчетность'],
        "code": '16f35ccc-b90f-4731-8178-11f3e0e3ca20',
        "name": 'Аудиторское заключение'
    },
    {
        "keys": ['Презентация компании', 'Обзор рынка', 'Обзор компании', 'История компании'],
        "path": ['Описание бизнеса'],
        "code": 'a397c2cf-c5ad-4560-bc65-db4f79840f82',
        "name": "Описание_деятельности_ГК"
    },
    {
        "keys": ['Протокол', 'ИТОГИ ГОЛОСОВАНИЯ', 'решение', 'Принято'],
        "path": ['Юридическое досье', 'Документы, подтверждающие полномочия на совершение сделки'],
        "code": '3af37c7f-d8b1-46de-98cc-683b0ffb3513',
        "name": "Решение_назначение ЕИО"
    }
]

# search_list_b_o_f_1 = ['бухгалтерский','баланс', 'форма', 'по', 'окуд', '0710001' ,'актив','пассив']
# search_list_b_o_f_2 = ['отчет о финансовых результатах','дата', 'форма', 'по', 'окуд', '0710002' ,'чистая прибыль','налог на прибыль']
# ustav = ['устав','уставный капитал','органы управления','резервный фонд','бюллетени']
# polozhenie_o_sd= ['положение о совете директоров','председатель совета директоров','письменное мнение','опросный лист','уведомление о проведении cовета директоров']
# search_list_b_o_f_1_p = ['бухгалтерский','баланс', 'форма', 'по', 'окуд', '0710001' ,'актив','пассив']
# search_list_b_o_f_2_p = ['отчет о финансовых результатах','дата', 'форма', 'по', 'окуд', '0710002' ,'чистая прибыль','налог на прибыль']
# auditor_zak = ['аудиторское заключение','сведения об аудируемом лице','сведения об аудиторе','основание для выражения мнения','ответственность аудитора']
# deyatelinosti_gk = ['презентация компании', 'история компании', 'обзор рынка', 'обзор компании']
# razreshenie_naznachenie = ['протокол совета директоров','дата составления протокола','избрание/назначение генерального директора','итоги голосования','принятое решение']
# nome_code_list = ['33a37ce4-c6a9-4dad-8424-707abd47c125','555ced1c-c169-4d61-9a82-348801494581','4f501f4a-c665-4cc8-9715-6ed26e7819f2','cabd193c-f9a9-4a9c-a4ae-80f0347adf40','2e321818-4571-43ae-9e08-2ade54b83e14','3b4f4647-f755-4100-bd63-059627107919','16f35ccc-b90f-4731-8178-11f3e0e3ca20','a397c2cf-c5ad-4560-bc65-db4f79840f82','3af37c7f-d8b1-46de-98cc-683b0ffb3513']


async def api_post_data(file_name: str, file_path: str, content_type: str, report: dict):
    return ["ok"]

    print(report)

    #auth = base64.encodebytes(b"Obigail:ObigailH4u")
    auth = 'T2JpZ2FpbDpPYmlnYWlsSDR1'

    headers = {
        'accept': '*/*',
        'Content-Type': 'multipart/form-data',
        'Authorization': f'Basic {auth}',
    }

    endpoint = 'http://elib-hackathon.psb.netintel.ru/elib/api/service/documents'

    async with aiohttp.ClientSession() as session:

        data = aiohttp.FormData()
        data.add_field('attachments',
                       open(file_path, 'rb'),
                       filename=file_path
                       )
        data.add_field('createRequest', json.dumps(report))

        print(data)

        async with session.get(endpoint, headers=headers, data=data) as resp:
            return await resp.json()


def pdf2txt(filePath):
    start = time.time()
    doc = convert_from_path(filePath)
    path, fileName = os.path.split(filePath)
    fileBaseName, fileExtension = os.path.splitext(fileName)
    txt=''
    for page_number, page_data in enumerate(doc):
        txt += pytesseract.image_to_string(Image.fromarray(np.asarray(page_data)), lang='rus')
    # detect_russian_word(doc)
    end = time.time()
    print("TIME", end - start)
    return txt

def xls2txt(filePath):
    df = pd.read_excel(filePath, 0)
    # print(df.to_string())
    # for word in df:
    dff = df.to_string().replace('NaN', '')
    dff1 = dff.replace('  ', '')
    return(dff1)

def doc2txt(filePath):
    text = textract.process(filePath)
    return text

def csv2txt(filePath):
    strr = ''
    with open(filePath, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            print(row)
            strr += str(row)
    return strr



app = FastAPI()


ALLOWED_TYPES = ["application/pdf", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]
ROOT_PATH = "/home/ivan/Загрузки/Промсвязьбанк Датасет/Тестовый dataset/"


def verify_text(txt, search_list):
    match = True

    for key in search_list["keys"]:
        match &= key.lower() in txt

    return match


class FileEntry:

    full_path: str
    parts: [str]
    guessed_type: str
    name: str


def get_all_files(directory: str):

    output = []
    for path, subdirs, files in os.walk(directory):

        for name in files:

            guessed_type = mimetypes.guess_type(name)[0]

            if guessed_type in ALLOWED_TYPES:

                file = FileEntry()
                file.full_path = os.path.join(path, name)
                file.guessed_type = guessed_type
                file.name = name
                file.parts = path.split(directory)[1].split('/')

                for i, part in enumerate(file.parts):
                    if part == "":
                        file.parts.pop(i)

                output.append(
                    file
                )

    return output


def verify_file(path: str, ftype: str):

    txt = ""

    if ftype == "application/pdf":
        txt = pdf2txt(path)

    elif ftype == "application/vnd.ms-excel" or ftype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        txt = xls2txt(path)

    txt = txt.lower()
    print(txt)

    r"([0-9]{1,2})[ ]+(января|февраля|марта|апреля|июня|июля|августа|сентября|октября|ноября|декабря)[ ]+([0-9]{4})"

    for search_list in file_types:
        verified = verify_text(txt, search_list)
        if verified:
            return search_list

    return None


async def company_verification(inn: str, root_path: str, folder: [str]):

    not_verified_dir = os.path.join(root_path, "Не верифицированные документы")

    output = []

    working_dir = root_path

    for f in folder:
        working_dir = os.path.join(working_dir, f)

    # Get all files and sub files
    files = get_all_files(working_dir)

    for file in files:

        ver_result = verify_file(file.full_path, file.guessed_type)
        if ver_result is None:
            print("Unrecognized! Moving..")
            os.rename(file.full_path, os.path.join(not_verified_dir, file.name))

        if ver_result is not None:

            print("Expected", ver_result["path"])
            print("Got", file.parts)

            print("File", file.name)

            req = {
                "documentNomenclatureId": ver_result["code"],
                "inn": inn,
                "unrecognised": False,
            }

            resp = await api_post_data(file.name, file.full_path, file.guessed_type, req)
            print(resp)



@app.get("/files")
async def get_goods_array(name: str):

    fpath = os.path.join(ROOT_PATH, name)

    files = [f for f in os.listdir(fpath) if os.path.isfile(os.path.join(fpath, f))]
    folders = [f for f in os.listdir(fpath) if not os.path.isfile(os.path.join(fpath, f))]

    return {
        "folders": folders,
        "files": files
    }




@app.get("/verify")
async def get_goods_array(path: str):

    # List of directories requested
    input_paths = path.split("/")
    root_path = ROOT_PATH

    for i, inpath in enumerate(input_paths):
        root_path = os.path.join(root_path, inpath)

        # Search for INN in folder name
        result_inn = re.findall(r"[0-9]{10}", inpath, re.MULTILINE)

        if len(result_inn) > 0:
            inn = result_inn[0]
            # Call for each INN it's own verify
            await company_verification(inn, root_path, input_paths[i+1:])

    return {}