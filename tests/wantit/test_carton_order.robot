*** Settings ***
Resource    ../../config/settings.robot
Resource    ../../config/variables.robot
Resource    ../../resources/keywords.robot
Resource    ../../config/wantit/carton_order_variables.robot
Resource    ../../resources/wantit/carton_order_keywords.robot
Resource    test_login.robot

Library    ../../scripts/features/co/synchronize_carton_order.py

*** Test Cases ***
Main Test
    # 登录
    Run Keyword  Login Test
    Run Keyword    Set Download Default Directory    ${DOWNLOAD_DEFAULT_DIRECTORY}

    ${export_file}    Set Variable    ${DOWNLOAD_DEFAULT_DIRECTORY}${CARTON_ORDER_FILE_NAME}
    # 导出前先删除本地文件
    Remove File    ${export_file}
    
    # 从ERP导出纸箱订单
    ${status}    ${message}=    Run Keyword And Ignore Error  CartonOrder QueryDownload Test
    # 执行异常发送消息
    Run Keyword If    '${status}'=='FAIL'    Log    ${message}
    ...    ELSE    Execute Sync    ${export_file}

*** Keywords ***
CartonOrder QueryDownload Test
    [Documentation]    This test case demonstrates querying and downloading carton order list
    Set Browser Implicit Wait    10 seconds

    # Perform product list query
    Input Carton Order Quick Menu    ${QUICK_MENU}
    Click Menu

    # 使用 Select Frame 切换到 iframe
    Select Frame    ${IFRAME_LOCATOR}
    # Unselect Frame

    Click Extend Display

    # 滚动到页面最下方
    Execute JavaScript    window.scrollTo(0, document.body.scrollHeight);

    # 产品类型：纸箱、彩盒
    Select Product Category

    Wait Until Element Is Visible    ${WINDOW_LOCATOR}

    Select Cardboard Box
    Select Colored Box

    Wait Until Element Is Visible    ${Confirm_Product_Category}
    Click Confirm Product Category

    # 订单状态：已排程、在生产
    Select Order Status

    Wait Until Element Is Visible    ${WINDOW_LOCATOR}

    Select Scheduled
    Select In Production

    Wait Until Element Is Visible    ${Confirm_Order Status}
    Click Confirm Order Status

    Input Query Details    ${QUERY_DETAILS}
    # Click Details
    Click Search Button

    # Wait for the product list to load
    ${wait_results}=    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    10x    1s    Check Table Data And Execute Download Task
    Run Keyword If    '${wait_results[0]}' == 'FAIL'    Handle Failure

    ${status}    ${message}=    Run Keyword And Ignore Error    Execute Download Task
    Run Keyword If    '${status}'=='FAIL'    Log    ${message}

    # 切回主界面
    Unselect Frame


Check Table Data And Execute Download Task
    @{elements}=    Get WebElements    xpath=//div[contains(@class, 'x-toolbar-text') and contains(@class, 'x-box-item') and contains(@class, 'x-toolbar-item') and contains(@class, 'x-toolbar-text-default')]
    # 遍历元素列表并执行操作：拼接
    ${concatenated_text}    Set Variable    ${EMPTY}    # Initialize variable as an empty string
    FOR    ${element}    IN    @{elements}
        ${text}    Get Text    ${element}    # Get text of the current element
        ${concatenated_text}    Set Variable    ${concatenated_text} ${text}    # Concatenate text to the variable
    END
    Log    Element Text: ${concatenated_text}    # Log the text of the current element
    Should Match Regexp    ${concatenated_text}    显示 \\d+ - \\d+条，共 \\d+ 条


Execute Download Task
    ${element_count}    Get Element Count    xpath=//tr[contains(@class, 'x-grid-row') and contains(@class, 'x-grid-data-row')]
    Log    ${element_count}
    # Download the product list
    Press Keys    css:body    CTRL+ALT+g
    # 等待菜单打开的一些操作
    Sleep    2s
    Click Export All Data

    Wait Until Keyword Succeeds    15x    1s    File Should Exist    ${DOWNLOAD_DEFAULT_DIRECTORY}${CARTON_ORDER_FILE_NAME}
    # Wait for the download to complete
    #Wait Until File Exists    ${DOWNLOAD_FOLDER}/${PRODUCT_LIST_FILE_NAME}
    Log    OK


Execute Sync
    [Arguments]    ${export_file_path}
    synchronize_carton_order    ${export_file_path}


Handle Failure
    Log    查询纸箱订单数据无