# OpenWebUI 文件类型路由功能实现指南

## 功能概述
实现了文件类型路由功能，允许不同类型的文件（PDF、Word、Excel、PPT、图片等）使用不同的解析引擎和配置。

## 核心问题与解决方案

### 1. 配置持久化问题

#### 问题描述
- 前端配置保存后，刷新页面配置丢失
- 配置无法持久化到数据库

#### 根本原因
1. **后端 PersistentConfig 对象处理错误**
   - `FILE_TYPE_ENGINE_MAPPING` 是 PersistentConfig 对象，但代码直接赋值而不是赋值给 `.value` 属性
   - 没有调用 `.save()` 方法持久化到数据库

2. **AppConfig 注册缺失**
   - `FILE_TYPE_ENGINE_MAPPING` 没有被注册到 AppConfig 实例的 `_state` 中
   - 导致 `AttributeError: Config key 'FILE_TYPE_ENGINE_MAPPING' not found`

#### 解决方案

##### 1. 修复后端配置更新逻辑 (`/backend/open_webui/routers/retrieval.py`)

```python
# 错误的方式
request.app.state.config.FILE_TYPE_ENGINE_MAPPING = form_data.FILE_TYPE_ENGINE_MAPPING

# 正确的方式
if hasattr(request.app.state.config.FILE_TYPE_ENGINE_MAPPING, 'value'):
    request.app.state.config.FILE_TYPE_ENGINE_MAPPING.value = (
        form_data.FILE_TYPE_ENGINE_MAPPING
        if form_data.FILE_TYPE_ENGINE_MAPPING is not None
        else request.app.state.config.FILE_TYPE_ENGINE_MAPPING.value
    )
    request.app.state.config.FILE_TYPE_ENGINE_MAPPING.save()  # 重要：调用save()方法持久化
```

##### 2. 修复配置获取逻辑

```python
# 获取配置时从 .value 属性读取
"FILE_TYPE_ENGINE_MAPPING": request.app.state.config.FILE_TYPE_ENGINE_MAPPING.value 
    if hasattr(request.app.state.config.FILE_TYPE_ENGINE_MAPPING, 'value') 
    else getattr(request.app.state.config, 'FILE_TYPE_ENGINE_MAPPING', {})
```

##### 3. 注册 PersistentConfig 到 AppConfig (`/backend/open_webui/main.py`)

```python
# 1. 导入 FILE_TYPE_ENGINE_MAPPING
from open_webui.config import (
    ...
    CONTENT_EXTRACTION_ENGINE,
    FILE_TYPE_ENGINE_MAPPING,  # 添加这行
    DATALAB_MARKER_API_KEY,
    ...
)

# 2. 注册到 app.state.config
app.state.config.CONTENT_EXTRACTION_ENGINE = CONTENT_EXTRACTION_ENGINE
app.state.config.FILE_TYPE_ENGINE_MAPPING = FILE_TYPE_ENGINE_MAPPING  # 添加这行
app.state.config.DATALAB_MARKER_API_KEY = DATALAB_MARKER_API_KEY
```

### 2. 前端配置管理问题

#### 问题描述
- 使用独立的 `fileTypeEngineMapping` 变量管理配置
- 配置加载时会覆盖从后端获取的数据

#### 解决方案

```javascript
// 修复前端配置加载逻辑 (src/lib/components/admin/Settings/Documents.svelte)
onMount(async () => {
    const config = await getRAGConfig(localStorage.token);
    
    // 先赋值给 RAGConfig
    RAGConfig = config;
    
    // 只有当后端有配置时才复制到 fileTypeEngineMapping
    if (config.FILE_TYPE_ENGINE_MAPPING && Object.keys(config.FILE_TYPE_ENGINE_MAPPING).length > 0) {
        fileTypeEngineMapping = JSON.parse(JSON.stringify(config.FILE_TYPE_ENGINE_MAPPING));
    } else {
        // 只有当后端没有配置时才使用默认值
        RAGConfig.FILE_TYPE_ENGINE_MAPPING = fileTypeEngineMapping;
    }
});
```

## 实现文件清单

### 后端文件

1. **`/backend/open_webui/config.py`**
   - 定义 `FILE_TYPE_ENGINE_MAPPING` PersistentConfig 对象
   ```python
   FILE_TYPE_ENGINE_MAPPING = PersistentConfig(
       "FILE_TYPE_ENGINE_MAPPING",
       "rag.file_type_engine_mapping",
       {},
   )
   ```

2. **`/backend/open_webui/routers/retrieval.py`**
   - 在 `ConfigForm` 中添加字段
   - 处理配置的保存和获取
   - 传递配置给 Loader

3. **`/backend/open_webui/retrieval/loaders/main.py`**
   - 实现文件类型路由逻辑
   - 根据文件扩展名选择对应的引擎

4. **`/backend/open_webui/main.py`**
   - 导入并注册 `FILE_TYPE_ENGINE_MAPPING` 到 AppConfig

### 前端文件

1. **`/src/lib/components/admin/Settings/Documents.svelte`**
   - 添加 "File Type Routing" 选项
   - 为每种文件类型提供配置界面
   - 处理配置的保存和加载

## 配置结构

```javascript
FILE_TYPE_ENGINE_MAPPING: {
    pdf: { 
        engine: 'tika',  // 可选: '', 'external', 'tika', 'docling', 等
        config: {
            TIKA_SERVER_URL: 'http://localhost:9998',
            // 其他引擎相关配置...
        }
    },
    docx: { engine: '', config: {...} },
    excel: { engine: '', config: {...} },
    ppt: { engine: '', config: {...} },
    image: { engine: '', config: {...} },
    default: { engine: '', config: {...} }
}
```

## 关键点总结

### PersistentConfig 使用要点

1. **赋值**：必须赋值给 `.value` 属性，不能直接赋值给对象
2. **保存**：修改后必须调用 `.save()` 方法持久化
3. **读取**：从 `.value` 属性读取值
4. **注册**：必须在 `main.py` 中注册到 `app.state.config`

### 调试技巧

1. **检查 PersistentConfig 是否注册**
   ```python
   # 在 main.py 中查找
   app.state.config.YOUR_CONFIG_NAME = YOUR_CONFIG_NAME
   ```

2. **检查配置保存逻辑**
   ```python
   # 确保使用 .value 和 .save()
   config.YOUR_CONFIG.value = new_value
   config.YOUR_CONFIG.save()
   ```

3. **检查前端配置加载**
   - 避免用默认值覆盖后端配置
   - 使用深拷贝避免引用问题

## 测试步骤

1. 重启后端服务
2. 在设置中选择 "File Type Routing"
3. 配置不同文件类型的引擎
4. 保存配置
5. 刷新页面验证配置是否持久化
6. 上传文件测试路由功能是否生效

## 注意事项

1. **配置键名格式**：PersistentConfig 的路径使用小写下划线格式（如 `rag.file_type_engine_mapping`）
2. **类型检查**：使用 `hasattr()` 检查是否有 `.value` 属性，兼容不同的配置对象
3. **默认值处理**：只在后端没有配置时才使用前端的默认值