import os
import zipfile
from selenium import webdriver
import time
from pathlib import Path
import pickle

from devices import DEVICES

script_path = os.path.dirname(os.path.realpath(__file__))


def checkpluggin(USER):
    plugginfile = os.path.join(script_path, USER + '_proxy_auth_plugin.zip')
    path = Path(plugginfile)
    if path.is_file():
        pluggin = True
    else:
        pluggin = False
    return pluggin


print("1) GALAXY S5 \n"
      "2) LG L90 \n"
      "3) GALAXY A50 \n"
      "4) Redmi Note 7 \n"
      "5) Moto E5 \n"
      "6) REDMI NOTE 9 PRO \n"
      "7) S3 NEO \n")
device_id = input('SELECT DEVICE:')
print('Selected {}'.format(DEVICES[device_id]['device_name']))


username = input('Username: ')
password = input('Password: ')
user_agent = DEVICES[device_id]['user_agent']
pixel_ratio = float(int(DEVICES[device_id]['pixel_ratio']) / 150)
width = int(int(DEVICES[device_id]['width']) / pixel_ratio)
height = int(int(DEVICES[device_id]['height']) / pixel_ratio)
print('Starting browser with: {}x{}x{}'.format(width, height, pixel_ratio))
pluggin = checkpluggin(username)

if not pluggin:
    proxy_data = input('INSERT PROXY(ip:port:login:pass): ').split(':')
    PROXY_HOST = proxy_data[0]
    PROXY_PORT = proxy_data[1]
    PROXY_USER = proxy_data[2]
    PROXY_PASS = proxy_data[3]
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Chrome Proxy",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
            singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
            },
            bypassList: ["localhost"]
            }
        };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
    pluginfile = username + '_proxy_auth_plugin.zip'
    with zipfile.ZipFile(pluginfile, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

opts = webdriver.ChromeOptions()
mobile_emulation = {

    "deviceMetrics": {"width": width, "height": height, "pixelRatio": pixel_ratio},

    "userAgent": user_agent}

opts.add_experimental_option("mobileEmulation", mobile_emulation)
opts.add_experimental_option('prefs', {'intl.accept_languages': 'ru,ru_RU'})
opts.add_argument("--lang=ru-RU")

pluginfile = username + '_proxy_auth_plugin.zip'
opts.add_extension(pluginfile)
driver = webdriver.Chrome(script_path + r"\chromedriver.exe", options=opts,
                          desired_capabilities=webdriver.DesiredCapabilities.ANDROID)
time.sleep(.5)
main_url = "https://www.instagram.com"
retries = 2
driver.get(main_url)
time.sleep(5)
try:
    cookies = pickle.load(open(username + ".pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    time.sleep(1)
    try:
        login_button = driver.find_element_by_xpath("//button[contains(text(),'Log In')]").click()
        time.sleep(3)
        username_input = driver.find_element_by_xpath("//input[@name='username']")
        username_input.send_keys(username)
        password_input = driver.find_element_by_xpath("//input[@name='password']")
        password_input.send_keys(password)
        login_button2 = driver.find_element_by_xpath("//div[contains(text(),'Log In')]/parent::button").click()
        time.sleep(2)
        print("LOGGEADO")
    except:
        print("cookie worked")

except:
    try:
        login_button = driver.find_element_by_xpath("//button[contains(text(),'Log In')]").click()
        time.sleep(3)
        username_input = driver.find_element_by_xpath("//input[@name='username']")
        username_input.send_keys(username)
        password_input = driver.find_element_by_xpath("//input[@name='password']")
        password_input.send_keys(password)
        login_button2 = driver.find_element_by_xpath("//div[contains(text(),'Log In')]/parent::button").click()
        time.sleep(2)
        print("LOGGEADO")
    except:
        print("Error in login automation")

try:
    while True:
        time.sleep(30)
        pickle.dump(driver.get_cookies(), open(username + ".pkl", "wb"))

except KeyboardInterrupt:
    print('interrupted!')
driver.close()
