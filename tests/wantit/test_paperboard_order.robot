*** Settings ***
Resource    ../../config/settings.robot
Resource    ../../config/variables.robot
Resource    ../../resources/keywords.robot
Resource    ../../config/wantit/paperboard_order_variables.robot
Resource    ../../resources/wantit/paperboard_order_keywords.robot
Resource    test_login.robot

Library    ../../scripts/features/po/synchronize_paperboard_order.py

*** Test Cases ***
Main Test
    # 登录
    Run Keyword    Login Test
    Run Keyword    Set Download Default Directory    ${DOWNLOAD_DEFAULT_DIRECTORY}

    ${export_file}    Set Variable    ${DOWNLOAD_DEFAULT_DIRECTORY}${PAPERBOARD_ORDER_FILE_NAME}
    # 导出前先删除本地文件
    Remove File    ${export_file}
    
    # 从ERP导出纸板订单
    ${status}    ${message}=    Run Keyword And Ignore Error  PaperboardOrder QueryDownload Test
    # 执行异常发送消息
    Run Keyword If    '${status}'=='FAIL'    Log    ${message}
    ...    ELSE    Execute Sync    ${export_file}

*** Keywords ***
PaperboardOrder QueryDownload Test
    [Documentation]    This test case demonstrates querying and downloading paperboard order list
    Set Browser Implicit Wait    10 seconds

    # Input parameters
    # ${TO}=    Get Current Date    result_format=${TWO_DIGIT_YEAR_FORMAT}
    # ${FROM}=    Set Variable    ${TO[:8]} 00:00:00
    ${FROM}    ${TO}=    Get Today Start and End Time    ${TWO_DIGIT_YEAR_FORMAT}
    # ${FROM}    ${TO}=    Get Start and End Time With Interval    30    ${TWO_DIGIT_YEAR_FORMAT}
    
    Log    Start Time: ${FROM}
    Log    End Time: ${TO}

    # Perform product list query
    Input Quick Menu    ${QUICK_MENU}
    Click Menu

    # 使用 Select Frame 切换到 iframe
    Select Frame    ${IFRAME_LOCATOR}

    # 清空开始时间
    Clear Start Time From
    Clear Start Time To

    # 工序类型
    Input Process Category
    # Select Corrugation Machine

    # 产品类型
    Select Product Category
    Wait Until Element Is Visible    ${WINDOW_LOCATOR}
    Select Cardboard Box
    Select Colored Box
    Wait Until Element Is Visible    ${Confirm_Product_Category}
    Click Confirm Product Category
    
    # 输入录入时间
    Input Entry Time From    ${FROM}
    Input Entry Time To    ${TO}

    # 查询
    Click Search Button

    # Wait for the product list to load
    ${wait_results}=    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    5x    1s    Check Table Data And Execute Download Task
    Run Keyword If    '${wait_results[0]}' == 'FAIL'    Handle Failure
    ...    ELSE    Download Paperboard Order

    # 关闭浏览器
    Close Browser


Check Table Data And Execute Download Task
    @{elements}=    Get WebElements    xpath=//div[@class="x-grid-cell-inner"]
    # 遍历元素列表并执行操作：拼接
    ${concatenated_text}    Set Variable    ${EMPTY}    # Initialize variable as an empty string
    FOR    ${index}    IN RANGE    0    5
        ${element}=    Set Variable    ${elements}[${index}]
        # Click Element    ${element}
        ${text}    Get Text    ${element}    # Get text of the current element
        ${concatenated_text}    Set Variable    ${concatenated_text} ${text}    # Concatenate text to the variable
    END
    Log    Element Text: ${concatenated_text}    # Log the text of the current element
    Should Match Regexp    ${concatenated_text}    1


Download Paperboard Order
    ${status}    ${message}=    Run Keyword And Ignore Error    Execute Download Task
    Run Keyword If    '${status}'=='FAIL'    Log    ${message}

Execute Download Task
    ${element}=    Get Webelement    xpath=//div[@class="x-grid-cell-inner" and text()="1"]
    Log    ${element}
    Click Element    ${element}
    # Download the product list
    Press Keys    css:body    CTRL+ALT+g
    # 等待菜单打开的一些操作
    Sleep    2s
    Click Export All Data

    Wait Until Keyword Succeeds    15x    1s    File Should Exist    ${DOWNLOAD_DEFAULT_DIRECTORY}${PAPERBOARD_ORDER_FILE_NAME}
    # Wait for the download to complete
    # Wait Until File Exists    ${DOWNLOAD_FOLDER}/${PRODUCT_LIST_FILE_NAME}
    Log    OK


Execute Sync
    [Arguments]    ${export_file_path}
    synchronize_paperboard_order    ${export_file_path}


Handle Failure
    Log    查询纸板数据无
    Fail    查询纸板数据无