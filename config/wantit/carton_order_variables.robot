*** Variables ***

# 企望ERP查询纸箱订单（包括彩盒）信息
${QUICK_MENU}    车间生产计划汇总分析
${QUERY_DETAILS}    明细
${QUERY_DETAILS_ELEMENT}    xpath=//li[@class='x-boundlist-item' and text()='明细']
${IFRAME_LOCATOR}    xpath=//iframe[@name='RptWorkPlanDTListWE-frame']
${WINDOW_LOCATOR}    xpath://div[contains(@class, 'x-window')]

${element_locator}=    css:.x-toolbar-text.x-box-item.x-toolbar-item.x-toolbar-text-default
${EXPORT_ALL_DATA}    xpath=//span[contains(@class, 'x-btn-inner-left') and text()='导出全部数据']

# 页面元素
${Quick_Search_Functionality}    css:input.x-form-field.x-form-empty-field.x-form-text[placeholder='快速检索功能']
${Customer_Carton_Order_Analysis}    xpath://span[@class='x-tree-node-text' and text()='车间生产计划汇总分析']
${Extend_Display}    xpath=//*[@id="ShowWEIsHidden"]
${Product_Category}    xpath=//input[contains(@name, 'MainReport_ProductCategory') and @placeholder='双击弹出']
${Cardboard_Box}    xpath://label[text()='纸箱']/preceding-sibling::input[contains(@class, 'x-form-cb')]
${Colored_Box}    xpath://label[text()='彩盒']/preceding-sibling::input[contains(@class, 'x-form-cb')]
${Confirm_Product_Category}    xpath=//span[contains(@class, 'x-btn-inner') and text()='确定']
${Order_Status}    xpath=//input[contains(@name, 'MainReport_Status') and @placeholder='双击弹出']
${Scheduled}    xpath://label[text()='已排程']/preceding-sibling::input[contains(@class, 'x-form-cb')]
${In_Production}    xpath://label[text()='在生产']/preceding-sibling::input[contains(@class, 'x-form-cb')]
${Confirm_Order_Status}    xpath=//span[contains(@class, 'x-btn-inner') and text()='确定']
${Grouping_Scheme}    xpath=//*[@id="ModelName-inputEl"]
${Search}    xpath=//*[@id="rptquery-btnInnerEl"]