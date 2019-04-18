# -*- coding: utf-8 -*-


{
    'name': '日志管理',
    'version': '1.1',
    'author': 'odoo SA',
    'website': 'http://www.kaisoft.com.cn',
    'category': 'Project Management',#分类
    'sequence': 8,
    'summary': '日志, 管理',#介绍
    'images': [
        'images/gantt.png',
    ],
    'depends': [
        'base_setup',
        'analytic',
        'board',
        'mail',
        'hr',
    ],
    'description': """
Track multi-level projects, tasks, work done on tasks
=====================================================

This application allows an operational project management system to organize your activities into tasks and plan the work you need to get the tasks completed.

Gantt diagrams will give you a graphical representation of your project plans, as well as resources availability and workload.

Dashboard / Reports for Project Management will include:
--------------------------------------------------------
* My Tasks
* Open Tasks
* Tasks Analysis
* Cumulative Flow
    """,
    'data': [
        'dailyrecord_data.xml',
        'security/daily_record_security.xml',
        'security/ir.model.access.csv',
        'dailyrecord_view.xml',
        'wizard/plan_done_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'js': [
        'static/src/js/daily_move_line_quickadd.js',
    ],
    'css':[
        'static/src/css/daily_move_line_quickadd.css'
    ]
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
