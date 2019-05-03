# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import datetime
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


    def set_to_done(self):
        print(self)
        print(self._context.get('name'))
        print(self._context.get('week_record_id'))
        print(self._context)
        week_mx = self.env['week.record.mx'].browse(self.env.context.get('active_ids'))
        week_num = datetime.datetime.now().isocalendar()[2]

        today = datetime.date.today()
        date_start = today - datetime.timedelta(week_num-1)
        date_end = today + datetime.timedelta(7-week_num)
        print(week_num)
        print(date_start)
        print(date_end)
        if self.probability <100:
            week_mx.write({'probability': self.probability, 'new_note': self.note})

            if self.note:
                week_mx.create({'name': '计划  ' + self._context.get('name') + ' 完成' + str(self.probability)
                                        + '%' + "\n" + u'举措：' + self.note, 'week_record_id': self._context.get('week_record_id'),
                                'original': self._context.get('active_id'), 'date_start':date_start, 'date_end':date_end, 'type': '2'})
        # if context is None:
        #     context = {}
        # data = self.read(cr, uid, ids, [], context=context)[0]
        # plan_id = context.get('active_id')
        # if plan_id:
        #     plan_obj = self.pool.get('daily.record.mx')
        #     daily_id = context.get('daily_id')
        #     progress = self.get('progress')
        #     if data.get('progress') < 100:
        #         plan_obj.write(cr, uid, [plan_id], {'progress': progress})
        #         if data.get('notes'):
        #             plan_obj.create(cr, uid, {'name': u'计划  ' + context.get('name') + u' 完成' + str(
        #                 progress) + '%' + "\n" + u'情况说明：' + data.get('notes'),
        #                                       'type': '12', 'daily_id': daily_id[0], 'original': plan_id,
        #                                       'hours': data.get('hours')})
        #         else:
        #             plan_obj.create(cr, uid,
        #                             {'name': u'计划  ' + context.get('name') + u' 完成' + str(progress) + '%', 'type': '12',
        #                              'daily_id': daily_id[0], 'original': plan_id, 'hours': data.get('hours')})
        #     elif data.get('progress') == 100:
        #         plan_obj.write(cr, uid, [plan_id], {'progress': progress, 'type': '9'})
        #         if data.get('notes'):
        #             plan_obj.create(cr, uid, {
        #                 'name': u'计划  ' + context.get('name') + u' 已完成' + "\n" + u'情况说明：' + data.get('notes'),
        #                 'type': '9', 'daily_id': daily_id[0], 'original': plan_id, 'hours': data.get('hours')})
        #         else:
        #             plan_obj.create(cr, uid, {'name': u'计划  ' + context.get('name') + u' 已完成', 'type': '9',
        #                                       'daily_id': daily_id[0], 'original': plan_id, 'hours': data.get('hours')})
        #     return {'type': 'ir.actions.act_window_close'}
        # else:
        #     return False



