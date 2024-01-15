*** Settings ***
Library           SeleniumLibrary
Resource          ../../resources/keywords.robot
Resource          ../../config/variables.robot

*** Test Cases ***
Create User
    # 登录
    Open Browser  ${LOGIN_URL}  ${BROWSER}
    Input Username  ${your_username}
    Input Password  ${your_password}
    Click Login Button

    # 创建用户
    Click Link  Create User
    Input Text  id=new_username_input  NewUser
    Input Text  id=new_password_input  NewPassword
    Click Button  id=create_user_button

    # 验证用户创建成功
    ${user_created}  Page Should Contain  User Created Successfully
    Should Be True  ${user_created}  User creation failed

    # 注销
    Click Link  Logout
    Close Browser
