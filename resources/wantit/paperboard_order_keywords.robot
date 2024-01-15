*** Keywords ***
# 输入关键字，快速定位菜单
Input Quick Menu
    [Arguments]    ${QUICK_MENU}
    Wait Until Page Contains Element    ${Quick_Search_Functionality}    timeout=10s
    Input Text    ${Quick_Search_Functionality}    ${QUICK_MENU}

Click Menu
    Wait Until Page Contains Element    ${Production_Status_Inquiry}    timeout=10s
    Click Element    ${Production_Status_Inquiry}

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

# 开始时间
Clear Start Time From
    Clear Element Text    ${Start_Time_From}
    
Clear Start Time To
    Clear Element Text    ${Start_Time_To}

# 录入时间
Input Entry Time From
    [Arguments]    ${Form}
    Input Text    ${Entry_Time_From}    ${Form}

Input Entry Time To
    [Arguments]    ${To}
    Input Text    ${Entry_Time_To}    ${To}

Input Process Category
    Input Text    ${Process_Category}    ${Corrugation_Machine}

Select Corrugation Machine
    Wait Until Page Contains Element    ${Corrugation_Machine_Option}    timeout=10s
    Click Element    ${Corrugation_Machine_Option}

Click Search Button
    Click Element    ${Search}

Click Export All Data
    Wait Until Page Contains Element    ${EXPORT_ALL_DATA}    timeout=10s
    Click Element    ${EXPORT_ALL_DATA}
