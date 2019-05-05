from odoo import api, fields, models
import datetime
from odoo.exceptions import Warning

class week_statistical_mx(models.Model):
    _name = 'week.statistical.mx'
    _description = '及时率汇总表'

    name = fields.Char('工单编号', required=True)
    two_level = fields.Char('二级网格')
    week_statistical_id = fields.Many2one('week.statistical', string='及时率明细')
    date_start = fields.Datetime('派单时间')
    date_end = fields.Datetime('回单时间')
    person_id = fields.Many2one('hr.employee', string='回单人')
    department_id = fields.Many2one(comodel_name='hr.department', string='部门', compute='_get_department')
    type = fields.Selection([('0', '安装回单'),
                            ('1', '安装响应'),
                            ('2', '维修回单'),
                            ('3', '维修响应'),
                            ], '单据类型', required=True)
    duration = fields.Float('时长', group_operator="sum")
    in_time = fields.Boolean('是否及时')


    def _get_department(self):

        for id in self.ids:
            print(id)
            level = self.search(id)
            print(level.two_level)
            level_id = self.env['level.department'].search([('two_level', '=', self.id.two_level)])
            print(level_id)
            if level_id:
                return level_id.department_id.id
            else:
                return False

class week_statistical(models.Model):
    _name = 'week.statistical'
    _description = '及时率明细表'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _get_name(self):
        self.env.cr.execute('SELECT id FROM week_statistical WHERE week_num=%s', (datetime.datetime.now().isocalendar()[1],))
        vids = [x[0] for x in self.env.cr.fetchall() if x[0]]
        if not vids:
            return '第' + str(datetime.datetime.now().isocalendar()[1]) + '周运维人员装维及时率汇总表'
        else:
            raise Warning('本周已添加周报，请在周报列表中查询')

    name = fields.Char('标题', default=_get_name, track_visibility='always')
    week_num = fields.Integer('周数', default=datetime.datetime.now().isocalendar()[1])
    week_statistical_mx_ids = fields.One2many('week.statistical.mx', 'week_statistical_id', string='周报明细', track_visibility='always')

class LevelToDepartment(models.Model):
    _name = 'level.department'
    _description = '部门对照'

    two_level = fields.Char('二级网格')
    department_id = fields.Many2one('hr.department', string='部门')
    _sql_constraints = [('department_uniq', 'unique (two_level,department_id)', '二级网格只能对应一个部门!')]