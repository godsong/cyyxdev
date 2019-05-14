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
    department_id = fields.Many2one(comodel_name='hr.department', string='部门', compute='_get_department', store=True)
    type = fields.Selection([('0', '安装回单'),
                            ('1', '安装响应'),
                            ('2', '维修回单'),
                            ('3', '维修响应'),
                            ], '单据类型', required=True)
    duration = fields.Float('时长', group_operator="sum")
    in_time = fields.Boolean('是否及时')

    @api.multi
    def _get_department(self):
        for level in self:
            level_id = self.env['level.department'].search([('two_level', '=', level.two_level)])
            print(level_id)
            if level_id:
                level.department_id = level_id.department_id

class week_statistical(models.Model):
    _name = 'week.statistical'
    _description = '及时率明细表'

    def _get_name(self):
        self.env.cr.execute('SELECT id FROM week_statistical WHERE week_num=%s', (datetime.datetime.now().isocalendar()[1],))
        vids = [x[0] for x in self.env.cr.fetchall() if x[0]]
        if not vids:
            return '第' + str(datetime.datetime.now().isocalendar()[1]) + '周运维人员装维及时率汇总表'
        else:
            raise Warning('本周已添加周报，请在周报列表中查询')

    name = fields.Char('标题', default=_get_name)
    week_num = fields.Integer('周数', default=datetime.datetime.now().isocalendar()[1])
    week_statistical_mx_ids = fields.One2many('week.statistical.mx', 'week_statistical_id', string='周报明细')
    level_reports = fields.One2many('level.report', 'week_statistical_id', string='报告明细')

    def level_report(self):
        person = []
        azxy = {}
        azhd = {}
        wxxy = {}
        wxhd = {}
        report = self.env['level.report'].search([('week_statistical_id','in',self.ids)])
        sataistical_mx = self.env['week.statistical.mx'].search([('week_statistical_id','=',self.ids[0])])
        azxy_time = 0
        azhd_time = 0
        wxxy_time = 0
        wxhd_time = 0
        if not report:
            if self.week_statistical_mx_ids:
                for mx_id in self.week_statistical_mx_ids:
                    person = person + [mx_id.person_id.id]
                new_person = []  # 创建一个新的数组来存储无重复元素的数组
                for element in person:
                    if (element not in new_person):
                        new_person.append(element)
                for per in new_person:
                    azxy_sum = len(sataistical_mx.search([('person_id','=',per),('type','=',1)]))
                    azxy_js = len(sataistical_mx.search([('person_id', '=', per), ('type', '=', 1),('in_time','=',True)]))
                    azhd_sum = len(sataistical_mx.search([('person_id', '=', per), ('type', '=', 0)]))
                    azhd_js = len(sataistical_mx.search([('person_id', '=', per), ('type', '=', 0),('in_time','=',True)]))
                    wxxy_sum = len(sataistical_mx.search([('person_id', '=', per), ('type', '=', 3)]))
                    wxxy_js = len(sataistical_mx.search([('person_id', '=', per), ('type', '=', 3),('in_time','=',True)]))
                    wxhd_sum = len(sataistical_mx.search([('person_id', '=', per), ('type', '=', 2)]))
                    wxhd_js = len(sataistical_mx.search([('person_id', '=', per), ('type', '=', 2),('in_time','=',True)]))
                    if azxy_sum > 0:
                        azxy_time = azxy_js/azxy_sum*100
                    else:
                        azxy_time = 100
                    if azhd_sum > 0:
                        azhd_time = azhd_js/azhd_sum*100
                    else:
                        azhd_time = 100
                    if wxxy_sum > 0:
                        wxxy_time = wxxy_js/wxxy_sum*100
                    else:
                        wxxy_time = 100
                    if wxhd_sum > 0:
                        wxhd_time = wxhd_js/wxhd_sum*100
                    else:
                        wxhd_time = 100
                    two_level = sataistical_mx.search([('person_id','=',per)])[0].two_level
                    if self.env['level.department'].search([('two_level','=',two_level)]):
                        department_id = self.env['level.department'].search([('two_level','=',two_level)])[0].department_id.id
                    else:
                        department_id = False

                    if self.env['hr.employee'].search([('id','=',per),('job_title','=','队长')]):
                        is_pm = False
                    else:
                        is_pm = True
                    report.create({'week_statistical_id': self.ids[0],'person_id':per,'azxy_sum':azxy_sum,
                                   'azxy_js':azxy_js, 'azhd_sum':azhd_sum, 'azhd_js':azhd_js, 'wxxy_sum':wxxy_sum,
                                   'wxxy_js':wxxy_js, 'wxhd_sum':wxhd_sum, 'wxhd_js':wxhd_js, 'azxy_time':azxy_time,
                                   'azhd_time':azhd_time, 'wxhd_time':wxhd_time, 'wxxy_time':wxxy_time,
                                   'two_level':two_level, 'department_id':department_id, 'is_pm':is_pm})
                self.env.cr.execute(
                    'select id, Rank() over (order by azxy_time desc) from level_report where is_pm = TRUE and week_statistical_id = %s',
                    (self.ids))
                vids = [x for x in self.env.cr.fetchall() if x[0]]
                if vids:
                    for azxy in vids:
                        self.env['level.report'].search([('id', '=', azxy[0])]).write({'azxy_pm': azxy[1]})
                self.env.cr.execute(
                    'select id, Rank() over (order by azhd_time desc) from level_report where is_pm = TRUE and week_statistical_id = %s',
                    (self.ids))
                vids = [x for x in self.env.cr.fetchall() if x[0]]
                if vids:
                    for azhd in vids:
                        self.env['level.report'].search([('id', '=', azhd[0])]).write({'azhd_pm': azhd[1]})
                self.env.cr.execute(
                    'select id, Rank() over (order by wxxy_time desc) from level_report where is_pm = TRUE and week_statistical_id = %s',
                    (self.ids))
                vids = [x for x in self.env.cr.fetchall() if x[0]]
                if vids:
                    for wxxy in vids:
                        self.env['level.report'].search([('id', '=', wxxy[0])]).write({'wxxy_pm': wxxy[1]})
                self.env.cr.execute(
                    'select id, Rank() over (order by wxhd_time desc) from level_report where is_pm = TRUE and week_statistical_id = %s',
                    (self.ids))
                vids = [x for x in self.env.cr.fetchall() if x[0]]
                if vids:
                    for wxhd in vids:
                        self.env['level.report'].search([('id', '=', wxhd[0])]).write({'wxhd_pm': wxhd[1]})
                # for px in self.env['level.report'].search([('week_statistical_id','in',self.ids),('is_pm','=',True)]):
                #     azxy[px.id] = px.azxy_time
                #     azhd[px.id] = px.azhd_time
                #     wxxy[px.id] = px.wxxy_time
                #     wxhd[px.id] = px.wxhd_time
                # azxy=sorted(azxy.items(), key=lambda x: x[1], reverse=True)
                # azhd=sorted(azhd.items(), key=lambda x: x[1], reverse=True)
                # wxxy = sorted(wxxy.items(), key=lambda x: x[1], reverse=True)
                # wxhd = sorted(wxhd.items(), key=lambda x: x[1], reverse=True)
                # a = 0; b = -1; i = 1;
                # for azxy_pm in azxy:
                #     if azxy_pm[1] < b:
                #         i = i + a
                #         a = 1
                #     else:
                #         a = a + 1
                #         b = azxy_pm[1]
                #     self.env['level.report'].search([('id', '=', azxy_pm[0])]).write({'azxy_pm': i})
                # a = 0
                # b = 0
                # i = 1
                # for azhd_pm in azhd:
                #     if azhd_pm[1] < b:
                #         i = i + a
                #         a = 1
                #     else:
                #         a = a + 1
                #         b = azhd_pm[1]
                #     self.env['level.report'].search([('id', '=', azhd_pm[0])]).write({'azhd_pm': i})
                # a = 0
                # b = 0
                # i = 1
                # for wxxy_pm in wxxy:
                #     if wxxy_pm[1] < b:
                #         i = i + a
                #         a = 1
                #     else:
                #         a = a + 1
                #         b = wxxy_pm[1]
                #     self.env['level.report'].search([('id', '=', wxxy_pm[0])]).write({'wxxy_pm': i})
                # a = 0
                # b = 0
                # i = 1
                # for wxhd_pm in wxhd:
                #     if wxhd_pm[1] < b:
                #         i = i + a
                #         a = 1
                #     else:
                #         a = a + 1
                #         b = wxhd_pm[1]
                #     self.env['level.report'].search([('id', '=', wxhd_pm[0])]).write({'wxhd_pm': i})
                for zh_per in self.env['level.report'].search([('week_statistical_id', 'in', self.ids), ('is_pm', '=', True)]):
                    zh_sum = zh_per.azxy_pm + zh_per.azhd_pm + zh_per.wxxy_pm + zh_per.wxhd_pm
                    zh_per.write({'zh_sum':zh_sum})
                self.env.cr.execute('select id, Rank() over (order by zh_sum asc) from level_report where is_pm = TRUE and week_statistical_id = %s',(self.ids))
                vids = [x for x in self.env.cr.fetchall() if x[0]]
                if vids:
                    for zh in vids:
                            self.env['level.report'].search([('id', '=', zh[0])]).write({'zh_pm': zh[1]})
        else:
            report.unlink()
            self.level_report()

