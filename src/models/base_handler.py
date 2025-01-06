from abc import ABC, abstractmethod

class BaseModelHandler(ABC):
    @abstractmethod
    def process_image(self, image_path: str):
        """Process an image and return analysis results"""
        pass