import enum


class ReportStyle(enum.Enum):
    """报告风格枚举类"""
    ACADEMIC = "academic"         # 学术风格
    POPULAR_SCIENCE = "popular_science"  # 科普风格
    NEWS = "news"                 # 新闻风格
    SOCIAL_MEDIA = "social_media"  # 社交媒体风格