class LevelToDepartment(models.Model):
    _name = 'level.department'
    _description = '部门对照'

    two_level = fields.Char('二级网格')
    department_id = fields.Many2one('hr.department', string='部门')
    _sql_constraints = [('department_uniq', 'unique (two_level,department_id)', '二级网格只能对应一个部门!')]

class LevelToReport(models.Model):
    _name = 'level.report'
    _description = '及时率报表'

    week_statistical_id = fields.Many2one('week.statistical', string='周及时率')
    person_id = fields.Many2one('hr.employee', string='回单人')
    two_level = fields.Char('二级网格')
    department_id = fields.Many2one('hr.department', string='部门')
    azxy_sum = fields.Integer('安装响应总数')
    azxy_js = fields.Integer('安装响应及时数')
    azxy_time = fields.Float('安装响应及时率', digits=(16, 2), group_operator="avg")
    azxy_pm = fields.Integer('安装响应排名', group_operator="avg")
    wxxy_sum = fields.Integer('维修响应总数')
    wxxy_js = fields.Integer('维修响应及时数')
    wxxy_time = fields.Float('维修响应及时率', digits=(16, 2), group_operator="avg")
    wxxy_pm = fields.Integer('维修响应排名', group_operator="avg")
    azhd_sum = fields.Integer('安装回单总数')
    azhd_js = fields.Integer('安装回单及时数')
    azhd_time = fields.Float('安装回单及时率', digits=(16, 2), group_operator="avg")
    azhd_pm = fields.Integer('安装回单排名', group_operator="avg")
    wxhd_sum = fields.Integer('维修回单总数')
    wxhd_js = fields.Integer('维修回单及时数')
    wxhd_time = fields.Float('维修回单及时率', digits=(16, 2), group_operator="avg")
    wxhd_pm = fields.Integer('维修回单排名', group_operator="avg")
    zh_sum = fields.Integer('名次合计')
    zh_pm = fields.Integer('综合排名', group_operator="avg")
    is_pm = fields.Boolean('是否排名',default=True)