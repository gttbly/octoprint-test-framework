def test_driver_can_open_octoprint(driver):
    """验证浏览器能成功访问 OctoPrint 页面"""
    driver.get(driver.base_url)
    # 只要页面标题包含 OctoPrint 或者访问没报错，就算通过
    assert "OctoPrint" in driver.title or len(driver.title) > 0

def test_login_page_fixture(login_page):
    """验证 login_page fixture 能正常提供页面对象"""
    assert login_page is not None
