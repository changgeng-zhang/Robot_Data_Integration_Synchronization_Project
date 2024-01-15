*** Settings ***
Library           SeleniumLibrary
Resource          ../../config/variables.robot
Resource          ../../resources/wantit/login_keywords.robot
Resource          ../../config/wantit/login_variables.robot

# *** Test Cases ***
# 注意：单个测试完毕后，整合到Main流程需要把Test Cases 改为 Keywords
*** Keywords ***
Login Test
    Open Browser  ${LOCAL_TEST}  ${BROWSER}
    Maximize Browser Window
    Input Username  ${USER_NAME}
    Input Password  ${PASSWORD}
    Click Login Button
    ${LOGIN_SUCCESSFUL}    Wait Until Page Contains    账号:${USER_NAME_ALIAS}    timeout=10s
    Log    Login successful: ${LOGIN_SUCCESSFUL}
    Capture Page Screenshot  login_test.png