def test_property_telegram_link(property_factory):
    expected_url = 'https://t.me/iv?url=https://rent.property.com/&rhash=7849b4bb7a02f2'
    real_property = property_factory(url='https://rent.property.com')
    assert real_property.telegram_link == expected_url
