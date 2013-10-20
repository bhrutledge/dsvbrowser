from app import app
from flask import render_template, request, redirect, url_for, abort
from models import Report


TEMPLATE_EXT = '.html'
DIRS_TEMPLATE = 'directories' + TEMPLATE_EXT
REPORTS_TEMPLATE = 'reports' + TEMPLATE_EXT


@app.route('/')
def list_directories():
    subdirs = Report.get_subdirs()
    return render_template(DIRS_TEMPLATE, subdirs=subdirs)


@app.route('/<subdir>', methods=['GET', 'POST'])
def list_reports(subdir):
    if not Report.is_subdir(subdir):
        abort(404)

    if request.method == 'POST':
        # TODO: Show error messages
        report = Report.from_upload(subdir, request.files['file'])
        if report:
            return redirect(url_for('show_report', 
                                    subdir=subdir, slug=report.slug))

    reports = Report.from_subdir(subdir)
    return render_template(REPORTS_TEMPLATE, subdir=subdir, reports=reports)


@app.route('/<subdir>/<slug>')
def show_report(subdir, slug):
    report = Report.from_slug(subdir, slug)
    if not report:
        abort(404)
 
    return render_template(subdir + TEMPLATE_EXT, subdir=subdir, report=report)
