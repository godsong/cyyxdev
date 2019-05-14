{
    'name': '城阳有线各站数据统计',
    'description': '城阳有线各站数据统计.',
    'author': 'Xiaofei Li',
    'depends': ['base','hr'],
    'application': True,
    'installable': True,

    'data': [
        'security/week_statistical_security.xml',
        'security/ir.model.access.csv',
        'views/week_statistical_view.xml',
        'views/week_statistical_menu.xml',
        'reports/level_report.xml'
    ],
}