*** Keywords ***
# 输入关键字，快速定位
Input Quick Menu
    [Arguments]    ${QUICK_MENU}
    Wait Until Page Contains Element    ${Quick_Search_Functionality}    timeout=10s
    Input Text    ${Quick_Search_Functionality}    ${QUICK_MENU}

Click Menu
    Wait Until Page Contains Element    ${Workshop_Data_Collection}    timeout=10s
    Double Click Element    ${Workshop_Data_Collection}

Clear Process Category
    Clear Element Text    ${Process_Category}
    
Input Process Category
    [Arguments]    ${Process_Category_Text}
    Input Text    ${Process_Category}    ${Process_Category_Text}

Input Machine Tool
    [Arguments]    ${Machine_Tool_Text}
    Input Text    ${Machine_Tool}    ${Machine_Tool_Text}

Input Work Team
    [Arguments]    ${Work_Team_Text}
    Input Text    ${Work_Team}    ${Work_Team_Text}

Input Scheduling Order Number
    [Arguments]    ${Scheduling_Order_Number_Text}
    Input Text    ${Scheduling_Order_Number}    ${Scheduling_Order_Number_Text}

Input Barcode
    [Arguments]    ${Barcode_Text}
    Input Text    ${Barcode}    ${Barcode_Text}
    Press Keys    ${Barcode}    ENTER

# 报工信息
Input Report Machine Tool
    [Arguments]    ${Report_Work_Team_Text}
    Input Text    ${Report_Machine_Tool}    ${Report_Work_Team_Text}

Input Report Work Team
    [Arguments]    ${Report_Work_Team_Text}
    Input Text    ${Report_Work_Team}    ${Report_Work_Team_Text}

Input Good Product Quantity
    [Arguments]    ${Good_Product_Quantity_Text}
    Input Text    ${Good_Product_Quantity}    ${Good_Product_Quantity_Text}

Input Production Start Time
    [Arguments]    ${Div_Element}    ${Production_Start_Time_Text}
    Wait Until Element Is Visible    ${Div_Element}    10s
    Click Element    ${Div_Element}
    Wait Until Element Is Visible    ${Production_Start_Time}    10s
    Input Text    ${Production_Start_Time}    ${Production_Start_Time_Text}

Input Production Finish Time
    [Arguments]    ${Div_Element}    ${Production_Finish_Time_Text}
    Wait Until Element Is Visible    ${Div_Element}    10s
    Click Element    ${Div_Element}
    Wait Until Element Is Visible    ${Production_Finish_Time}    10s
    Input Text    ${Production_Finish_Time}    ${Production_Finish_Time_Text}
    
Click Save
    Click Element    ${Save_Report}

Click Delete
    Wait Until Element Is Visible    ${Delete_Report}    10s
    Click Element    ${Delete_Report}
    ${xpath}=    Set Variable    //div[contains(text(), '${DELETE_ELEMENT_TEXT}')]
    Wait Until Element Is Visible    ${xpath}    10s
    # Click Element    ${Confirm_Delete}
    Execute JavaScript    var buttons = document.getElementsByClassName('x-btn-inner x-btn-inner-center'); for(var i = 0; i < buttons.length; i++) { if(buttons[i].textContent.trim() === '是') { buttons[i].click(); break; } }

# 不良信息
Click Add Defect
    Click Element    ${Defect_Process}

Input Operation Filter
    Input Text    ${Operation_Filter}    -1

Clear Operation Filter
    Clear Element Text    ${Operation_Filter}

Input Defect_Cause
    [Arguments]    ${Div_Element}    ${Defect_Cause_Text}
    Wait Until Element Is Visible    ${Div_Element}    10s
    Click Element    ${Div_Element}
    Wait Until Element Is Visible    ${Defect_Cause}    10s
    Input Text    ${Defect_Cause}    ${Defect_Cause_Text}

Input Defective_Quantity
    [Arguments]    ${Div_Element}    ${Defective_Quantity_Text}
    Wait Until Element Is Visible    ${Div_Element}    10s
    Click Element    ${Div_Element}
    Wait Until Element Is Visible    ${Defective_Quantity}    10s
    Input Text    ${Defective_Quantity}    ${Defective_Quantity_Text}

Click Save Defective
    Click Element    ${Save_Defective_Product}

Click Save Defective F4
    Click Element    ${Save_Defect}

# 报工人信息
Click Add Reporter
    Click Element    ${Create_Reporter}

Input Reporter Name
    [Arguments]    ${Reporter_Name_Text}
    Wait Until Element Is Visible    ${Reporter_Name}    10s
    Input Text    ${Reporter_Name}    ${Reporter_Name_Text}

Click Search Reporter
    Click Element    ${Search_Reporter}

Select Reporter
    [Arguments]    ${Div_Element}
    Wait Until Element Is Visible    ${Div_Element}    10s
    Click Element    ${Div_Element}
    
Click Confirm Reporter
    # Click Element    ${Confirm_Reporter}
    Click Element    ${Reporter_Window_Close}

Click Confirm Reporter Keep Open
    Click Element    ${Confirm_Reporter_Keep_Open}

Click Save Reporter
    Wait Until Element Is Visible    ${Save_Single_Item_Reporter}    10s
    Click Element    ${Save_Reporter}
    # Wait Until Keyword Succeeds    10x    1s    Element Attribute Value Should Be    ${Save_Single_Item_Reporter}    unselectable    on
    Wait Until Element Is Visible    ${Disabled_Save_Single_Item_Reporter}    10s




