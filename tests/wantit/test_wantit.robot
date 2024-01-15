*** Settings ***
Library    SeleniumLibrary
Resource    ../../config/variables.robot
Resource    test_login.robot
Resource    test_product_profile.robot
Resource    test_carton_order.robot

*** Test Cases ***
Main Test
    # 登录
    Run Keyword  Login Test
    Run Keyword    Set Download Default Directory    ${DOWNLOAD_DEFAULT_DIRECTORY}

    # 产品档案
    ${status}    ${message}=    Run Keyword And Ignore Error  ProductProfile QueryDownload Test
    # 执行异常发送消息
    # Run Keyword If    '${status}'=='FAIL'    Log    ${message}

    # 纸箱订单
    ${status}    ${message}=    Run Keyword And Ignore Error  CartonOrder QueryDownload Test
    # 执行异常发送消息
    # Run Keyword If    '${status}'=='FAIL'    Log    ${message}

    # 纸板订单

*** Keywords ***
Set Download Default Directory
    [Arguments]    ${DOWNLOAD_DEFAULT_DIRECTORY}
    # 创建一个 Chrome 的自定义配置
    ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    # 设置默认下载路径
    Call Method    ${chrome_options}    add_experimental_option    prefs    {"download.default_directory": "${DOWNLOAD_DEFAULT_DIRECTORY}"}
