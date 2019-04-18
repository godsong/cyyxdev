from odoo import http

class work(http.Controller):

    @http.route('/cyyx/work', auth='user')
    def list(self, **kwargs):
        work = http.request.env['cyyx.work']
        works = work.search([])
        return http.request.render(
            'work_app.work_list_template', {'works':works})