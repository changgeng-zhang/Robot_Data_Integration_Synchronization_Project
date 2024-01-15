*** Variables ***

# 企望ERP查询纸箱订单（包括彩盒）信息
${QUICK_MENU}    生产情况查询
${Corrugation_Machine}    瓦楞机
${IFRAME_LOCATOR}    xpath=//iframe[@name='WorkProductionRpt-frame']
${WINDOW_LOCATOR}    xpath://div[contains(@class, 'x-window')]

${element_locator}=    css:.x-toolbar-text.x-box-item.x-toolbar-item.x-toolbar-text-default
${EXPORT_ALL_DATA}    xpath=//span[contains(@class, 'x-btn-inner-left') and text()='导出全部数据']

# 页面元素
${Quick_Search_Functionality}    css:input.x-form-field.x-form-empty-field.x-form-text[placeholder='快速检索功能']
${Production_Status_Inquiry}    xpath://span[@class='x-tree-node-text' and text()='生产情况查询']
${Product_Category}    xpath=//input[contains(@name, 'WITDC_ProductCategory') and @placeholder='双击弹出']
${Cardboard_Box}    xpath://label[text()='纸箱']/preceding-sibling::input[contains(@class, 'x-form-cb')]
${Colored_Box}    xpath://label[text()='彩盒']/preceding-sibling::input[contains(@class, 'x-form-cb')]
${Confirm_Product_Category}    xpath=//span[contains(@class, 'x-btn-inner') and text()='确定']
${Process_Category}    xpath=//input[contains(@name, 'WITDC_ProcessCode')]
${Corrugation_Machine_Option}    xpath=//li[@role='option' and @class='x-boundlist-item' and text()='瓦楞机']
${Start_Time_From}    xpath=//input[contains(@class, 'x-form-field') and contains(@class, 'x-form-text') and contains(@name, 'WITDC_ProdStartDatetimeFrom')]
${Start_Time_To}    xpath=//input[contains(@class, 'x-form-field') and contains(@class, 'x-form-text') and contains(@name, 'WITDC_ProdStartDatetimeTo')]
${Entry_Time_From}    xpath=//input[contains(@class, 'x-form-field') and contains(@class, 'x-form-text') and contains(@name, 'WITDC_KeyInOnFrom')]
${Entry_Time_To}    xpath=//input[contains(@class, 'x-form-field') and contains(@class, 'x-form-text') and contains(@name, 'WITDC_KeyInOnTo')]
${Search}    xpath=//span[contains(@class, 'x-btn-inner') and text()='查询(F5)']