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
    person_ids = fields.Many2many('hr.employee',string='责任人')
    department_id = fields.Many2one('hr.department', string='部门')
    probability = fields.Float('进度', group_operator="avg")
    note = fields.Text('上周进展描述')
    original = fields.Integer(u'原单编号')
    type= fields.Selection([('0', '计划'),
                            ('1', '常规工作'),
                            ('2', '计划进行')
                            ], u'类型',default='0')
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
        return {
            'name':'本周举措',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'week.record.mx.done',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'week_record_id':self.week_record_id,
                       'name':self.name,
                       'probability':self.probability,}
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


    def _get_name(self):
        if self._get_user_department():
            self.env.cr.execute('SELECT id FROM week_record WHERE department_id = %s and week_num=%s', (self._get_user_department().id,datetime.datetime.now().isocalendar()[1]))
            vids = [x[0] for x in self.env.cr.fetchall() if x[0]]
            if not vids:
            #print(self._get_user_department().id)
            #print(self.department_id)
            #print(self.search(('department_id','=',self._get_user_department().id),('week_num','=',datetime.datetime.now().isocalendar()[1])))
            #if not self.search(('department_id','=',self._get_user_department().id),('week_num','=',datetime.datetime.now().isocalendar()[1])):
                return self._get_user_department().name + '第' + str(datetime.datetime.now().isocalendar()[1]) + '周周报'
            else:
                raise Warning('本周已添加周报，请在周报列表中查询')

    name = fields.Char('标题', default = _get_name)
    department_id = fields.Many2one('hr.department', string='部门',default = _get_user_department)
    week_num = fields.Integer('周数',default= datetime.datetime.now().isocalendar()[1])
    week_record_mx_ids = fields.One2many('week.record.mx','week_record_id', string='周报明细')