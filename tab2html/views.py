import os
import flask

from flask import Blueprint, render_template, request, redirect, url_for, abort
from .models import Report, ReportDirectory


TEMPLATE_EXT = '.html'
DIRS_TEMPLATE = 'directories' + TEMPLATE_EXT
REPORTS_TEMPLATE = 'reports' + TEMPLATE_EXT


frontend = Blueprint('frontend', __name__)


# TODO: Move to config and/or util module?
def report_dir_path(*args):
    return os.path.join(flask.current_app.instance_path, 'reports', *args)


@frontend.route('/')
def list_subdirs():
    subdirs = os.walk(report_dir_path()).next()[1]
    return render_template(DIRS_TEMPLATE, subdirs=subdirs)


@frontend.route('/<subdir>', methods=['GET', 'POST'])
def list_reports(subdir):
    error = None
    report_dir = ReportDirectory(report_dir_path(subdir))

    if request.method == 'POST':
        report = report_dir.upload_file(request.files['file'])
        if report:
            return redirect(url_for('show_report', 
                                    subdir=subdir, slug=report.slug))
        else:
            error = "Invalid file"

    reports = report_dir.get_reports()
    return render_template(REPORTS_TEMPLATE, subdir=subdir, reports=reports,
                           error=error)


@frontend.route('/<subdir>/<slug>')
def show_report(subdir, slug):
    report_dir = ReportDirectory(report_dir_path(subdir))
    report = report_dir.get_report(slug)
    return render_template(subdir + TEMPLATE_EXT, subdir=subdir, report=report)
