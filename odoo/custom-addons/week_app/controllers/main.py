from odoo import http

class week(http.Controller):

    @http.route('/cyyx/week', auth='user')
    def list(self, **kwargs):
        week = http.request.env['week.record']
        weeks = week.search([])
        return http.request.render(
            'week_app.week_list_template', {'weeks':weeks})