*** Keywords ***
Input Username
    [Arguments]    ${username}
    Input Text    xpath=//*[@id="netWorkId-inputEl"]    ${username}

Input Password
    [Arguments]    ${password}
    Input Text    xpath=//*[@id="passWord-inputEl"]    ${password}

Click Login Button
    Click Element     xpath=//*[@id="sure-btnWrap"]

