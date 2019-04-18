from odoo import api, fields, models
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
    department_id = fields.Many2one('hr.employee', string='部门', compute='_compute_department')
    probability = fields.Float('Probability', group_operator="avg")

    # @api.depends('person_id.department_id')
    # def _compute_department(self):
    #
    #         for work in self:
    #             if work.person_id.id:
    #                 work.department_id = work.person_id.department_id.id

    # @api.multi
    # def _check_isbn(self):
    #     self.ensure_one()
    #     isbn = self.isbn.replace('-', '')  # 为保持兼容性 Alan 自行添加
    #     digits = [int(x) for x in isbn if x.isdigit()]
    #     if len(digits) == 13:
    #         ponderations = [1, 3] * 6
    #         terms = [a * b for a, b in zip(digits[:12], ponderations)]
    #         remain = sum(terms) % 10
    #         check = 10 - remain if remain != 0 else 0
    #         return digits[-1] == check
    #
    # @api.multi
    # def button_check_isbn(self):
    #     for work in self:
    #         if not work.isbn:
    #             raise Warning('Please provide an ISBN for %s' % work.name)
    #         if work.isbn and not work._check_isbn():
    #             raise Warning('%s is an invalid ISBN' % work.isbn)
    #         return True