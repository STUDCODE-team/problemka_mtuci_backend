from domain.models.enums.user_roles import UserRole


def test_admin_is_privileged():
    assert UserRole.ADMIN.is_privileged is True


def test_manager_is_privileged():
    assert UserRole.MANAGER.is_privileged is True


def test_user_is_not_privileged():
    assert UserRole.USER.is_privileged is False


def test_admin_value():
    assert UserRole.ADMIN.value == "admin"


def test_manager_value():
    assert UserRole.MANAGER.value == "manager"


def test_user_value():
    assert UserRole.USER.value == "user"
