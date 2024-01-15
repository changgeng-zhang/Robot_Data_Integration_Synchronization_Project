*** Settings ***
Library           SeleniumLibrary
Resource          ../../resources/keywords.robot
Resource          ../../config/variables.robot

*** Test Cases ***
Login Test
    Open Browser  ${LOGIN_URL}  ${BROWSER}
    Maximize Browser Window
    Input Username  ${your_username}
    Input Password  ${your_password}
    Click Login Button
    ${login_successful}    Wait Until Page Contains    ${your_alias}    timeout=10s
    Log    Login successful: ${login_successful}
    Capture Page Screenshot  login_test.png
    Click UserInfo Icon
    Sleep    1s
    Click Logout Button

