*** Settings ***
Resource    ../../config/settings.robot
Resource    ../../config/variables.robot
Resource    ../../resources/keywords.robot
Resource    ../../config/wantit/production_reports_variables.robot
Resource    ../../resources/wantit/production_reports_keywords.robot
Resource    test_login.robot
Resource    test_production_reports_defects.robot
Resource    test_production_reports_reporter.robot

Library    Collections
Library    ../../scripts/excel/pr/retrieve_production_reports.py
Library    ../../scripts/excel/pr/synchronize_operation_results.py

*** Test Cases ***
Main Test
    # 登录
    Run Keyword    Login Test
    Set Browser Implicit Wait    10 seconds
    Input Quick Menu    ${QUICK_MENU}

    # 调用智控宝获取报工记录
    ${task_reporting_records}=    retrieve_production_reports
    ${record_length}=    Get Length    ${task_reporting_records}

    # 检查是否有需要填报的数据
    Run Keyword If    ${record_length} <= 1    Fatal Error    无报工数据，流程结束。

    # 循环输入ERP
    ${sync_records}    Create List    # 创建一个空列表
    FOR    ${element}    IN RANGE    1    ${record_length}
        Click Menu
        # 使用 Select Frame 切换到 iframe
        Wait Until Element Is Visible    ${IFRAME_LOCATOR}    timeout=10s
        Select Frame    ${IFRAME_LOCATOR}

        # 获取参数
        ${record}    Set Variable    ${task_reporting_records[${element}]}
        Log    Array element at index ${element}: ${record}
        ${box_order_code}    Set Variable    ${record[0]}
        ${erp_process_type}    Set Variable    ${record[16]}
        ${reporting_machine_tool}    Set Variable    ${record[17]}
        ${reporting_team}    Set Variable    ${record[7]}
        ${erp_scheduling_order_number}    Set Variable    ${record[12]}
        ${completed_quantity}    Set Variable    ${record[3]}
        ${defective_quantity}    Set Variable    ${record[4]}
        ${defect_description}    Set Variable    ${record[5]}
        ${operator_information}    Set Variable    ${record[6]}
        ${start_production_time}    Set Variable    ${record[15]}
        ${reporting_time}    Set Variable    ${record[8]}
        ${reporting_id}    Set Variable    ${record[11]}
        # 信息输入
        ${status}    ${message}=    Run Keyword And Ignore Error  Production Reports Test    ${box_order_code}    ${erp_process_type}    ${reporting_machine_tool}    ${reporting_team}    ${erp_scheduling_order_number}    ${completed_quantity}    ${defective_quantity}    ${defect_description}    ${operator_information}    ${start_production_time}    ${reporting_time}

        # 执行异常发送消息及业务处理
        ${sync_info}=    Set Variable If    '${status}'=='FAIL'    [${reporting_id}, 回写失败, ${message}]    [${reporting_id}, 回写成功, 回写成功]
        Append To List    ${sync_records}    ${sync_info}
        Log    ${sync_records}
        Unselect Frame
    END
    
    synchronize_operation_results_tuple    ${sync_records}
    # 关闭浏览器
    Close Browser

*** Keywords ***
Production Reports Test
    [Documentation]    This test case demonstrates production reports
    [Arguments]    ${box_order_code}    ${erp_process_type}    ${reporting_machine_tool}    ${reporting_team}    ${erp_scheduling_order_number}    ${completed_quantity}    ${defective_quantity}    ${defect_description}    ${operator_information}    ${start_production_time}    ${reporting_time}

    # 清空工序类型
    Clear Process Category

    # 机床
    Input Machine Tool    ${reporting_machine_tool}

    # 班组
    Input Work Team    ${reporting_team}

    # 排序单号
    Input Scheduling Order Number    ${erp_scheduling_order_number}

    # 条码（套件工号）
    Input Barcode    ${box_order_code}

    # 良品
    ${wait_results}=    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    10x    1s    Check Table Data And Execute Good Product Input
    Run Keyword If    '${wait_results[0]}' == 'FAIL'    Handle Failure
    ...    ELSE    Input Good Product Information    ${box_order_code}    ${completed_quantity}    ${start_production_time}    ${reporting_time}

    # 不良品（等待良品保存成功）
    ${status}    Run Keyword And Return Status    Wait Until Element Is Visible    ${Save_Report_Success}    10s
    Run Keyword If    '${status}' == 'True'    Report Defects Collection Split    ${defect_description}
    ...    ELSE    Delete Report
    
    # 报工人
    Execute Input Reporter    ${operator_information}

