# 高级 PDF 解析功能实现说明

## 功能概述
在 OpenWebUI 中实现了高级 PDF 解析功能，允许用户在聊天时选择使用更强大的 PDF 解析引擎来处理 PDF 文件。

## 实现细节

### 1. 后端修改

#### `/backend/open_webui/retrieval/loaders/main.py`
- 在 `_get_loader` 方法中添加了对 `advanced_pdf` 的支持
- 当检测到 `use_advanced_pdf` 标志时，使用配置的高级 PDF 引擎

```python
# Check for advanced PDF processing first
if file_ext == "pdf" and mapping.get("advanced_pdf") and self.kwargs.get("use_advanced_pdf"):
    selected_engine = mapping["advanced_pdf"].get("engine", "")
    selected_config = mapping["advanced_pdf"].get("config", {})
```

#### `/backend/open_webui/routers/retrieval.py`
- 在 `process_file` 函数中添加了对 `use_advanced_pdf` 标志的处理
- 从文件的 metadata 中读取该标志并传递给 Loader

```python
# Check if advanced PDF parsing is requested
use_advanced_pdf = file.meta.get("use_advanced_pdf", False) if file.meta else False

loader = Loader(
    engine=request.app.state.config.CONTENT_EXTRACTION_ENGINE,
    FILE_TYPE_ENGINE_MAPPING=...,
    use_advanced_pdf=use_advanced_pdf,
    ...
)
```

### 2. 前端修改

#### `/src/lib/components/admin/Settings/Documents.svelte`
- 在 `fileTypeEngineMapping` 中添加了 `advanced_pdf` 配置项
- 添加了 Advanced PDF 配置界面，支持多种引擎选择
- 修复了初始化逻辑，确保 `advanced_pdf` 属性始终存在

```javascript
// Ensure advanced_pdf exists with proper structure
if (!fileTypeEngineMapping.advanced_pdf) {
    fileTypeEngineMapping.advanced_pdf = {
        engine: '',
        config: { ... }
    };
}
```

#### `/src/lib/components/chat/MessageInput.svelte`
- 添加了 `advancedPdfEnabled` 状态变量
- 在文件上传时，如果开启了高级 PDF 解析，在 metadata 中添加标志
- 添加了高级 PDF 解析按钮，用户可以点击开启/关闭

```javascript
// Add advanced PDF parsing flag if enabled
if (advancedPdfEnabled && file.type === 'application/pdf') {
    metadata = {
        ...metadata,
        use_advanced_pdf: true
    };
}
```

### 3. 支持的高级 PDF 引擎

配置界面支持以下引擎：
- External（外部 API）
- Tika
- Docling
- Datalab Marker API
- Document Intelligence
- Mistral OCR

每种引擎都有相应的配置选项，如 API Key、服务器 URL 等。

## 使用流程

1. **管理员配置**：
   - 进入 Admin Settings > Documents
   - 选择 "File Type Routing" 作为内容提取引擎
   - 在 "Advanced PDF" 部分选择并配置所需的引擎

2. **用户使用**：
   - 在聊天界面点击 "Advanced PDF" 按钮开启高级解析
   - 上传 PDF 文件
   - 系统会自动使用配置的高级引擎处理 PDF

## 技术特点

1. **灵活性**：支持多种解析引擎，管理员可根据需求选择
2. **用户控制**：用户可以选择是否使用高级解析
3. **向后兼容**：不影响现有的文件上传和处理功能
4. **错误处理**：添加了安全检查，防止访问未定义的属性

## 注意事项

1. 高级 PDF 解析可能需要更多的处理时间
2. 某些引擎需要额外的 API Key 或服务配置
3. 建议在生产环境使用前进行充分测试

## 故障排除

如果 Documents 设置页面无法加载：
1. 检查 `fileTypeEngineMapping` 初始化是否正确
2. 确保所有必需的属性都存在
3. 查看浏览器控制台的错误信息

## 后续优化建议

1. 添加解析进度提示
2. 支持批量高级 PDF 处理
3. 添加解析质量对比功能
4. 实现解析结果缓存