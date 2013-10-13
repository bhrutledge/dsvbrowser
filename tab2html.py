import csv
import glob
import os
import sys

from flask import Flask, render_template, request, redirect, url_for, abort
from werkzeug import secure_filename

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
REPORT_DIR = os.path.join(SCRIPT_DIR, 'reports')
REPORT_EXT = '.txt'

app = Flask(__name__)


def get_report_name(rpt_fname):
    return os.path.splitext(os.path.basename(rpt_fname))[0]


def get_report_path(rpt_dir, rpt_fname):
    return os.path.join(REPORT_DIR, rpt_dir, secure_filename(rpt_fname))
    

def list_report_dir(rpt_dir):
    rpt_path = os.path.join(REPORT_DIR, rpt_dir, '*' + REPORT_EXT)
    return [ get_report_name(f) for f in glob.glob(rpt_path)]


def nonblank_lines(line_iter):
    for line in (l.strip() for l in line_iter):
        if line:
            yield line


def parse_input(in_path):    
    with open(in_path, 'U') as in_file:
        line_iter = nonblank_lines(in_file)        
        title = line_iter.next()

        row_iter = csv.reader(line_iter, delimiter='\t')
        head_row = row_iter.next()
        body_rows = list(row_iter)
        
    return (title, head_row, body_rows)


@app.route('/')
def list_directories():
    try:
        rpt_dirs = [ d for d in os.listdir(REPORT_DIR) 
                    if os.path.isdir(os.path.join(REPORT_DIR, d)) ]
    except OSError:
        abort(404)

    return render_template('directories.html', rpt_dirs=rpt_dirs)


@app.route('/<rpt_dir>', methods=['GET', 'POST'])
def list_reports(rpt_dir):
    if not os.path.isdir(os.path.join(REPORT_DIR, rpt_dir)):
        abort(404)

    if request.method == 'POST':
        rpt_file = request.files['file']
        # TODO: Error on invalid files
        if rpt_file and rpt_file.filename.endswith(REPORT_EXT):
            rpt_path = get_report_path(rpt_dir, rpt_file.filename)
            rpt_file.save(rpt_path)

            return redirect(url_for('show_report', rpt_dir=rpt_dir, 
                                    rpt_name=get_report_name(rpt_path)))

    return render_template('reports.html',
                           rpt_dir=rpt_dir,
                           rpt_names=list_report_dir(rpt_dir))


@app.route('/<rpt_dir>/<rpt_name>')
def show_report(rpt_dir, rpt_name):
    rpt_path = get_report_path(rpt_dir, rpt_name + REPORT_EXT)

    try:
        title, head, body = parse_input(rpt_path)
    except IOError:
        abort(404)
        
    return render_template(rpt_dir + '.html', 
                           rpt_dir=rpt_dir, rpt_name=rpt_name,
                           title=title, head=head, body=body)


if __name__ == '__main__':
    app.run(debug=True)
