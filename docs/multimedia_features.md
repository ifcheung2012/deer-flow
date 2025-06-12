# DeerFlow 多媒体功能

## 概述

DeerFlow 不仅提供文本形式的研究报告，还支持多种多媒体输出格式，包括播客音频和演示文稿。这些功能使研究成果能够以更丰富、更具吸引力的方式呈现，满足不同场景下的需求。

## 播客音频生成

### 功能描述

播客音频生成功能将研究报告转换为高质量的语音内容，适合以下场景：

- 在通勤或运动时收听研究内容
- 为视障用户提供无障碍访问
- 创建教育内容和培训材料
- 制作专业播客节目

### 技术实现

DeerFlow 使用 volcengine TTS API 进行文本到语音的转换：

```python
class VolcengineTTS:
    """使用 volcengine TTS API 的文本转语音工具。"""
    
    def __init__(self):
        self.access_key = os.getenv("VOLCENGINE_ACCESS_KEY")
        self.secret_key = os.getenv("VOLCENGINE_SECRET_KEY")
        self.service_id = os.getenv("VOLCENGINE_SERVICE_ID")
        
    def synthesize_speech(
        self,
        text: str,
        speed_ratio: float = 1.0,
        volume_ratio: float = 1.0,
        pitch_ratio: float = 1.0
    ) -> bytes:
        """将文本转换为语音。"""
        # 实现 volcengine TTS API 调用
        # 返回音频数据
```

### 配置选项

播客音频生成支持以下配置选项：

1. **语速比例 (speed_ratio)**：调整语音的速度，范围 0.5-2.0
2. **音量比例 (volume_ratio)**：调整语音的音量，范围 0.5-2.0
3. **音调比例 (pitch_ratio)**：调整语音的音调，范围 0.5-2.0

### API 接口

```
POST /api/tts
```

**请求体**:

```json
{
  "text": "要转换为语音的文本内容",
  "speed_ratio": 1.0,
  "volume_ratio": 1.0,
  "pitch_ratio": 1.0
}
```

**响应**: 二进制音频数据 (MP3 格式)

### Web 界面集成

在 Web 界面中，播客音频生成功能通过以下组件实现：

```tsx
export function PodcastGenerator({ content }: PodcastGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState("");
  const [settings, setSettings] = useState({
    speedRatio: 1.0,
    volumeRatio: 1.0,
    pitchRatio: 1.0,
  });
  
  const generatePodcast = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/tts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: content,
          ...settings,
        }),
      });
      
      const blob = await response.blob();
      setAudioUrl(URL.createObjectURL(blob));
    } catch (error) {
      console.error('Error generating podcast:', error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  return (
    <div className="podcast-generator">
      {/* 组件内容 */}
    </div>
  );
}
```

## 演示文稿生成

### 功能描述

演示文稿生成功能将研究报告转换为结构化的 PowerPoint 演示文稿，适合以下场景：

- 业务演示和汇报
- 教育讲座和课程
- 会议和研讨会
- 产品介绍和营销

### 技术实现

DeerFlow 使用 marp-cli 工具生成演示文稿：

```python
def generate_presentation(content: str, template: str = "default") -> bytes:
    """生成演示文稿。"""
    # 创建临时 Markdown 文件
    with tempfile.NamedTemporaryFile(suffix=".md", mode="w", delete=False) as f:
        f.write(format_content_for_presentation(content, template))
        temp_md_path = f.name
    
    # 创建临时输出目录
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = os.path.join(temp_dir, "presentation.pptx")
        
        # 调用 marp-cli 生成演示文稿
        subprocess.run([
            "marp",
            temp_md_path,
            "--output", output_path,
            "--pptx",
            "--theme", template,
        ], check=True)
        
        # 读取生成的文件
        with open(output_path, "rb") as f:
            presentation_data = f.read()
    
    # 清理临时文件
    os.unlink(temp_md_path)
    
    return presentation_data
```

### 模板系统

演示文稿生成支持多种模板，定义在 `src/ppt/templates/` 目录中：

