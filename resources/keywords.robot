*** Keywords ***
# 测试
Input InInIn Username
    [Arguments]    ${username}
    Input Text    xpath=//*[@id="app"]/div/div[1]/div[2]/form/div[1]/div/div/input    ${username}

Input InInIn Password
    [Arguments]    ${password}
    Input Text    xpath=//*[@id="app"]/div/div[1]/div[2]/form/div[2]/div/div/input    ${password}

Click InInIn Login Button
    Click Button     xpath=//*[@id="app"]/div/div[1]/div[2]/div[3]/button

Click InInIn UserInfo Icon
    Click Element     xpath=//*[@id="app"]/div[1]/header/div/div/div[1]

Click InInIn Logout Button
    Click Element     xpath=//div[contains(text(), '退出登录')]

# 项目
Set Download Default Directory
    [Arguments]    ${DOWNLOAD_DEFAULT_DIRECTORY}
    # 创建一个 Chrome 的自定义配置
    ${chrome_options}=    Evaluate    sys.modules['selenium.webdriver'].ChromeOptions()    sys, selenium.webdriver
    # 设置默认下载路径
    Call Method    ${chrome_options}    add_experimental_option    prefs    {"download.default_directory": "${DOWNLOAD_DEFAULT_DIRECTORY}"}

Get Today Start and End Time
    [Arguments]    ${Format}
    ${end_time}=    Get Current Date    result_format=${Format}
    ${start_time}=    Run Keyword If    '${Format}' == '${TWO_DIGIT_YEAR_FORMAT}'    Set Variable    ${end_time[:8]} 00:00:00
    ...    ELSE    Set Variable    ${end_time[:10]} 00:00:00

    Log    Start Time: ${start_time}
    Log    End Time: ${end_time}

    [Return]    ${start_time}    ${end_time}

Get Start and End Time With Interval
    [Arguments]    ${Days}    ${Format}
    ${current_time}=  Get Time    epoch  # 获取当前时间的 epoch 格式
    
    ${interval}=    Convert To Integer    ${Days}
    ${interval_days_ago}=  Evaluate  ${current_time} - ${interval}*24*60*60  # 计算N天前的时间（秒）

    ${start_time}=  Convert Date    ${interval_days_ago}    result_format=${Format}
    ${end_time}=  Convert Date    ${current_time}    result_format=${Format}
    
    Log    Start Time: ${start_time}
    Log    End Time: ${end_time}
    
    [Return]    ${start_time}    ${end_time}