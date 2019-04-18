# -*- coding: utf-8 -*-

from odoo.osv import fields, osv


class daily_plan_done(osv.osv_memory):
    _name = 'daily.plan.done'
    
    _columns = {
        'name':fields.char(u'工作摘要', size=128),
        'progress':fields.integer(u"进度",help="输入一个0-100之间的数字，当为100时表示任务完成"),
        'hours': fields.float(u'工时'),
        'notes': fields.text(u'情况说明')
    }
    
    _defaults = {
        'name': lambda obj, cr, uid, context: context.get('name'),
        'progress': lambda obj, cr, uid, context: context.get('progress')
        }
    def _check_progress(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        obj_daily = self.browse(cr, uid, ids[0], context=context)
        progress = obj_daily.progress or False
        if progress :
            if progress > 100 or progress< 0 :
                return False
        return True

    _constraints = [
        (_check_progress, '进度必须介于0-100之间', ['计划进度'])
    ]
    
    def set_to_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, [], context=context)[0]
        plan_id = context.get('active_id')
        if plan_id:
            plan_obj = self.pool.get('daily.record.mx')
            daily_id = context.get('daily_id')
            progress = data.get('progress')
            if data.get('progress') < 100:
                plan_obj.write(cr, uid, [plan_id], {'progress': progress})
                if data.get('notes'):
                    plan_obj.create(cr, uid, {'name':u'计划  ' + context.get('name') + u' 完成' + str(progress) + '%' + "\n" + u'情况说明：' + data.get('notes'),
                                              'type':'12','daily_id':daily_id[0],'original':plan_id,'hours':data.get('hours')})
                else:
                    plan_obj.create(cr, uid, {'name':u'计划  ' + context.get('name') + u' 完成' + str(progress) + '%','type':'12','daily_id':daily_id[0],'original':plan_id,'hours':data.get('hours')})
            elif data.get('progress') == 100:
                plan_obj.write(cr, uid, [plan_id], {'progress': progress,'type':'9'})
                if data.get('notes'):
                    plan_obj.create(cr, uid, {'name':u'计划  ' + context.get('name') + u' 已完成' + "\n" + u'情况说明：' + data.get('notes'),'type':'9','daily_id':daily_id[0],'original':plan_id,'hours':data.get('hours')})
                else:
                    plan_obj.create(cr, uid, {'name':u'计划  ' + context.get('name') + u' 已完成','type':'9','daily_id':daily_id[0],'original':plan_id,'hours':data.get('hours')})
            return {'type': 'ir.actions.act_window_close'}
        else:
            return False
        
daily_plan_done()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
