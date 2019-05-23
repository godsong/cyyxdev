from odoo import api, fields, models
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

    def _get_user_department(self):
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if employee_ids:
            return employee_ids[0].department_id or False
        else:
            raise Warning('在人力资源中没有关联用户，请联系管理员设置')

    name = fields.Char('事项', required=True)
    week_record_id = fields.Many2one('week.record', string='工作周报')
    week_num = fields.Integer('周数', default=datetime.datetime.now().isocalendar()[1])
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='优先级', index=True,
                                default=AVAILABLE_PRIORITIES[0][0])
    date_start = fields.Date('开始时间')
    date_end = fields.Date('结束时间')
    date_start = fields.Date('开始时间')
    date_end = fields.Date('结束时间')
    person_ids = fields.Many2many('hr.employee', string='责任人')
    department_id = fields.Many2one('hr.department', string='部门', default=_get_user_department)
    probability = fields.Float('进度', group_operator="avg")
    note = fields.Char('上周进展描述')
    new_note = fields.Char('本周举措')
    original = fields.Integer(u'原单编号')
    original_ids = fields.One2many('week.record.mx', 'original', string='举措明细')
    type = fields.Selection([('0', '新单据'),
                             ('1', '流转单据')
                             ], '类型', default='0')
    state = fields.Selection([('0', '新计划'),
                              ('1', '历史数据'),
                              ('2', '完成'),
                              ], '状态', default='0')

    @api.multi
    def unlink(self):
        if self.original > 0:
            raise Warning('导入的数据不允许删除')

    def done_history(self):
        self.env.cr.execute('SELECT id FROM week_record_mx WHERE original = %s', (self.original,))
        vids = [x[0] for x in self.env.cr.fetchall() if x[0]]
        if vids:
            action = {
                'name': '计划历程',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'week.record.mx',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'views': [(self.env.ref('week_app.view_tree_week_record_history').id, 'tree'),
                          (self.env.ref('week_app.view_form_week_record_mx').id, 'form')],
                'nodestroy': True,
                'target': 'new',
                'domain': [('id', 'in', vids)],
            }
            return action
        else:
            raise Warning('没有历史记录')

    @api.multi
    def done(self):
        if self.department_id.id == self._get_user_department().id:
            return {
                'name': '本周举措',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'week.record.mx.done',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': {'week_record_id': self.week_record_id.id,
                            'name': self.name,
                            'probability': self.probability}
            }
        else:
            raise Warning('不能修改其他部门的进度')

    def remove(self):
        print(self)
        if self.department_id.id == self._get_user_department().id and self.state == '0':
            super(week_record_mx, self).unlink()
        else:
            raise Warning('不能删除其他部门或者导入的数据')


class week_record(models.Model):
    _name = 'week.record'
    _description = '工作周报'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_user_department(self):
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        if employee_ids:
            return employee_ids[0].department_id or False
        else:
            raise Warning('在人力资源中没有关联用户，请联系管理员设置')

    def _get_name(self):
        if self._get_user_department():
            self.env.cr.execute('SELECT id FROM week_record WHERE department_id = %s and week_num=%s',
                                (self._get_user_department().id, datetime.datetime.now().isocalendar()[1]))
            vids = [x[0] for x in self.env.cr.fetchall() if x[0]]
            if not vids:
                return self._get_user_department().name + '第' + str(datetime.datetime.now().isocalendar()[1]) + '周周报'
            else:
                raise Warning('本周已添加周报，请在周报列表中查询')

    name = fields.Char('标题', default=_get_name, track_visibility='always')
    department_id = fields.Many2one('hr.department', string='部门', default=_get_user_department)
    week_num = fields.Integer('周数', default=datetime.datetime.now().isocalendar()[1])
    week_record_mx_ids = fields.One2many('week.record.mx', 'week_record_id', string='周报明细', track_visibility='always')

    # week_mx_ok_ids = fields.One2many(comodel_name='week.record.mx', string='周报列表', compute='_week_mx_ok_ids')

    # def _week_mx_ok_ids(self):
    #     if self.department_id:
    #         self.week_mx_ok_ids = self.week_record_mx_ids.search(
    #             [('type', 'not in', ('2', '3')), ('department_id', '=', self.department_id.id)])

    @api.multi
    def write(self):
        if self.department_id.id != self._get_user_department().id:
            raise Warning('不能删除其他部门的单据')

    def get_week_mx(self):
        new_mx = self.week_record_mx_ids.search(
            [('state', 'not in', ('1', '2')), ('department_id', '=', self.department_id.id), ('probability', '!=', 100),
             ('week_num', '!=', datetime.datetime.now().isocalendar()[1])])
        week = datetime.datetime.now().isocalendar()[2]
        today = datetime.date.today()
        date_start = today - datetime.timedelta(week - 1)
        date_end = today + datetime.timedelta(7 - week)
        if new_mx:
            for mx in new_mx:
                mx.write({'state': '1', 'original': mx.week_record_id})
                mx.copy({'week_record_id': self.ids[0], 'date_start': date_start, 'date_end': date_end, 'note': '',
                         'new_note': '', 'state': '0', 'type': '1',
                         'week_num': datetime.datetime.now().isocalendar()[1]})
        else:
            raise Warning('没有可导入的数据')

    def new_week_mx(self):
        return {
            'name': '新增计划',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'week.record.mx',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'context': {'default_week_record_id': self.id, 'default_type': '0'},
            'nodestroy': True,
            'target': 'new',
        }
