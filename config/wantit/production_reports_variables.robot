*** Variables ***

# 生产报工
${QUICK_MENU}    车间数据收集
${Corrugation_Machine}    瓦楞机
${IFRAME_LOCATOR}    xpath=//iframe[@name='WorkProductionD-frame']
${WINDOW_LOCATOR}    xpath://div[contains(@class, 'x-window')]

${element_locator}=    css:.x-toolbar-text.x-box-item.x-toolbar-item.x-toolbar-text-default
${EXPORT_ALL_DATA}    xpath=//span[contains(@class, 'x-btn-inner-left') and text()='导出全部数据']

# 页面元素：定位订单
${Quick_Search_Functionality}    css:input.x-form-field.x-form-empty-field.x-form-text[placeholder='快速检索功能']
${Workshop_Data_Collection}    xpath://span[@class='x-tree-node-text' and text()='车间数据收集']
${Process_Category}    xpath=//input[contains(@name, 'WITDC_ProcessCode')]
${Machine_Tool}    xpath=//input[contains(@name, 'WITDC_Machine')]
${Work_Team}    xpath=//input[contains(@name, 'WITDC_ShiftID')]
${Scheduling_Order_Number}    xpath=//input[contains(@name, 'WITDC_WorkPlanID')]
${Barcode}    xpath=//input[contains(@name, 'WITDC_WEBarcode')]

# 良品
${Report_Machine_Tool}    xpath=//input[@id="WEB-车间数据收集Machine-inputEl" and @name="Machine"]
${Report_Work_Team}    xpath=//input[@id="WEB-车间数据收集ShiftID-inputEl" and @name="ShiftID"]
${Good_Product_Quantity}    xpath=//input[@id="WEB-车间数据收集GoodQty-inputEl" and @name="GoodQty"]
${Production_Start_Time}    xpath=//input[@id="WEB-车间数据收集ProdStartDatetime-inputEl" and @name="ProdStartDatetime"]
${Production_Finish_Time}    xpath=//*[@id="WEB-车间数据收集ProdFinishDateTime-inputEl" and @name="ProdFinishDateTime"]
${Delete_Report}    XPath=//img[contains(@class, 'x-action-col-icon') and contains(@class, 'x-action-col-0') and contains(@src, 'javascript/img/delete.gif')]
${Save_Report}    XPath=//img[contains(@class, 'x-action-col-icon') and contains(@class, 'x-action-col-1') and contains(@src, 'javascript/img/save.gif')]
${Good_Product_TR}    xpath=//tr[contains(@class, 'x-grid-row') and contains(@class, 'x-grid-data-row') and contains(@class, 'x-grid-row-selected')]
# 良品表格关键元素定位
${ELEMENT_XPATH}    //*[contains(text(), 'X2311240143')]
${PARENT_XPATH}    ${ELEMENT_XPATH}/../..
${DIV_XPATH}    ${PARENT_XPATH}//td/div
${DELETE_ELEMENT_TEXT}   确定要删除当前选中记录？

${Confirm_Delete_Window}    xpath=//div[contains(@class, 'x-form-display-field') and starts-with(@id, 'messagebox-') and ends-with(@id, '-inputEl')]
${Confirm_Delete}    xpath=//span[contains(@class, 'x-btn-inner') and contains(text(), '是')]

${Save_Report_Success}    XPath=//img[contains(@class, 'x-action-col-icon') and contains(@class, 'x-action-col-1') and contains(@class, 'x-item-disabled') and contains(@src, 'javascript/img/save.gif')]

# 不良品
${Defective_Product_Grid_Panel}    //div[@id='WorkProdBGridPanel']
${Save_Defect}    xpath=${Defective_Product_Grid_Panel}//span[contains(@class,'x-btn-inner') and contains(text(),'保存(F4)')]
${Defect_Process}    xpath=${Defective_Product_Grid_Panel}//span[contains(@class,'x-btn-inner') and contains(text(),'本道次品')]
${Defect_Previous_Process}    xpath=${Defective_Product_Grid_Panel}//span[contains(@class,'x-btn-inner') and contains(text(),'前道次品')]

${Defective_Product_Grid_Panel_Body}    //div[@id='WorkProdBGridPanel-body']
${Operation_Filter}    xpath=${Defective_Product_Grid_Panel_Body}//input[@name='Item' and @class='x-form-field x-form-text']
${Defect_Cause}    xpath=${Defective_Product_Grid_Panel_Body}//input[@id="WEB-车间数据收集-次品情况Cause-inputEl" and @name="Cause"]
${Defective_Quantity}    xpath=${Defective_Product_Grid_Panel_Body}//*[@id="WEB-车间数据收集-次品情况BadQty-inputEl" and @name="BadQty"]
${Save_Defective_Product}    xpath=${Defective_Product_Grid_Panel_Body}//*[contains(@class, 'x-action-col-icon') and contains(@class, 'x-action-col-1') and contains(@src, 'javascript/img/save.gif')]

# 不良良品表格关键元素定位
${DEFECTIVE_PRODUCT_ELEMENT_XPATH}    ${Defective_Product_Grid_Panel_Body}//*[contains(text(), '-1')]
${DEFECTIVE_PRODUCT_PARENT_XPATH}    ${DEFECTIVE_PRODUCT_ELEMENT_XPATH}/../..
${DEFECTIVE_PRODUCT_DIV_XPATH}    ${DEFECTIVE_PRODUCT_PARENT_XPATH}//td/div

# 报工人
${Reporter_Grid_Panel}    //div[@id='WorkProdFeeGridPanel']
${Create_Reporter}    xpath=${Reporter_Grid_Panel}//span[contains(@class,'x-btn-inner') and contains(text(),'添加工人')]
${Save_Single_Item_Reporter}    xpath=${Reporter_Grid_Panel}//*[contains(@class, 'x-action-col-icon') and contains(@class, 'x-action-col-1') and contains(@src, 'javascript/img/save.gif')]
${Disabled_Save_Single_Item_Reporter}    xpath=${Reporter_Grid_Panel}//*[contains(@class, 'x-action-col-icon') and contains(@class, 'x-action-col-1') and contains(@src, 'javascript/img/save.gif') and contains(@class, 'x-item-disabled')]
${Save_Reporter}    xpath=${Reporter_Grid_Panel}//span[contains(@class,'x-btn-inner') and contains(text(),'保存(F4)')]

${Reporter_Window}    //div[@id='LookUpWorkerWindow']
${Reporter_Name}    xpath=${Reporter_Window}//input[@name="WITDC_StaffNameFilter"]
${Search_Reporter}    xpath=${Reporter_Window}//span[contains(@class, 'x-btn-inner') and contains(text(), '查询(F5)')]
${Confirm_Reporter}    xpath=${Reporter_Window}//span[contains(@class, 'x-btn-inner') and contains(text(), '确定(S)')]
${Confirm_Reporter_Keep_Open}    xpath=${Reporter_Window}//span[contains(@class, 'x-btn-inner') and contains(text(), '确定(不关闭H)')]
${Reporter_Window_Close}    XPath=${Reporter_Window}//img[contains(@class, 'x-tool-img') and contains(@class, 'x-tool-close')]

${REPORTER_WINDOW_ELEMENT_XPATH}    ${Reporter_Window}//div[contains(text(), '李万里')]
${REPORTER_GRID_PANEL_ELEMENT_XPATH}    ${Reporter_Window}//div[contains(text(), '李万里')]