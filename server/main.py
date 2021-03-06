import asyncio
import re
import time
import os
import csv
import mimetypes

from fastapi import FastAPI, Header, WebSocket, Request
import textract
from pdf2image import convert_from_path
import pandas as pd
import pytesseract
import numpy as np
from PIL import Image

from options import file_types, global_filter
from api import api_post_data

#auth = 'T2JpZ2FpbDpPYmlnYWlsSDR1'


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


class FileEntry:
    full_path: str
    parts: [str]
    guessed_type: str
    name: str
    text: str


def get_all_files(directory: str, root_dir: str):

    output = []
    for path, subdirs, files in os.walk(directory):

        for name in files:

            guessed_type = mimetypes.guess_type(name)[0]

            if guessed_type in ALLOWED_TYPES:

                file = FileEntry()
                file.full_path = os.path.join(path, name)
                file.guessed_type = guessed_type
                file.name = name
                file.parts = path.split(root_dir)[1].split('/')

                for i, part in enumerate(file.parts):
                    if part == "":
                        file.parts.pop(i)

                output.append(
                    file
                )

    return output


class ModularCategorizer:

    input_path: str
    root_path: str
    not_verified_dir: str
    files: [FileEntry]
    inn: str

    def analyse_input_path(self):

        # List of directories requested
        input_paths = self.input_path.split("/")

        self.root_path = ROOT_PATH

        for i, inpath in enumerate(input_paths):

            self.root_path = os.path.join(self.root_path, inpath)

            # Search for INN in folder name
            result_inn = re.findall(r"[0-9]{10}", inpath, re.MULTILINE)

            if len(result_inn) > 0:

                self.inn = result_inn[0]
                yield self.company_verification(input_paths[i + 1:])


    def company_verification(self, folder: [str]):

        self.not_verified_dir = os.path.join(self.root_path, "Не верифицированные документы")

        working_dir = self.root_path

        for f in folder:
            working_dir = os.path.join(working_dir, f)

        # Get all files and sub files
        self.files = get_all_files(working_dir, self.root_path)

        return


    async def verificate_one(self, file):

        if file.guessed_type == "application/pdf":
            txt = pdf2txt(file.full_path)

        elif file.guessed_type == "application/vnd.ms-excel" or file.guessed_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            txt = xls2txt(file.full_path)
        else:
            return

        txt = txt.lower()

        file.text = txt

        return await self.verify_file(self.inn, file)

    async def verify_file(self, inn, file: FileEntry):

        for category in file_types:

            verified = await self.verify_category(category, file)

            if verified:

                await self.report_to_api(inn, file, category)

                return

        print("Unrecognized! Moving..")
        os.rename(file.full_path, os.path.join(self.not_verified_dir, file.name))
        file.full_path = os.path.join(self.not_verified_dir, file.name)

        await self.report_fail_to_api(inn, file)

        return


    async def verify_category(self, category, file) -> bool:
        matching = await self.require_keys(file, category)

        if not matching:
            return False

        cat_path = category["path"]

        months = ['января','февраля','мая','марта','апреля','июня','июля','августа','сентября','октября','ноября','декабря']
        months2 = ['январь','февраль','март','апрель','май','июнь','июль','август','сентябрь','октябрь','ноябрь','декабрь']

        data_re = r"([0-9]{1,2})[ ]+(января|февраля|мая|марта|апреля|июня|июля|августа|сентября|октября|ноября|декабря)[ ]+([0-9]{4})"
        data_re2 = r"(январь|февраль|март|апрель|май|июнь|июль|август|сентябрь|октябрь|ноябрь|декабрь)[ \-]+(январь|февраль|март|апрель|май|июнь|июль|август|сентябрь|октябрь|ноябрь|декабрь)[ ]+([0-9]{4})"
        data_re3 = r"(января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)[ ]+([0-9]{4})"

        month = None
        year = None

        # print(file.text)

        result_data = re.findall(data_re2, file.text, re.MULTILINE)
        if len(result_data) > 0:
            month = months2.index(result_data[0][1]) + 1
            year = result_data[0][2]
        else:
            result_data = re.findall(data_re, file.text, re.MULTILINE)
            if len(result_data) > 0:
                month = months.index(result_data[0][1]) + 1
                year = result_data[0][2]
            else:
                result_data = re.findall(data_re3, file.text, re.MULTILINE)
                if len(result_data) > 0:
                    month = months.index(result_data[0][0]) + 1
                    year = result_data[0][1]

        print(month, year)


        # If we found date, and it is needed to be filtered
        if month is not None and "months" in category:
            if month not in category["months"]:
                return False

            quartal = 4

            if month < 4:
                quartal = 1
            elif month < 7:
                quartal = 2
            elif month < 10:
                quartal = 3

            for i, p in enumerate(cat_path):
                if p == "$quart":
                    cat_path[i] = f"{quartal} квартал"
                elif p == "$year":
                    cat_path[i] = year

        expected_path = self.root_path
        for d in cat_path:
            expected_path = os.path.join(expected_path, d)


        expected_name = category["name"] + file.name.split('.')[1]

        expected_path = os.path.join(expected_path, expected_name)

        print(file.full_path, "->", expected_path)

        os.rename(file.full_path, expected_path)
        file.full_path = expected_path

        return matching

    async def require_keys(self, file: FileEntry, category) -> bool:
        match = True

        for key in category["keys"]:
            match &= key.lower() in file.text

        global_match = False
        for key in global_filter:

            key_match = True
            for k in key.lower().split():
                key_match &= k in file.text

            global_match |= key_match

        if "block" in category:
            for b in category["block"]:
                if b in file.text:
                    return False

        return match & global_match


    async def report_to_api(self, inn, file, category):
        req = {
            "documentNomenclatureId": category["code"],
            "inn": inn,
            "unrecognised": False,
        }

        resp = await api_post_data(file.name, file.full_path, file.guessed_type, req)

    async def report_fail_to_api(self, inn, file):
        req = {
            "unrecognised": True,
        }

        resp = await api_post_data(file.name, file.full_path, file.guessed_type, req)


