# PDF 深度解析功能实现方案

## 功能需求
在聊天和知识库上传 PDF 文件时，添加一个"深度解析"开关按钮。当开关打开时，PDF 文件将使用专门的深度解析引擎处理，以获得更好的文档解析效果。

## 技术可行性分析

### 现有架构分析

#### 1. 文件上传流程
```
前端组件(MessageInput/KnowledgeBase) 
  ↓ uploadFileHandler
  ↓ uploadFile API (/api/v1/files/)
  ↓ 后端 files.py
  ↓ process_file (retrieval.py)
  ↓ Loader类处理
```

#### 2. 当前文件处理机制
- **前端**：通过 `uploadFile` API 上传文件，可携带 metadata
- **后端**：根据文件类型和配置选择解析引擎
- **Loader类**：已支持文件类型路由功能，可根据文件扩展名选择不同引擎

#### 3. 现有引擎选项
- Tika
- Docling  
- External (外部API)
- Datalab Marker
- Document Intelligence
- Mistral OCR

## 实现方案

### 方案一：扩展现有文件类型路由（推荐）

利用现有的文件类型路由机制，添加深度解析模式：

1. **前端改动**
   - 在 MessageInput.svelte 和 KnowledgeBase.svelte 添加深度解析开关
   - 开关状态存储在组件状态中
   - 上传时通过 metadata 传递深度解析标志

2. **后端改动**
   - 在 process_file 函数中识别深度解析标志
   - 当标志为 true 且文件为 PDF 时，使用专门的深度解析引擎
   - 可配置深度解析使用的具体引擎和参数

### 方案二：新增独立的深度解析路径

创建专门的深度解析上传端点：

1. **新增 API 端点**
   - `/api/v1/files/deep-parse` - 专门处理深度解析请求
   - 复用现有文件上传逻辑，但使用不同的处理引擎

2. **前端选择性调用**
   - 根据开关状态选择调用普通上传或深度解析上传

### 方案三：动态引擎切换

在现有架构基础上实现动态引擎切换：

1. **metadata 扩展**
   ```javascript
   metadata: {
     collection_name: "...",
     deep_parse: true,
     deep_parse_engine: "datalab_marker" // 或其他引擎
   }
   ```

2. **Loader 类改进**
   - 检查 metadata 中的 deep_parse 标志
   - 动态切换到深度解析引擎

## 具体实现步骤（基于方案一）

### 1. 前端组件修改

#### MessageInput.svelte
```svelte
// 添加深度解析状态
let deepParseEnabled = false;

// 修改 uploadFileHandler
const uploadFileHandler = async (file, fullContext: boolean = false) => {
    // ... 现有代码 ...
    
    const metadata = {
        collection_name: $settings?.knowledge?.selectedCollection?.name ?? null,
        deep_parse: deepParseEnabled && file.type === 'application/pdf'
    };
    
    const uploadedFile = await uploadFile(localStorage.token, file, metadata);
    // ... 现有代码 ...
};

// 添加开关UI
<label class="flex items-center gap-2">
    <input type="checkbox" bind:checked={deepParseEnabled} />
    <span>{$i18n.t('Deep Parse PDF')}</span>
</label>
```

#### KnowledgeBase.svelte
```svelte
// 类似的修改
let deepParseEnabled = false;

const uploadFileHandler = async (file) => {
    // ... 现有代码 ...
    
    const metadata = {
        collection_name: knowledge.id,
        deep_parse: deepParseEnabled && file.type === 'application/pdf'
    };
    
    const uploadedFile = await uploadFile(localStorage.token, file, metadata);
    // ... 现有代码 ...
};
```

### 2. 后端处理逻辑

#### files.py
```python
@router.post("/", response_model=FileModelResponse)
def upload_file(
    request: Request,
    file: UploadFile = File(...),
    metadata: Optional[dict | str] = Form(None),
    # ... 其他参数 ...
):
    # ... 现有代码 ...
    
    file_metadata = metadata if metadata else {}
    deep_parse = file_metadata.get("deep_parse", False)
    
    # 传递深度解析标志到 process_file
    if deep_parse:
        file_metadata["deep_parse_engine"] = request.app.state.config.DEEP_PARSE_ENGINE
    
    # ... 继续处理 ...
```

