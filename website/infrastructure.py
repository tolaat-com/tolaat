import os
import socket
import logging

from flask import render_template, request, Response, g, redirect, abort
from . import db
from . import hebrew


def add_infrastructure(app):
    def user_agent_parsing():
        if 'User-Agent' in request.headers:
            ua = request.headers['User-Agent']
            g.is_mobile = 'Mobi' in ua or request.args.get('mobile', 'false') == 'true'
        else:
            g.is_mobile = False

    def is_netanyahu():
        g.netanyahu = os.environ.get('netanyahu', '') == 'true'
        t = 'תיק/67104-01-20'
        if g.netanyahu and t not in request.path and request.path != '/' and 'static' not in request.path:
            return redirect(f'https://xn----8hcborozt8bdd.xn--9dbq2a{request.path}')

    def block_bad_ip_host():
        if request.method == 'POST':
            return
        bypass = request.args.get('bypass', 'false') == 'true'
        remote_ip = request.remote_addr
        ip = None
        if 'X-Forwarded-For' in request.headers:
            ips = request.headers.get('X-Forwarded-For')
            ip = ips.split(',')[0].strip()

        s = set()
        if ip:
            s.add(ip)
        s.add(remote_ip)
        for ip in s:
            out = '?'
            try:
                out = socket.gethostbyaddr(ip)
                g.gethostbyaddr = out
            except socket.herror as e:
                logging.info('could not reverse lookup: %s', ip)
                return
            name = out[0]
            logging.info('socket.gethostbyaddr(%s) is %s', ip, name)
            cloud_providers = ['.amazonaws.com', '.linode.com', '.vulture.com', '.wowrack.com', '.ahrefs.com']
            for c in cloud_providers:
                if name.endswith(c):
                    logging.info('cloud provider %s detected from ip %s', c, ip)
                    if not bypass:
                        abort(410)

    def is_google_bot():
        if 'User-Agent' in request.headers:
            host = '?'
            ua = request.headers['User-Agent']
            if 'Google' in ua:
                if 'X-Forwarded-For' in request.headers:
                    ips = request.headers.get('X-Forwarded-For')
                    ip = ips.split(',')[0].strip()
                    try:
                        if hasattr(g, 'gethostbyaddr'):
                            out = g.gethostbyaddr
                        else:
                            out = socket.gethostbyaddr(ip)
                    except socket.herror as e:
                        logging.info('could not reverse lookup %s %s', ua, ip)
                        abort(410)
                    name = out[0]
                    if name.endswith('.google.com') or name.endswith('googlebot.com'):
                        host = socket.gethostbyname(name)
                        if host == ip:
                            g.is_google_bot = True
                            return
                logging.info('False google bot ua=%s,ip=%s,host=%s', ua, ip, host)
                abort(410)
        g.is_google_bot = False

    def enrich_template_context():
        m = {'h': hebrew,
             'netanyahu': g.netanyahu,
             'is_mobile': g.is_mobile,
             'g_analytics_ua': 'UA-38558199-2',
             'is_google_bot': g.is_google_bot,
             'data_version': app.config['MAJOR'] + '.' + app.config['MINOR']}

        if g.netanyahu:
            m['g_analytics_ua'] = 'UA-38558199-3'

        return m

    app.before_request(user_agent_parsing)
    app.before_request(block_bad_ip_host)
    app.before_request(is_google_bot)
    app.before_request(is_netanyahu)
    app.template_context_processors = {None: [enrich_template_context]}


    db.init_app(app)

    @app.before_first_request
    def before_first_request():
        logging.info('Before first request')

    @app.errorhandler(500)
    def error_handler(err):
        return Response(render_template('error.html'), status=500)

    @app.errorhandler(404)
    def error_handler(err):
        return Response(render_template('404.html'), status=404)


