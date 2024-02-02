## 数据集成与同步项目（使用 Robot Framework 开发自己的 RPA 业务）

### 项目说明
```bash
robot_project/
|-- tests/
|   |-- login/
|   |   |-- test_login.robot
|   |-- registration/
|   |   |-- test_registration.robot
|-- resources/
|   |-- keywords.robot
|   |-- data/
|   |   |-- test_data.csv
|-- results/
|-- logs/
|-- config/
|   |-- settings.robot
|   |-- variables.robot
|-- scripts/
|-- README.md
|-- requirements.txt
```
**tests/** : 存放测试用例文件，按功能或模块进行划分。每个测试用例文件包含一个或多个测试用例。

**resources/**: 存放关键字定义、测试数据和其他资源文件。

**results/**: 存放测试运行后生成的结果文件，如日志和报告。

**logs/**: 存放测试日志文件。

**config/**: 存放配置文件，包括全局设置和变量定义。

**scripts/**: 存放可能由测试用例调用的脚本文件，如自定义库。

**README.md**: 项目说明文档，描述项目的结构、用法和其他相关信息。

**requirements.txt**: 包含项目的依赖项列表，可用于安装所需的 Python 包。

### 重点配置说明
**ignore_paperboard_process_flag**: 1
* 忽略纸板线工序，设置为True后由服务端过滤掉纸板线工序，注意RS不可设置为True

**ignore_carton_process_flag**: 1,
* 忽略纸箱订单工序流程，部份ERP的纸箱订单中没有工序流程信息，可设置为True后可不传递该参数，使用服务端产品档案的工序流程

**erp_schedule_obj_id_expand_logic_flag**: 0,
* 扩展ERP逻辑，依赖ERP中的OBJ ID字段，实现订单撤单

