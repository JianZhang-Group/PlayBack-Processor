import re


class PathChecker:
    def __init__(self, path: str):
        self.path = path

    def contains_chinese(self) -> bool:
        """检测是否包含中文"""
        return bool(re.search(r"[\u4e00-\u9fff]", self.path))

    def contains_space(self) -> bool:
        """检测是否包含空格"""
        return " " in self.path

    def contains_chinese_or_space(self) -> bool:
        """检测是否包含中文或空格"""
        return self.contains_chinese() or self.contains_space()


if __name__ == "__main__":
    # 使用示例
    checker = PathChecker("C:/My Files/测试/abc.txt")
    print(checker.contains_chinese())  # True
    print(checker.contains_space())  # True
    print(checker.contains_chinese_or_space())  # True
