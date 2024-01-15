*** Settings ***
Library           SeleniumLibrary
Resource          ../../resources/keywords.robot
Resource          ../../config/variables.robot

*** Test Cases ***
Set Permissions
    # 登录
    Open Browser  ${LOGIN_URL}  ${BROWSER}
    Input Username  ${your_username}
    Input Password  ${your_password}
    Click Login Button

    # 设置用户权限
    Click Link  Manage Permissions
    Input Text  id=username_input  NewUser
    Select From List by Index  id=permission_dropdown  2  # 假设 2 是某种权限的索引
    Click Button  id=set_permissions_button

    # 验证权限设置成功
    ${permissions_set}  Page Should Contain  Permissions Set Successfully
    Should Be True  ${permissions_set}  Permissions setting failed

    # 注销
    Click Link  Logout
    Close Browser