1. **default**: 默认模板，适合一般演示
2. **academic**: 学术风格模板，适合研究报告
3. **business**: 商业风格模板，适合业务汇报
4. **creative**: 创意风格模板，适合设计和创意内容

### 内容处理

演示文稿生成过程中，会对研究报告内容进行特殊处理：

1. **自动分割**：根据标题和内容长度自动分割幻灯片
2. **提取关键点**：从长段落中提取关键点，以便于演示
3. **格式优化**：调整格式以适应幻灯片显示
4. **图表生成**：将数据转换为图表（如果可能）

### API 接口

```
POST /api/ppt
```

**请求体**:

```json
{
  "content": "要转换为演示文稿的内容",
  "template": "default"
}
```

**响应**: 二进制演示文稿数据 (PPTX 格式)

### Web 界面集成

在 Web 界面中，演示文稿生成功能通过以下组件实现：

```tsx
export function PresentationGenerator({ content }: PresentationGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState("");
  const [template, setTemplate] = useState("default");
  
  const generatePresentation = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch('/api/ppt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          template,
        }),
      });
      
      const blob = await response.blob();
      setDownloadUrl(URL.createObjectURL(blob));
    } catch (error) {
      console.error('Error generating presentation:', error);
    } finally {
      setIsGenerating(false);
    }
  };
  
  return (
    <div className="presentation-generator">
      {/* 组件内容 */}
    </div>
  );
}
```

## 图表和可视化

### 功能描述

DeerFlow 支持在研究报告中生成各种图表和可视化，以增强数据表现力：

- 折线图和面积图：显示趋势和时间序列数据
- 柱状图和条形图：比较不同类别的数值
- 饼图和环形图：显示比例和分布
- 散点图：显示相关性和分布
- 热图：显示复杂的多变量数据

### 技术实现

图表生成使用 Python 的 Matplotlib 和 Plotly 库，通过 Python REPL 工具执行：

```python
def generate_chart(chart_type, data, options=None):
    """生成图表。"""
    if chart_type == "line":
        plt.figure(figsize=(10, 6))
        plt.plot(data["x"], data["y"])
        plt.title(data.get("title", ""))
        plt.xlabel(data.get("xlabel", ""))
        plt.ylabel(data.get("ylabel", ""))
        
        # 保存图表到临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        plt.savefig(temp_file.name)
        plt.close()
        
        # 将图片转换为 base64
        with open(temp_file.name, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # 清理临时文件
        os.unlink(temp_file.name)
        
        return f"data:image/png;base64,{image_data}"
    
    # 其他图表类型的实现...
```

### 集成到研究流程

图表生成通过以下步骤集成到研究流程中：

1. **数据收集**：研究员代理收集相关数据
2. **数据处理**：编码员代理处理和分析数据
3. **图表生成**：编码员代理使用 Python REPL 工具生成图表
4. **报告集成**：报告生成器将图表嵌入到最终报告中

### 示例用法

```python
# 在编码员代理中生成图表
import matplotlib.pyplot as plt
import numpy as np
import base64
import io

# 生成数据
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 创建图表
plt.figure(figsize=(10, 6))
plt.plot(x, y)
plt.title("Sine Wave")
plt.xlabel("X")
plt.ylabel("sin(X)")

# 将图表转换为 base64
buf = io.BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)
image_base64 = base64.b64encode(buf.read()).decode('utf-8')
plt.close()

# 返回 Markdown 格式的图片
markdown_image = f"![Sine Wave](data:image/png;base64,{image_base64})"
print(markdown_image)
```

## 未来扩展计划

DeerFlow 计划在未来版本中添加更多多媒体功能：

1. **视频生成**：将研究报告转换为简短的视频摘要
2. **交互式可视化**：支持交互式图表和数据探索
3. **AR/VR 集成**：将研究内容呈现在增强现实或虚拟现实环境中
4. **多语言音频支持**：扩展 TTS 功能以支持更多语言和声音
5. **实时协作**：支持多用户实时协作编辑多媒体内容 