from filter import is_user_thumbs_up


def test_is_user_thumbs_up_positive():
    assert is_user_thumbs_up("👍") is True


def test_is_user_thumbs_up_negative():
    assert is_user_thumbs_up("❤️") is False
    assert is_user_thumbs_up("") is False
    assert is_user_thumbs_up(None) is False
