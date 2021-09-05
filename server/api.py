
import aiohttp
import json

async def api_post_data(file_name: str, file_path: str, content_type: str, report: dict):
    #return ["ok"]

    print(report)

    #auth = base64.encodebytes(b"Obigail:ObigailH4u")
    auth = 'T2JpZ2FpbDpPYmlnYWlsSDR1'

    headers = {
        'Content-Type': 'multipart/form-data',
        'Authorization': f'Basic {auth}',
    }

    endpoint = 'http://elib-hackathon.psb.netintel.ru/elib/api/service/documents'

    async with aiohttp.ClientSession() as session:

        data = aiohttp.FormData()
        data.add_field('attachments',
                       open(file_path, 'rb').read(),
                       filename=file_path
                       )
        data.add_field('createRequest', json.dumps(report))

        # data = {
        #     'attachments': open(file_path, 'rb'),
        #     'createRequest': json.dumps(report)
        # }

        # data = {'attachments': (file_path, open(file_path, 'rb')),
        #         'createRequest': json.dumps(report)}

        #print(data)

        async with session.post(endpoint, headers=headers, data=data) as resp:
            print(await resp.json())
