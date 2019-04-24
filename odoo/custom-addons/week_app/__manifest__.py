{
    'name': '城阳有线周报系统',
    'description': '城阳有线周报系统.',
    'author': 'Xiaofei Li',
    'depends': ['base','hr'],
    'application': True,
    'installable': True,

    'data': [
        'security/week_security.xml',
        'security/ir.model.access.csv',
        'views/week_record_view.xml',
        'views/week_list_template.xml',
        'wizard/week_record_mx_done_view.xml',
        'views/week_menu.xml',
    ],
}