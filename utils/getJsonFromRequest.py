import json


class GetJsonFromRequest:
    def __int__(self, request):
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        return body
    def jsonArrToJson(self, jsonArray):
        return jsonArray[1:len(jsonArray)-1]