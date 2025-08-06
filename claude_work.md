# Claude Work 工作记录

## 2025-08-06 MinerU文档解析引擎集成

### 功能概述
为OpenWebUI添加MinerU文档解析引擎支持，用于深度解析包含图表的PDF文档。

### 实现细节

#### 1. MinerU Loader实现
创建了专门的MinerULoader类来处理与MinerU API的通信：
- 支持两种处理后端：
  - `pipeline`: 标准处理模式
  - `vlm-sglang-client`: VLM加速模式（Vision-Language Model）
- 使用multipart/form-data格式POST请求
- 自动处理多种响应格式

#### 2. File Type Routing集成
将MinerU集成到文件类型路由系统中：
- 可以为不同文件类型配置使用MinerU
- 支持独立配置每种文件类型的处理参数
- 配置会持久化保存

#### 3. 前端配置界面
为每种文件类型添加了MinerU配置选项：
- MinerU服务器URL输入
- Backend模式选择下拉框
- 条件显示的SGLang服务器URL输入（仅vlm-sglang-client模式需要）

### 技术要点
1. MinerU API使用POST而非PUT请求（与其他loader不同）
2. 需要正确设置multipart/form-data格式
3. vlm-sglang-client模式需要额外的server_url参数
4. 响应可能是JSON对象或字符串，需要灵活处理

### 测试配置
- MinerU服务地址：http://192.168.1.25:30000
- 建议先使用pipeline模式测试
- vlm-sglang-client模式需要配置SGLang服务器地址

### 相关文件
- 后端Loader: `backend/open_webui/retrieval/loaders/mineru.py`
- 主加载器: `backend/open_webui/retrieval/loaders/main.py`
- 前端配置: `src/lib/components/admin/Settings/Documents.svelte`