@app.get("/files")
async def get_fs_in_folder(name: str):

    fpath = os.path.join(ROOT_PATH, name)

    files = [f for f in os.listdir(fpath) if os.path.isfile(os.path.join(fpath, f))]
    folders = [f for f in os.listdir(fpath) if not os.path.isfile(os.path.join(fpath, f))]

    return {
        "folders": folders,
        "files": files
    }


@app.websocket("/verify")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    path = await websocket.receive_text()

    categorizer = ModularCategorizer()
    categorizer.input_path = path

    for t in categorizer.analyse_input_path():

        await websocket.send_json({
            "type": "total",
            "msg": len(categorizer.files)
        })
        print(len(categorizer.files))

        for i, file in enumerate(categorizer.files):

            tasks = []
            ev = asyncio.Event()

            async def message(r):
                await websocket.send_json({
                    "type": "current",
                    "msg": i + 1
                })
                r.set()

            async def runner(f, r):
                await r.wait()
                await categorizer.verificate_one(f)

            tasks.append(asyncio.ensure_future(message(ev)))
            tasks.append(asyncio.ensure_future(runner(file, ev)))

            await asyncio.gather(*tasks)

            print(i + 1)

    return

@app.get("/criteria")
async def get_criteria():

    global file_types

    return file_types


@app.post("/criteria")
async def update_criteria(request: Request):

    global file_types
    file_types = await request.json()

    return {
        "status": "ok"
    }

@app.get("/global")
async def get_global_filter():

    global global_filter

    return global_filter


@app.post("/global")
async def update_global_filter(request: Request):

    global global_filter
    global_filter = await request.json()

    return {
        "status": "ok"
    }