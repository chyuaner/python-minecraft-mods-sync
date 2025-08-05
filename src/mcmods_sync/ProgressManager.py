# src/mcmods_sync/progress_manager.py

class ProgressManager:
    def __init__(self, step_weights: dict[str, float]):
        self.set_weights(step_weights)

    def set_weights(self, step_weights: dict[str, float]):
        total = sum(step_weights.values()) or 1
        self.steps = {
            step: {
                "weight": weight / total,
                "progress": 0.0
            }
            for step, weight in step_weights.items()
        }
        self.current_step: str | None = None
        self.current_step_weight: float = 0
        self.total_progress: float = 0.0

        self.step_progress: float = 0.0
        self.file_progress: float = 0.0
        self.current_filename: str | None = None
        self.file_count: int = 0
        self.file_index: int = 0

    def start_step(self, step_name: str, file_count: int = 1):
        self.current_step = step_name
        self.current_step_weight = self.steps.get(step_name, {}).get("weight", 0)
        self.step_progress = 0.0
        self.file_progress = 0.0
        self.file_count = file_count
        self.file_index = 0

        if file_count == 0:
            self.update_step_progress(1.0)

    def update_file_progress(self, file_index: int, file_progress: float):
        self.file_index = file_index
        self.file_progress = file_progress
        per_file_weight = 1 / max(self.file_count, 1)
        self.step_progress = per_file_weight * file_index + per_file_weight * file_progress

        if self.current_step is not None:
            self.steps[self.current_step]["progress"] = self.step_progress

    def update_step_progress(self, progress: float):
        clamped = max(0.0, min(1.0, progress))
        if self.current_step in self.steps:
            self.steps[self.current_step]["progress"] = clamped
            self.step_progress = clamped

            # 若不是使用多檔案處理，則 file_progress 與 step_progress 相同
            if self.file_count <= 1:
                self.file_progress = clamped

    def get_total_progress(self) -> float:
        return sum(step["weight"] * step["progress"] for step in self.steps.values())

    def get_progress_info(self) -> dict:
        return {
            "total": self.get_total_progress(),
            "current_step": self.current_step,
            "file_index": self.file_index,
            "file_count": self.file_count,
            "file_progress": self.file_progress,
            "current_filename": self.current_filename,  # 新增
            "step_progress": self.step_progress,
            "steps": {
                name: {
                    "weight": data["weight"],
                    "progress": data["progress"]
                } for name, data in self.steps.items()
            }
        }
