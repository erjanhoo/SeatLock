from django.db import migrations


def seed_access_data(apps, schema_editor):
    Action = apps.get_model('user', 'Action')
    Resource = apps.get_model('user', 'Resource')
    Role = apps.get_model('user', 'Role')
    RolePermission = apps.get_model('user', 'RolePermission')
    User = apps.get_model('user', 'MyUser')
    UserRole = apps.get_model('user', 'UserRole')

    actions = [
        ('read', 'Read'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]
    resources = [
        ('profile', 'User Profile'),
        ('admin_panel', 'Admin Panel'),
    ]
    roles = [
        ('user', 'User'),
        ('admin', 'Administrator'),
    ]

    action_map = {}
    for code, name in actions:
        action_map[code], _ = Action.objects.get_or_create(code=code, defaults={'name': name})

    resource_map = {}
    for code, name in resources:
        resource_map[code], _ = Resource.objects.get_or_create(code=code, defaults={'name': name})

    role_map = {}
    for code, name in roles:
        role_map[code], _ = Role.objects.get_or_create(code=code, defaults={'name': name})

    def allow(role_code, resource_code, action_code):
        RolePermission.objects.get_or_create(
            role=role_map[role_code],
            resource=resource_map[resource_code],
            action=action_map[action_code],
            defaults={'allow': True},
        )

    # User role permissions
    for action_code in ('read', 'update', 'delete'):
        allow('user', 'profile', action_code)
    

    

    # Admin role permissions
    for action_code in action_map.keys():
        allow('admin', 'profile', action_code)
    allow('admin', 'admin_panel', 'read')

    # Demo users
    if not User.objects.filter(email='admin@example.local').exists():
        admin = User.objects.create_user(
            username='Admin',
            email='admin@example.local',
            password='Admin12345',
            last_name='Admin',
            first_name='Account',
            patronymic='',
        )
        UserRole.objects.get_or_create(user=admin, role=role_map['admin'])

    if not User.objects.filter(email='user@example.local').exists():
        user = User.objects.create_user(
            username='User',
            email='user@example.local',
            password='User12345',
            last_name='Ivanov',
            first_name='Ivan',
            patronymic='Ivanovich',
        )
        UserRole.objects.get_or_create(user=user, role=role_map['user'])


def unseed_access_data(apps, schema_editor):
    Action = apps.get_model('user', 'Action')
    Resource = apps.get_model('user', 'Resource')
    Role = apps.get_model('user', 'Role')
    RolePermission = apps.get_model('user', 'RolePermission')
    UserRole = apps.get_model('user', 'UserRole')

    UserRole.objects.all().delete()
    RolePermission.objects.all().delete()
    Role.objects.all().delete()
    Resource.objects.all().delete()
    Action.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_access_control'),
    ]

    operations = [
        migrations.RunPython(seed_access_data, unseed_access_data),
    ]
