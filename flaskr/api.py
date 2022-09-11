"""REST API for Web App Report of Formula one Qualification Racing
    This API intended to get report of Monaco 2018 qualification (Q1)
    Call this api passing a version of api and type of report
    (report or pilots). You can also add format parameter
    (?format=json or ?format=xml) JSON is default.
    Example:
        /api/v1/report/?format=xml
        /api/v1/report/?format=json
        or
        /api/v1/pilots/

    To extract OpenAPI-Specification go to:
    apidocs/

    Functions:
        qual_report_to_xml_et(report) -> str:
            Convert qualification report to XML. Return xml string

        pilots_report_to_xml_et(report) -> str:
            Convert pilots report to XML. Return xml string
"""

from flask import jsonify, make_response
from flask_restful import Resource, Api, abort, request
from flasgger import Swagger
from f_one import f_one
from app import app
import xml.etree.ElementTree as ET

api = Api(app)
swagger = Swagger(app)


def qual_report_to_xml_et(report) -> str:
    """Convert qualification report to XML. Return xml string"""
    root = ET.Element('MonacoQ1Report')
    for record in report:
        position = ET.SubElement(root, 'position')

        position_number = ET.SubElement(position, 'position_number')
        position_number.text = str(record[0])

        pilot = ET.SubElement(position, 'pilot')
        pilot.text = record[1]

        car = ET.SubElement(position, 'car')
        car.text = record[2]

        time = ET.SubElement(position, 'time')
        time.text = record[3]
    xml_str = ET.tostring(root, encoding="utf-8", method="xml")
    return xml_str


def pilots_report_to_xml_et(report) -> str:
    """Convert pilots report to XML. Return xml string"""
    root = ET.Element('MonacoPilotsQ1Report>')
    for record in report:
        pilot = ET.SubElement(root, 'pilot')

        code = ET.SubElement(pilot, 'code')
        code.text = record[0]

        name = ET.SubElement(pilot, 'name')
        name.text = record[1]

        car = ET.SubElement(pilot, 'car')
        car.text = record[2]

    xml_str = ET.tostring(root, encoding="utf-8", method="xml")
    return xml_str


# def qual_report_to_xml(report):
#     report_for_xml = ['<?xml version="1.0" encoding="UTF-8"?>\n'
#                       '<root>\n',
#                       '<MonacoQ1Report>\n']
#     for record in report:
#         element = f'<position>\n' \
#                   f'<position_number>{record[0]}</position_number>\n' \
#                   f'<pilot>{record[1]}</pilot>\n' \
#                   f'<car>{record[2]}</car>\n' \
#                   f'<time>{record[3]}</time>\n' \
#                   f'</position>\n'
#         report_for_xml.append(element)
#     report_for_xml.append('</MonacoQ1Report>\n</root>')
#     report_for_xml = ''.join(report_for_xml)
#     return report_for_xml


# def pilots_report_to_xml(report):
#     report_for_xml = ['<?xml version="1.0" encoding="UTF-8"?>\n'
#                       '<root>\n',
#                       '<MonacoPilotsQ1Report>\n']
#     for record in report:
#         element = f'<pilot>\n' \
#                   f'<code>{record[0]}</code>\n' \
#                   f'<name>{record[1]}</name>\n' \
#                   f'<car>{record[2]}</car>\n' \
#                   f'</pilot>\n'
#         report_for_xml.append(element)
#     report_for_xml.append('</MonacoPilotsQ1Report>\n</root>')
#     report_for_xml = ''.join(report_for_xml)
#     return report_for_xml


class FOneQReport(Resource):

    laps_dir = 'static/data'
    qualification_report, pilots, unreliable_data = f_one.build_report(laps_dir)
    current_report = []

    def get_json_response(self):
        json_report = jsonify({'Monaco Q1 Results': self.current_report})
        resp = make_response(json_report, 200)
        resp.mimetype = r'application\json'
        return resp

    def get_xml_response(self):
        if self.current_report == self.qualification_report:
            report_xml = qual_report_to_xml_et(self.current_report)
        else:
            report_xml = pilots_report_to_xml_et(self.current_report)
        resp = make_response(report_xml, 200)
        resp.mimetype = r'application\xml'
        return resp

    def get(self, api_version, report_type):
        """This api intended to get report of Monaco 2018 qualification (Q1)
    Call this api passing a version of api and type of report
    (report or pilots). You can also add format parameter
    (?format=json or ?format=xml)
    Example:
        /api/v1/report/?format=xml
        or
        /api/v1/pilots/
    ---

    tags:
      - Api for retrieving data about F1 Monaco qualification 2018 (Q1)
    parameters:
      - name: api_version
        in: path
        type: string
        required: true
        description: Version of api. Current v1
      - name: report_type
        in: path
        type: string
        required: true
        description: type of report (report, pilots)
      - name: format
        in: query
        type: string
        description: format of retrieved data (xml or json)
    produces:
      - application/json
      - application/xml
    responses:
      404:
        description: wrong api or report type or format
      200:
        description: requested data table"""

        if not self.qualification_report:
            self.qualification_report, self.pilots = f_one.build_report(
                self.laps_dir)

        if "v1" != api_version:
            abort(404, description=f"not supported api version: {api_version}")
        if "report" == report_type:
            self.current_report = self.qualification_report
        elif "pilots" == report_type:
            self.current_report = self.pilots
        else:
            abort(404, description=f"not supported report type: {report_type}")
        resp_format = request.args.get("format")
        if "json" == resp_format or resp_format is None:
            return self.get_json_response()
        elif "xml" == resp_format:
            return self.get_xml_response()
        else:
            abort(404, description=f"not supported format: {resp_format}")


api.add_resource(FOneQReport, '/api/<string:api_version>/<string:report_type>/')

if __name__ == '__main__':
    app.run(debug=True)