#### retrieval.py
```python
def process_file(
    request: Request,
    form_data: ProcessFileForm,
    user=Depends(get_verified_user),
):
    # ... 现有代码 ...
    
    file = Files.get_file_by_id(form_data.file_id)
    
    # 检查是否需要深度解析
    deep_parse = file.meta.get("deep_parse", False)
    
    if deep_parse and file.filename.lower().endswith(".pdf"):
        # 使用深度解析引擎
        engine = file.meta.get("deep_parse_engine", "datalab_marker")
    else:
        # 使用常规引擎
        engine = request.app.state.config.CONTENT_EXTRACTION_ENGINE
    
    # ... 继续处理 ...
```

#### main.py (Loader类)
```python
def _get_loader(self, filename: str, file_content_type: str, file_path: str):
    file_ext = filename.split(".")[-1].lower()
    
    # 检查是否是深度解析请求
    if self.kwargs.get("deep_parse") and file_ext == "pdf":
        engine = self.kwargs.get("deep_parse_engine", "datalab_marker")
        # 使用指定的深度解析引擎
        return self._get_engine_loader(engine, file_path, file_content_type)
    
    # ... 现有的文件类型路由逻辑 ...
```

### 3. 配置管理

#### config.py
```python
# 添加深度解析配置
DEEP_PARSE_ENGINE = PersistentConfig(
    "DEEP_PARSE_ENGINE",
    "rag.deep_parse_engine",
    "datalab_marker",  # 默认使用 Datalab Marker
)

DEEP_PARSE_CONFIG = PersistentConfig(
    "DEEP_PARSE_CONFIG",
    "rag.deep_parse_config",
    {
        "datalab_marker": {
            "api_key": "",
            "do_picture_description": True,
            "picture_description_mode": "detailed"
        },
        "docling": {
            "image_export_mode": "ocr",
            "table_mode": "accurate"
        }
    }
)
```

### 4. UI 优化

#### 添加开关组件
```svelte
<div class="flex items-center justify-between p-2 border rounded">
    <div class="flex items-center gap-2">
        <svg class="w-5 h-5"><!-- PDF图标 --></svg>
        <span class="text-sm font-medium">
            {$i18n.t('Deep PDF Parsing')}
        </span>
        <Tooltip content={$i18n.t('Enable advanced PDF parsing for better text extraction')} />
    </div>
    <label class="switch">
        <input type="checkbox" bind:checked={deepParseEnabled} />
        <span class="slider"></span>
    </label>
</div>
```

## 优势分析

### 方案一优势
1. **复用现有架构**：最小化代码改动
2. **灵活性高**：可根据需要扩展到其他文件类型
3. **配置简单**：通过 metadata 传递配置
4. **向后兼容**：不影响现有功能

### 实现难点
1. **状态管理**：需要在前端组件中管理深度解析开关状态
2. **引擎配置**：需要为不同深度解析引擎提供配置界面
3. **性能考虑**：深度解析可能耗时较长，需要良好的进度提示

## 建议的实现顺序

1. **Phase 1：基础功能**
   - 添加前端开关UI
   - 实现 metadata 传递
   - 后端识别深度解析标志

2. **Phase 2：引擎集成**
   - 集成 Datalab Marker 或 Docling 作为深度解析引擎
   - 添加引擎配置界面

3. **Phase 3：优化提升**
   - 添加进度提示
   - 支持批量深度解析
   - 添加解析质量对比功能

## 测试要点

1. **功能测试**
   - 开关切换正常
   - PDF 文件正确路由到深度解析引擎
   - 非 PDF 文件不受影响

2. **性能测试**
   - 深度解析耗时监控
   - 并发上传处理

3. **兼容性测试**
   - 现有文件上传功能正常
   - 文件类型路由功能正常

## 总结

该功能完全可行，建议采用方案一（扩展现有文件类型路由），因为：
1. 代码改动最小
2. 复用现有架构
3. 易于维护和扩展
4. 不影响现有功能

预计开发时间：2-3天完成基础功能，1周完成完整功能。