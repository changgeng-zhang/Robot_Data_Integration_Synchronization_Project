*** Keywords ***
Report Defects Collection Split
    [Arguments]    ${DEFECT_DESCRIPTION_FULL_TEXT}
    ${condition}=    Evaluate    ',' in """${DEFECT_DESCRIPTION_FULL_TEXT}"""

    Run Keyword If    ${condition}
    ...    Report Defects Collection From List    ${DEFECT_DESCRIPTION_FULL_TEXT}
    ...    ELSE
    ...    Report Defects Split   ${DEFECT_DESCRIPTION_FULL_TEXT}

Report Defects Collection From List
    [Arguments]     ${DEFECT_DESCRIPTIONS}

    @{defect_description_array}=   Split String   ${DEFECT_DESCRIPTIONS}  ,

    FOR   ${description}  IN   @{defect_description_array}
         Report Defects Split  ${description}
    END

Report Defects Split
    [Arguments]    ${DEFECT_DESCRIPTION_TEXT}
    ${condition}=    Evaluate    '_' in """${DEFECT_DESCRIPTION_TEXT}"""

    Run Keyword If    ${condition}
    ...    Report Defects From List    ${DEFECT_DESCRIPTION_TEXT}
    ...    ELSE    
    ...    Log    ${DEFECT_DESCRIPTION_TEXT}：不符合不良信息标准格式

Report Defects From List
    [Arguments]     ${DEFECT_DESCRIPTION}

    @{defect_description_array}=   Split String   ${DEFECT_DESCRIPTION}  _

    ${array_length}=    Get Length    ${defect_description_array}

    Run Keyword If    ${array_length} == 2    
    ...    Report Defects    ${defect_description_array[0]}    ${defect_description_array[1]}
    ...    ELSE    
    ...    Log    ${DEFECT_DESCRIPTION}：不符合不良信息标准格式

Report Defects
    [Arguments]    ${DEFECT_DESCRIPTION_TEXT}    ${DEFECTIVE_QUANTITY_TEXT}
    # 点击添加不良按钮
    Click Add Defect
    ${defect_wait_results}=    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    10x    1s    Check Table Data And Execute Defective Product Input
    Run Keyword If    '${defect_wait_results[0]}' == 'FAIL'    
    ...    Log    添加不良失败
    ...    ELSE    
    ...    Input Defective Product Information    ${DEFECT_DESCRIPTION_TEXT}    ${DEFECTIVE_QUANTITY_TEXT}

Check Table Data And Execute Defective Product Input
    # 验证点了添加不良按钮后，可输入项是否出现
    @{elements}=    Get WebElements    xpath=//div[@id='WorkProdBGridPanel-body']//div[@class="x-grid-cell-inner"]
    # 遍历元素列表并执行操作：拼接
    ${concatenated_text}    Set Variable    ${EMPTY}    # Initialize variable as an empty string
    FOR    ${element}    IN    @{elements}
        # ${text}    Get Text    ${element}    # Get text of the current element
        ${keyword_text}=    Run Keyword And Ignore Error    Get Text    ${element}
        ${text}=    Set Variable If    "'PASS' in ${keyword_text} and ${keyword_text[1]} != ''"    ${keyword_text[1]}    ${EMPTY}
        ${concatenated_text}=    Set Variable    ${concatenated_text} ${text}
    END
    Log    Check Defective Product Input Element Text: ${concatenated_text}    # Log the text of the current element
    Should Match Regexp    ${concatenated_text}    -1 0 0


Input Defective Product Information
    [Arguments]    ${DEFECT_DESCRIPTION_TEXT}    ${DEFECTIVE_QUANTITY_TEXT}
    Clear Operation Filter
    Input Operation Filter
    # 临时用sleep，应该等待 -1
    Sleep    2
    ${status}    ${message}=    Run Keyword And Ignore Error    Execute Input Defective Product    ${DEFECT_DESCRIPTION_TEXT}    ${DEFECTIVE_QUANTITY_TEXT}
    Run Keyword If    '${status}'=='FAIL'    
    ...    Log    ${message}


Execute Input Defective Product
    [Arguments]    ${DEFECT_DESCRIPTION_TEXT}    ${DEFECTIVE_QUANTITY_TEXT}
    # 点击本道次品
    # 等待-1出现
    # 输入-1，过滤出唯一输入
    # 输入致次原因（不良原因）
    # 输入次品数
    # 点击保存

    # 动态生成xpath，使用订单号动态定位
    # ${xpath}=    Set Variable    //*[contains(text(), '${DEFECTIVE_PRODUCT_ELEMENT_TEXT}')]
    Wait Until Element Is Visible    ${DEFECTIVE_PRODUCT_ELEMENT_XPATH}    10s
    # 定位元素
    ${defective_product_element}=    Get WebElement    ${DEFECTIVE_PRODUCT_ELEMENT_XPATH}
    # 在这里可以继续进行其他操作，例如获取文本内容
    ${defective_product_text}=  Get Text  ${defective_product_element}
    Log  Element Text: ${defective_product_text}

    # 获取子元素的xpath
    ${defective_product_index}    Set Variable    0
    @{defective_product_div_elements}=    Get Webelements    ${DEFECTIVE_PRODUCT_DIV_XPATH}
    FOR    ${defective_product_div}    IN    @{defective_product_div_elements}
        ${defective_product_text}=    Get Text    ${defective_product_div}
        Run Keyword If    '${defective_product_index}' == '4'    Input Defect_Cause    ${defective_product_div}    ${DEFECT_DESCRIPTION_TEXT}
        ...    ELSE IF    '${defective_product_index}' == '2'    Input Defective_Quantity    ${defective_product_div}    ${DEFECTIVE_QUANTITY_TEXT}
        ...    ELSE    No Operation
        ${defective_product_index}=    Evaluate    ${defective_product_index} + 1
        # 输入完不良原因后就退出循环
        Exit For Loop If    ${defective_product_index} == 5
    END

    Click Save Defective
    # 临时用sleep，应该等待保存按钮变灰为不可用，确保保存成功
    Sleep    2
    Log    Input Defective Product Done.