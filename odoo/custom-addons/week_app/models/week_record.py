from odoo import api, fields, models, tools
import datetime
from odoo.exceptions import Warning

AVAILABLE_PRIORITIES = [
    ('0', 'D'),
    ('1', 'C'),
    ('2', 'B'),
    ('3', 'A'),
]

class week_record_mx(models.Model):
    _name = 'week.record.mx'
    _description = '周报明细'

    name = fields.Char('事项', required=True)
    week_record_id = fields.Many2one('week.record',string='工作周报')
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='优先级', index=True,
                                default=AVAILABLE_PRIORITIES[0][0])
    date_start = fields.Date('开始时间')
    date_end = fields.Date('结束时间')
    #active = fields.Boolean('Active?', default=True)

    #image = fields.Binary('Cover')
    #publisher_id = fields.Many2one('res.partner', string='Publisher')
    #author_ids = fields.Many2many('res.partner', string='Authors')
    person_ids = fields.Many2many('hr.employee',string='责任人')
    #person_id = fields.Many2one('hr.employee', string='责任人1')
    department_id = fields.Many2one('hr.department', string='部门')
    probability = fields.Float('进度', group_operator="avg")
    note = fields.Text('上周进展描述')
    original = fields.Integer(u'原单编号')
    type= fields.Selection([('0', u'计划'),
                            ('1', u'常规工作')
                            ], u'类型',default='0')
    # @api.depends('person_id.department_id')
    # def _compute_department(self):
    #
    #         for week in self:
    #             if week.person_id.id:
    #                 week.department_id = week.person_id.department_id.id

    @api.multi
    def done_history(self):
        if self.original:
            self.env.cr.execute('SELECT id FROM week_record_mx WHERE original = %s', (self.original,))
            vids = [x[0] for x in self.env.cr.fetchall() if x[0]]
            if vids:
                action = {
                    'name': '计划历程',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'week.record.mx',
                    'type': 'ir.actions.act_window',
                    'view_id' : False,
                    'nodestroy': True,
                    'target': 'new',
                    'domain': [('id', 'in', vids)],
                    }
                return action
        else:
            return False
    @api.multi
    def done(self):
        date = datetime.datetime.now().isocalendar()
        print(date)
        return {
        }


    class week_record(models.Model):
        _name = 'week.record'
        _description = '工作周报'

        def _get_user_department(self):
            employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
            if employee_ids:
                return employee_ids[0].department_id or False
            else:
                raise Warning('在人力资源中没有关联用户，请联系管理员设置')
            # res = obj.read(['id', 'department_id'])
            # try:
            #     if res[0]['department_id']:
            #         return res[0]['department_id'][0] or 0
            #     return False
            # except:
            #     raise Warning('在人力资源中没有关联用户，请联系管理员设置')

        name = fields.Char('标题', required=True)
        department_id = fields.Many2one('hr.department', string='部门',default = _get_user_department)
        week_num = fields.Integer('周数',default= datetime.datetime.now().isocalendar()[1])
        week_record_mx_ids = fields.One2many('week.record.mx','week_record_id', string='周报明细')