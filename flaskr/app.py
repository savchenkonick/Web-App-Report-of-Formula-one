r"""Web App for Report of Formula one Qualification Racing
Web app for that provides report of Formula 1 qualification results.
Report is build in f_one module. Web interface provides whole report, that can be
sorted ascending or descending, pilots info and report for particular pilot.

Functions:
    pilots_info():
    Return a list with information about pilots to template

    report():
    Call build_report function of f_one module and return render_template obj
    with content dict. Content has qualification report

"""

from flask import Flask, render_template, request
import sys
from f_one import f_one

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template('base.html')


@app.route('/report/pilots', methods=['GET'])
def pilots_info():
    """Return a list with information about pilots to template"""
    laps_dir = 'static/data'
    qualification_report, pilots, unreliable_data = f_one.build_report(laps_dir)
    args = request.args
    order = args.get('order')
    pilot_id = args.get('pilot_id')
    if pilot_id:
        pilot_name = next(p[1] for p in pilots if p[0] == pilot_id)
        try:
            pilot_result = next(r for r in qualification_report
                                if r[1] == pilot_name)
        except StopIteration:
            pilot_result = next(r for r in unreliable_data
                                if r[1] == pilot_name)
        content = {'results': [pilot_result],
                   'reversed': False
                   }
        return render_template('report.html', content=content)
    pilots.sort()
    if order == 'desc':
        pilots.reverse()
    return render_template('pilots.html', content=pilots)


@app.route('/report')
def report():
    """Call build_report function of f_one module and return render_template obj
     with content dict. Content has qualification report"""
    laps_dir = 'static/data'
    qualification_report, pilots, unreliable_data = f_one.build_report(laps_dir)
    results_reversed = False
    args = request.args
    order = args.get('order')
    if order == 'desc':  # and not results_reversed:
        qualification_report.reverse()
        results_reversed = True
    content = {'results': qualification_report,
               'reversed': results_reversed}

    return render_template('report.html', content=content)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run(debug=True)
