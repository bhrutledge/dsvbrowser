import os

from flask import Blueprint, render_template, request, redirect, url_for, abort
from .models import Report, ReportDirectory
from .constants import *
from .utils import *


frontend = Blueprint('frontend', __name__)


@frontend.route('/')
def show_index():
    subdirs = os.walk(report_dir_path()).next()[1]
    return render_template(DIRS_TEMPLATE, subdirs=subdirs)


@frontend.route('/<subdir>', methods=['GET', 'POST'])
def show_subdir(subdir):
    error = None
    report_dir = ReportDirectory(report_dir_path(subdir))

    # TODO: Break up into functions
    if request.method == 'POST':
        action = request.args.get('action', '')

        if action == 'upload':
            upload = request.files['file']
            if valid_upload(upload):
                try:
                    report = report_dir.upload_file(upload)
                except EnvironmentError as e:
                    raise_errno(e)

                return redirect(
                    url_for('.show_report', subdir=subdir, slug=report.slug))
            else:
                error = "Invalid file"
        elif action == 'delete':
            for slug in request.form.getlist('slug'):
                try:
                    report_dir.delete_report(slug)
                except EnvironmentError as e:
                    pass
            return redirect(url_for('.show_subdir', subdir=subdir))

    try:
        reports = report_dir.get_reports()
    except EnvironmentError as e:
        raise_errno(e)

    return render_template(REPORTS_TEMPLATE, subdir=subdir, reports=reports,
                           error=error)


@frontend.route('/<subdir>/<slug>', methods=['GET', 'POST'])
def show_report(subdir, slug):
    report_dir = ReportDirectory(report_dir_path(subdir))

    # TODO: Break up into functions
    if request.method == 'POST':
        action = request.args.get('action', '')

        if action == 'delete':
            try:
                report_dir.delete_report(slug)
            except EnvironmentError as e:
                raise_errno(e)

            return redirect(url_for('.show_subdir', subdir=subdir))

    try:
        report = report_dir.get_report(slug)
    except EnvironmentError as e:
        raise_errno(e)
    
    return render_template(subdir + TEMPLATE_EXT, subdir=subdir, report=report)
