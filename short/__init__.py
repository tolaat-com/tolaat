import os

from flask import Flask, redirect, abort
from urllib.parse import quote


def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_pyfile('config.py', silent=True)


    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    domain = 'xn----8hcborozt8bdd.xn--9dbq2a'
    prefix = f'https://{domain}'
    case = 'תיק'
    transport_case = 'תיק-תעבורה'
    decision = 'החלטה'
    preview = 'תצוגה-ישירה'
    ugc = 'תוכן-גולשים'
    document = 'מסמך'
    verdict = 'פסק-דין'
    scrape = 'טופס-גירוד'
    developers = 'מפתחים'
    fax_url = 'פקס-חינם-לבית-המשפט'

    @app.route('/<int:number>-<int:month>-<int:year>')
    def redirectcatch_case(number, month, year):
        month = str(month).zfill(2)
        year = str(year).zfill(2)
        return redirect(f"{prefix}/{quote(case)}/{number}-{month}-{year}", code=301)

    @app.route('/t-<int:number>-<int:month>-<int:year>')
    def redirectcatch_transport_case(number, month, year):
        month = str(month).zfill(2)
        year = str(year).zfill(2)
        return redirect(f"{prefix}/{quote(transport_case)}/{number}-{month}-{year}", code=301)

    @app.route('/d-<int:number>-<int:month>-<int:year>')
    def redirectcatch_preview_case(number, month, year):
        month = str(month).zfill(2)
        year = str(year).zfill(2)
        return redirect(f"{prefix}/{quote(preview)}-{quote(case)}/{number}-{month}-{year}", code=301)

    @app.route('/bb')
    def netanyahu():
        return redirect('https://xn----8hcdjg1aqa6a1cp.xn--9dbq2a/', code=301)

    @app.route('/dt-<int:number>-<int:month>-<int:year>')
    def redirectcatch_preview_transport_case(number, month, year):
        month = str(month).zfill(2)
        year = str(year).zfill(2)
        return redirect(f"{prefix}/{quote(preview)}-{quote(transport_case)}/{number}-{month}-{year}", code=301)

    @app.route('/<int:number>-<int:month>-<int:year>-<int:decisionnumber>')
    def redirectcatch_decision(number, month, year, decisionnumber):
        month = str(month).zfill(2)
        year = str(year).zfill(2)
        return redirect(f"{prefix}/{quote(case)}/{number}-{month}-{year}/{quote(decision)}/{decisionnumber}",
                            code=301)

    @app.route('/t-<int:number>-<int:month>-<int:year>-<int:decisionnumber>')
    def redirectcatch_transport_decision(number, month, year, decisionnumber):
        month = str(month).zfill(2)
        year = str(year).zfill(2)
        return redirect(f"{prefix}/{quote(transport_case)}/{number}-{month}-{year}/{quote(decision)}/{decisionnumber}",
                            code=301)

    def get_hebrew_decision_type(decision_type):
        m = {'v': verdict, 'd': decision}
        if decision_type not in m:
            abort(404)
        return m[decision_type]

    @app.route('/t-<int:number>-<int:month>-<int:year>-<string:dectype>-<int:decisionnumber>')
    def redirectcatch_transport_decision_v2(number, month, year, dectype, decisionnumber):
        hebrew_dec_type = get_hebrew_decision_type(dectype)
        month = str(month).zfill(2)
        year = str(year).zfill(2)
        print('3')
        return redirect(f"{prefix}/{quote(transport_case)}/{number}-{month}-{year}/{quote(document)}/{quote(hebrew_dec_type)}/{decisionnumber}",
                        code=301)


    @app.route('/<int:number>-<int:month>-<int:year>-<string:dectype>-<int:decisionnumber>')
    def redirectcatch_case_decision_v2(number, month, year, dectype, decisionnumber):
        hebrew_dec_type = get_hebrew_decision_type(dectype)
        month = str(month).zfill(2)
        year = str(year).zfill(2)

        return redirect(f"{prefix}/{quote(case)}/{number}-{month}-{year}/{quote(document)}/{quote(hebrew_dec_type)}/{decisionnumber}",
                        code=301)

    @app.route('/')
    def main():
        return redirect(prefix, code=301)

    @app.route('/stay')
    def stay():
        return 'ok'

    @app.route('/u-<int:number>')
    def redirect_ugc(number):
        return redirect(f'{prefix}/{quote(ugc)}/{number}', code=301)

    @app.route('/u-<int:number>-<string:key>')
    def redirect_ugc_with_key(number, key):
        return redirect(f'{prefix}/{quote(ugc)}/{number}?k={key}', code=301)

    @app.route('/scrape')
    def redirect_scrape_form():
        return redirect(f'{prefix}/{quote(scrape)}', code=301)

    @app.route('/api')
    def api():
        q =quote(developers)
        return redirect(f'{prefix}/{q}', code=301)

    @app.route('/fax')
    def fax():
        q = quote(fax_url)
        return redirect(f'{prefix}/{q}', code=301)

    return app


