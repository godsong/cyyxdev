{
    'name': '城阳有线周报系统',
    'description': '城阳有线周报系统.',
    'author': 'Xiaofei Li',
    'depends': ['base','hr'],
    'application': True,
    'installable': True,

    'data': [
        'security/work_security.xml',
        'security/ir.model.access.csv',
        'views/work_menu.xml',
        'views/work_view.xml',
        'views/work_list_template.xml'
    ],
}