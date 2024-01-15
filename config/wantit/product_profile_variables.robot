*** Variables ***

# 企望ERP查询产品档案信息
${QUICK_MENU}    客户产品汇总分析
${QUERY_DETAILS}    明细
${QUERY_DETAILS_ELEMENT}    xpath=//li[@class='x-boundlist-item' and text()='明细']
${IFRAME_LOCATOR}    xpath=//iframe[@name='RptProductListWE-frame']
${WINDOW_LOCATOR}    xpath://div[contains(@class, 'x-window')]

${element_locator}=    css:.x-toolbar-text.x-box-item.x-toolbar-item.x-toolbar-text-default
${EXPORT_ALL_DATA}    xpath=//span[contains(@class, 'x-btn-inner-left') and text()='导出全部数据']

# 页面元素
${Quick_Search_Functionality}    css:input.x-form-field.x-form-empty-field.x-form-text[placeholder='快速检索功能']
${Customer_Product_Summary_Analysis}    xpath://span[@class='x-tree-node-text' and text()='客户产品汇总分析']
${Extend_Display}    xpath=//*[@id="ShowWEIsHidden"]
${Product_Category}    xpath=//input[contains(@name, 'MainReport_ProductCategory') and @placeholder='双击弹出']
${Cardboard_Box}    xpath://label[text()='纸箱']/preceding-sibling::input[contains(@class, 'x-form-cb')]
${Colored_Box}    xpath://label[text()='彩盒']/preceding-sibling::input[contains(@class, 'x-form-cb')]
${Confirm_Product_Category}    xpath=//span[contains(@class, 'x-btn-inner') and text()='确定']
${Completion_Design_Time_From}    xpath=//input[contains(@class, 'x-form-field') and contains(@class, 'x-form-text') and contains(@name, 'MainReport_ConfirmedOnFrom')]
${Completion_Design_Time_To}    xpath=//input[contains(@class, 'x-form-field') and contains(@class, 'x-form-text') and contains(@name, 'MainReport_ConfirmedOnTo')]
${Grouping_Scheme}    xpath=//*[@id="ModelName-inputEl"]
${Search}    xpath=//*[@id="rptquery-btnInnerEl"]