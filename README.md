# Web App Report of Formula 1 Qualification Racing Report

> Application that builds and prints results of Formula 1 qualification
results.

## Table of Contents
* [About](#About)
* [Examples](#Examples)
* [Technologies Used](#technologies-)
* [Github Link](#Github-link)
* [Requirements](#Requirements)


## About
Web app for that provides report of Formula 1 qualification results.
Report is build in f_one module. Web interface provides whole report, that can be
sorted ascending or descending, pilots info and report for particular pilot.
API is also available.
## Examples:
API available in json and xml formats. For info go to:
/apidocs

JSON (default) and XML available:
/api/v1/report/?format=xml
/api/v1/report/?format=json
or
/api/v1/pilots/

## Technologies Used
- Python v3.10
- Flask 2.2.2
- Flask-RESTful 0.3.9
- Flasgger 0.9.5

## Requirements
Available in requirements.txt

## Github link
https://github.com/savchenkonick/web-app-f1-racing-report