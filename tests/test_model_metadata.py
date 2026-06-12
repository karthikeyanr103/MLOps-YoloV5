"""Validation for class names embedded in exported YOLOv5 ONNX models."""

from types import SimpleNamespace

from app.services.onnx_inference import model_class_names
from app.services.postprocessing import COCO_NAMES


class FakeSession:
    """Expose the small ONNX Runtime metadata surface used by the service."""

    def __init__(self, names: str | None) -> None:
        self.names = names

    def get_modelmeta(self) -> SimpleNamespace:
        metadata = {} if self.names is None else {"names": self.names}
        return SimpleNamespace(custom_metadata_map=metadata)


def test_metadata_labels_keep_numeric_class_order() -> None:
    names = model_class_names(FakeSession("{'1': 'bicycle', '0': 'person'}"))

    assert names == ("person", "bicycle")


def test_invalid_metadata_falls_back_to_official_coco_labels() -> None:
    assert model_class_names(FakeSession("not valid metadata")) == COCO_NAMES
