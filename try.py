from typing import Optional, List, Any
from pydantic import BaseModel, Field, root_validator
import torch
import pickle

class MyModel(BaseModel):
    name: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    collaborators: Optional[List[str]] = Field(default=[])
    institute: Optional[str] = Field(default=None)
    embed: Optional[Any] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True


# 创建模型实例
embed_tensor = torch.tensor([1.0, 2.0, 3.0])
model_instance = MyModel(
    name="John Doe",
    bio="Researcher in AI",
    collaborators=["Alice", "Bob"],
    institute="Tech University",
    embed=embed_tensor
)

print(model_instance)

# 保存模型实例到文件
with open('model_instance.pkl', 'wb') as f:
    pickle.dump(model_instance, f)

# 从文件加载模型实例
with open('model_instance.pkl', 'rb') as f:
    loaded_instance = pickle.load(f)

print(loaded_instance)
print(loaded_instance.embed)  # 输出: tensor([1., 2., 3.])
