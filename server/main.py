import asyncio
import base64
import json
import re


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
from fastapi import FastAPI, Header, WebSocket, Request
import requests
import base64
from requests_toolbelt.multipart.encoder import MultipartEncoder
import mimetypes

from options import file_types
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

        await self.report_fail_to_api(inn, file)

        return


    async def verify_category(self, category, file) -> bool:
        matching = await self.require_keys(file, category)

        print("Expected", category["path"])
        print("Got", file.parts)
        print("File", file.name)

        data_re = r"([0-9]{1,2})[ ]+(января|февраля|марта|апреля|июня|июля|августа|сентября|октября|ноября|декабря)[ ]+([0-9]{4})"
        result_data = re.findall(data_re, file.text, re.MULTILINE)

        if len(result_data) > 0:
            print(result_data[0])

        return matching

    async def require_keys(self, file: FileEntry, category) -> bool:
        match = True

        for key in category["keys"]:
            match &= key.lower() in file.text

        return match


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


    async def send_msg(self, msg):
        await self.socket.send_text(json.dumps(msg))

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