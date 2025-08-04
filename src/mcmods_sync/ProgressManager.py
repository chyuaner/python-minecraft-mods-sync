class ProgressManager:
    def __init__(self, steps: dict[str, float]):
        """
        steps: dict 步驟名稱 -> 佔整體進度比例 (0~1，總和須約等於1)
        例如: {"fetch_mods": 0.1, "download": 0.7, "delete": 0.2}
        """
        self.steps = steps
        self.current_step = None
        self.current_step_weight = 0
        self.total_progress = 0.0

        self.step_progress = 0.0  # 0~1
        self.file_progress = 0.0  # 0~1
        self.file_count = 0
        self.file_index = 0

    def start_step(self, step_name: str, file_count: int = 1):
        self.current_step = step_name
        self.current_step_weight = self.steps.get(step_name, 0)
        self.step_progress = 0.0
        self.file_progress = 0.0
        self.file_count = file_count
        self.file_index = 0

    def update_file_progress(self, file_index: int, file_progress: float):
        """
        file_index: 當前第幾個檔案（0-based）
        file_progress: 該檔案下載進度 0~1
        """
        self.file_index = file_index
        self.file_progress = file_progress
        # 計算當前步驟的總進度（檔案內進度加上檔案間進度）
        per_file_weight = 1 / max(self.file_count, 1)
        self.step_progress = per_file_weight * file_index + per_file_weight * file_progress

    def update_step_progress(self, step_progress: float):
        # 直接設定當前步驟整體進度(0~1)
        self.step_progress = step_progress

    def get_total_progress(self):
        # 計算 total_progress = 已完成步驟總和 + 當前步驟比例 * 當前步驟進度
        total_done = 0.0
        passed = True
        for step, weight in self.steps.items():
            if passed:
                if step == self.current_step:
                    total_done += weight * self.step_progress
                    passed = False
                else:
                    total_done += weight
            else:
                break
        self.total_progress = total_done
        return int(self.total_progress * 100)

    def get_progress_info(self):
        return {
            "total_progress": self.get_total_progress(),
            "step_name": self.current_step,
            "step_progress": int(self.step_progress * 100),
            "file_index": self.file_index,
            "file_count": self.file_count,
            "file_progress": int(self.file_progress * 100),
        }