Delete Report
    Log    删除报工记录,关闭浏览器
    Click Delete
    Fatal Error    报工流程中断，删除报工记录

Handle Failure
    Log    查询数据无
    Fatal Error    查询数据无


Check Table Data And Execute Good Product Input
    @{elements}=    Get WebElements    xpath=//div[@class="x-grid-cell-inner"]
    # 遍历元素列表并执行操作：拼接
    ${concatenated_text}    Set Variable    ${EMPTY}    # Initialize variable as an empty string
    ${index}    Set Variable    0
    FOR    ${element}    IN    @{elements}
        Log    ${element}
        ${text}    Get Text    ${element}    # Get text of the current element
        ${concatenated_text}    Set Variable    ${concatenated_text} ${text}    # Concatenate text to the variable
        ${index}=    Evaluate    ${index} + 1
        Exit For Loop If    ${index} == 5
    END
    Log    Element Text: ${concatenated_text}    # Log the text of the current element
    Should Match Regexp    ${concatenated_text}    1


Input Good Product Information
    [Arguments]    ${BOX_ORDER_CODE_TEXT}    ${COMPLETED_QUANTITY_TEXT}    ${START_PRODUCTION_TIME_TEXT}    ${REPORTING_TIME_TEXT}
    ${status}    ${message}=    Run Keyword And Ignore Error    Execute Input Good Product    ${BOX_ORDER_CODE_TEXT}    ${COMPLETED_QUANTITY_TEXT}    ${START_PRODUCTION_TIME_TEXT}    ${REPORTING_TIME_TEXT}
    Run Keyword If    '${status}'=='FAIL'    Log    ${message}

Execute Input Good Product
    [Arguments]    ${BOX_ORDER_CODE_TEXT}    ${COMPLETED_QUANTITY_TEXT}    ${START_PRODUCTION_TIME_TEXT}    ${REPORTING_TIME_TEXT}
    # 输入良品数、生产开始时间、生产结束时间

    # 动态生成xpath，使用订单号动态定位
    ${MODIFIED_BOX_ORDER_CODE_TEXT}=    Evaluate    "${BOX_ORDER_CODE_TEXT}"[:-1]
    ${BOX_ORDER_CODE_XPATH}=    Set Variable    //*[contains(text(), '${MODIFIED_BOX_ORDER_CODE_TEXT}')]
    Wait Until Element Is Visible    ${BOX_ORDER_CODE_XPATH}    10s
    # 定位元素
    ${element}=    Get WebElement    ${BOX_ORDER_CODE_XPATH}
    # 在这里可以继续进行其他操作，例如获取文本内容
    ${text}=  Get Text  ${element}
    Log  Element Text: ${text}

    # 获取子元素的xpath
    ${CURRENT_DIV_XPATH}=    Set Variable    ${BOX_ORDER_CODE_XPATH}/../..//td/div
    ${index}    Set Variable    0
    @{div_elements}=    Get Webelements    ${CURRENT_DIV_XPATH}
    FOR    ${div}    IN    @{div_elements}
        ${text}=    Get Text    ${div}
        Run Keyword If    '${index}' == '5'    Input Good Product Quantity    ${COMPLETED_QUANTITY_TEXT}
        ...    ELSE IF    '${index}' == '8'    Input Production Start Time    ${div}    ${START_PRODUCTION_TIME_TEXT}
        ...    ELSE IF    '${index}' == '10'    Input Production Finish Time    ${div}    ${REPORTING_TIME_TEXT}
        ...    ELSE    No Operation
        ${index}=    Evaluate    ${index} + 1
    END

    Click Save
    Log    Input Good Product Done.
    
Sync Successful Modify List Element
    [Arguments]    ${RECORD}
    Set List Value    ${RECORD}    10    成功
    
Sync Failed Modify List Element
    [Arguments]    ${RECORD}    ${FAIL_MESSAGE}
    Set List Value    ${RECORD}    10    成功
    Set List Value    ${RECORD}    14    ${FAIL_MESSAGE}
