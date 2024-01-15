*** Keywords ***
# 输入关键字，快速定位菜单
Input Carton Order Quick Menu
    [Arguments]    ${QUICK_MENU}
    Wait Until Page Contains Element    ${Quick_Search_Functionality}    timeout=10s
    Input Text    ${Quick_Search_Functionality}    ${QUICK_MENU}

Click Menu
    Wait Until Page Contains Element    ${Customer_Carton_Order_Analysis}    timeout=10s
    Click Element    ${Customer_Carton_Order_Analysis}

Click Extend Display
    Wait Until Page Contains Element    ${Extend_Display}    timeout=10s
    Click Element    ${Extend_Display}

Select Product Category
    Wait Until Page Contains Element    ${Product_Category}    timeout=10s
    Double Click Element    ${Product_Category}

# 纸箱
Select Cardboard Box
    Click Element    ${Cardboard_Box}
# 彩盒
Select Colored Box
    Click Element    ${Colored_Box}
# 确定产品类别
Click Confirm Product Category
    # Click Element    xpath=//span[contains(@class, 'x-btn-inner') and text()='确定']
    Execute JavaScript    var buttons = document.getElementsByClassName('x-btn-inner x-btn-inner-center'); for(var i = 0; i < buttons.length; i++) { if(buttons[i].textContent.trim() === '确定') { buttons[i].click(); break; } }

# 设计完成时间
Select Order Status
    Wait Until Page Contains Element    ${Order_Status}    timeout=10s
    Double Click Element    ${Order_Status}

# 纸箱
Select Scheduled
    Click Element    ${Scheduled}
# 彩盒
Select In Production
    Click Element    ${In_Production}
# 确定产品类别
Click Confirm Order Status
    # Click Element    xpath=//span[contains(@class, 'x-btn-inner') and text()='确定']
    Execute JavaScript    var buttons = document.getElementsByClassName('x-btn-inner x-btn-inner-center'); for(var i = 0; i < buttons.length; i++) { if(buttons[i].textContent.trim() === '确定') { buttons[i].click(); break; } }


# 查询明细
Input Query Details
    [Arguments]    ${QUERY_DETAILS}
    Input Text    ${Grouping_Scheme}    ${QUERY_DETAILS}

Click Search Button
    Click Element    ${Search}

Click Export All Data
    Wait Until Page Contains Element    ${EXPORT_ALL_DATA}    timeout=10s
    Click Element    ${EXPORT_ALL_DATA}
