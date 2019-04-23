# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class WeekRecordMxDone(models.TransientModel):
    _name = 'week.record.mx.done'
    _description = '本周举措'

    def _check_probability(self):
        probability = self.progress or False
        if probability:
            if probability > 100 or probability < 0:
                return False
        return True

    name = fields.Char('事项', required=True, default=lambda self: self._context.get('name'))
    probability = fields.Float('进度', default=lambda self: self._context.get('probability'))
    note = fields.Text('进展描述')

    _constraints = [
        (_check_probability, '进度必须介于0-100之间', ['计划进度'])
    ]

    def set_to_done(self):
        print(self)
        print(self._context.get('name'))
        print(self._context.get('week_record_id'))
        print(self._context)
        week_mx = self.env['week.record.mx'].browse(self.env.context.get('active_ids'))
        if self.probability <100 and self.probability != self._context.get('probability'):
            week_mx.write({'probability': self.probability})
            print(self.note)
            if self.note:
                week_mx.create({'name': '计划  ' + self._context.get('name') + ' 完成' + str(self.probability)
                                        + '%' + "\n" + u'举措：' + self.note, 'week_record_id': self._context.get('week_record_id'),
                                'original': self._context.get('active_id'), 'type': 2})
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



