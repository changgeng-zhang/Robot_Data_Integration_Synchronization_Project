*** Keywords ***
Report Reporter Collection Split
    [Arguments]    ${REPORTER_FULL_TEXT}
    ${condition}=    Evaluate    ',' in """${REPORTER_FULL_TEXT}"""

    Run Keyword If    ${condition}
    ...    Report Reporter Collection From List    ${REPORTER_FULL_TEXT}
    ...    ELSE
    ...    Search Select Reporter   ${REPORTER_FULL_TEXT}

Report Reporter Collection From List
    [Arguments]     ${REPORTERS}

    @{reporter_array}=   Split String   ${REPORTERS}  ,

    FOR   ${reporter}  IN   @{reporter_array}
         Search Select Reporter  ${reporter}
    END

Search Select Reporter
    # 支持循环输入
    [Arguments]    ${reporter}
    Input Reporter Name    ${reporter}
    Click Search Reporter
    ${wait_results}=    Run Keyword And Ignore Error    Wait Until Keyword Succeeds    5x    1s    Check Table Data And Execute Select Reporter    ${reporter}
    Run Keyword If    '${wait_results[0]}' == 'FAIL'    Log    报工人查询未加载：${reporter}
    ...    ELSE    Execute Select Reporter    ${reporter}

Check Table Data And Execute Select Reporter
    [Arguments]    ${reporter}
    ${SEARCH_REPORTER_XPATH}=    Set Variable    ${Reporter_Window}//div[contains(text(), '${reporter}')]
    Wait Until Element Is Visible    ${SEARCH_REPORTER_XPATH}    10s
    ${reporter_element}=    Get WebElement    ${SEARCH_REPORTER_XPATH}
    ${text}=  Get Text  ${reporter_element}
    Should Match Regexp    ${text}    ${reporter}

Execute Select Reporter
    [Arguments]    ${reporter}
    ${reporter_element}=    Get WebElement    ${Reporter_Window}//div[contains(text(), '${reporter}')]
    Select Reporter    ${reporter_element}
    Click Confirm Reporter Keep Open
    
Execute Input Reporter
    [Arguments]    ${REPORTER_FULL_TEXT}
    Click Add Reporter
    Report Reporter Collection Split    ${REPORTER_FULL_TEXT}

    Click Confirm Reporter
    Click Save Reporter