# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class WeekRecordMxDone(models.TransientModel):
    _name = 'week.record.mx.done'
    _description = '本周举措'

    @api.constrains('probability')
    def _constrain_probability_valid(self):
        probability = self.probability or False
        if probability:
            if probability > 100 or probability < 0:
                raise ValidationError('%s 数据不合法错误 必须介于0-100之间' % probability)
            elif probability < self._context.get('probability'):
                raise ValidationError('新进度%s 应大于或等于原进度%s' % (probability, self._context.get('probability')))

    name = fields.Char('事项', required=True, default=lambda self: self._context.get('name'))
    probability = fields.Float('进度', required=True, default=lambda self: self._context.get('probability'))
    note = fields.Text('进展描述', required=True)
    new_note = fields.Text('本周举措', required=True)

    def set_to_done(self):
        week_mx = self.env['week.record.mx'].browse(self.env.context.get('active_ids'))
        week_mx.write({'probability': self.probability, 'note': self.note, 'new_note': self.new_note})
        if self.probability == 100:
            week_mx.write({'state': '3'})



