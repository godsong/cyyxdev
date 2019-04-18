# -*- coding: utf-8 -*-

import datetime
import time
from odoo import api, fields, models

class daily_record(models.Model):
    _name = 'daily.record'
    _description = u'日志'
    _order = 'daily_date desc'
    _inherit = ['mail.thread'] #继承消息模块，用于发消息
    _track = {
        'state': {
            'daily_record.mt_daily_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'daily_record.mt_daily_confirm': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm',
            }, #自动发送系统消息，用于记录日志
    }
    
    #获取当前用户所属的员工
    def _employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False
    
    def _get_user_department(self, cr, uid, context={}): 
        obj = self.pool.get('hr.employee') 
        ids = obj.search(cr, uid, [('user_id','=',uid)]) 
        res = obj.read(cr, uid, ids, ['id','department_id'], context)
        try:
            if res[0]['department_id']: 
                return res[0]['department_id'][0] or 0
            return False
        except:
            raise osv.except_osv((u'警告!'),(u'您在人力资源中没有关联相关用户，请联系管理员设置'))
    
    def _check_time(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        obj_task = self.browse(cr, uid, ids[0], context=context)
        start = obj_task.create_date or False
        end = obj_task.daily_date or False
        if start and end :
            if start < end:
                return False
        return True
    
    def _bw_all(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        bw = self.pool.get('daily.record.mx')
        employee = self.browse(cr, uid, ids[0], context=context).employee_id.id
        user = self.browse(cr, uid, ids[0], context=context).create_uid.id
        cr.execute('SELECT id FROM daily_record WHERE employee_id = %s' %(employee))
        vids = [x[0] for x in cr.fetchall() if x[0]]
        b_id = bw.search(cr, uid, [('bw_id','in',vids),('type','=','8')])
        w_id = bw.search(cr, uid, [('type','=','11'),('create_uid','=',user),('daily_id','=',False)])
        for id in ids:
            res[id] = b_id + w_id
        return res

   
    _columns = {
        'name': fields.char(u'标题', size=64, track_visibility='onchange'),
        'employee_id' : fields.many2one('hr.employee', u'职员', required = True, select = True, invisible = False, readonly = True),
        'department_id' : fields.many2one('hr.department', u'部门', readonly = True,store = True),#部门         
        'description': fields.text(u'工作总结',required=True, track_visibility='onchange'),
        'create_uid':  fields.many2one('res.users', u'创建人', readonly=True, track_visibility='onchange'),
        'create_date': fields.datetime(u'创建时间', select=True, readonly=True),
        'daily_date': fields.date(u'日志时间', select=True, track_visibility='onchange'),
        'isadd' : fields.boolean(u'补日志'),
        'company_id': fields.many2one('res.company', 'Company'),
        'work_ids': fields.one2many('daily.record.mx', 'daily_id', u'工作摘要'),
        'bwork_ids': fields.one2many('daily.record.mx', 'bw_id', u'备忘事项'),
        'state' : fields.selection([('draft', u'草稿'),('confirm', u'锁定')], u'状态', readonly = True, track_visibility='onchange'),
        'bw_all': fields.function(_bw_all, string=u"全部备忘记录", type='one2many', relation='daily.record.mx', method=True, store=False),
    }
    
    _defaults = {    
        'state' :"draft",
        'employee_id': _employee_get,
        'department_id': lambda self,cr,uid,context: self._get_user_department(cr,uid,context),
        'daily_date': lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self, cr, uid, ctx=None: self.pool.get('res.company')._company_default_get(cr, uid, 'daily.record', context=ctx),
        'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'daily.record'),
    }
    
    _constraints = [
        (_check_time, '输入检查! 日志时间不能大于当前日期，请输入有效的日志日期', ['日志时间'])
    ]
    
    _sql_constraints = [
        ('daily_date_uniq', 'unique(daily_date, employee_id)', u'您选择的日志日期中已存在记录，不能重复添加!'),
    ]
  
    def list_creator(self, cr, uid, context=None):
        m_list = []
        mod = self.pool.get('res.users')
        for i in mod.search(cr, uid, [], context=context):
            m_list.append([i,mod.browse(cr, uid, i, context=context).name])
        return m_list

    def add_all_option(self, cr, uid, ids, context=None):
        #Reactive all unactive values
        
        return True
    
    def onchange_des(self, cr, uid, ids, isadd, daily_date, employee_id, context=None):
        result = {'value': {}}
        employee_obj = self.pool.get('hr.employee')
        employee_list = employee_obj.browse(cr, uid, [employee_id], context=context)
        employee_rec = employee_list[0]
        employee_name = employee_rec.name
        if isadd:
            result['value'] = {'name' :  u'(补)' + employee_name + ' '+ str(daily_date) +' '+ u'的工作日志'}
        else:
            result['value'] = {'daily_date' : datetime.datetime.strptime(fields.date.today(),'%Y-%m-%d').__format__('%Y-%m-%d'),'name' :  employee_name + ' '+ str(daily_date) +' '+ u'的工作日志'}
        return result
    
    def create(self, cr, uid, vals, context=None):
        vals['state'] = 'confirm'
        if len(vals.get('description')) == 0:
            raise osv.except_osv((u'警告!'),(u'工作总结没有填写，请填写工作总结'))
        elif len(vals.get('description')) < 10:
            raise osv.except_osv((u'太好了!'),(u'您完成了今天的工作，但是工作总结会让你做的更好，请认真填写工作总结'))
        employee_obj = self.pool.get('hr.employee')
        if context == None:
            context = {}
        add = vals.get('isadd')
        employee = employee_obj.search(cr, uid, [('user_id', '=', uid)], context=context)
        real_date = datetime.datetime.strptime(fields.date.today(),'%Y-%m-%d').__format__('%Y-%m-%d')
        create_day = datetime.datetime.strptime(vals.get('daily_date'), '%Y-%m-%d').__format__('%Y-%m-%d')
        if add == True:
            if real_date and create_day :
                if real_date == create_day:
                    raise osv.except_osv((u'警告!'),(u'如果您添加的是今天的日志，请取消选择 补日志 '))
        context = dict(context, mail_create_nolog=True)
        daily_id = super(daily_record, self).create(cr, uid, vals, context=context)
        rec = employee_obj.browse(cr, uid, employee[0], context=context)
        if rec.id and rec.parent_id and rec.parent_id.user_id:
            self.message_subscribe_users(cr, uid, [daily_id], user_ids=[rec.parent_id.user_id.id], context=context)
        self.add_all_option(cr, uid, [daily_id], context=None)
        return daily_id
    
    def unlink(self, cr, uid, ids, context=None):
        real_date = datetime.datetime.strptime(fields.date.today(),'%Y-%m-%d').__format__('%Y-%m-%d')
        
        for rec in self.browse(cr, uid, ids, context=context):
            create_day = datetime.datetime.strptime(rec.create_date, '%Y-%m-%d %H:%M:%S').__format__('%Y-%m-%d')
            if rec.create_uid.id != uid or create_day != real_date:
                raise osv.except_osv(_(u'警告!'),_(u'您不能删除别人的日志或者您不能删除隔日的日志！'))
        return super(daily_record, self).unlink(cr, uid, ids, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        real_date = datetime.datetime.strptime(fields.date.today(),'%Y-%m-%d').__format__('%Y-%m-%d')
        for rec in self.browse(cr, uid, ids, context=context):
            create_day = datetime.datetime.strptime(rec.create_date, '%Y-%m-%d %H:%M:%S').__format__('%Y-%m-%d')
            if rec.create_uid.id != uid or create_day != real_date:
                raise osv.except_osv(_(u'警告!'),_(u'您不能修改别人的日志或者您不能修改隔日的日志！'))
        return super(daily_record, self).write(cr, uid, ids, vals, context=context)


class daily_record_mx(models.Model):
    _name = 'daily.record.mx'
    _description = u'工作摘要'
    _order = 'create_date desc'
    
    _columns = {
        'name': fields.char(u'工作摘要', size=128, required=True),
        'date': fields.datetime(u'开始时间', select="1"),
        #'daily_date': fields.date(u'日志时间', select=True),
        'daily_id': fields.many2one('daily.record', u'日志', ondelete='cascade', select="1"),
        'bw_id': fields.many2one('daily.record', u'日志', ondelete='restrict', select="1"),
        'hours': fields.float(u'工时'),
        'user_id': fields.many2one('res.users', u'完成人', select="1"),
        'create_uid': fields.many2one('res.users', u'创建人', select="1"),
        'isin' : fields.boolean(u'是否为导入'),
        'create_date': fields.datetime(u'创建时间', select=True, readonly=True),
        'start_date': fields.date(u'计划开始时间', select=True),
        'end_date': fields.date(u'预计结束时间', select=True),
        'source':fields.char("source"),
        'target':fields.char("target"),
        'links_type':fields.char("links_type"),
        'progress':fields.integer(u"进度"),
        'priority':fields.selection([
                ("1",u"高"),
                ("2",u"中"),
                ("3",u"低"),
                ],u"权重"),
        'phone_num' : fields.integer(u'次数'),
        'phone_time' : fields.char(u'累计时间'),
        'partner_num' : fields.integer(u'客户数'),
        'billsec': fields.float(u'通话时长'),
        'original':fields.integer(u'原单编号'),
        'type' : fields.selection([('0', u'自行添加'),
                                   ('1', u'任务'),
                                   ('2', u'通话日志'),
                                   ('3', u'服务日志'),
                                   ('4', u'任务检查'),
                                   ('5', u'创建任务'),
                                   ('6', u'创建商机'),
                                   ('7', u'跟进记录'),
                                   ('8', u'计划'),
                                   ('9', u'计划完成'),
                                   ('10', u'自动汇总'),
                                   ('11', u'常规工作'),
                                   ('12', u'执行任务'),
                                   ],u'类型'),
        'hz_type' : fields.selection([('outphone', u'拨出电话'),('inphone', u'拨入电话'),('housephone', u'内部电话'),
                                   ('service_open', u'服务开单'),('service_visit', u'服务回访'),('no_phone', u'未处理电话'),
                                   ],u'汇总类型')
    }

    _defaults = {
        'isin': False,
        'progress': 0,
        'priority': '3',
        'user_id': lambda obj, cr, uid, context: uid,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'start_date':time.strftime('%Y-%m-%d'),
        'end_date': (datetime.date.today() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    }
    
    _sql_constraints = [('name_uniq','unique (name)','工作计划或工作摘要不能为空，请填写内容 !')]
    
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
    def onchange_type(self, cr, uid, ids, name, context=None):
        result = {'value': {}}
        employee_id = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)[0]
        cr.execute('SELECT id FROM daily_record WHERE employee_id = %s' %(employee_id))
        vids = [x[0] for x in cr.fetchall() if x[0]]
        if vids:
            bw_id = max(vids)
        else:
            today = fields.date.today()
            user_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).name
            name = u'（自动）' + user_id + ' ' + today + ' ' + u'创建的日志'
            bw_id = self.pool.get('daily.record').create(cr, uid, vals={'name': name,'daily_date':today,'description':u'本日志由系统初始化自动创建，请点击编辑进行修改','state' :"draft"}, context=context)
        result['value'] = {'bw_id' : bw_id, 'type' : '8'}
        return result
    
    def onchange_work_type(self, cr, uid, ids, name, context=None):
        result = {'value': {}}
        result['value'] = {'type' : '11'}
        return result
    
    def create(self, cr, uid, vals, context=None):
        daily = self.pool.get('daily.record')
        today = fields.date.today()
        bw_id = vals.get('bw_id')
        daily_date = daily.browse(cr, uid, bw_id, context=context).daily_date
        if type == '8':
            if daily_date != today:
                raise osv.except_osv(_(u'警告!'),_(u'请在 %s 的日志中添加该计划，不支持计划在今天之前添加！' %(today)))
        #vals['daily_date'] = daily_date
        return super(daily_record_mx, self).create(cr, uid, vals, context=context)
      
    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.create_uid.id != uid:
                raise osv.except_osv(_(u'警告!'),_(u'您不能删除别人的摘要！'))
        return super(daily_record_mx, self).unlink(cr, uid, ids, context)
    
    def write(self, cr, uid, ids, vals, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.create_uid.id != uid:
                raise osv.except_osv(_(u'警告!'),_(u'您不能修改别人的摘要！'))
        return super(daily_record_mx, self).write(cr, uid, ids, vals, context=context)
    
    def done_history(self, cr, uid, ids, context=None):
        original = self.browse(cr, uid, ids[0], context=context).original
        cr.execute('SELECT id FROM daily_record_mx WHERE original = %s' %(original))
        vids = [x[0] for x in cr.fetchall() if x[0]]
        if vids:
            action = {
                'name': '服务单明细',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'daily.record.mx',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': [('id', 'in', vids)],
                }
            return action
        else:
            return False
    
    def done(self, cr, uid, ids, context=None):
        
        daily = self.pool.get('daily.record')
        today = fields.date.today()
        rec = self.browse(cr, uid, ids[0], context = context)
        daily_id = daily.search(cr, uid, [('create_uid', '=', rec.create_uid.id),('daily_date','=',today)], context=context)
        #今天的日志ID
        if daily_id:
            if rec.type == '8':
                return {
                        'view_type': 'form',
                        "view_mode": 'form',
                        'res_model': 'daily.plan.done',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context':{'daily_id':daily_id,
                                   'name':rec.name,
                                   'progress':rec.progress}
                 }
            if rec.type == '11':
                self.write(cr, uid, ids, {'start_date':False,'end_date':False,'progress':False,'priority':False}, context)
                return self.create(cr, uid, {'name':rec.name,'type':'11','daily_id':daily_id[0],'start_date':False,'end_date':False})
        else:
            raise osv.except_osv(_(u'警告!'),_(u'计划只能在今天的日志中完成，请创建今天的日志！'))
